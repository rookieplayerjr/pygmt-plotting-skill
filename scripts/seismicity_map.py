#!/usr/bin/env python
"""Earthquake catalog map: epicenters on shaded relief, colored by depth, sized by
magnitude, with optional focal mechanisms, fault traces, an auto-placed
magnitude-statistics panel and a map scale.

House-style plain frame, square panel label, horizontal depth colorbar. Runs
standalone on the bundled REAL USGS Japan-trench catalog; replace `cat`
(lon, lat, depth, mag) and `mechs` with your catalog / GCMT solutions.

Usage:  python seismicity_map.py
"""
import os
import sys

import numpy as np
import pandas as pd
import pygmt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.expanduser("~/.claude/skills/pygmt-plotting/scripts"))  # fallback when this file is copied elsewhere
from style_presets import colorbar, panel_label, style

# ---------------- CONFIG ----------------
STYLE = "house"                # house / journal / classic / minimal / presentation / dark
REGION = [138, 147, 35, 42.5]
PROJECTION = "M12c"
DEPTH_RANGE = [0, 250]         # km, for the CPT
DEPTH_CMAP = "inferno"         # sequential; reversed below so shallow = bright
SIZE_SCALE = 0.0025            # circle size = SIZE_SCALE * 2**mag (cm). TUNE THIS:
                               # dense catalog or Mmax>4.5 saturates -> drop it, add
                               # transparency, thin the pen.
RELIEF = True                  # grayscale shaded-relief background (context by default)
RELIEF_RES = "auto"            # "auto": 03s <=1 deg span, 15s <=3 deg, else 01m
FAULTS = None                  # optional GMT multi-segment fault-trace file (drawn w/ halo)
MAG_CLASSES = None             # stats-panel bins; None = auto from catalog magnitudes
STATS_INSET = True             # magnitude-class count panel, auto-placed in the EMPTIEST
                               # corner so it never covers the seismicity (QC hard rule)
SCALE_BAR = True               # map scale, bottom-right (moves to BL if stats live at BR)
PANEL = "A"
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


def emptiest_corner(df, region):
    """Corner quadrant (as a GMT j-code) holding the fewest epicenters."""
    xm = (region[0] + region[1]) / 2
    ym = (region[2] + region[3]) / 2
    counts = {
        "TL": ((df.lon < xm) & (df.lat >= ym)).sum(),
        "TR": ((df.lon >= xm) & (df.lat >= ym)).sum(),
        "BL": ((df.lon < xm) & (df.lat < ym)).sum(),
        "BR": ((df.lon >= xm) & (df.lat < ym)).sum(),
    }
    counts.pop("TL", None)   # TL belongs to the panel label
    return min(counts, key=counts.get)


fig = pygmt.Figure()
with style(STYLE):
    fig.basemap(region=REGION, projection=PROJECTION, frame=["WSne", "xaf", "yaf"])
    if RELIEF:
        span = max(REGION[1] - REGION[0], REGION[3] - REGION[2])
        res = RELIEF_RES if RELIEF_RES != "auto" else \
            ("03s" if span <= 1 else "15s" if span <= 3 else "01m")
        relief = pygmt.datasets.load_earth_relief(resolution=res, region=REGION)
        shade = pygmt.grdgradient(grid=relief, azimuth=315, normalize="t1")
        zlo, zhi = float(relief.min()), float(relief.max())
        pygmt.makecpt(cmap="gray", series=[zlo * 1.25 if zlo < 0 else zlo - 800, zhi + 1800])
        fig.grdimage(grid=relief, shading=shade, cmap=True)
        fig.coast(shorelines="0.4p,gray30", water="lightsteelblue@30", resolution="i")
    else:
        fig.coast(land="gray92", water="white", shorelines="0.5p,black", resolution="i")

    if FAULTS:
        fig.plot(data=FAULTS, pen="1.2p,white")
        fig.plot(data=FAULTS, pen="0.7p,black")

    # epicenters: color = depth, size = magnitude
    pygmt.makecpt(cmap=DEPTH_CMAP, series=[DEPTH_RANGE[0], DEPTH_RANGE[1], 1], reverse=True)
    fig.plot(x=cat.lon, y=cat.lat, fill=cat.depth, cmap=True,
             size=SIZE_SCALE * 2 ** cat.mag, style="cc", pen="0.15p,black", transparency=30)

    # focal mechanisms (colored by depth via the same CPT). When spec is a DataFrame the
    # longitude/latitude/depth columns are read from it — do NOT also pass them as kwargs.
    # Beachballs must READ over the epicenter cloud (GOTCHAS 8.10).
    if len(mechs):
        fig.meca(spec=mechs, scale="0.4c", convention="aki", cmap=True)

    # magnitude-class counts (GMT China ex009 pattern), auto-placed in the corner with
    # the FEWEST events so the panel never hides the seismicity.
    stats_corner = None
    if STATS_INSET:
        classes = MAG_CLASSES
        if classes is None:
            lo = float(np.floor(cat.mag.min() * 2) / 2)
            classes = [(lo, lo + 1), (lo + 1, lo + 2), (lo + 2, lo + 3), (lo + 3, 10.0)]
        stats_corner = emptiest_corner(cat, REGION)
        with fig.inset(position=f"j{stats_corner}+w4.2c/3.4c+o0.15c",
                       box="+gwhite+p0.8p,black"):
            for k, (m0, m1) in enumerate(classes):
                n = int(((cat.mag >= m0) & (cat.mag < m1)).sum())
                y = 0.85 - 0.22 * k
                mrep = (m0 + min(m1, cat.mag.max())) / 2
                fig.plot(x=[0.13], y=[y], style=f"c{SIZE_SCALE * 2 ** mrep:.3f}c",
                         fill="gray40", pen="0.3p,black",
                         region=[0, 1, 0, 1], projection="X4.2c/3.4c")
                lab = f"M {m0:.1f}-{m1:.1f}" if m1 < 10 else f"M >= {m0:.1f}"
                fig.text(x=0.28, y=y, text=f"{lab}: {n}", justify="ML",
                         font="9p,Helvetica,black")

    if SCALE_BAR:
        corner = "jBL" if stats_corner == "BR" else "jBR"
        km = int(round((REGION[1] - REGION[0]) * 111 * 0.2 / 50) * 50) or 50
        fig.basemap(map_scale=f"{corner}+w{km}k+f+u+o0.6c/0.6c"
                              f"+c{np.mean(REGION[2:]):.0f}")

    panel_label(fig, PANEL, style_name=STYLE)
    colorbar(fig, "Hypocenter depth (km)", style_name=STYLE, width=8)

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
