#!/usr/bin/env python
"""Focal-mechanism map: beachballs sized by magnitude, colored by depth.

The dedicated meca figure (GMT China community 地震/meca card): notable events
with GCMT-approximate mechanisms, manual Mw->radius sizing (the `+m` modifier
is visually flat across M5-M7, GOTCHAS 8.3), depth-colored via the session CPT.

Usage:  python focal_mechanisms.py
"""
import os
import sys

import pandas as pd
import pygmt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.expanduser("~/.claude/skills/pygmt-plotting/scripts"))  # fallback when this file is copied elsewhere
from style_presets import coast_colors, colorbar, panel_label, style

# ---------------- CONFIG ----------------
STYLE = "house"
REGION = [128, 148, 30, 46]
PROJECTION = "M13c"
DEPTH_RANGE = [0, 60]
OUT = "focal_mechanisms.png"
# ----------------------------------------

# Notable Japan events, GCMT-approximate solutions (strike/dip/rake). Replace
# with your GCMT/F-net catalog (same columns) for production use.
mechs = pd.DataFrame([
    # lon, lat, depth, strike, dip, rake, mag, label
    (142.37, 38.30, 24, 203, 10, 88, 9.1, "2011 Tohoku"),
    (143.90, 41.78, 27, 230, 20, 109, 8.3, "2003 Tokachi"),
    (130.75, 32.79, 12, 226, 84, -142, 7.0, "2016 Kumamoto"),
    (137.27, 37.50, 12, 45, 42, 90, 7.5, "2024 Noto"),
    (135.02, 37.23, 17, 25, 65, 15, 6.6, "2007 Chuetsu-oki"),
    (141.60, 36.10, 30, 210, 15, 95, 7.6, "2011 Ibaraki-oki"),
    (135.62, 34.60, 13, 130, 40, 55, 6.9, "1995 Kobe"),
    (140.68, 41.78, 33, 240, 25, 105, 7.8, "1994 Sanriku-oki"),
], columns=["longitude", "latitude", "depth", "strike", "dip", "rake",
            "magnitude", "label"])

fig = pygmt.Figure()
with style(STYLE):
    fig.basemap(region=REGION, projection=PROJECTION, frame=["WSne", "xaf", "yaf"])
    fig.coast(**coast_colors(STYLE), resolution="i")
    pygmt.makecpt(cmap="inferno", series=DEPTH_RANGE, reverse=True)
    # manual Mw sizing: radius = 0.18 + 0.13*(Mw-6) cm reads clearly from M6.6 to M9.1
    for _, e in mechs.iterrows():
        size = 0.18 + 0.13 * (e.magnitude - 6.0)
        fig.meca(spec=dict(strike=e.strike, dip=e.dip, rake=e.rake,
                           magnitude=e.magnitude),
                 scale=f"{size:.2f}c", longitude=e.longitude, latitude=e.latitude,
                 depth=e.depth, convention="aki", cmap=True, outline="0.5p,gray20")
        fig.text(x=e.longitude, y=e.latitude, text=e.label,
                 offset=f"0c/{size + 0.28:.2f}c", font="7.5p,Helvetica,gray10",
                 fill="white@30", clearance="1p/1p")
    panel_label(fig, "A", style_name=STYLE)
    colorbar(fig, "Centroid depth (km)", style_name=STYLE, width=8)

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
