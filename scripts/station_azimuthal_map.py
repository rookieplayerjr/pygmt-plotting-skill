#!/usr/bin/env python
"""Station-centered azimuthal-equidistant map with epicentral-distance rings.

The standard teleseismic-geometry figure (receiver functions, SKS splitting,
array analysis): the whole far field at true azimuth and distance from one
station, with 30/60/90-degree rings. PyGMT adaptation of GMT China community
ex011 (docs.gmt-china.org), restyled to the house rules.

Runs standalone; replace STATION and the `events` table with your own.

Usage:  python station_azimuthal_map.py
"""
import os
import sys
import tempfile

import pygmt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.expanduser("~/.claude/skills/pygmt-plotting/scripts"))  # fallback when this file is copied elsewhere
from style_presets import panel_label, style

# ---------------- CONFIG ----------------
STYLE = "house"              # house / journal / classic / minimal / presentation / dark
STATION = (105.0, 30.0)      # lon, lat of the receiver
HORIZON = 150                # degrees of the far field to show
RINGS = [30, 60, 90, 120]    # epicentral-distance circles (deg)
OUT = "station_azimuthal_map.png"
# ----------------------------------------

# Demo events: well-known large earthquakes (lon, lat, label)
events = [
    (142.37, 38.30, "Tohoku 2011"),
    (95.98, 3.30, "Sumatra 2004"),
    (-72.71, -35.91, "Maule 2010"),
    (-147.34, 61.35, "Alaska 2018"),
    (37.03, 37.17, "Turkiye 2023"),
    (84.73, 28.23, "Gorkha 2015"),
]

fig = pygmt.Figure()
with style(STYLE):
    fig.coast(region="g", projection=f"E{STATION[0]}/{STATION[1]}/{HORIZON}/14c",
              land="gray88", water="white", shorelines="0.3p,gray45",
              area_thresh=20000, frame="g30")
    # epicentral-distance rings: style E- reads "lon lat diameter" per row —
    # diameter = 2x the epicentral distance, in degrees (unit d)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        for r in RINGS:
            f.write(f"{STATION[0]} {STATION[1]} {2 * r}d\n")
        rings = f.name
    fig.plot(data=rings, style="E-", pen="0.8p,firebrick,-")
    os.unlink(rings)
    # ring labels straight south of the station
    fig.text(x=[STATION[0]] * len(RINGS), y=[STATION[1] - r for r in RINGS],
             text=[f"{r}\\260" for r in RINGS], font="9p,Helvetica,firebrick",
             offset="0c/0.25c", fill="white", clearance="1p/1p")
    # events + station
    fig.plot(x=[e[0] for e in events], y=[e[1] for e in events],
             style="a0.42c", fill="gold", pen="0.6p,black")
    fig.text(x=[e[0] for e in events], y=[e[1] for e in events],
             text=[e[2] for e in events], font="8p,Helvetica,black",
             offset="0c/0.4c", fill="white@25", clearance="1p/1p")
    fig.plot(x=[STATION[0]], y=[STATION[1]], style="t0.5c", fill="royalblue3",
             pen="0.8p,black")
    panel_label(fig, "A", style_name=STYLE)

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
