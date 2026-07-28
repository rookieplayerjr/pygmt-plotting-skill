---
name: pygmt-plotting
description: Create publication-quality scientific maps and figures with PyGMT (Python GMT). Covers the full PyGMT API — basemaps, coastlines, topography/grids (grdimage/grdcontour/grdview), CPT color scales, scatter/line/vector plots, focal mechanisms (meca), velocity fields (velo), cross-sections (project/grdtrack), and multi-panel layout (subplot/inset/shift_origin). Use when plotting any map or figure with PyGMT/GMT, or when the user mentions topography/relief maps, InSAR/displacement fields, earthquake catalogs, beachballs, GPS velocities, profiles, or `import pygmt`.
---

# PyGMT Plotting

PyGMT wraps the Generic Mapping Tools. Every method parameter accepts both a Python
full name (`projection`) and the GMT single-letter alias (`J`) — this skill uses full
names. Grid-processing functions return `xarray.DataArray` when `outgrid=None`, so
results chain directly into plotting functions.

## Required figure format (house style)

All scientific figures MUST follow these format rules:

- **Frame**: `MAP_FRAME_TYPE='plain'`, `MAP_FRAME_PEN='1p,black'`. Never draw frame twice (no basemap + plot both setting frame).
- **Panel labels**: UPPERCASE letter (A, B, C...) in top-left corner inside frame, **no parentheses**, bold ≥10p, **square box** (white fill + 0.8p black pen, `clearance='1.5p/1.5p/1.5p/1.5p'`). Equal distance from left and top borders. Title text (e.g., "East") centered at top separately.
- **Tick labels**: Only on left (W) and bottom (S) edges.
- **Colorbar**: Horizontal at bottom, with unit label, enough offset from axis labels (`+o0c/0.8c`).
- **Color scale**: `vik` for diverging displacement, sequential: `inferno` or `roma`.
- **Depth axes read POSITIVE, down** (hard rule for fault/cross-section/3D figures): the depth axis must be labelled `0, 20, 40 …` (positive kilometres), never `0, -20, -40`. Store depth as a **positive** value (depth increases downward), set the region depth range to `[0, zmax]`, and **flip the axis with a negative height**: 2D cross-sections use `projection="X<w>c/-<h>c"` (negative height → y increases downward); 3D perspective plots use `zsize="-<h>c"` (negative → deep at the bottom, labels positive). Never emit negative z data just to get "up = positive" — that puts minus signs on the depth axis. When you flip a 3D z-axis this way, any in-plane up-dip vector's **vertical component also flips sign** (up-dip now means *decreasing* positive depth).
- **No double frames**: subplot handles frame → do NOT call basemap(frame=) inside panels.
- **Self-check**: After generating each figure, read/inspect it. Fix double frames, clipped content, inconsistent labels before showing to user.

## Quick start

```python
import pygmt

fig = pygmt.Figure()
with pygmt.config(MAP_FRAME_TYPE="plain", MAP_FRAME_PEN="1p,black"):
    fig.basemap(region=[-125, -114, 32, 42], projection="M12c", frame=["WSne", "xaf", "yaf"])
    fig.coast(land="gray90", water="white", shorelines="0.5p,black")
    pygmt.makecpt(cmap="vik", series=[-10, 10])         # sets the session CPT
    fig.plot(x=[-119.5], y=[35.3], style="c0.3c", fill=[5.0], cmap=True, pen="0.5p,black")
    fig.colorbar(frame="x+lVelocity (mm/yr)", position="JBC+w8c/0.4c+h+o0c/0.8c")
fig.savefig("map.png", dpi=300, crop=True)
```

`fig.show()` previews; `fig.savefig("f.pdf")` (vector) or `.png`/`.tif` (raster, pass `dpi=`).

## The three universal parameters

Every map command takes these; the first command sets them and later commands reuse them.

- **`region`** (R) — `[W, E, S, N]` (note order: West, East, South, North). `"g"`/`"d"` = global; `"JP"` = ISO country code; append `+r` for corner coordinates.
- **`projection`** (J) — `code[params/]width`, width **must carry a unit** (`c`/`i`/`p`): `"M12c"` Mercator, `"X10c/6c"` linear, `"L-100/35/33/45/12c"` Lambert conic, `"G-120/40/12c"` orthographic.
- **`frame`** (B) — `["WSne", "xaf", "yaf+lLabel", "+tTitle"]`. Uppercase edge = axis+ticks+annotations, lowercase = no annotations. `a`=annotation/major, `f`=minor tick, `g`=grid. Axis labels `+l` work **only on Cartesian (X) projections**, not geographic.

## Choosing a projection / CPT (cheat sheet)

| Need | Projection |
|---|---|
| Region map (low–mid lat, InSAR/swarm) | `M` Mercator `"M12c"` |
| Continental, low distortion | `L` Lambert conic `"L lon0/lat0/lat1/lat2/w"` |
| Locator inset / hemisphere | `G` orthographic `"G lon0/lat0/w"` |
| Global | `W` Mollweide / `N` Robinson / `H` Hammer |
| Depth/distance section | `X` linear, negative height → y points down: `"X12c/-4c"` |

| Data kind | CPT |
|---|---|
| Diverging (displacement, velocity, anomaly; zero-centered) | `vik`, `roma`, `broc`, `polar` |
| Sequential scalar | `inferno`, `roma`, `batlow`, `viridis`, `turbo` |
| Topography | `geo` (land), `oleron`/`relief` (land+ocean), `gray` (hillshade) |
| Cyclic (wrapped phase, azimuth) | `romaO`, `vikO` |

Make a CPT with `pygmt.makecpt(cmap="vik", series=[-50, 50, 5])` — with no `output=` it
becomes the **session CPT**, so subsequent `grdimage`/`plot(cmap=True)`/`colorbar` use it
automatically. Histogram-equalize a grid's colors with `pygmt.grd2cpt(grid=g, cmap="geo")`.

## House style (enforce on every figure)

These are the skill's opinionated defaults — override them when a target journal says otherwise:

1. Wrap drawing in `with pygmt.config(MAP_FRAME_TYPE="plain", MAP_FRAME_PEN="1p,black"):`. **Never draw the frame twice** (subplot/basemap handles it — don't re-pass `frame=` inside panels).
2. Tick labels only on **W (left)** and **S (bottom)** edges → `frame=["WSne", ...]`.
3. Panel labels: UPPERCASE letter (A, B, C…), **no parentheses**, bold ≥10p, in a **square white box** (white fill + 0.8p black pen), equal offset from left and top:
   ```python
   fig.text(position="TL", text="A", font="12p,Helvetica-Bold,black",
            justify="TL", offset="j0.2c", fill="white", pen="0.8p,black", clearance="1.5p/1.5p")
   ```
4. Colorbar: **horizontal at bottom**, with unit label, generous offset from axis labels: `position="JBC+w8c/0.4c+h+o0c/0.8c"`, `frame="x+lQuantity (unit)"`.
5. Diverging displacement → `vik`; sequential → `inferno`/`roma`.
6. **Raster resolution — no moiré (hard rule)**: when imaging fringe/speckle grids (wrapped interferograms, coherence), the rendered panel pixel count MUST be ≥ the grid's native columns: `panel_cm × dpi / 2.54 >= n_columns`. Default: single panel ≥16 cm at `dpi=400` (GMT modern mode: `gmt begin fig png E400`). If a multi-panel layout would undersample, split into single-panel figures instead of shrinking. Undersampled dense fringes alias into moiré ripples — a recurring failure mode on ScanSAR wrapped-phase panels.
7. **Self-check**: after saving, Read the output image and fix double frames, clipped content, inconsistent labels, or moiré/grid-like false texture in dense-fringe areas before showing the user.

## Workflow for a new figure

1. Decide region, projection, and CPT from the cheat sheet above.
2. Pick the closest template in [GALLERY.md](GALLERY.md) or `scripts/` and adapt it.
3. Draw inside the house-style `config` block; build bottom layer → top layer (relief → coast → data → annotations → colorbar).
4. `fig.savefig(..., dpi=300)` (dpi=400+ and check the pixel-count rule for fringe/speckle rasters), then Read the image and self-check (step 7 above).

## References

- [REFERENCE.md](REFERENCE.md) — complete API: figure lifecycle, coast/plot/text, grdimage/grdcontour/grdview, makecpt/colorbar, datasets, grid processing (grdcut/grdgradient/grdtrack/surface…), xarray, meca, velo, project, subplot/inset/shift_origin/legend.
- [GOTCHAS.md](GOTCHAS.md) — community-sourced pitfalls the API docs don't mention: region/dateline/projection traps, session-CPT overwrite & "no z-slices" error, xarray gtype/registration reset after arithmetic, grdimage-all-black, earth_relief cache, font-config scope, multi-panel colorbars, 0.x parameter renames, Ghostscript/conda install fixes. **§8 field-tested traps:** inset basemap drops annotations/labels (draw manually or use `shift_origin`); inset forces a default frame so `box="+p"` makes a double frame; `meca +m` Mw-scaling is invisible (size beachballs manually); `meca(cmap=True)` on negative depths segfaults; hand-written rasterio tif → `grdimage` segfault (use xarray instead); `shading` dimension mismatch (grdsample first); inset colorbar label overflow (`+mal`); `fig.plot(fill="white")` adds a stray black border. **§9 vector arrowheads (`style="v"`):** `+g`/`+h` are NOT broken — a head only appears if you also pass `+e`/`+b`, a vector shorter than the head length silently loses its head (fix with `+n<len>`), and `+h` near 1 degenerates the head so the fill vanishes. **Read this when a PyGMT figure misbehaves or errors unexpectedly.**
- [CRAFT.md](CRAFT.md) — community publication-craft: painter-model layer order, scientific colormaps (diverging must be zero-centered & symmetric), hillshade azimuth conventions, scalebar/compass/graticule, multi-panel alignment & shared colorbars, vector-vs-raster export, seismotectonic layering. **Read this to make a figure look good and submission-ready.**
- [GALLERY.md](GALLERY.md) — 13 ready-to-adapt scenario templates (basemap, multi-panel, inset, classified scatter, velocity field, histogram, rose, 3D, contours, cross-section, dual-axis).
- `scripts/` — runnable, parameterized templates: `displacement_map.py`, `seismicity_map.py`, `cross_section.py`, `multipanel_components.py`. Each runs standalone with demo data; edit the CONFIG block at the top.
