"""Fetches the roads for the Eats & Errands map (Shekou area) from OpenStreetMap via Overpass and writes _tools/osm_roads_nanshan.json.
Run:  python3 _tools/prep_roads.py   (needs network). Motorways (the Shenzhen Bay Bridge) are left out; the map draws only what is on land."""
import json, subprocess
Q = '[out:json][timeout:60];way["highway"~"^(trunk|primary|secondary|tertiary)$"](22.465,113.89,22.502,113.96);out geom;'
raw = subprocess.run(['curl','-s','-m','90','-A','expat-guide-build/1.0','--data-urlencode',f'data={Q}','https://overpass-api.de/api/interpreter'],capture_output=True,text=True).stdout
out = []
for w in json.loads(raw)['elements']:
    t = w['tags']
    out.append({'class': t['highway'], 'name': t.get('name:en') or '', 'pts': [[round(p['lon'],5), round(p['lat'],5)] for p in w['geometry']]})
json.dump(out, open('_tools/osm_roads_nanshan.json','w'), separators=(',',':'))
print(len(out), 'ways')
