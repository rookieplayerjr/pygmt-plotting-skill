#!/usr/bin/env python
"""Earthquake catalog map: epicenters colored by depth, sized by magnitude, with optional
focal-mechanism beachballs.

House-style plain frame, square panel label, horizontal depth colorbar. Runs standalone
with synthetic data; replace the `cat` DataFrame (lon, lat, depth, mag) and `mechs` list
with your catalog / GCMT solutions.

Usage:  python seismicity_map.py
"""
import numpy as np
import pandas as pd
import pygmt

# ---------------- CONFIG ----------------
REGION = [-118.5, -117.0, 35.0, 36.2]
PROJECTION = "M12c"
DEPTH_RANGE = [0, 15]          # km, for the CPT
DEPTH_CMAP = "inferno"         # sequential; reversed below so shallow = bright
PANEL = "A"
OUT = "seismicity_map.png"
# ----------------------------------------

# Demo catalog. Replace with your own (e.g. from USGS / SCEC).
rng = np.random.default_rng(1)
N = 250
cat = pd.DataFrame({
    "lon": rng.uniform(REGION[0], REGION[1], N),
    "lat": rng.uniform(REGION[2], REGION[3], N),
    "depth": rng.uniform(1, 14, N),
    "mag": rng.uniform(1.0, 4.5, N),
})

# Demo focal mechanisms (Aki convention). Replace or set to [] to skip.
mechs = pd.DataFrame({
    "longitude": [-117.8, -117.4],
    "latitude": [35.5, 35.9],
    "depth": [6.0, 9.0],
    "strike": [320, 45], "dip": [80, 60], "rake": [-170, 90],
    "magnitude": [5.2, 4.8],
})

fig = pygmt.Figure()
with pygmt.config(MAP_FRAME_TYPE="plain", MAP_FRAME_PEN="1p,black",
                  FONT_ANNOT_PRIMARY="9p", FONT_LABEL="10p"):
    fig.basemap(region=REGION, projection=PROJECTION, frame=["WSne", "xaf", "yaf"])
    fig.coast(land="gray92", water="white", shorelines="0.5p,black", resolution="f")

    # epicenters: color = depth, size = magnitude
    pygmt.makecpt(cmap=DEPTH_CMAP, series=[DEPTH_RANGE[0], DEPTH_RANGE[1], 1], reverse=True)
    fig.plot(x=cat.lon, y=cat.lat, fill=cat.depth, cmap=True,
             size=0.015 * 2 ** cat.mag, style="cc", pen="0.2p,black")

    # focal mechanisms (colored by depth via the same CPT). When spec is a DataFrame the
    # longitude/latitude/depth columns are read from it — do NOT also pass them as kwargs.
    if len(mechs):
        fig.meca(spec=mechs, scale="0.4c", convention="aki", cmap=True)

    fig.text(position="TL", text=PANEL, font="12p,Helvetica-Bold,black", justify="TL",
             offset="j0.2c", fill="white", pen="0.8p,black", clearance="1.5p/1.5p")
    fig.colorbar(position="JBC+w8c/0.4c+h+o0c/0.9c", frame="x+lHypocenter depth (km)")

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
