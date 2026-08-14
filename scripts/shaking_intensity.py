#!/usr/bin/env python
"""ShakeMap-style ground-shaking intensity map (MODELED product).

Instrumental-intensity field from a simple GMPE-type attenuation around a real
epicenter, drawn ShakeMap-fashion: intensity CPT, integer-intensity contours,
epicenter star. PyGMT adaptation of the GMT China community grdshake card.
The FIELD IS A MODEL (as every ShakeMap is) — label it as such; the epicenter,
magnitude and geography here are the real 2026-07-28 Kumamoto earthquake.

Usage:  python shaking_intensity.py
"""
import os
import sys

import numpy as np
import pygmt
import xarray as xr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.expanduser("~/.claude/skills/pygmt-plotting/scripts"))  # fallback when this file is copied elsewhere
from style_presets import panel_label, style

# ---------------- CONFIG ----------------
STYLE = "house"
REGION = [129.4, 132.2, 31.3, 34.0]
EPI = (130.722, 32.682)      # 2026-07-28 Kumamoto (JMA prelim)
MAG = 7.1                    # Mj
DEPTH = 10.0                 # km
OUT = "shaking_intensity.png"
# ----------------------------------------

# Modeled intensity: I = a*M - b*log10(R_hyp) - c*R_hyp + d  (JMA-intensity-like
# attenuation; coefficients illustrative). Replace the grid with a real ShakeMap
# / grdshake output for production.
lons = np.linspace(REGION[0], REGION[1], 500)
lats = np.linspace(REGION[2], REGION[3], 480)
LON, LAT = np.meshgrid(lons, lats)
repi = np.hypot((LON - EPI[0]) * 111.32 * np.cos(np.radians(EPI[1])),
                (LAT - EPI[1]) * 111.32)
rhyp = np.hypot(repi, DEPTH)
inten = 1.72 * MAG - 3.0 * np.log10(rhyp) - 0.002 * rhyp - 2.1
inten = np.clip(inten, 0.5, 7.0)
grid = xr.DataArray(inten, coords=[("lat", lats), ("lon", lons)])
grid.gmt.gtype = 1
grid.gmt.registration = 0

relief = pygmt.datasets.load_earth_relief(resolution="15s", region=REGION)
shade = pygmt.grdgradient(grid=relief, azimuth=315, normalize="t1")

fig = pygmt.Figure()
with style(STYLE):
    fig.basemap(region=REGION, projection="M13c", frame=["WSne", "xaf", "yaf"])
    pygmt.makecpt(cmap="gray", series=[-6000, 3000])
    fig.grdimage(grid=relief, shading=shade, cmap=True)
    # ShakeMap ramp: pale -> yellow -> orange -> red with intensity
    pygmt.makecpt(cmap="white,lightyellow,gold,orange,orangered,darkred",
                  series=[1, 7], continuous=True)
    fig.grdimage(grid=grid, cmap=True, transparency=45)
    fig.grdcontour(grid=grid, levels=1, annotation="1+f9p", pen="0.6p,gray20")
    fig.coast(shorelines="0.5p,black", water="lightsteelblue", resolution="f")
    fig.plot(x=[EPI[0]], y=[EPI[1]], style="a0.55c", fill="yellow", pen="1p,black")
    fig.text(position="BL", text=f"MODELED intensity — Mj {MAG}, {DEPTH:.0f} km",
             offset="j0.25c", justify="BL", font="8.5p,Helvetica-Oblique,gray20",
             fill="white@25", clearance="1.5p/1.5p")
    panel_label(fig, "A", style_name=STYLE)
    fig.colorbar(position="JBC+w8c/0.4c+h+o0c/0.8c",
                 frame=["xa1", "x+lModeled instrumental intensity"])

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
from qc_check import qc_image
qc_image(OUT)   # hard QC gate — a broken render aborts here instead of shipping

