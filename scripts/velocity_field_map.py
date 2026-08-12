#!/usr/bin/env python
"""GPS/GNSS velocity field map: velo arrows with 1-sigma error ellipses on a coast
basemap, a boxed reference-scale vector, and a map scale bar.

Standard interseismic velocity-field figure (pattern follows GMT China community
ex015). Runs standalone with synthetic stations; replace `sta` with your solution
(lon, lat, ve, vn, se, sn, corr, site) in mm/yr.

Usage:  python velocity_field_map.py
"""
import os
import sys

import numpy as np
import pandas as pd
import pygmt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.expanduser("~/.claude/skills/pygmt-plotting/scripts"))  # fallback when this file is copied elsewhere
from style_presets import coast_colors, panel_label, style

# ---------------- CONFIG ----------------
STYLE = "house"          # house / journal / classic / minimal / presentation / dark
REGION = [-124.5, -119.5, 34.0, 38.5]
PROJECTION = "M12c"
VSCALE = 0.06            # cm per mm/yr (velo length scale). Pick so the SMALLEST velocity
                         # you care about maps to >= the 0.25c head length (here >=4.2 mm/yr)
                         # — shorter vectors silently lose their heads. Do NOT "fix" this
                         # with +n on geographic maps: +n<len>q shrinks ALL heads away
                         # (GOTCHAS 9.4, verified GMT 6.6).
REF_MMYR = 20            # reference vector magnitude for the legend box
PANEL = "A"
OUT = "velocity_field_map.png"
# ----------------------------------------

# Demo: synthetic dextral shear across a NW-SE fault. Replace with your field.
# COMPASS azimuth az (deg clockwise from North) -> ve = V*sin(az), vn = V*cos(az).
# Using cos for ve / sin for vn (math-angle habit) rotates the whole field ~90 deg
# — e.g. a requested WNW field silently renders SSW. Check arrows against the
# stated direction after rendering.
# UNITS: ve/vn/se/sn must be in the same unit VSCALE assumes (mm/yr here) — after
# rendering, station arrows must look commensurate with the reference arrow; if they
# come out ~10x shorter, your velocities are in cm/yr while VSCALE is mm/yr-based.
rng = np.random.default_rng(11)
n = 40
lon = rng.uniform(REGION[0] + 0.3, REGION[1] - 0.3, n)
lat = rng.uniform(REGION[2] + 0.3, REGION[3] - 0.3, n)
dist = (lon + 121.8) * np.cos(np.radians(40)) + (lat - 36.2) * np.sin(np.radians(40))
vpar = 20 * np.tanh(dist / 0.6)                       # fault-parallel (mm/yr)
sta = pd.DataFrame({
    "lon": lon, "lat": lat,
    "ve": vpar * np.cos(np.radians(-40)) + rng.normal(0, 0.6, n),
    "vn": vpar * np.sin(np.radians(-40)) + rng.normal(0, 0.6, n),
    "se": rng.uniform(0.5, 1.2, n), "sn": rng.uniform(0.5, 1.2, n),
    "corr": np.zeros(n),
})  # an optional 8th text column would be plotted as station labels (spec +f<font>)

fig = pygmt.Figure()
with style(STYLE):
    fig.basemap(region=REGION, projection=PROJECTION, frame=["WSne", "xaf", "yaf"])
    fig.coast(**coast_colors(STYLE), resolution="i", borders="2/0.3p,gray50")

    # velocity arrows + 1-sigma ellipses (spec e<scale>/<conf>: 0.39 = 1 sigma)
    fig.velo(data=sta, spec=f"e{VSCALE}/0.39", uncertaintyfill="gray70",
             pen="0.4p,firebrick", line=True, fill="firebrick",
             vector="0.25c+e+gfirebrick+h0.5")

    # boxed reference vector: draw a fake one-station velo inside a cleared corner
    ref = pd.DataFrame({"lon": [REGION[0] + 0.55], "lat": [REGION[2] + 0.28],
                        "ve": [REF_MMYR], "vn": [0], "se": [0], "sn": [0],
                        "corr": [0]})
    fig.velo(data=ref, spec=f"e{VSCALE}/0.39", pen="0.4p,firebrick", fill="firebrick",
             line=True, vector="0.25c+e+gfirebrick+h0.5")
    fig.text(x=REGION[0] + 0.55 + REF_MMYR * VSCALE / 2 / 1.1, y=REGION[2] + 0.42,
             text=f"{REF_MMYR} mm/yr", font="8p,Helvetica,black", justify="MC")

    # map scale (+c: latitude at which the scale is true)
    fig.basemap(map_scale=f"jBR+w100k+f+u+o0.6c/0.6c+c{np.mean(REGION[2:]):.0f}")

    panel_label(fig, PANEL, style_name=STYLE)

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
