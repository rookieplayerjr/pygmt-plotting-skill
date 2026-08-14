#!/usr/bin/env python
"""Map + cross-section: a profile line A-B on a relief map (top), with a topographic profile
and earthquakes projected onto a depth section (bottom).

Demonstrates pygmt.project (generate line + project points) and pygmt.grdtrack (sample DEM).
Runs standalone on the REAL built-in Japan-trench catalog (the section shows the dipping
Wadati-Benioff zone); replace `eqs` (lon, lat, depth, mag) with your own catalog.

Usage:  python cross_section.py
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
STYLE = "house"         # house / journal / classic / minimal / presentation / dark
REGION = [138.0, 147.0, 35.0, 42.5]
PROJECTION = "M12c"
RELIEF_RES = "01m"      # earth_relief resolution (small regions: 15s/03s)
A = [139.2, 38.2]       # profile start [lon, lat] — place A-B THROUGH the target feature
B = [146.0, 39.8]       # profile end; sanity-check: profile peak/depth must match the
                        # feature's known values (a summit missed by a few km reads low).
                        # For a fault-PERPENDICULAR section: A-B must cross the seismicity
                        # trend at ~90 deg through its DENSEST part, not skim an edge.
SWATH_KM = 100.0        # keep events within +/- this perpendicular distance
DEPTH_MAX = 250.0       # km, section depth axis
OUT = "cross_section.png"
# ----------------------------------------

# Demo: REAL Japan-trench seismicity — USGS catalog M>=4.5, 2000-2025 (public domain,
# bundled as scripts/data/japan_trench_usgs.csv). The section across the trench shows
# the westward-deepening Wadati-Benioff zone directly.
eqs = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "data", "japan_trench_usgs.csv"))

relief = pygmt.datasets.load_earth_relief(resolution=RELIEF_RES, region=REGION)

fig = pygmt.Figure()
with style(STYLE):
    # ---- bottom: map ----
    shade = pygmt.grdgradient(grid=relief, azimuth=315, normalize="t1")
    fig.basemap(region=REGION, projection=PROJECTION, frame=["WSne", "xaf", "yaf"])
    fig.grdimage(grid=relief, shading=shade, cmap="oleron")
    fig.coast(shorelines="0.5p,black", resolution="f")
    fig.plot(x=[A[0], B[0]], y=[A[1], B[1]], pen="1.5p,red")
    fig.text(x=[A[0], B[0]], y=[A[1], B[1]], text=["A", "B"],
             offset="0c/0.3c", font="12p,Helvetica-Bold,red")
    panel_label(fig, "A", style_name=STYLE)

    # project earthquakes onto the section: p = along-track km, z = depth, keep |q| < SWATH
    proj = pygmt.project(data=eqs[["lon", "lat", "depth", "mag"]], center=A, endpoint=B,
                         convention="pz", unit=True, width=[-SWATH_KM, SWATH_KM])
    proj.columns = ["p", "depth", "mag"]
    # generate="1k" walks the line in 1 km steps; column p is along-track distance,
    # so its last value IS the section length.
    seclen = float(pygmt.project(center=A, endpoint=B, generate="1k",
                                 unit=True).p.iloc[-1])

    # ---- top: depth section (negative height -> depth increases downward) ----
    fig.shift_origin(yshift="h+3.4c")   # gap must hold: section x-annots + x-label +
                                        # colorbar (offset 1.5c + bar + its annots/label)
    pygmt.makecpt(cmap="inferno", series=[0, DEPTH_MAX, 1], reverse=True)
    fig.basemap(region=[0, seclen, 0, DEPTH_MAX], projection="X12c/-4c",
                frame=["WSne", "xaf+lDistance (km)", "yaf+lDepth (km)"])
    fig.plot(x=proj.p, y=proj.depth, fill=proj.depth, cmap=True,
             size=0.0025 * 2 ** proj.mag, style="cc", pen="0.15p,black", transparency=25)
    fig.text(x=[0, seclen], y=[0, 0], text=["A", "B"], no_clip=True,
             offset="0c/0.25c", font="11p,Helvetica-Bold,red")
    # offset=1.5: the section's "Distance (km)" x-label stacks below the axis — the
    # style default (0.8c) overprints it
    colorbar(fig, "Depth (km)", style_name=STYLE, width=7, offset=1.5)

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
from qc_check import qc_image
qc_image(OUT)   # hard QC gate — a broken render aborts here instead of shipping

