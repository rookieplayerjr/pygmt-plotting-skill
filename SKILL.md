---
name: pygmt-plotting
description: REQUIRED for ANY geographic map task (takes precedence over generic chart/dataviz guidance for maps) — publication-quality scientific maps and figures with PyGMT (Python GMT), with mandatory ready-to-run templates for common figure types and a mandatory pre-delivery QC loop (catches colorbar/label overlap, clipped text, missing arrowheads, layout collisions). Covers the full PyGMT API — basemaps, coastlines, topography/grids (grdimage/grdcontour/grdview), CPT color scales, scatter/line/vector plots, focal mechanisms (meca), velocity fields (velo), cross-sections (project/grdtrack), multi-panel layout (subplot/inset/shift_origin) — plus six selectable visual styles (house/journal/classic/minimal/presentation/dark). Use when plotting any map, topography/relief, profile/cross-section, InSAR/displacement field, wrapped interferogram, earthquake catalog, beachball, or GPS velocity figure — with PyGMT/GMT or any Python mapping code — or when the user mentions figure styles/themes/dark mode or `import pygmt`.
---

# PyGMT Plotting

PyGMT wraps the Generic Mapping Tools. Every method parameter accepts both a Python
full name (`projection`) and the GMT single-letter alias (`J`) — this skill uses full
names. Grid-processing functions return `xarray.DataArray` when `outgrid=None`, so
results chain directly into plotting functions.

## Load discipline (don't burn tokens on unused docs)

The DEFAULT path costs only this file + one template copy: route via the table below →
`cp` the script → edit CONFIG → render → QC. Do NOT preload the companion docs "for
context" — each opens only on its trigger, and at most once per session:

| Doc | Open ONLY when |
|---|---|
| [GOTCHAS.md](GOTCHAS.md) | a PyGMT call errors or the rendered figure shows an artifact (it's symptom-keyed — grep the symptom, read that section, not the whole file) |
| [REFERENCE.md](REFERENCE.md) | you need an API signature/param the template doesn't already demonstrate |
| [GALLERY.md](GALLERY.md) | no scripts/ template matches (second-tier routing below) — read the ONE matching snippet |
| [STYLES.md](STYLES.md) | choosing beyond the one-line style hints below, or customizing a preset |
| [CRAFT.md](CRAFT.md) | aesthetic/publication-polish decisions the presets don't settle |
| [QC.md](QC.md) | first figure delivery of the session; later figures reuse the checklist you already read |
| [COMMUNITY.md](COMMUNITY.md) | needing a GMT-China community example (3D finite-fault fence, station-centered azimuthal map, M-T plot…), Chinese/CJK labels, China border/fault datasets, or transparency/escape syntax |

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

## Template routing — check BEFORE writing any code

If the task matches a row below, the workflow is MECHANICAL — do these three steps literally:

1. `cp <skill>/scripts/<template>.py mywork.py` (real file copy — not "following the pattern")
2. Run it UNCHANGED first; confirm the demo figure renders.
3. Edit only the CONFIG block and the demo-data section for your case; rerun.

Do NOT re-implement the figure type by eye after skimming the template or the conventions —
two rounds of blind tests show every hand-rolled attempt reproduced exactly the traps the
templates already solve (hollow/detached/wrong-direction velo arrows, clipped profile panels,
blocky relief, wrap-band artifacts), while costing 10× the tokens. The templates run standalone
in ~5 s with synthetic demo data shaped like the real use case:

| Task looks like | Start from |
|---|---|
| Scalar displacement/velocity map (InSAR LOS, uplift, subsidence) | `scripts/displacement_map.py` |
| Earthquake catalog / seismicity map (± beachballs) | `scripts/seismicity_map.py` |
| Map + profile / depth section (topo or hypocenters) | `scripts/cross_section.py` |
| Multi-panel component grids (E/N/U, data-model-residual) | `scripts/multipanel_components.py` |
| GPS/GNSS vectors + error ellipses | `scripts/velocity_field_map.py` (velo arrows fail **silently** — GOTCHAS §9) |
| Wrapped interferogram / fringes | `scripts/wrapped_phase_map.py` (cyclic CPT + `interpolation="n"` + moiré guard) |
| 3D finite-fault slip distribution (fence diagram) | `scripts/fault_slip_3d.py` (plot3d polygons + -Z headers; depth positive-down) |
| Station-centered teleseismic geometry (distance rings) | `scripts/station_azimuthal_map.py` (azimuthal equidistant + `style="E-"` rings) |

**No scripts/ match? Check [GALLERY.md](GALLERY.md)'s 13 templates SECOND** — copy the matching
snippet before writing anything fresh: global/regional basemap #1, relief+sampled points #2,
subplot grid #3, **locator inset #4** (`fig.inset` overlaid on a map corner + `dcw` highlight —
do NOT detach the globe with shift_origin unless the inset itself needs tick labels, GOTCHAS 8.1),
grouped scatter #5, categorical scatter #6, velo demo #7, **histogram #8** (`fig.histogram` —
never hand-build bars from polygons), rose #9, 3D grdview #10, contours #11, map+profile #12,
dual-axis #13. Write from scratch only when NEITHER scripts/ nor GALLERY matches.

**Style routing** (set `STYLE` in the template's CONFIG): user says slides/talk → `presentation`;
dark slides/poster → `dark`; journal submission → `journal`; "classic look" → `classic`;
web/minimal → `minimal`; otherwise `house`. An explicit user style request overrides the default.

**Relief background resolution**: for regions ≤ ~1°, use `earth_relief` `"15s"`/`"03s"` (needs
`region=`); minute-class grids over small regions render as visible square blocks.

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
- **`frame`** (B) — `["WSne+tTitle", "xaf", "yaf+lLabel"]`. Uppercase edge = axis+ticks+annotations, lowercase = no annotations. `a`=annotation/major, `f`=minor tick, `g`=grid. Axis labels `+l` work **only on Cartesian (X) projections**, not geographic. **`+tTitle` must share the edge-letters entry** — a separate `"+tTitle"` list item hard-fails on GMT 6.6 (`-B parsing failure`).

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

These match the user's global plotting rules — apply unless told otherwise:

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
7. **Mandatory QC loop** — run the full render→Read→checklist→fix→re-render cycle in [QC.md](QC.md) before delivering ANY figure. It enumerates the micro-defects that actually ship (colorbar-over-label offsets, colliding panel ticks, clipped text, headless vectors, printed quote marks, detached insets, banded continuous fields) plus data anchors (fringe count vs displacement, arrow scale vs reference, azimuth convention, profile peak vs known elevation) and a requirement-echo pass against the user's literal request. "The code was fixed" ≠ "the image is fixed" — re-Read after every fix.

## Style presets (selectable looks)

Six ready styles in `scripts/style_presets.py` — `house` (default), `journal` (submission,
tighter), `classic` (GMT fancy frame), `minimal` (light modern), `presentation` (big fonts for
slides), `dark` (dark-background slides/posters). Template scripts switch via `STYLE = "..."`
in their CONFIG block; standalone use:

```python
from style_presets import style, panel_label, colorbar, coast_colors
with style("dark"):
    fig.basemap(..., frame=["WSne", "xaf", "yaf"])
    ...
    panel_label(fig, "A", style_name="dark")
    colorbar(fig, "LOS (mm)", style_name="dark")
```

Every style keeps the house hard rules (W/S-only annotations, bottom horizontal colorbar,
positive-down depth axes). Previews, per-style guidance (esp. dark-mode data-layer advice),
and how to add custom styles: [STYLES.md](STYLES.md).

## Workflow for a new figure

1. Decide region, projection, and CPT from the cheat sheet above; pick a style
   (default `house`; slides → `presentation`/`dark`; submission → `journal`).
2. Pick the closest template in [GALLERY.md](GALLERY.md) or `scripts/` and adapt it.
3. Draw inside `with style(...)` (or the house-style `config` block); build bottom layer →
   top layer (relief → coast → data → annotations → colorbar).
4. `fig.savefig(..., dpi=300)` (dpi=400+ and check the pixel-count rule for fringe/speckle rasters), then run the [QC.md](QC.md) loop (step 7 above) until every checklist item passes — only then deliver. Token discipline: Read a downsized copy once per round, batch ALL fixes into one re-render, cap at 3 renders.

## References

- [REFERENCE.md](REFERENCE.md) — complete API: figure lifecycle, coast/plot/text, grdimage/grdcontour/grdview, makecpt/colorbar, datasets, grid processing (grdcut/grdgradient/grdtrack/surface…), xarray, meca, velo, project, subplot/inset/shift_origin/legend.
- [GOTCHAS.md](GOTCHAS.md) — community-sourced pitfalls the API docs don't mention: region/dateline/projection traps, session-CPT overwrite & "no z-slices" error, xarray gtype/registration reset after arithmetic, grdimage-all-black, earth_relief cache, font-config scope, multi-panel colorbars, 0.x parameter renames, Ghostscript/conda install fixes. **§8 field-tested traps:** inset basemap drops annotations/labels (draw manually or use `shift_origin`); inset forces a default frame so `box="+p"` makes a double frame; `meca +m` Mw-scaling is invisible (size beachballs manually); `meca(cmap=True)` on negative depths segfaults; hand-written rasterio tif → `grdimage` segfault (use xarray instead); `shading` dimension mismatch (grdsample first); inset colorbar label overflow (`+mal`); `fig.plot(fill="white")` adds a stray black border. **§9 vector arrowheads (`style="v"`):** `+g`/`+h` are NOT broken — a head only appears if you also pass `+e`/`+b`, a vector shorter than the head length silently loses its head (fix with `+n<len>`), and `+h` near 1 degenerates the head so the fill vanishes. **Read this when a PyGMT figure misbehaves or errors unexpectedly.**
- [CRAFT.md](CRAFT.md) — community publication-craft: painter-model layer order, scientific colormaps (diverging must be zero-centered & symmetric), hillshade azimuth conventions, scalebar/compass/graticule, multi-panel alignment & shared colorbars, vector-vs-raster export, seismotectonic layering. **Read this to make a figure look good and submission-ready.**
- [QC.md](QC.md) — the mandatory pre-delivery QC loop: overlap/clipping/missing-element/spurious-ink/layout checklists (each item from a real observed failure), data-anchor checks, and the requirement-echo pass. Read it before the FIRST figure delivery of a session; apply from memory for the rest — the loop itself stays mandatory for every figure.
- [STYLES.md](STYLES.md) — the six style presets: preview images, config anchors (GMT_THEME classic/minimal, house rules, community dark recipe), dark-mode pitfalls, CJK note, how to extend.
- [GALLERY.md](GALLERY.md) — 13 ready-to-adapt scenario templates (basemap, multi-panel, inset, classified scatter, velocity field, histogram, rose, 3D, contours, cross-section, dual-axis).
- `scripts/` — runnable, parameterized templates, all style-switchable via `STYLE` in CONFIG: `displacement_map.py`, `seismicity_map.py`, `cross_section.py`, `multipanel_components.py`, `velocity_field_map.py` (GPS velo + error ellipses + ref vector + scale bar), `wrapped_phase_map.py` (InSAR fringes: cyclic CPT + nearest interpolation + moiré guard). Each runs standalone with demo data; edit the CONFIG block at the top. `style_presets.py` defines the styles; `render_style_previews.py` regenerates `previews/`.
