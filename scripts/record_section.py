#!/usr/bin/env python
"""Teleseismic record section: distance-sorted vertical traces + TauP arrival curves.

The waveform figure of the GMT China community 地震/sac card, in PyGMT: each
trace drawn as a wiggle offset to its epicentral distance, with iasp91 P and S
travel-time curves overlaid. Runs on REAL bundled data — 11 IU/II LHZ records
of the 2026-07-28 Mw 6.8 Kumamoto earthquake (EarthScope FDSN, public domain).

Requires obspy to read the bundled miniSEED (and to refetch other events).

Usage:  python record_section.py
"""
import csv
import os
import sys

import numpy as np
import pygmt
from obspy import read
from obspy.taup import TauPyModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.expanduser("~/.claude/skills/pygmt-plotting/scripts"))  # fallback when this file is copied elsewhere
from style_presets import panel_label, style

# ---------------- CONFIG ----------------
STYLE = "house"
TMAX = 2400              # s after origin
DRANGE = [20, 90]        # deg
GAIN = 3.2               # wiggle height in degrees of distance
BP = (0.02, 0.1)         # bandpass (Hz) for LHZ display
OUT = "record_section.png"
# ----------------------------------------

d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
st = read(os.path.join(d, "recsec_kumamoto2026.mseed"))
with open(os.path.join(d, "recsec_kumamoto2026_meta.csv")) as f:
    meta = {(r["net"], r["sta"]): float(r["dist_deg"]) for r in csv.DictReader(f)}
origin_time, ev_lat, ev_lon, ev_dep, ev_mag = \
    open(os.path.join(d, "recsec_kumamoto2026_event.txt")).read().split()

st.detrend("demean")
st.taper(0.02)
st.filter("bandpass", freqmin=BP[0], freqmax=BP[1], corners=4, zerophase=True)

fig = pygmt.Figure()
with style(STYLE):
    fig.basemap(region=[0, TMAX, DRANGE[0], DRANGE[1]], projection="X15c/11c",
                frame=["WSne+tKumamoto 2026 Mw 6.8 — vertical LHZ",
                       "xa300f100+lTime since origin (s)",
                       "ya10f5+lEpicentral distance (deg)"])
    # TauP predicted arrivals (iasp91), drawn under the traces
    model = TauPyModel("iasp91")
    for phase, pen in [("P", "0.9p,royalblue3,-"), ("S", "0.9p,firebrick,-")]:
        dd, tt = [], []
        for dist in np.arange(DRANGE[0], DRANGE[1] + 1, 2):
            arr = model.get_travel_times(source_depth_in_km=float(ev_dep),
                                         distance_in_degree=float(dist),
                                         phase_list=[phase])
            if arr:
                dd.append(dist)
                tt.append(arr[0].time)
        fig.plot(x=tt, y=dd, pen=pen)
        k = int(len(dd) * 0.72)   # label on the curve interior, not the clipped top edge
        fig.text(x=tt[k], y=dd[k], text=phase, offset="-0.42c/0c",
                 font=f"11p,Helvetica-Bold,{pen.split(',')[1]}", justify="MR",
                 fill="white@20", clearance="1p/1p")
    # traces: normalized wiggles offset to their distance
    for tr in st:
        key = (tr.stats.network, tr.stats.station)
        if key not in meta:
            continue
        dist = meta[key]
        t = np.arange(tr.stats.npts) * tr.stats.delta
        keep = t <= TMAX
        amp = tr.data[keep] / (np.abs(tr.data[keep]).max() or 1)
        fig.plot(x=t[keep], y=dist + amp * GAIN / 2, pen="0.5p,gray10")
        fig.text(x=TMAX, y=dist, text=f"{key[0]}.{key[1]}", justify="ML",
                 offset="0.15c/0c", font="7.5p,Helvetica,gray25", no_clip=True)
    panel_label(fig, "A", style_name=STYLE)

fig.savefig(OUT, dpi=300, crop=True)
print(f"wrote {OUT}")
from qc_check import qc_image
qc_image(OUT)   # hard QC gate — a broken render aborts here instead of shipping

