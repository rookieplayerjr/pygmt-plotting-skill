#!/usr/bin/env python
"""Earthquake catalog map: epicenters colored by depth, sized by magnitude, with optional
focal-mechanism beachballs.

House-style plain frame, square panel label, horizontal depth colorbar. Runs standalone
with synthetic data; replace the `cat` DataFrame (lon, lat, depth, mag) and `mechs` list
with your catalog / GCMT solutions.

Usage:  python seismicity_map.py
"""
import os
import sys

import numpy as np
import pandas as pd
import pygmt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.expanduser("~/.claude/skills/pygmt-plotting/scripts"))  # fallback when this file is copied elsewhere
from style_presets import coast_colors, colorbar, panel_label, style

# ---------------- CONFIG ----------------
STYLE = "house"                # house / journal / classic / minimal / presentation / dark
REGION = [138, 147, 35, 42.5]
PROJECTION = "M12c"
DEPTH_RANGE = [0, 250]         # km, for the CPT
DEPTH_CMAP = "inferno"         # sequential; reversed below so shallow = bright
SIZE_SCALE = 0.0025             # circle size = SIZE_SCALE * 2**mag (cm). TUNE THIS:
                               # dense catalog (>200 events in a tight region) or Mmax>4.5
                               # saturates the map -> drop it, add transparency=40,
                               # thin the pen. Epicenters must stay individually resolvable.
PANEL = "A"
OUT = "seismicity_map.png"
# ----------------------------------------

# Demo catalog: REAL Japan-trench seismicity — USGS M>=4.5, 2000-2025 (public domain,
# bundled as scripts/data/japan_trench_usgs.csv). Replace with your own catalog.
cat = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "data", "japan_trench_usgs.csv"))

# Demo focal mechanisms (Aki convention): interplate-thrust style at the two largest
# events, for illustration. Replace with GCMT solutions or set to [] to skip.
big = cat.nlargest(2, "mag")
mechs = pd.DataFrame({
    "longitude": big.lon.values, "latitude": big.lat.values,
    "depth": big.depth.values,
    "strike": [200, 195], "dip": [20, 25], "rake": [90, 95],
    "magnitude": big.mag.values,
})

fig = pygmt.Figure()
with style(STYLE):
    fig.basemap(region=REGION, projection=PROJECTION, frame=["WSne", "xaf", "yaf"])
    fig.coast(**coast_colors(STYLE), resolution="f")

    # epicenters: color = depth, size = magnitude
    pygmt.makecpt(cmap=DEPTH_CMAP, series=[DEPTH_RANGE[0], DEPTH_RANGE[1], 1], reverse=True)
    fig.plot(x=cat.lon, y=cat.lat, fill=cat.depth, cmap=True,
             size=SIZE_SCALE * 2 ** cat.mag, style="cc", pen="0.15p,black", transparency=30)

    # focal mechanisms (colored by depth via the same CPT). When spec is a DataFrame the
    # longitude/latitude/depth columns are read from it — do NOT also pass them as kwargs.
    # Beachballs must READ over the epicenter cloud: keep scale >= 2x the largest epicenter
    # circle, or plot them at offset positions with tie-lines (GOTCHAS 8.10).
    if len(mechs):
        fig.meca(spec=mechs, scale="0.4c", convention="aki", cmap=True)

    panel_label(fig, PANEL, style_name=STYLE)
    colorbar(fig, "Hypocenter depth (km)", style_name=STYLE, width=8)

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
