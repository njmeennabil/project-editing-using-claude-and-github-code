"""Map data for Nabil Pulang: fetch public tiles and turn them into terrain assets, for three areas.

  sel   Selangor (KLIA, Shah Alam, Jeram)   imagery z12, terrain z11
  btu   Bintulu (UPM Bintulu, the airport)  imagery z12, terrain z11
  wide  Sumatra edge → Borneo, the crossing imagery z9,  terrain z8

Sources (see ../CREDITS):
- Elevation + bathymetry: AWS Terrain Tiles (Mapzen/Tilezen terrarium PNG), https://registry.opendata.aws/terrain-tiles/
- Imagery: EOX Sentinel-2 cloudless 2016 (layer s2cloudless_3857), CC BY 4.0. Later releases are CC BY-NC-SA and are not used.

Every URL is logged in raw/manifest.jsonl. Assets per area: assets/<a>_height.bin (float32 m, row 0 = north),
assets/<a>_albedo.jpg, assets/<a>_water.png, assets/<a>_meta.json. The world scale is one shared Web Mercator
reference (zoom 12 pixels at latitude 3°), so every mesh sits in one km world.
usage (library root): .venv/bin/python -I <project>/tools/data.py <project>
"""
import sys, os, io, json, math, time, datetime, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image
from scipy import ndimage

D = sys.argv[1]
RAW = os.path.join(D, 'raw'); OUT = os.path.join(D, 'assets')
os.makedirs(RAW, exist_ok=True); os.makedirs(OUT, exist_ok=True)
Image.MAX_IMAGE_PIXELS = None
UA = {'User-Agent': 'map-film/1.0'}
LOG = open(os.path.join(RAW, 'manifest.jsonl'), 'a')
REF_Z, REF_LAT = 12, 3.0
KM_REF = 40075.016 * math.cos(math.radians(REF_LAT)) / (2 ** REF_Z * 256)   # km per zoom-12 pixel

AREAS = {
    'sel':  {'bbox': [101.12, 2.62, 101.88, 3.36], 'zi': 12, 'zt': 11, 'grid': 4, 'minwater_km2': 4.0},
    'btu':  {'bbox': [112.86, 2.98, 113.24, 3.34], 'zi': 12, 'zt': 11, 'grid': 4, 'minwater_km2': 4.0},
    'wide': {'bbox': [98.3, -1.6, 116.3, 6.3],     'zi': 9,  'zt': 8,  'grid': 4, 'minwater_km2': 60.0},
}


def merc(lon, lat, z):
    n = 2 ** z * 256
    return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n


def get(url):
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                b = r.read()
            LOG.write(json.dumps({'url': url, 'bytes': len(b), 'date': datetime.date.today().isoformat()}) + '\n'); LOG.flush()
            return b
        except Exception:
            if k == 4:
                raise
            time.sleep(2 + 3 * k)


def mosaic(name, tmpl, bbox, z, ext):
    W, S, E, N = bbox
    dst = os.path.join(RAW, f'{name}_z{z}.{ext}')
    x0, y0 = merc(W, N, z); x1, y1 = merc(E, S, z)
    tx0, ty0, tx1, ty1 = int(x0 // 256), int(y0 // 256), int(x1 // 256), int(y1 // 256)
    if not os.path.exists(dst):
        jobs = [(x, y) for y in range(ty0, ty1 + 1) for x in range(tx0, tx1 + 1)]
        im = Image.new('RGB', ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256))
        with ThreadPoolExecutor(6) as ex:
            for (x, y), b in ex.map(lambda j: (j, get(tmpl.format(z=z, x=j[0], y=j[1]))), jobs):
                im.paste(Image.open(io.BytesIO(b)).convert('RGB'), ((x - tx0) * 256, (y - ty0) * 256))
        im.save(dst, quality=95) if ext == 'jpg' else im.save(dst)
    print(name, z, (tx1 - tx0 + 1) * (ty1 - ty0 + 1), 'tiles')
    return {'z': z, 'tx0': tx0, 'ty0': ty0}


def prep(a, A):
    W, S, E, N = A['bbox']
    zi, zt = A['zi'], A['zt']
    mi = mosaic(a + '_s2', 'https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/{z}/{y}/{x}.jpg', A['bbox'], zi, 'jpg')
    mt = mosaic(a + '_ter', 'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png', A['bbox'], zt, 'png')
    x0, y0 = merc(W, N, zi); x1, y1 = merc(E, S, zi)
    img = Image.open(os.path.join(RAW, f'{a}_s2_z{zi}.jpg')).convert('RGB')
    img = img.crop((int(x0 - mi['tx0'] * 256), int(y0 - mi['ty0'] * 256), int(x1 - mi['tx0'] * 256), int(y1 - mi['ty0'] * 256)))
    IW, IH = img.size
    km_px = KM_REF * 2 ** (REF_Z - zi)
    tx0, ty0 = merc(W, N, zt); tx1, ty1 = merc(E, S, zt)
    t = np.asarray(Image.open(os.path.join(RAW, f'{a}_ter_z{zt}.png')).convert('RGB'), np.float64)
    h = t[..., 0] * 256 + t[..., 1] + t[..., 2] / 256 - 32768
    ys = (np.arange(IH) + .5) / IH * (ty1 - ty0) + ty0 - mt['ty0'] * 256 - .5
    xs = (np.arange(IW) + .5) / IW * (tx1 - tx0) + tx0 - mt['tx0'] * 256 - .5
    X, Y = np.meshgrid(xs, ys)
    hi = ndimage.map_coordinates(h, [Y, X], order=3, mode='nearest').astype(np.float32)

    arr = np.asarray(img, np.float32) / 255
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    lum = .3 * r + .59 * g + .11 * b
    # The coastal plain here is ~0-3 m in the terrain tiles, so height alone can't separate land from sea.
    # Candidates: real bathymetry, or low ground that isn't green-dominant vegetation (palm plantations are dark
    # but green), or bright muddy shallows. Only candidates connected to true sea (deeper than 4 m) are kept,
    # so inland plantations and low fields never turn into sea.
    veg = g > b * 1.12 + .015
    cand = (hi <= -1.5) | (~veg & (lum < .55) & (hi < 3)) | ((hi < 1.5) & (lum > .2) & (g > r * 1.02) & (g > b * .95))
    it = 2 if zi >= 11 else 1
    # morphology treats the image border as background; pad with the edge so the border keeps its own class
    morph = lambda f, x: f(np.pad(x, it + 1, mode='edge'), iterations=it)[it + 1:-(it + 1), it + 1:-(it + 1)]
    cand = morph(ndimage.binary_opening, cand)
    lab, n = ndimage.label(cand)
    seeds = np.unique(lab[(hi < -4) & cand]); seeds = seeds[seeds > 0]
    water = np.isin(lab, seeds)
    water = morph(ndimage.binary_closing, water)
    lab, n = ndimage.label(water)
    if n:
        sizes = ndimage.sum(water, lab, range(1, n + 1))
        keep = np.zeros(n + 1, bool); keep[1:] = sizes * km_px * km_px > A['minwater_km2']
        water = keep[lab]
    land = ~water
    hl = np.where(land, np.maximum(hi, 2.0), np.minimum(hi, -1.0))
    dist_land = ndimage.distance_transform_edt(water) * km_px

    lin = arr ** 2.2
    L = lin.copy()
    l = (L * [.2126, .7152, .0722]).sum(-1, keepdims=True)
    L = l + (L - l) * .82
    L = L * np.array([1.06, 1.0, .88])
    L = np.clip(L * .9, 0, 1)
    L = L ** 1.12 * 1.08
    depth = np.clip(-hl, 0, 120)
    sh = np.exp(-depth / 9.0)
    sh = np.maximum(sh, np.exp(-dist_land / .34) * .6)
    deep = np.array([.008, .030, .066]); mid = np.array([.014, .055, .095]); teal = np.array([.03, .17, .19])
    dd = np.clip(depth / 90, 0, 1)[..., None]
    sea = mid * (1 - dd) + deep * dd
    shallow = .55 * teal + .45 * lin * np.array([.55, .95, 1.0])
    sea = sea * (1 - sh[..., None] * .85) + shallow * (sh[..., None] * .85)
    wm = ndimage.gaussian_filter(water.astype(np.float32), 1.2 if zi >= 11 else .6)[..., None]
    alb = L * (1 - wm) + sea * wm
    Image.fromarray((np.clip(alb, 0, 1) ** (1 / 2.2) * 255 + .5).astype(np.uint8)).save(os.path.join(OUT, f'{a}_albedo.jpg'), quality=92)
    Image.fromarray((wm[..., 0] * 255).astype(np.uint8)).resize((IW // 2, IH // 2), Image.LANCZOS).save(os.path.join(OUT, f'{a}_water.png'))
    GW, GH = IW // A['grid'], IH // A['grid']
    hg = np.asarray(Image.fromarray(hl).resize((GW, GH), Image.BILINEAR), np.float32)
    hg.astype('<f4').tofile(os.path.join(OUT, f'{a}_height.bin'))
    rx0, ry0 = merc(W, N, REF_Z); rx1, ry1 = merc(E, S, REF_Z)
    meta = {'GW': GW, 'GH': GH, 'IW': IW, 'IH': IH, 'bbox': [W, S, E, N], 'z': zi, 'ref': [rx0, ry0, rx1, ry1],
            'km_px': km_px, 'width_km': (rx1 - rx0) * KM_REF, 'height_km': (ry1 - ry0) * KM_REF,
            'hmax': float(hl.max()), 'hmin': float(hl.min()), 'water': float(water.mean())}
    json.dump(meta, open(os.path.join(OUT, f'{a}_meta.json'), 'w'), indent=1)
    print(a, {k: meta[k] for k in ('GW', 'GH', 'IW', 'IH', 'width_km', 'height_km', 'hmax', 'hmin', 'water')})


json.dump({'REF_Z': REF_Z, 'REF_LAT': REF_LAT, 'KM_REF': KM_REF}, open(os.path.join(OUT, 'world.json'), 'w'))
for a in (sys.argv[2:] or AREAS):
    prep(a, AREAS[a])
