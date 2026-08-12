#!/usr/bin/env python
"""Map + cross-section: a profile line A-B on a relief map (top), with a topographic profile
and earthquakes projected onto a depth section (bottom).

Demonstrates pygmt.project (generate line + project points) and pygmt.grdtrack (sample DEM).
Runs standalone with synthetic earthquakes; replace `eqs` (lon, lat, depth, mag) with yours.

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
REGION = [-118.5, -117.0, 35.0, 36.2]
PROJECTION = "M12c"
A = [-118.3, 35.2]      # profile start [lon, lat] — place A-B THROUGH the target feature
B = [-117.2, 36.0]      # profile end; sanity-check: profile peak must match the feature's
                        # known elevation/depth (a summit missed by a few km reads ~2000 m low).
                        # For a fault-PERPENDICULAR section: A-B must cross the seismicity
                        # trend at ~90 deg through its DENSEST part (NE-trending zone ->
                        # NW-SE line), not skim an edge.
SWATH_KM = 15.0         # keep events within +/- this perpendicular distance
DEPTH_MAX = 15.0        # km, section depth axis
OUT = "cross_section.png"
# ----------------------------------------

# Demo: an aftershock cloud on a NE-dipping structure along the A-B azimuth — depth
# increases across strike so the section shows a coherent dip, like a real sequence.
rng = np.random.default_rng(2)
N = 220
along = rng.uniform(0, 1, N)                      # position along the zone
across = rng.normal(0, 0.045, N)                  # scatter across the zone
zone_az = np.arctan2(0.8, 1.1)                    # A->B direction
eqs = pd.DataFrame({
    "lon": -118.3 + along * 1.1 + across * np.sin(zone_az),
    "lat": 35.2 + along * 0.8 - across * np.cos(zone_az),
    # deepens toward B along the zone -> the A-B section shows a coherent dipping band
    "depth": np.clip(2.5 + 9.5 * along + rng.normal(0, 1.0, N), 1, 14.5),
    "mag": rng.gamma(2.0, 0.55, N) + 1.0,         # Gutenberg-Richter-ish, M1-4.5
})

relief = pygmt.datasets.load_earth_relief(resolution="15s", region=REGION)

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
             size=0.015 * 2 ** proj.mag, style="cc", pen="0.2p,black")
    fig.text(x=[0, seclen], y=[0, 0], text=["A", "B"], no_clip=True,
             offset="0c/0.25c", font="11p,Helvetica-Bold,red")
    # offset=1.5: the section's "Distance (km)" x-label stacks below the axis — the
    # style default (0.8c) overprints it
    colorbar(fig, "Depth (km)", style_name=STYLE, width=7, offset=1.5)

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
