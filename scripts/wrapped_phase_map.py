#!/usr/bin/env python
"""Wrapped interferogram (InSAR fringe) map done right.

Encodes the two hard rules that dense-fringe rasters keep violating:
1. CYCLIC colormap (romaO) + nearest-neighbor interpolation ("n") — bilinear
   smoothing across the +/-pi wrap paints a false gray band (GOTCHAS 8.13).
2. No moire: rendered pixels >= grid columns, i.e. width_cm * dpi / 2.54 >= ncols
   (SKILL.md hard rule 6). The script checks this and refuses to undersample.

Runs standalone with a synthetic coseismic fringe pattern; replace `phase` with
your wrapped-phase DataArray (radians, geographic coords).

Usage:  python wrapped_phase_map.py
"""
import os
import sys
import tempfile

import numpy as np
import pygmt
import xarray as xr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.expanduser("~/.claude/skills/pygmt-plotting/scripts"))  # fallback when this file is copied elsewhere
from style_presets import panel_label, style

# ---------------- CONFIG ----------------
STYLE = "house"          # house / journal / classic / minimal / presentation / dark
REGION = [-119.9, -119.1, 35.1, 35.7]
WIDTH_CM = 16            # single panel >= 16 cm for fringe rasters
DPI = 400
PANEL = "A"
WAVELENGTH_CM = 5.55     # C-band; one fringe = lambda/2 = 2.78 cm LOS
OUT = "wrapped_phase_map.png"
# ----------------------------------------

# Demo: wrap a synthetic LOS displacement field (two lobes, ~8 fringes).
lons = np.linspace(REGION[0], REGION[1], 900)
lats = np.linspace(REGION[2], REGION[3], 700)
LON, LAT = np.meshgrid(lons, lats)
los_cm = 22 * np.exp(-(((LON + 119.55) / 0.09) ** 2 + ((LAT - 35.42) / 0.07) ** 2)) \
    - 9 * np.exp(-(((LON + 119.35) / 0.12) ** 2 + ((LAT - 35.30) / 0.09) ** 2))
phase = xr.DataArray(np.angle(np.exp(1j * 4 * np.pi * los_cm / WAVELENGTH_CM)),
                     coords=[("lat", lats), ("lon", lons)])
phase.gmt.gtype = 1
phase.gmt.registration = 0

# moire guard: rendered pixel count must cover the grid columns
ncols = phase.sizes["lon"]
if WIDTH_CM * DPI / 2.54 < ncols:
    raise SystemExit(f"undersampled: {WIDTH_CM}cm@{DPI}dpi = "
                     f"{WIDTH_CM * DPI / 2.54:.0f}px < {ncols} columns -> widen or raise DPI")

fig = pygmt.Figure()
with style(STYLE):
    fig.basemap(region=REGION, projection=f"M{WIDTH_CM}c", frame=["WSne", "xaf", "yaf"])
    pygmt.makecpt(cmap="romaO", series=[-np.pi, np.pi], cyclic=True)
    # interpolation="n": never smooth across the wrap discontinuity
    fig.grdimage(grid=phase, cmap=True, interpolation="n")
    fig.coast(shorelines="0.5p,black", resolution="f")
    panel_label(fig, PANEL, style_name=STYLE)
    # cyclic colorbar annotated at -pi/0/pi via a GMT custom-annotation file
    # ("xc<file>"); @~..@~ switches to the Symbol font so "p" renders as pi
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(f"{-np.pi} a -@~p@~\n0 a 0\n{np.pi} a @~p@~\n")
        annots = f.name
    fig.colorbar(position=f"JBC+w{WIDTH_CM - 8}c/0.4c+h+o0c/0.8c",
                 frame=[f"xc{annots}",
                        f"x+lWrapped phase, one cycle = {WAVELENGTH_CM / 2:.2f} cm LOS"])
    os.unlink(annots)

fig.savefig(OUT, dpi=DPI, crop=True)
print(f"wrote {OUT} ({WIDTH_CM}cm @ {DPI}dpi, {ncols} cols)")
from qc_check import qc_image
qc_image(OUT)   # hard QC gate — a broken render aborts here instead of shipping

