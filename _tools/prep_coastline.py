"""Condenses raw OpenStreetMap coastline (Overpass: way["natural"="coastline"](south,west,north,east); out geom;)
into _tools/osm_coastline.json: a list of chains of [lon, lat], water on the right of each chain's direction.
Where OSM data was missing, chains traced from a screenshot (_tools/traced_coast.json, see trace_coast.py) replace
the OSM coastline inside their box and are joined to the OSM chains at the box edge.
Run:  python3 _tools/prep_coastline.py raw1.json raw2.json ...   (needs shapely)"""
import json, sys
from shapely.geometry import LineString

ways = {}
for f in sys.argv[1:]:
    for e in json.load(open(f))['elements']:
        if e['type'] == 'way' and e.get('geometry'): ways[e['id']] = [(p['lon'], p['lat']) for p in e['geometry']]

by_start = {}
for wid, pts in ways.items(): by_start.setdefault(pts[0], []).append(wid)
used, chains = set(), []
for wid, pts in ways.items():
    if wid in used: continue
    used.add(wid); chain = list(pts)
    while chain[0] != chain[-1]:  # follow end node to the next way that starts there
        nxt = [w for w in by_start.get(chain[-1], []) if w not in used]
        if not nxt: break
        used.add(nxt[0]); chain += ways[nxt[0]][1:]
    chains.append(chain)
# chains that start where another ends (walked from the middle of a run) are rare; merge those too
merged = True
while merged:
    merged = False
    ends = {c[-1]: i for i, c in enumerate(chains) if c[0] != c[-1]}
    for i, c in enumerate(chains):
        if c[0] != c[-1] and c[0] in ends and ends[c[0]] != i:
            j = ends[c[0]]; chains[j] = chains[j] + c[1:]; chains.pop(i); merged = True; break
import os, math
from shapely.geometry import box
if os.path.exists('_tools/traced_coast.json'):
    t = json.load(open('_tools/traced_coast.json')); bx = box(*t['box']); kept = []
    for c in chains:
        g = LineString(c).difference(bx)
        kept += [list(x.coords) for x in ([g] if g.geom_type == 'LineString' else getattr(g, 'geoms', [])) if x.geom_type == 'LineString' and not x.is_empty]
    chains = kept + [[tuple(p) for p in c] for c in t['chains']]
    near = lambda p: bx.exterior.distance(__import__('shapely.geometry', fromlist=['Point']).Point(p)) < 0.03
    while True:  # join open ends that sit near the box edge to the nearest chain start
        best = None
        for i, a in enumerate(chains):
            if a[0] == a[-1] or not near(a[-1]): continue
            for j, b in enumerate(chains):
                if i == j or not near(b[0]): continue
                d = math.hypot(a[-1][0]-b[0][0], a[-1][1]-b[0][1])
                if d < 0.03 and (best is None or d < best[0]): best = (d, i, j)
        if not best: break
        _, i, j = best; chains[i] = chains[i] + chains[j]
        chains.pop(j)
out = []
for c in chains:
    s = list(LineString(c).simplify(0.00015, preserve_topology=False).coords)
    if len(s) >= 2: out.append([[round(x, 5), round(y, 5)] for x, y in s])
json.dump(out, open('_tools/osm_coastline.json', 'w'), separators=(',', ':'))
print(len(ways), 'ways ->', len(out), 'chains,', sum(len(c) for c in out), 'points')
