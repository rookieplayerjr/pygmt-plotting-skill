#!/usr/bin/env python
"""Magnitude-time (M-T) plot: each event a vertical line, height = magnitude.

Datetime x-axis with primary/secondary annotation (years / months), the standard
sequence-overview figure. PyGMT adaptation of GMT China community ex012
(docs.gmt-china.org), house-styled; runs on the bundled REAL USGS Japan-trench
catalog (M>=4.5, 2000-2025).

Usage:  python mt_plot.py
"""
import os
import sys

import pandas as pd
import pygmt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.expanduser("~/.claude/skills/pygmt-plotting/scripts"))  # fallback when this file is copied elsewhere
from style_presets import panel_label, style

# ---------------- CONFIG ----------------
STYLE = "house"
TSPAN = ["2009-01-01T00:00:00", "2016-01-01T00:00:00"]   # zoom on the Tohoku sequence
MAG_RANGE = [4.0, 9.5]
HIGHLIGHT_MAG = 7.0          # events >= this get a star on top
OUT = "mt_plot.png"
# ----------------------------------------

cat = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "data", "japan_trench_usgs.csv"), parse_dates=["time"])
cat = cat[(cat.time >= TSPAN[0]) & (cat.time <= TSPAN[1])]

fig = pygmt.Figure()
with style(STYLE):
    fig.basemap(region=[TSPAN[0], TSPAN[1], MAG_RANGE[0], MAG_RANGE[1]],
                projection="X16cT/7c",
                frame=["WSne", "sxa1Y", "pxf1o", "ya1f0.5+lMagnitude"])
    # one vertical line per event (multi-segment file with -Z headers -> single
    # plot call, each segment colored by magnitude through the session CPT)
    pygmt.makecpt(cmap="inferno", series=[MAG_RANGE[0], 8.0], reverse=True)
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        for _, e in cat.iterrows():
            t = e.time.strftime("%Y-%m-%dT%H:%M:%S")
            f.write(f"> -Z{e.mag}\n{t} {MAG_RANGE[0]}\n{t} {e.mag}\n")
        seg = f.name
    fig.plot(data=seg, pen="0.8p", cmap=True)
    os.unlink(seg)
    big = cat[cat.mag >= HIGHLIGHT_MAG]
    fig.plot(x=big.time, y=big.mag, style="a0.4c", fill="gold", pen="0.6p,black")
    for _, e in big.nlargest(1, "mag").iterrows():
        fig.text(x=e.time, y=e.mag, text=f"M{e.mag:.1f}", offset="0.5c/0.15c",
                 font="10p,Helvetica-Bold,black", justify="ML")
    panel_label(fig, "A", style_name=STYLE)
    # NOTE for adapters: if you add a colorbar under this Cartesian panel, use
    # colorbar(..., offset=1.5) — the default 0.8c overprints the x-axis label
    # (shipped failure on a global blind test).

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
from qc_check import qc_image
qc_image(OUT)   # hard QC gate — a broken render aborts here instead of shipping

