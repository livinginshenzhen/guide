"""Builds the Landmarks-page map includes from Aliyun DataV boundaries (GCJ-02, converted to WGS-84).
  _includes/shenzhen-map-base.html         main city map (base layers + labels)
  _includes/shenzhen-map-inset-base.html   zoomed core map (Shekou to Luohu)
  _includes/shenzhen-map-pins.html         pins for the main map   (reads _data/landmark_pins.yml)
  _includes/shenzhen-map-inset-pins.html   pins for the inset
Run:  python3 _tools/build_shenzhen_map.py   (needs network)"""
import json, math, subprocess

VIEWS = {  # lon0 = left edge, lat1 = top edge, P = pixels per degree of latitude
    'main':  dict(lon0=113.68, lat1=22.94, P=1050.0, lon1=114.70, lat0=22.34),
    'inset': dict(lon0=113.85, lat1=22.60, P=3500.0, lon1=114.14, lat0=22.45),
}
COS = math.cos(math.radians(22.63))
for v in VIEWS.values():
    v['K'] = v['P'] * COS
    v['W'] = round((v['lon1'] - v['lon0']) * v['K']); v['H'] = round((v['lat1'] - v['lat0']) * v['P'])

WATER, SZ_LAND, OTHER_LAND = '#d3e4f1', '#f7f5ee', '#e2dfd3'

def gcj_to_wgs(lon, lat):
    a, ee = 6378245.0, 0.00669342162296594323
    def tl(x, y):
        r = -100.0+2.0*x+3.0*y+0.2*y*y+0.1*x*y+0.2*math.sqrt(abs(x))
        r += (20.0*math.sin(6.0*x*math.pi)+20.0*math.sin(2.0*x*math.pi))*2.0/3.0
        r += (20.0*math.sin(y*math.pi)+40.0*math.sin(y/3.0*math.pi))*2.0/3.0
        r += (160.0*math.sin(y/12.0*math.pi)+320*math.sin(y*math.pi/30.0))*2.0/3.0
        return r
    def tn(x, y):
        r = 300.0+x+2.0*y+0.1*x*x+0.1*x*y+0.1*math.sqrt(abs(x))
        r += (20.0*math.sin(6.0*x*math.pi)+20.0*math.sin(2.0*x*math.pi))*2.0/3.0
        r += (20.0*math.sin(x*math.pi)+40.0*math.sin(x/3.0*math.pi))*2.0/3.0
        r += (150.0*math.sin(x/12.0*math.pi)+300.0*math.sin(x/30.0*math.pi))*2.0/3.0
        return r
    dlat = tl(lon-105.0, lat-35.0); dlon = tn(lon-105.0, lat-35.0)
    rl = lat/180.0*math.pi; m = math.sin(rl); m = 1-ee*m*m; sm = math.sqrt(m)
    dlat = (dlat*180.0)/((a*(1-ee))/(m*sm)*math.pi); dlon = (dlon*180.0)/(a/sm*math.cos(rl)*math.pi)
    return lon-dlon, lat-dlat

def proj(v, lon, lat): return (lon-v['lon0'])*v['K'], (v['lat1']-lat)*v['P']

def clip(poly, W, H, m=6):  # Sutherland-Hodgman against the view rectangle (+margin)
    def edge(pts, inside, inter):
        out = []
        for i, cur in enumerate(pts):
            prev = pts[i-1]
            if inside(cur):
                if not inside(prev): out.append(inter(prev, cur))
                out.append(cur)
            elif inside(prev): out.append(inter(prev, cur))
        return out
    def ix(x0):
        return lambda a, b: (x0, a[1]+(b[1]-a[1])*(x0-a[0])/((b[0]-a[0]) or 1e-9))
    def iy(y0):
        return lambda a, b: (a[0]+(b[0]-a[0])*(y0-a[1])/((b[1]-a[1]) or 1e-9), y0)
    pts = poly
    for ins, it in [(lambda p: p[0] >= -m, ix(-m)), (lambda p: p[0] <= W+m, ix(W+m)), (lambda p: p[1] >= -m, iy(-m)), (lambda p: p[1] <= H+m, iy(H+m))]:
        if not pts: break
        pts = edge(pts, ins, it)
    return pts

def rdp(pts, eps):
    if len(pts) < 3: return pts
    (x1,y1),(x2,y2) = pts[0], pts[-1]; dx,dy = x2-x1, y2-y1; n = math.hypot(dx,dy) or 1e-9
    dmax, idx = 0, 0
    for i in range(1, len(pts)-1):
        d = abs(dy*pts[i][0]-dx*pts[i][1]+x2*y1-y2*x1)/n
        if d > dmax: dmax, idx = d, i
    if dmax > eps: return rdp(pts[:idx+1], eps)[:-1] + rdp(pts[idx:], eps)
    return [pts[0], pts[-1]]

def path_for(geom, v, eps):
    d = ''
    for poly in geom['coordinates']:
        for ring in poly:
            pts = [proj(v, *gcj_to_wgs(lon, lat)) for lon, lat in ring]
            if len(pts) > 3:
                far = max(range(len(pts)), key=lambda i: (pts[i][0]-pts[0][0])**2+(pts[i][1]-pts[0][1])**2)
                pts = rdp(pts[:far+1], eps)[:-1] + rdp(pts[far:], eps)
            pts = clip(pts, v['W'], v['H'])
            if len(pts) >= 3: d += 'M' + 'L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + 'Z'
    return d

def fetch(code):
    return json.loads(subprocess.run(['curl','-s','-m','60',f'https://geo.datav.aliyun.com/areas_v3/bound/{code}.json'],capture_output=True,text=True).stdout)

full = fetch('440300_full'); outline = fetch('440300')
neighbours = {c: fetch(c) for c in ['810000','441900','441300','440100','440400','442000','820000']}
EN = {'罗湖区':'Luohu','福田区':'Futian','南山区':'Nanshan','宝安区':"Bao’an",'龙岗区':'Longgang','盐田区':'Yantian','龙华区':'Longhua','坪山区':'Pingshan','光明区':'Guangming'}

def text(v, lon, lat, s, size=12, fill='#7d8ba0', italic=False, weight=600, halo='#f7f5ee', anchor='middle'):
    x, y = proj(v, lon, lat)
    st = ' font-style="italic"' if italic else ''
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" letter-spacing=".04em" fill="{fill}" '
            f'stroke="{halo}" stroke-width="3" paint-order="stroke"{st}>{s}</text>')

LABELS = {
 'main': [('d','Nanshan',113.965,22.605),('d','Futian',114.06,22.585),('d','Longgang',114.26,22.745),('d','Bao’an',113.83,22.77),
          ('d','Longhua',None,None),('d','Guangming',None,None),('d','Luohu',None,None),('d','Yantian',None,None),('d','Pingshan',None,None),
          ('o','HONG KONG',114.14,22.43),('o','DONGGUAN',113.97,22.925),('o','HUIZHOU',114.5,22.865),
          ('w','Pearl River Estuary',113.745,22.45),('w','Shenzhen Bay',113.99,22.488),('w','Daya Bay',114.62,22.52),('x','Dapeng',114.50,22.60)],
 'inset': [('d','Nanshan',113.905,22.575),('d','Futian',114.06,22.585),('d','Luohu',114.12,22.595),('o','HONG KONG',114.075,22.455),('w','Shenzhen Bay',113.995,22.505),('w','Qianhai',113.865,22.51)],
}
centres = {EN[f['properties']['name']]: f['properties']['center'] for f in full['features']}

def base(name):
    v = VIEWS[name]; eps = 0.7 if name == 'main' else 0.6
    out = [f'<svg viewBox="0 0 {v["W"]} {v["H"]}" role="img" aria-label="{"Map of Shenzhen showing where each landmark is" if name=="main" else "Zoomed map of Shenzhen from Shekou to Luohu showing the landmarks in the core"}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block;font-family:inherit">',
           f'<rect width="{v["W"]}" height="{v["H"]}" fill="{WATER}"/>']
    for code, g in neighbours.items():
        out.append(f'<path d="{path_for(g["features"][0]["geometry"], v, eps*2.5)}" fill="{OTHER_LAND}" stroke="#c9c5b6" stroke-width="1"/>')
    for f in full['features']:
        out.append(f'<path d="{path_for(f["geometry"], v, eps)}" fill="{SZ_LAND}" stroke="#bfc9d4" stroke-width="1" stroke-linejoin="round"/>')
    out.append(f'<path d="{path_for(outline["features"][0]["geometry"], v, eps)}" fill="none" stroke="#6b7b8f" stroke-width="1.6" stroke-linejoin="round"/>')
    for kind, label, lon, lat in LABELS[name]:
        if lon is None:
            cx, cy = centres[label]; lon, lat = gcj_to_wgs(cx, cy)
        if kind == 'd': out.append(text(v, lon, lat, label.upper()))
        elif kind == 'x': out.append(text(v, lon, lat, label.upper()))
        elif kind == 'o': out.append(text(v, lon, lat, label, size=12, fill='#8f8a78', halo=OTHER_LAND, italic=True, weight=600))
        else: out.append(text(v, lon, lat, label, size=11, fill='#6d8aa6', halo=WATER, italic=True, weight=500))
    if name == 'main':  # outline of the inset area
        i = VIEWS['inset']; x0, y0 = proj(v, i['lon0'], i['lat1']); x1, y1 = proj(v, i['lon1'], i['lat0'])
        out.append(f'<a href="#landmark-map-zoom" class="map-zoom-link" role="button" aria-expanded="false" aria-label="Show or hide the inset map of Shekou to Luohu"><rect x="{x0:.1f}" y="{y0:.1f}" width="{x1-x0:.1f}" height="{y1-y0:.1f}" fill="#2563eb" fill-opacity="0.05" stroke="#2563eb" stroke-width="1.6" stroke-dasharray="5 3" pointer-events="all"/>'
                   f'<text x="{x0+4:.1f}" y="{y0-6:.1f}" font-size="11" font-weight="700" fill="#2563eb" stroke="{WATER}" stroke-width="3" paint-order="stroke">Inset Section &#9662;</text></a>')
    out.append('{% include ' + ('shenzhen-map-pins.html' if name == 'main' else 'shenzhen-map-inset-pins.html') + ' %}')
    out.append('</svg>')
    open(f'_includes/shenzhen-map-{"base" if name=="main" else "inset-base"}.html', 'w', encoding='utf-8').write('\n'.join(out))

def pins(name):
    v = VIEWS[name]; r, hit, rs = (5, 13, 2) if name == 'main' else (7, 17, 2.5)
    cond = ''
    if name == 'inset':
        cond = f'{{% if p.lat >= {v["lat0"]} and p.lat <= {v["lat1"]} and p.lon >= {v["lon0"]} and p.lon <= {v["lon1"]} %}}'
    body = (f'{{% assign cx = p.lon | minus: {v["lon0"]} | times: {v["K"]:.2f} | round: 1 %}}{{% assign cy = {v["lat1"]} | minus: p.lat | times: {v["P"]:.0f} | round: 1 %}}'
            f'<a href="#{{{{ p.id }}}}" class="map-pin" aria-label="{{{{ p.name | escape }}}}"><circle cx="{{{{ cx }}}}" cy="{{{{ cy }}}}" r="{hit}" fill="transparent" data-tip="{{{{ p.name | escape }}}}{{% if p.approx %}} (approximate location){{% endif %}}"/>'
            f'{{% if p.approx %}}<circle cx="{{{{ cx }}}}" cy="{{{{ cy }}}}" r="{r}" fill="#fff" stroke="#2563eb" stroke-width="{rs}" stroke-dasharray="3 2" pointer-events="none"/>'
            f'{{% else %}}<circle cx="{{{{ cx }}}}" cy="{{{{ cy }}}}" r="{r+0.5}" fill="#2563eb" stroke="#fff" stroke-width="1.5" pointer-events="none"/>{{% endif %}}</a>')
    txt = ('{% comment %} Projects pins from _data/landmark_pins.yml. Constants are written by _tools/build_shenzhen_map.py - do not edit by hand. {% endcomment %}\n'
           '{% for p in site.data.landmark_pins %}' + cond + body + ('{% endif %}' if cond else '') + '\n{% endfor %}')
    open(f'_includes/shenzhen-map-{"pins" if name=="main" else "inset-pins"}.html', 'w', encoding='utf-8').write(txt)

for n in VIEWS: base(n); pins(n)
for n, v in VIEWS.items(): print(n, v['W'], 'x', v['H'])
