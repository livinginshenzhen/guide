"""Traces a land/sea boundary from an Apple Maps screenshot (sea = bright blue) where OSM data was unavailable.
Georeferenced by fitting the screenshot to the OSM coastline on either side (see fit below), then written to
_tools/traced_coast.json as chains of [lon, lat] (land on the left) clipped to BOX = (lon0, lat0, lon1, lat1).
Run:  python3 _tools/trace_coast.py shot.webp P dx dy   (P, dx, dy from the fit)   (needs numpy, scipy, scikit-image, shapely)"""
import json, math, sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure
from shapely.geometry import LineString, box

BOX = (114.23, 22.375, 114.47, 22.70)
img, P, dx, dy = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
cosf = math.cos(math.radians(22.55))
a = np.array(Image.open(img).convert('RGB')).astype(int); R, G, B = a[..., 0], a[..., 1], a[..., 2]
water = (B > 235) & (G > 190) & (B-R > 85)
water = ndi.binary_opening(ndi.binary_closing(water, iterations=2), iterations=2)
lab, n = ndi.label(water); sz = ndi.sum(water, lab, range(1, n+1))
water = np.isin(lab, [i+1 for i, s in enumerate(sz) if s > 150])  # keep bays and islands' surroundings, drop label noise
land = ndi.gaussian_filter((~water).astype(float), 1.2)
def lonlat(col, row): return 114.12 + (col-130-dx)/(P*cosf), 22.55 - (row-652-dy)/P
frame = box(*BOX); out = []
for c in measure.find_contours(land, 0.5):
    pts = [lonlat(col, row) for row, col in c]
    if len(pts) < 4: continue
    # orient with land on the left
    k = len(pts)//2; (x0, y0), (x1, y1) = pts[k], pts[k+1]; mx, my = (x0+x1)/2, (y0+y1)/2; d = math.hypot(x1-x0, y1-y0) or 1e-9
    lx, ly = mx - (y1-y0)/d*0.0006, my + (x1-x0)/d*0.0006
    col = 130+dx+(lx-114.12)*P*cosf; row = 652+dy+(22.55-ly)*P
    if not land[int(min(max(row, 0), land.shape[0]-1)), int(min(max(col, 0), land.shape[1]-1))] > 0.5: pts.reverse()
    g = LineString(pts).simplify(0.0003).intersection(frame)
    for s in ([g] if g.geom_type == 'LineString' else list(getattr(g, 'geoms', []))):
        if s.geom_type == 'LineString' and len(s.coords) >= 2 and s.length > 0.003: out.append([[round(x, 5), round(y, 5)] for x, y in s.coords])
json.dump({'box': BOX, 'chains': out}, open('_tools/traced_coast.json', 'w'), separators=(',', ':'))
print(len(out), 'traced chains,', sum(len(c) for c in out), 'points')
