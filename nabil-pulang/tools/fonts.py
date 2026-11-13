"""Barlow Condensed Regular / Medium / SemiBold (SIL OFL 1.1) from github.com/google/fonts (ofl/barlowcondensed, via raw.githubusercontent.com).
usage: python3 -I <project>/tools/fonts.py <project>
"""
import os, sys, urllib.request
F = os.path.join(sys.argv[1], 'fonts'); os.makedirs(F, exist_ok=True)
get = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read()
for w in ('Regular', 'Medium', 'SemiBold'):
    p = os.path.join(F, f'BarlowCondensed-{w}.ttf')
    if not os.path.exists(p):
        open(p, 'wb').write(get(f'https://raw.githubusercontent.com/google/fonts/main/ofl/barlowcondensed/BarlowCondensed-{w}.ttf'))
p = os.path.join(F, 'OFL-barlow.txt')
if not os.path.exists(p):
    open(p, 'wb').write(get('https://raw.githubusercontent.com/google/fonts/main/ofl/barlowcondensed/OFL.txt'))
print('fonts ok')
