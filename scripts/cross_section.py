#!/usr/bin/env python
"""Map + cross-section: a profile line A-B on a relief map (top), with a topographic profile
and earthquakes projected onto a depth section (bottom).

Demonstrates pygmt.project (generate line + project points) and pygmt.grdtrack (sample DEM).
Runs standalone with synthetic earthquakes; replace `eqs` (lon, lat, depth, mag) with yours.

Usage:  python cross_section.py
"""
import numpy as np
import pandas as pd
import pygmt

# ---------------- CONFIG ----------------
REGION = [-118.5, -117.0, 35.0, 36.2]
PROJECTION = "M12c"
A = [-118.3, 35.2]      # profile start [lon, lat]
B = [-117.2, 36.0]      # profile end
SWATH_KM = 15.0         # keep events within +/- this perpendicular distance
DEPTH_MAX = 15.0        # km, section depth axis
OUT = "cross_section.png"
# ----------------------------------------

rng = np.random.default_rng(2)
N = 200
eqs = pd.DataFrame({
    "lon": rng.uniform(REGION[0], REGION[1], N),
    "lat": rng.uniform(REGION[2], REGION[3], N),
    "depth": rng.uniform(1, 14, N),
    "mag": rng.uniform(1.0, 4.0, N),
})

relief = pygmt.datasets.load_earth_relief(resolution="15s", region=REGION)

fig = pygmt.Figure()
with pygmt.config(MAP_FRAME_TYPE="plain", MAP_FRAME_PEN="1p,black",
                  FONT_ANNOT_PRIMARY="9p", FONT_LABEL="10p"):
    # ---- bottom: map ----
    shade = pygmt.grdgradient(grid=relief, azimuth=315, normalize="t1")
    fig.basemap(region=REGION, projection=PROJECTION, frame=["WSne", "xaf", "yaf"])
    fig.grdimage(grid=relief, shading=shade, cmap="oleron")
    fig.coast(shorelines="0.5p,black", resolution="f")
    fig.plot(x=[A[0], B[0]], y=[A[1], B[1]], pen="1.5p,red")
    fig.text(x=[A[0], B[0]], y=[A[1], B[1]], text=["A", "B"],
             offset="0c/0.3c", font="12p,Helvetica-Bold,red")
    fig.text(position="TL", text="A", font="12p,Helvetica-Bold,black", justify="TL",
             offset="j0.2c", fill="white", pen="0.8p,black", clearance="1.5p/1.5p")

    # project earthquakes onto the section: p = along-track km, z = depth, keep |q| < SWATH
    proj = pygmt.project(data=eqs[["lon", "lat", "depth", "mag"]], center=A, endpoint=B,
                         convention="pz", unit=True, width=[-SWATH_KM, SWATH_KM])
    proj.columns = ["p", "depth", "mag"]
    # generate="1k" walks the line in 1 km steps; column p is along-track distance,
    # so its last value IS the section length.
    seclen = float(pygmt.project(center=A, endpoint=B, generate="1k",
                                 unit=True).p.iloc[-1])

    # ---- top: depth section (negative height -> depth increases downward) ----
    fig.shift_origin(yshift="h+2.1c")   # gap must clear the colorbar below the section
    pygmt.makecpt(cmap="inferno", series=[0, DEPTH_MAX, 1], reverse=True)
    fig.basemap(region=[0, seclen, 0, DEPTH_MAX], projection="X12c/-4c",
                frame=["WSne", "xaf+lDistance (km)", "yaf+lDepth (km)"])
    fig.plot(x=proj.p, y=proj.depth, fill=proj.depth, cmap=True,
             size=0.015 * 2 ** proj.mag, style="cc", pen="0.2p,black")
    fig.text(x=[0, seclen], y=[0, 0], text=["A", "B"], no_clip=True,
             offset="0c/0.25c", font="11p,Helvetica-Bold,red")
    fig.colorbar(position="JBC+w7c/0.35c+h+o0c/0.9c", frame="x+lDepth (km)")

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
