#!/usr/bin/env python
"""Multi-panel component figure (e.g. East / North / Up displacement) sharing one CPT and a
single horizontal colorbar below all panels.

Demonstrates fig.subplot with autolabel and a shared colorbar drawn OUTSIDE the subplot
block. Runs standalone with synthetic grids; replace the `grids`/`titles` with your data
(xarray.DataArray or .grd files).

Usage:  python multipanel_components.py
"""
import numpy as np
import pygmt
import xarray as xr

# ---------------- CONFIG ----------------
REGION = [-120.0, -119.0, 35.0, 35.8]
PROJECTION = "M?"          # '?' lets subplot auto-size each panel
CMAP = "vik"
CLIM = [-30, 30]
UNIT = "Displacement (mm)"
TITLES = ["East", "North", "Up"]
OUT = "multipanel_components.png"
# ----------------------------------------

# Demo grids: three offset Gaussian blobs. Replace with your component grids.
lons = np.linspace(REGION[0], REGION[1], 120)
lats = np.linspace(REGION[2], REGION[3], 100)
LON, LAT = np.meshgrid(lons, lats)
def blob(c_lon, c_lat, amp):
    return amp * np.exp(-(((LON - c_lon) / 0.12) ** 2 + ((LAT - c_lat) / 0.10) ** 2))
grids = [
    xr.DataArray(blob(-119.5, 35.4, -22), coords=[("lat", lats), ("lon", lons)]),
    xr.DataArray(blob(-119.6, 35.5, 15), coords=[("lat", lats), ("lon", lons)]),
    xr.DataArray(blob(-119.45, 35.35, 28), coords=[("lat", lats), ("lon", lons)]),
]
for g in grids:           # mark as geographic, gridline-registered
    g.gmt.gtype = 1
    g.gmt.registration = 0

INC = (CLIM[1] - CLIM[0]) / 40.0
pygmt.makecpt(cmap=CMAP, series=[CLIM[0], CLIM[1], INC], continuous=True)  # session CPT

fig = pygmt.Figure()
with pygmt.config(MAP_FRAME_TYPE="plain", MAP_FRAME_PEN="1p,black",
                  FONT_ANNOT_PRIMARY="8p", FONT_LABEL="9p", FONT_TAG="12p,Helvetica-Bold"):
    # autolabel modifiers give the house-style square white box around A/B/C
    with fig.subplot(nrows=1, ncols=3, figsize=("18c", "5c"),
                     autolabel="A+jTL+o0.2c+gwhite+p0.8p,black",
                     margins="0.4c", frame=["WSne", "xaf", "yaf"], sharey="l"):
        for k, (grid, title) in enumerate(zip(grids, TITLES)):
            fig.basemap(region=REGION, projection=PROJECTION, panel=k)
            fig.grdimage(grid=grid, projection=PROJECTION)     # uses session CPT
            fig.coast(shorelines="0.4p,black", resolution="f")
            fig.text(position="TC", text=title, font="10p,Helvetica-Bold,black",
                     offset="0c/-0.3c", no_clip=True)
    # shared colorbar OUTSIDE the subplot block, centered under all panels
    fig.colorbar(position="JBC+w9c/0.4c+h+o0c/1.0c", frame=f"x+l{UNIT}")

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
