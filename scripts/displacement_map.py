#!/usr/bin/env python
"""Standard displacement / velocity map (InSAR LOS, GPS vertical, etc.).

A geographic map of a diverging quantity on a relief-shaded background, with a square
panel label, horizontal bottom colorbar, and house-style plain frame. Runs standalone
with synthetic demo data; replace the CONFIG block and the `lon/lat/value` arrays (or a
grid) with your own.

Usage:  python displacement_map.py
"""
import os
import sys

import numpy as np
import pygmt
import xarray as xr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.expanduser("~/.claude/skills/pygmt-plotting/scripts"))  # fallback when this file is copied elsewhere
from style_presets import colorbar, panel_label, style

# ---------------- CONFIG ----------------
STYLE = "house"                           # house / journal / classic / minimal / presentation / dark
REGION = [-118.2, -117.2, 35.4, 36.15]  # [W, E, S, N] — Ridgecrest 2019 area
PROJECTION = "M12c"                       # Mercator, 12 cm wide
CMAP = "vik"                              # diverging: vik / roma / polar
CLIM = [-30, 30]                          # color limits (e.g. cm)
UNIT = "LOS displacement (cm)"
PANEL = "A"                               # panel label (uppercase, no parentheses)
RELIEF_RES = "03s"                        # earth_relief resolution (<=1 deg region -> 03s/15s)
INSET = "globe"                           # "globe" = corner locator globe OVERLAID on the
                                          # map (fig.inset, GALLERY #4) — never a detached
                                          # globe floating outside the frame
OUT = "displacement_map.png"
# ----------------------------------------

# Demo data: a gridded coseismic LOS field with the four-quadrant pattern of a NW-SE
# strike-slip rupture (Ridgecrest-like), draped semi-transparently over real terrain.
# Replace `los` with your own grid (xarray/NetCDF/GeoTIFF) — or scatter points, see
# the commented scatter branch below.
F_AZ = np.radians(-40)                    # fault strike (NW-SE)
F_LON, F_LAT = -117.55, 35.77             # fault center
lons = np.linspace(REGION[0], REGION[1], 700)
lats = np.linspace(REGION[2], REGION[3], 550)
LON, LAT = np.meshgrid(lons, lats)
xf = (LON - F_LON) * np.cos(F_AZ) + (LAT - F_LAT) * np.sin(F_AZ)   # along-strike
yf = -(LON - F_LON) * np.sin(F_AZ) + (LAT - F_LAT) * np.cos(F_AZ)  # fault-normal
# four-quadrant butterfly of a strike-slip event (dipole along AND across strike),
# with the LOS asymmetry that makes one lobe pair dominate
u, v = xf / 0.28, yf / 0.11
los = 165 * u * v * np.exp(-u ** 2 - v ** 2) * (1 + 0.35 * np.tanh(v))
los_grid = xr.DataArray(los, coords=[("lat", lats), ("lon", lons)])
los_grid.gmt.gtype = 1
los_grid.gmt.registration = 0
# fault surface trace (along-strike line through the center)
t = np.linspace(-0.35, 0.35, 50)
trace_lon = F_LON + t * np.cos(F_AZ)
trace_lat = F_LAT + t * np.sin(F_AZ)

fig = pygmt.Figure()
with style(STYLE):
    # 1. relief-shaded background (grayscale, so the data CPT reads clearly)
    relief = pygmt.datasets.load_earth_relief(resolution=RELIEF_RES, region=REGION)
    shade = pygmt.grdgradient(grid=relief, azimuth=315, normalize="t1")
    fig.basemap(region=REGION, projection=PROJECTION, frame=["WSne", "xaf", "yaf"])
    fig.grdimage(grid=relief, shading=shade, cmap="gray", projection=PROJECTION)

    # 2. data layer: semi-transparent gridded field over the grayscale relief
    pygmt.makecpt(cmap=CMAP, series=[CLIM[0], CLIM[1]], continuous=True)
    fig.grdimage(grid=los_grid, cmap=True, transparency=35, nan_transparent=True)
    fig.plot(x=trace_lon, y=trace_lat, pen="1.2p,black")   # fault surface trace
    # Scatter alternative (GPS/leveling points):
    #   fig.plot(x=lon, y=lat, fill=value, cmap=True, style="c0.18c", pen="0.25p,black")
    # Scatter -> continuous grid: blockmean + surface first — never feed scatter
    # straight to xyz2grd (vertical-stripe artifact, GOTCHAS 3.5).

    # 3. coastline / context
    fig.coast(shorelines="0.5p,black", borders="2/0.3p,gray40", resolution="f")

    # 4. optional corner locator globe, overlaid INSIDE the map frame
    if INSET == "globe":
        c_lon, c_lat = (REGION[0] + REGION[1]) / 2, (REGION[2] + REGION[3]) / 2
        with fig.inset(position="jTR+w3c+o0.25c"):
            fig.coast(region="g", projection=f"G{c_lon}/{c_lat}/?", land="gray75",
                      water="white", shorelines="0.2p,gray50", area_thresh=10000)
            fig.plot(x=[c_lon], y=[c_lat], style="s0.3c", fill="red", pen="0.8p,red")

    # 5. panel label (boxed uppercase letter) + bottom colorbar, both style-aware
    panel_label(fig, PANEL, style_name=STYLE)
    colorbar(fig, UNIT, style_name=STYLE, width=8)

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
