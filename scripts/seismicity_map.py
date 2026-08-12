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
STATS_INSET = True             # ex009-style magnitude-class count panel (top-right)
OUT = "seismicity_map.png"
# ----------------------------------------

# Demo catalog: REAL Japan-trench seismicity — USGS M>=4.5, 2000-2025 (public domain,
# bundled as scripts/data/japan_trench_usgs.csv). Replace with your own catalog.
cat = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "data", "japan_trench_usgs.csv"))

# Focal mechanisms for the two largest events, GCMT-approximate values
# (2011 Tohoku Mw9.1: 203/10/88; 2003 Tokachi-oki Mw8.3: 230/20/109).
# Replace with your GCMT solutions or set mechs = mechs.iloc[:0] to skip.
big = cat.nlargest(2, "mag").sort_values("mag", ascending=False)
mechs = pd.DataFrame({
    "longitude": big.lon.values, "latitude": big.lat.values,
    "depth": big.depth.values,
    "strike": [203, 230], "dip": [10, 20], "rake": [88, 109],
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

    # magnitude-class legend with counts (GMT China ex009 pattern). The inset
    # draws NO axis annotations (suppressed anyway, GOTCHAS 8.1) — symbols+text only.
    if STATS_INSET:
        classes = [(4.5, 5.5), (5.5, 6.5), (6.5, 8.0), (8.0, 10.0)]
        with fig.inset(position="jTR+w4.2c/3.4c+o0.15c", box="+gwhite+p0.8p,black"):
            for k, (m0, m1) in enumerate(classes):
                n = int(((cat.mag >= m0) & (cat.mag < m1)).sum())
                y = 0.85 - 0.22 * k
                mrep = (m0 + min(m1, 9.1)) / 2
                fig.plot(x=[0.13], y=[y], style=f"c{SIZE_SCALE * 2 ** mrep:.3f}c",
                         fill="gray40", pen="0.3p,black",
                         region=[0, 1, 0, 1], projection="X4.2c/3.4c")
                lab = f"M {m0:.1f}-{m1:.1f}" if m1 < 10 else f"M >= {m0:.1f}"
                fig.text(x=0.28, y=y, text=f"{lab}: {n}", justify="ML",
                         font="9p,Helvetica,black")
    panel_label(fig, PANEL, style_name=STYLE)
    colorbar(fig, "Hypocenter depth (km)", style_name=STYLE, width=8)

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
