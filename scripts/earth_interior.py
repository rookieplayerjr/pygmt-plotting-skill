#!/usr/bin/env python
"""Earth-interior cross-section: shells to scale with seismic ray paths.

Polar (r-theta) projection with the real discontinuity radii — 410 / 660 km,
core-mantle boundary (r 3480 km), inner-core boundary (r 1221 km) — and
schematic PcP / PKiKP ray chords. PyGMT adaptation of GMT China community
ex002 (docs.gmt-china.org), house-styled.

Usage:  python earth_interior.py
"""
import os
import sys

import numpy as np
import pygmt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.expanduser("~/.claude/skills/pygmt-plotting/scripts"))  # fallback when this file is copied elsewhere
from style_presets import style

# ---------------- CONFIG ----------------
STYLE = "house"
R_EARTH = 6371.0
SHELLS = [                     # (outer radius, fill, name at that boundary)
    (R_EARTH, "wheat", "410 km"),
    (R_EARTH - 410, "navajowhite", "660 km"),
    (R_EARTH - 660, "burlywood", "CMB (2891 km)"),
    (3480.0, "darkorange", "ICB (5150 km)"),
    (1221.0, "gold", None),
]
OUT = "earth_interior.png"
# ----------------------------------------


def ring(r):
    th = np.linspace(0, 360, 721)
    return th, np.full_like(th, r)


def chord(th1, r1, th2, r2, n=200):
    """Straight Cartesian chord between two polar points, as (theta, r) samples."""
    a1, a2 = np.radians(th1), np.radians(th2)
    x1, y1 = r1 * np.cos(a1), r1 * np.sin(a1)
    x2, y2 = r2 * np.cos(a2), r2 * np.sin(a2)
    t = np.linspace(0, 1, n)
    x, y = x1 + t * (x2 - x1), y1 + t * (y2 - y1)
    return np.degrees(np.arctan2(y, x)) % 360, np.hypot(x, y)


fig = pygmt.Figure()
with style(STYLE):
    fig.basemap(region=[0, 360, 0, R_EARTH], projection="P14c+a", frame="+n")
    # shells, outermost first (painter model)
    for r, fill, _ in SHELLS:
        th, rr = ring(r)
        fig.plot(x=np.append(th, th[::-1]), y=np.append(rr, np.zeros_like(rr)),
                 fill=fill, close=True)
    # boundary circles
    for r, _, _ in SHELLS:
        th, rr = ring(r)
        fig.plot(x=th, y=rr, pen="0.6p,gray25")
    # PcP: down to the CMB bounce point and back up (reflection at r = 3480)
    for th_s, r_s, th_e, r_e in [(115, R_EARTH, 90, 3480), (90, 3480, 65, R_EARTH)]:
        th, rr = chord(th_s, r_s, th_e, r_e)
        fig.plot(x=th, y=rr, pen="1.6p,royalblue3")
    # PKiKP: through the inner core (schematic chord grazing the ICB)
    th, rr = chord(150, R_EARTH, 330, R_EARTH)
    fig.plot(x=th, y=rr, pen="1.6p,firebrick")
    # stations & source
    fig.plot(x=[115, 150], y=[R_EARTH, R_EARTH], style="a0.55c", fill="yellow",
             pen="0.8p,black", no_clip=True)
    fig.plot(x=[65, 330], y=[R_EARTH, R_EARTH], style="t0.5c", fill="royalblue3",
             pen="0.8p,black", no_clip=True)
    # labels
    fig.text(x=97, y=4400, text="PcP", font="12p,Helvetica-Bold,royalblue3",
             fill="white@25", clearance="1p/1p")
    fig.text(x=285, y=2600, text="PKiKP", font="12p,Helvetica-Bold,firebrick",
             fill="white@25", clearance="1p/1p")
    # boundary labels fanned along the upper-left so they don't stack
    for ang, rad, lab in [(215, 6050, "410"), (222, 5800, "660"),
                          (232, 3600, "CMB"), (248, 1350, "ICB")]:
        fig.text(x=ang, y=rad, text=lab, font="9p,Helvetica-Bold,gray15",
                 fill="white@25", clearance="1p/1p")

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
from qc_check import qc_image
qc_image(OUT)   # hard QC gate — a broken render aborts here instead of shipping

