#!/usr/bin/env python
"""Multi-panel component figure (e.g. East / North / Up displacement) sharing one CPT and a
single horizontal colorbar below all panels.

Demonstrates fig.subplot with autolabel and a shared colorbar drawn OUTSIDE the subplot
block. Runs standalone with synthetic grids; replace the `grids`/`titles` with your data
(xarray.DataArray or .grd files).

Usage:  python multipanel_components.py
"""
import os
import sys

import numpy as np
import pygmt
import xarray as xr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.expanduser("~/.claude/skills/pygmt-plotting/scripts"))  # fallback when this file is copied elsewhere
from style_presets import STYLES, colorbar, style

# ---------------- CONFIG ----------------
STYLE = "house"            # house / journal / classic / minimal / presentation / dark
REGION = [-118.2, -117.2, 35.4, 36.15]   # Ridgecrest 2019 area
PROJECTION = "M?"          # '?' lets subplot auto-size each panel
CMAP = "vik"
CLIM = [-40, 40]
UNIT = "Displacement (cm)"
TITLES = ["East", "North", "Up"]
OUT = "multipanel_components.png"
# ----------------------------------------

# Demo grids: physically consistent E/N/U of a NW-SE right-lateral rupture — E and N are
# the anti-symmetric strike-slip quadrants projected on each axis, U is a weak compact
# dipole. Replace with your decomposed component grids.
lons = np.linspace(REGION[0], REGION[1], 300)
lats = np.linspace(REGION[2], REGION[3], 240)
LON, LAT = np.meshgrid(lons, lats)
F_AZ = np.radians(-40)
F_LON, F_LAT = -117.55, 35.77
xf = (LON - F_LON) * np.cos(F_AZ) + (LAT - F_LAT) * np.sin(F_AZ)
yf = -(LON - F_LON) * np.sin(F_AZ) + (LAT - F_LAT) * np.cos(F_AZ)
u, v = xf / 0.28, yf / 0.11
horiz = 2.7 * v * np.exp(-u ** 2 - v ** 2) * (1 + 0.3 * np.tanh(u))  # fault-parallel slip
comp = {
    "East": 40 * horiz * np.cos(F_AZ),
    "North": 40 * horiz * np.sin(F_AZ),
    "Up": 30 * u * v * np.exp(-u ** 2 - v ** 2),
}
grids = [xr.DataArray(comp[t], coords=[("lat", lats), ("lon", lons)]) for t in TITLES]
for g in grids:           # mark as geographic, gridline-registered
    g.gmt.gtype = 1
    g.gmt.registration = 0

INC = (CLIM[1] - CLIM[0]) / 40.0
pygmt.makecpt(cmap=CMAP, series=[CLIM[0], CLIM[1], INC], continuous=True)  # session CPT

fig = pygmt.Figure()
# subplot's autolabel draws the panel-letter box, so pull its colors/font from the
# style preset (FONT_TAG styles the autolabel text).
_box = STYLES[STYLE]["label_box"]
with style(STYLE, FONT_TAG=STYLES[STYLE]["label_font"]):
    # xa30mf: coarse lon annotations — auto ("xaf") packs 15' labels that COLLIDE across
    # adjacent panels at this panel width. If labels still touch, coarsen further or widen
    # margins; check the seam between panels in the rendered image.
    with fig.subplot(nrows=1, ncols=3, figsize=("18c", "5c"),
                     autolabel=f"A+jTL+o0.2c+g{_box['fill']}+p{_box['pen']}",
                     margins="0.4c", frame=["WSne", "xa30mf10m", "yaf"], sharey="l"):
        for k, (grid, title) in enumerate(zip(grids, TITLES)):
            fig.basemap(region=REGION, projection=PROJECTION, panel=k)
            fig.grdimage(grid=grid, projection=PROJECTION)     # uses session CPT
            fig.coast(shorelines="0.4p,black", resolution="f")
            fig.text(position="TC", text=title, font="10p,Helvetica-Bold,black",
                     offset="0c/-0.3c", no_clip=True)
    # shared colorbar OUTSIDE the subplot block, centered under all panels
    colorbar(fig, UNIT, style_name=STYLE, width=9)

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
from qc_check import qc_image
qc_image(OUT)   # hard QC gate — a broken render aborts here instead of shipping

