#!/usr/bin/env python
"""Standard displacement / velocity map (InSAR LOS, GPS vertical, etc.).

A geographic map of a diverging quantity on a relief-shaded background, with a square
panel label, horizontal bottom colorbar, and house-style plain frame. Runs standalone
with synthetic demo data; replace the CONFIG block and the `lon/lat/value` arrays (or a
grid) with your own.

Usage:  python displacement_map.py
"""
import numpy as np
import pygmt

# ---------------- CONFIG ----------------
REGION = [-120.0, -119.0, 35.0, 35.8]   # [W, E, S, N]
PROJECTION = "M12c"                       # Mercator, 12 cm wide
CMAP = "vik"                              # diverging: vik / roma / polar
CLIM = [-30, 30]                          # color limits (e.g. mm)
UNIT = "LOS displacement (mm)"
PANEL = "A"                               # panel label (uppercase, no parentheses)
RELIEF_RES = "15s"                        # earth_relief resolution
OUT = "displacement_map.png"
# ----------------------------------------

# Demo data: a Gaussian uplift blob. Replace with your observations / grid.
rng = np.random.default_rng(0)
lon = rng.uniform(REGION[0], REGION[1], 400)
lat = rng.uniform(REGION[2], REGION[3], 400)
c_lon, c_lat = -119.5, 35.4
value = 28 * np.exp(-(((lon - c_lon) / 0.12) ** 2 + ((lat - c_lat) / 0.10) ** 2))

fig = pygmt.Figure()
with pygmt.config(MAP_FRAME_TYPE="plain", MAP_FRAME_PEN="1p,black",
                  FONT_ANNOT_PRIMARY="9p", FONT_LABEL="10p"):
    # 1. relief-shaded background (grayscale, so the data CPT reads clearly)
    relief = pygmt.datasets.load_earth_relief(resolution=RELIEF_RES, region=REGION)
    shade = pygmt.grdgradient(grid=relief, azimuth=315, normalize="t1")
    fig.basemap(region=REGION, projection=PROJECTION, frame=["WSne", "xaf", "yaf"])
    fig.grdimage(grid=relief, shading=shade, cmap="gray", projection=PROJECTION)

    # 2. data layer
    pygmt.makecpt(cmap=CMAP, series=[CLIM[0], CLIM[1], (CLIM[1] - CLIM[0]) / 40.0], continuous=True)
    fig.plot(x=lon, y=lat, fill=value, cmap=True, style="c0.18c", pen="0.25p,black")

    # 3. coastline / context
    fig.coast(shorelines="0.5p,black", borders="2/0.3p,gray40", resolution="f")

    # 4. panel label: square white box, equal offset from left & top
    fig.text(position="TL", text=PANEL, font="12p,Helvetica-Bold,black", justify="TL",
             offset="j0.2c", fill="white", pen="0.8p,black", clearance="1.5p/1.5p")

    # 5. horizontal colorbar at bottom with unit and generous offset
    fig.colorbar(position="JBC+w8c/0.4c+h+o0c/0.9c", frame=f"x+l{UNIT}")

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
