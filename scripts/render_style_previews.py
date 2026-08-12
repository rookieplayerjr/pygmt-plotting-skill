"""Render the same demo map in every style preset -> previews/style_<name>.png.

Run after editing style_presets.py to regenerate the preview sheet embedded in
the styles section of SKILL.md. Synthetic data only — no downloads, runs offline in ~15 s.
"""

import os
import sys

import numpy as np
import pygmt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style_presets import STYLES, coast_colors, colorbar, panel_label, style

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "previews")
REGION = [-124, -119, 33.5, 37.5]

rng = np.random.default_rng(7)
lon = rng.uniform(REGION[0] + 0.3, REGION[1] - 0.3, 250)
lat = rng.uniform(REGION[2] + 0.3, REGION[3] - 0.3, 250)
val = 30 * np.exp(-(((lon + 121.5) ** 2 + (lat - 35.5) ** 2) / 0.8)) + rng.normal(0, 1.5, lon.size)

os.makedirs(OUTDIR, exist_ok=True)
for name in STYLES:
    fig = pygmt.Figure()
    with style(name):
        frame = [f"WSne+t{name}", "xaf", "yaf"]
        if name in ("minimal", "dark"):
            frame = [f"WSne+t{name}", "xafg", "yafg"]  # these styles carry a light grid
        fig.basemap(region=REGION, projection="M8c", frame=frame)
        fig.coast(**coast_colors(name), resolution="i")
        pygmt.makecpt(cmap="vik", series=[-30, 30])
        fig.plot(x=lon, y=lat, style="c0.14c", fill=val, cmap=True, pen="0.3p,gray30")
        panel_label(fig, "A", style_name=name)
        colorbar(fig, "LOS displacement (mm)", style_name=name, width=6)
    fig.savefig(os.path.join(OUTDIR, f"style_{name}.png"), dpi=150)
    print(f"wrote previews/style_{name}.png")
