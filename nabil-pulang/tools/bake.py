"""Bake the low sun's terrain shadows into textures (no shadow maps at render time, so nothing shimmers in flight).
Adapted from the library's 3D Map Explainer tools. Sun from the east-north-east, about 20 degrees up.
Heights are the exaggerated ones the page uses (metres / 1000 * EX, sea flat at 0).
Writes assets/<area>_shadow.png (2x the height grid).
usage (library root): .venv/bin/python -I <project>/tools/bake.py <project>
"""
import sys, os, json, math
import numpy as np
from PIL import Image
from scipy import ndimage

D = sys.argv[1]; A = os.path.join(D, 'assets')
EX = 3.0
SUN = np.array([140.0, 60.0, -90.0])            # world: x east, y up, z south
hor = math.hypot(SUN[0], SUN[2]); TAN = SUN[1] / hor
dx, dz = SUN[0] / hor, SUN[2] / hor


def bake(a, up=2, reach=40.0):
    m = json.load(open(os.path.join(A, f'{a}_meta.json')))
    GW, GH = m['GW'], m['GH']
    h = np.fromfile(os.path.join(A, f'{a}_height.bin'), '<f4').reshape(GH, GW)
    y = np.maximum(h, 0) / 1000 * EX
    if up > 1:
        y = ndimage.zoom(y, up, order=1)
    H, Wd = y.shape
    kx = m['width_km'] / (Wd - 1); kz = m['height_km'] / (H - 1)
    step = min(kx, kz) * 0.75
    R, C = np.mgrid[0:H, 0:Wd].astype(np.float32)
    occ = np.zeros_like(y)
    d = step
    while d < reach:
        rr = R + dz * d / kz; cc = C + dx * d / kx
        hs = ndimage.map_coordinates(y, [rr, cc], order=1, mode='nearest')
        occ = np.maximum(occ, (hs - (y + d * TAN)) / (0.02 + d * 0.04))
        d += step * (1 + d / 25)
    lit = np.clip(1 - occ, 0, 1)
    lit = lit * lit * (3 - 2 * lit)
    Image.fromarray((lit * 255 + .5).astype(np.uint8)).save(os.path.join(A, f'{a}_shadow.png'))
    print(a, Wd, H, 'shadowed', round(float((lit < .5).mean()), 3))


bake('sel', reach=30); bake('btu', reach=30); bake('wide', up=2, reach=60)
