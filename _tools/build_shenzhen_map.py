"""Builds the Landmarks-page map includes from Aliyun DataV boundaries (GCJ-02, converted to WGS-84).
  _includes/shenzhen-map-base.html         main city map (base layers + labels)
  _includes/shenzhen-map-inset-base.html   zoomed core map (Shekou to Luohu)
  _includes/shenzhen-map-pins.html         pins for the main map   (reads _data/landmark_pins.yml)
  _includes/shenzhen-map-inset-pins.html   pins for the inset
Land/sea comes from OpenStreetMap coastline (_tools/osm_coastline.json, see prep_coastline.py); Shenzhen's boundary and districts from DataV.
Run:  python3 _tools/build_shenzhen_map.py   (needs network and shapely)"""
import json, math, subprocess
from shapely.geometry import LineString, Polygon, MultiPolygon, box, Point
from shapely.ops import polygonize, unary_union

VIEWS = {  # lon0 = left edge, lat1 = top edge, P = pixels per degree of latitude
    'main':  dict(lon0=113.68, lat1=22.94, P=1050.0, lon1=114.70, lat0=22.38),
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

COAST = json.load(open('_tools/osm_coastline.json'))

def land_polygons(v, pad=0.03):
    """Land (as shapely polygons in view pixels) from the OSM coastline: water is on the right of each chain."""
    lon0, lon1, lat0, lat1 = v['lon0']-pad, v['lon1']+pad, max(v['lat0']-pad, 22.375), v['lat1']+pad  # 22.375: south edge of the traced coast data
    frame = box(lon0, lat0, lon1, lat1)
    pieces = []
    for c in COAST:
        g = LineString(c).intersection(frame)
        pieces += [g] if g.geom_type == 'LineString' else [x for x in getattr(g, 'geoms', []) if x.geom_type == 'LineString']
    faces = list(polygonize(unary_union(pieces + [frame.exterior])))
    land = []
    for f in faces:
        for ln in pieces:  # find a coastline segment on this face's edge and test which side the face is on
            hit = ln.intersection(f.boundary.buffer(1e-9))
            if hit.is_empty or hit.length < 1e-7: continue
            cs = list(ln.coords)
            for (x0, y0), (x1, y1) in zip(cs, cs[1:]):
                mx, my = (x0+x1)/2, (y0+y1)/2
                if f.boundary.distance(Point(mx, my)) < 1e-9:
                    dx, dy = x1-x0, y1-y0; n = math.hypot(dx, dy) or 1e-12
                    if f.contains(Point(mx - dy/n*1e-6, my + dx/n*1e-6)): land.append(f)
                    break
            else: continue
            break
    return unary_union(land)

def to_px(geom, v, tol, min_area):
    out = []
    for poly in (geom.geoms if hasattr(geom, 'geoms') else [geom]):
        q = Polygon([proj(v, x, y) for x, y in poly.exterior.coords], [[proj(v, x, y) for x, y in r.coords] for r in poly.interiors])
        q = q.simplify(tol, preserve_topology=True)
        if q.area >= min_area and not q.is_empty: out.append(q)
    return out

def svg_path(polys):
    d = ''
    for q in polys:
        for ring in [q.exterior] + list(q.interiors):
            d += 'M' + 'L'.join(f'{x:.1f},{y:.1f}' for x, y in list(ring.coords)[:-1]) + 'Z'
    return d

def base(name):
    v = VIEWS[name]; eps = 0.25 if name == 'main' else 0.2
    tol, min_area = (1.2, 14) if name == 'main' else (2.0, 40)
    out = [f'<svg viewBox="0 0 {v["W"]} {v["H"]}" role="img" aria-label="{"Map of Shenzhen showing where each landmark is" if name=="main" else "Zoomed map of Shenzhen from Shekou to Luohu showing the landmarks in the core"}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block;font-family:inherit">',
           f'<rect width="{v["W"]}" height="{v["H"]}" fill="{WATER}"/>']
    land = svg_path(to_px(land_polygons(v), v, tol, min_area))
    sz = path_for(outline["features"][0]["geometry"], v, eps*2)
    # Shenzhen's boundary, grown slightly so the true coast is never clipped by DataV's generalised one
    szb = ''
    for poly in outline['features'][0]['geometry']['coordinates']:
        g = Polygon([gcj_to_wgs(*pt) for pt in poly[0]]).buffer(0.0015)
        szb += svg_path(to_px(g, v, 0.5, 0))
    out.append(f'<defs><path id="land-{name}" d="{land}"/><clipPath id="landc-{name}"><use href="#land-{name}"/></clipPath><clipPath id="szc-{name}"><path d="{szb}"/></clipPath></defs>')
    out.append(f'<use href="#land-{name}" fill="{OTHER_LAND}" stroke="#c9c5b6" stroke-width="1" fill-rule="evenodd"/>')
    out.append(f'<g clip-path="url(#szc-{name})"><use href="#land-{name}" fill="{SZ_LAND}" stroke="#6b7b8f" stroke-width="1.6" stroke-linejoin="round" fill-rule="evenodd"/></g>')
    out.append(f'<g clip-path="url(#landc-{name})" fill="none" stroke-linejoin="round">')
    for f in full['features']:  # district borders: coarser than the coastline
        out.append(f'<path d="{path_for(f["geometry"], v, eps*5)}" stroke="#bfc9d4" stroke-width="1"/>')
    out.append(f'<path d="{sz}" stroke="#6b7b8f" stroke-width="1.6"/></g>')
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
    v = VIEWS[name]; r, hit, sw = (10, 11, 1.8) if name == 'main' else (14, 15, 2)
    cond = ''
    i = VIEWS['inset']
    inmain = (f'{{% if p.lat >= {i["lat0"]} and p.lat <= {i["lat1"]} and p.lon >= {i["lon0"]} and p.lon <= {i["lon1"]} %}} in-inset{{% endif %}}' if name == 'main' else '')
    if name == 'inset':
        cond = f'{{% if p.lat >= {v["lat0"]} and p.lat <= {v["lat1"]} and p.lon >= {v["lon0"]} and p.lon <= {v["lon1"]} %}}'
    body = (f'{{% assign cx = p.lon | minus: {v["lon0"]} | times: {v["K"]:.2f} | round: 1 %}}{{% assign cy = {v["lat1"]} | minus: p.lat | times: {v["P"]:.0f} | round: 1 %}}'
            f'<a href="#{{{{ p.id }}}}" class="map-pin{inmain}" aria-label="{{{{ p.name | escape }}}}"><circle cx="{{{{ cx }}}}" cy="{{{{ cy }}}}" r="{hit}" fill="transparent" stroke="#2563eb" stroke-width="{sw}" data-tip="{{{{ p.name | escape }}}}"/></a>')
    txt = ('{% comment %} Projects pins from _data/landmark_pins.yml. Constants are written by _tools/build_shenzhen_map.py - do not edit by hand. {% endcomment %}\n'
           '{% for p in site.data.landmark_pins %}' + cond + body + ('{% endif %}' if cond else '') + '\n{% endfor %}')
    open(f'_includes/shenzhen-map-{"pins" if name=="main" else "inset-pins"}.html', 'w', encoding='utf-8').write(txt)

for n in VIEWS: base(n); pins(n)
for n, v in VIEWS.items(): print(n, v['W'], 'x', v['H'])
