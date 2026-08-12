#!/usr/bin/env python
"""3D finite-fault slip distribution (fence diagram) with plot3d.

Subfault polygons in (lon, lat, depth) colored by slip via a multi-segment file
with -Z headers — the standard way to show a slip-inversion result in 3D.
PyGMT adaptation of GMT China community ex030 (docs.gmt-china.org), restyled to
the house rules (depth positive-down via negative zsize, plain frame).

Runs standalone with a synthetic two-asperity model; replace `subfaults` with
your inversion output (corner coordinates + slip per patch).

Usage:  python fault_slip_3d.py
"""
import os
import sys
import tempfile

import numpy as np
import pygmt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.expanduser("~/.claude/skills/pygmt-plotting/scripts"))  # fallback when this file is copied elsewhere
from style_presets import style

# ---------------- CONFIG ----------------
STYLE = "house"          # house / journal / classic / minimal / presentation / dark
REGION = [130.33, 130.75, 32.42, 32.84, 0, 20]   # [W, E, S, N, zmin, zmax(km, positive down)]
PERSPECTIVE = [150, 28]  # azimuth, elevation
ZSIZE = "-5c"          # NEGATIVE height -> depth increases downward, labels positive
CMAP = "hot"             # slip: white->yellow->red reads well; or "lajolla"
SLIP_MAX = 4.0           # m, CPT ceiling
OUT = "fault_slip_3d.png"
# ----------------------------------------

# Demo: a 44x18 km fault plane, strike N40E, dip 72NW, 11x6 subfaults, two asperities.
# Replace with your subfault corners + slip (each row: 4 corners in lon/lat/depth + slip).
STRIKE, DIP = np.radians(40), np.radians(72)
LON0, LAT0 = 130.42, 32.48          # top-left corner of the plane at the surface trace
KM_LAT = 111.32
KM_LON = KM_LAT * np.cos(np.radians(32.7))
ns, nd = 11, 6
L, W = 44.0, 18.0                    # km along strike / downdip
ds, dd = L / ns, W / nd

def corner(s_km, d_km):
    """Along-strike / downdip (km) -> (lon, lat, depth_km_positive)."""
    h = d_km * np.cos(DIP)           # horizontal shift toward dip direction (NW of strike)
    lon = LON0 + (s_km * np.sin(STRIKE) - h * np.cos(STRIKE)) / KM_LON
    lat = LAT0 + (s_km * np.cos(STRIKE) + h * np.sin(STRIKE)) / KM_LAT
    return lon, lat, d_km * np.sin(DIP)

subfaults = []
for i in range(ns):
    for j in range(nd):
        s0, d0 = i * ds, j * dd
        slip = 3.6 * np.exp(-((s0 - 12) / 9) ** 2 - ((d0 - 5) / 5) ** 2) \
             + 2.2 * np.exp(-((s0 - 31) / 7) ** 2 - ((d0 - 11) / 6) ** 2)
        cs = [corner(s0, d0), corner(s0 + ds, d0), corner(s0 + ds, d0 + dd), corner(s0, d0 + dd)]
        subfaults.append((cs, slip))

# multi-segment file with -Z slip headers: plot3d colors each closed polygon by -Z
with tempfile.NamedTemporaryFile("w", suffix=".gmt", delete=False) as f:
    for cs, slip in subfaults:
        f.write(f"> -Z{slip:.3f}\n")
        for lon, lat, dep in cs:
            f.write(f"{lon:.5f} {lat:.5f} {dep:.3f}\n")
    seg = f.name

fig = pygmt.Figure()
with style(STYLE):
    pygmt.makecpt(cmap=CMAP, series=[0, SLIP_MAX], reverse=True, continuous=True)
    fig.basemap(region=REGION, projection="M11c", zsize=ZSIZE, perspective=PERSPECTIVE,
                frame=["xa0.2f", "ya0.2f", "za5f+lDepth (km)", "wSEnZ"])
    fig.plot3d(data=seg, close=True, cmap=True, pen="0.25p,gray35",
               perspective=True)
    # surface trace of the plane's updip edge
    tr = [corner(s, 0) for s in np.linspace(0, L, 30)]
    fig.plot3d(x=[p[0] for p in tr], y=[p[1] for p in tr], z=[0] * len(tr),
               pen="1.2p,black", perspective=True)
    fig.colorbar(position="JBC+w7c/0.35c+h+o0c/1.2c", frame="x+lSlip (m)")
os.unlink(seg)

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
