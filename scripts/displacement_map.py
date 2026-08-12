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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.expanduser("~/.claude/skills/pygmt-plotting/scripts"))  # fallback when this file is copied elsewhere
from style_presets import colorbar, panel_label, style

# ---------------- CONFIG ----------------
STYLE = "house"                           # house / journal / classic / minimal / presentation / dark
REGION = [-120.0, -119.0, 35.0, 35.8]   # [W, E, S, N]
PROJECTION = "M12c"                       # Mercator, 12 cm wide
CMAP = "vik"                              # diverging: vik / roma / polar
CLIM = [-30, 30]                          # color limits (e.g. mm)
UNIT = "LOS displacement (mm)"
PANEL = "A"                               # panel label (uppercase, no parentheses)
RELIEF_RES = "15s"                        # earth_relief resolution
INSET = None                              # "globe" = corner locator globe OVERLAID on the
                                          # map (fig.inset, GALLERY #4) — never a detached
                                          # globe floating outside the frame
OUT = "displacement_map.png"
# ----------------------------------------

# Demo data: a Gaussian uplift blob. Replace with your observations / grid.
rng = np.random.default_rng(0)
lon = rng.uniform(REGION[0], REGION[1], 400)
lat = rng.uniform(REGION[2], REGION[3], 400)
c_lon, c_lat = -119.5, 35.4
value = 28 * np.exp(-(((lon - c_lon) / 0.12) ** 2 + ((lat - c_lat) / 0.10) ** 2))

fig = pygmt.Figure()
with style(STYLE):
    # 1. relief-shaded background (grayscale, so the data CPT reads clearly)
    relief = pygmt.datasets.load_earth_relief(resolution=RELIEF_RES, region=REGION)
    shade = pygmt.grdgradient(grid=relief, azimuth=315, normalize="t1")
    fig.basemap(region=REGION, projection=PROJECTION, frame=["WSne", "xaf", "yaf"])
    fig.grdimage(grid=relief, shading=shade, cmap="gray", projection=PROJECTION)

    # 2. data layer
    pygmt.makecpt(cmap=CMAP, series=[CLIM[0], CLIM[1], (CLIM[1] - CLIM[0]) / 40.0], continuous=True)
    fig.plot(x=lon, y=lat, fill=value, cmap=True, style="c0.18c", pen="0.25p,black")
    # For a CONTINUOUS field from scattered points, grid first then grdimage — never feed
    # scatter straight to xyz2grd (vertical-stripe artifact, GOTCHAS 3.5):
    #   binned = pygmt.blockmean(data=..., region=REGION, spacing="30s")
    #   grid   = pygmt.surface(data=binned, region=REGION, spacing="30s", tension=0.35)
    #   fig.grdimage(grid=grid, cmap=True, transparency=30)

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
