#!/usr/bin/env python
"""Epicenter map colored by origin TIME (sequence migration at a glance).

Continuous time -> color via a decimal-year CPT, magnitude -> size. PyGMT
adaptation of GMT China community ex010 (docs.gmt-china.org), house-styled;
runs on the bundled REAL USGS Japan-trench catalog.

Usage:  python time_colored_seismicity.py
"""
import os
import sys

import pandas as pd
import pygmt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.expanduser("~/.claude/skills/pygmt-plotting/scripts"))  # fallback when this file is copied elsewhere
from style_presets import colorbar, panel_label, style

# ---------------- CONFIG ----------------
STYLE = "house"
REGION = [138, 147, 35, 42.5]
TSPAN = [2011.0, 2012.0]       # decimal years: the Tohoku year
SIZE_SCALE = 0.0035
OUT = "time_colored_seismicity.png"
# ----------------------------------------

cat = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "data", "japan_trench_usgs.csv"), parse_dates=["time"])
cat["dyear"] = cat.time.dt.year + cat.time.dt.dayofyear / 365.25
cat = cat[(cat.dyear >= TSPAN[0]) & (cat.dyear <= TSPAN[1])]
print(f"{len(cat)} events in window")

fig = pygmt.Figure()
with style(STYLE):
    fig.basemap(region=REGION, projection="M12c", frame=["WSne", "xaf", "yaf"])
    span = max(REGION[1] - REGION[0], REGION[3] - REGION[2])
    res = "03s" if span <= 1 else "15s" if span <= 3 else "01m"
    relief = pygmt.datasets.load_earth_relief(resolution=res, region=REGION)
    shade = pygmt.grdgradient(grid=relief, azimuth=315, normalize="t1")
    zlo, zhi = float(relief.min()), float(relief.max())
    pygmt.makecpt(cmap="gray", series=[zlo * 1.25 if zlo < 0 else zlo - 800, zhi + 1800])
    fig.grdimage(grid=relief, shading=shade, cmap=True)
    fig.coast(shorelines="0.4p,gray30", water="lightsteelblue@30",
              lakes="lightsteelblue", resolution="i")
    pygmt.makecpt(cmap="batlow", series=TSPAN)
    fig.plot(x=cat.lon, y=cat.lat, fill=cat.dyear, cmap=True,
             size=SIZE_SCALE * 2 ** cat.mag, style="cc",
             pen="0.15p,gray20", transparency=20)
    big = cat.nlargest(1, "mag")
    fig.plot(x=big.lon, y=big.lat, style="a0.55c", fill="yellow", pen="0.9p,black")
    panel_label(fig, "A", style_name=STYLE)
    colorbar(fig, "Origin time (decimal year)", style_name=STYLE, width=8,
             frame_extra=["xa0.25f"])

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
from qc_check import qc_image
qc_image(OUT)   # hard QC gate — a broken render aborts here instead of shipping

