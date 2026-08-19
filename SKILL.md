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
| [GOTCHAS.md](GOTCHAS.md) | a PyGMT call errors or the rendered figure shows an artifact (symptom-keyed — grep the symptom, read that section only) |
| [REFERENCE.md](REFERENCE.md) | you need an API signature the template doesn't demonstrate, or publication-craft guidance (layer order, colormap choice, hillshade, export — its final chapters) |
| [GALLERY.md](GALLERY.md) | no scripts/ template matches (second-tier routing below) — read the ONE matching snippet |
| [COMMUNITY.md](COMMUNITY.md) | GMT-China community examples, Chinese/CJK labels, China datasets, transparency/escape syntax |

## Required figure format (house style)

All scientific figures MUST follow these format rules:

- **Frame**: `MAP_FRAME_TYPE='plain'`, `MAP_FRAME_PEN='1p,black'`. Never draw frame twice (no basemap + plot both setting frame).
- **Panel labels**: UPPERCASE letter (A, B, C...), **no parentheses**, bold ≥10p, placed **OUTSIDE the frame** above the top-left corner, flush with the frame edge (`panel_label()` default — no box needed on the page background). Only when panels sit flush with no outside room, fall back to `panel_label(..., inside=True)`: in-map top-left, square white box + 0.8p black pen. Title text (e.g., "East") centered at top separately.
- **Tick labels**: Only on left (W) and bottom (S) edges.
- **Colorbar**: Horizontal at bottom, with unit label, enough offset from axis labels (`+o0c/0.8c`).
- **Color scale**: `vik` for diverging displacement, sequential: `inferno` or `roma`.
- **Depth axes read POSITIVE, down** (hard rule for fault/cross-section/3D figures): the depth axis must be labelled `0, 20, 40 …` (positive kilometres), never `0, -20, -40`. Store depth as a **positive** value (depth increases downward), set the region depth range to `[0, zmax]`, and **flip the axis with a negative height**: 2D cross-sections use `projection="X<w>c/-<h>c"` (negative height → y increases downward); 3D perspective plots use `zsize="-<h>c"` (negative → deep at the bottom, labels positive). Never emit negative z data just to get "up = positive" — that puts minus signs on the depth axis. When you flip a 3D z-axis this way, any in-plane up-dip vector's **vertical component also flips sign** (up-dip now means *decreasing* positive depth).
- **No double frames**: subplot handles frame → do NOT call basemap(frame=) inside panels.
- **Self-check**: After generating each figure, read/inspect it. Fix double frames, clipped content, inconsistent labels before showing to user.

## Step 0 — Auto-expand the request into a brief (before routing)

User prompts arrive terse ("画一下玛多的地震分布"). BEFORE routing, expand the request
into the five-slot brief below, filling every missing slot from the defaults column —
then STATE the completed brief back in 3-5 lines before plotting, so the user can
course-correct cheaply. Never skip this; never ask about a slot the defaults can fill.

| Slot | If the prompt doesn't say, fill with |
|---|---|
| 图型 + 模板 | route via the template table below |
| 区域 / 事件参数 | named EARTHQUAKES: coordinates MUST come from `data_fetch.usgs_mainshock(start, end, minmag)` — NEVER from memory (a verification run recalled the 2025 Dingri epicenter 2° wrong); places: geocode then sanity-check against a map render; region = source dimension padded ~0.5-1°, then `qc_check.assert_in_region(lon, lat, REGION, "event")` |
| 数据来源 + 回退 | real data first: user's files > live USGS/EarthScope fetch > bundled data/; synthetic ONLY as a fallback and the brief must SAY it is synthetic |
| 风格 | scene words → style routing below (slides→presentation, 黑底→dark, 投稿→journal, 海报/经典→classic, 网页→minimal); else house |
| QC 验收点 + 输出 | attach the figure type's trap notes from the routing table (cyclic+nearest for fringes, no +n for velo, zsize for 3D, positive-down depth...) + `<name>.png` at 300 dpi (400 for fringe rasters) |

Ask the user ONLY for a slot that is genuinely undecidable (e.g. which of two同名 events);
one question max, then proceed.

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
| Earthquake catalog / seismicity map (± beachballs) | `scripts/seismicity_map.py` — set `CATALOG=dict(minmag=..., start=..., end=...)` for a live USGS fetch (NEVER hand-write fetch code) and `EVENT=(lon, lat)` to assert+star the mainshock |
| Map + profile / depth section | `scripts/cross_section.py` — `SECTION="topo"` for elevation profiles (needs NO catalog; never invent events), `"events"` for hypocenter sections; `CATALOG=dict(...)` = built-in USGS fetch; `EVENT=(lon,lat)` asserts the epicenter inside REGION; aspect guard caps tall regions |
| Multi-panel component grids (E/N/U, data-model-residual) | `scripts/multipanel_components.py` |
| GPS/GNSS vectors + error ellipses | `scripts/velocity_field_map.py` (velo arrows fail **silently** — GOTCHAS §9) |
| Wrapped interferogram / fringes | `scripts/wrapped_phase_map.py` (cyclic CPT + `interpolation="n"` + moiré guard) |
| 3D finite-fault slip distribution (fence diagram) | `scripts/fault_slip_3d.py` (plot3d polygons + -Z headers; depth positive-down) |
| Station-centered teleseismic geometry (distance rings) | `scripts/station_azimuthal_map.py` (azimuthal equidistant + `style="E-"` rings) |
| Earth-interior shells + ray-path diagram | `scripts/earth_interior.py` (polar P projection, Cartesian chords in polar coords) |
| Focal-mechanism (beachball) overview map | `scripts/focal_mechanisms.py` (manual Mw sizing — `+m` is flat, GOTCHAS 8.3) |
| Magnitude-time sequence plot | `scripts/mt_plot.py` (datetime axis, multi-segment -Z bars) |
| Time-colored epicenter map (sequence migration) | `scripts/time_colored_seismicity.py` (decimal-year CPT; `CATALOG`/`EVENT` as above) |
| Teleseismic waveform record section | `scripts/record_section.py` (needs obspy; bundled real LHZ data + TauP curves) |
| ShakeMap-style intensity map | `scripts/shaking_intensity.py` (modeled field — label it as such) |

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
7. **Mandatory QC loop** — run the render→Read→checklist→fix→re-render cycle in the "QC 自检回路" section at the end of this file before delivering ANY figure. "The code was fixed" ≠ "the image is fixed" — re-Read after every fix. Every template additionally ends with a PROGRAMMATIC gate (`scripts/qc_check.py`): a near-empty/hollow/dead render aborts the script instead of shipping. Hand-written scripts must run `python scripts/qc_check.py <fig.png>` themselves before delivery.
8. **Synthetic fallback is BANNED for real referents** — a task that names a real place, event or dataset must be drawn from real data. If the fetch or parse fails, STOP and report the failure; NEVER substitute synthetic values (the worst shipped failures in this skill's history were silent fabrications that self-reported "QC passed"). Synthetic demo fields are allowed only when the user explicitly asked for a demo/synthetic case or no real-world referent exists — and the figure or caption must say so. Before plotting fetched grids, sanity-check them with `qc_check.assert_real_field`.

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
positive-down depth axes). Previews: `previews/styles_all.png` (+ per-style PNGs). Notes:
`dark` changes only page/frame/font/tick/grid colors (never CPT extremes) — use
`coast_colors("dark")`, bright CPTs (turbo/batlow/vik), and no `transparent=True` export;
per-figure tweaks override inline (`style("house", MAP_FRAME_PEN="1.2p,black")`); to ADD a
style, extend the `STYLES` dict in `scripts/style_presets.py` and re-run
`scripts/render_style_previews.py`; CJK labels: see COMMUNITY.md's 中文出图配方.

## Workflow for a new figure

0. Expand the request into the five-slot brief (Step 0 above) and state it back.
1. Decide region, projection, and CPT from the cheat sheet above; pick a style
   (default `house`; slides → `presentation`/`dark`; submission → `journal`).
2. Pick the closest template in [GALLERY.md](GALLERY.md) or `scripts/` and adapt it.
3. Draw inside `with style(...)` (or the house-style `config` block); build bottom layer →
   top layer (relief → coast → data → annotations → colorbar).
4. `fig.savefig(..., dpi=300)` (dpi=400+ and check the pixel-count rule for fringe/speckle rasters), then run the QC loop (step 7 above / final section of this file) until every checklist item passes — only then deliver. Token discipline: Read a downsized copy once per round, batch ALL fixes into one re-render, cap at 3 renders.

## References

- [REFERENCE.md](REFERENCE.md) — complete API: figure lifecycle, coast/plot/text, grdimage/grdcontour/grdview, makecpt/colorbar, datasets, grid processing (grdcut/grdgradient/grdtrack/surface…), xarray, meca, velo, project, subplot/inset/shift_origin/legend.
- [GOTCHAS.md](GOTCHAS.md) — community-sourced pitfalls the API docs don't mention: region/dateline/projection traps, session-CPT overwrite & "no z-slices" error, xarray gtype/registration reset after arithmetic, grdimage-all-black, earth_relief cache, font-config scope, multi-panel colorbars, 0.x parameter renames, Ghostscript/conda install fixes. **§8 field-tested traps:** inset basemap drops annotations/labels (draw manually or use `shift_origin`); inset forces a default frame so `box="+p"` makes a double frame; `meca +m` Mw-scaling is invisible (size beachballs manually); `meca(cmap=True)` on negative depths segfaults; hand-written rasterio tif → `grdimage` segfault (use xarray instead); `shading` dimension mismatch (grdsample first); inset colorbar label overflow (`+mal`); `fig.plot(fill="white")` adds a stray black border. **§9 vector arrowheads (`style="v"`):** `+g`/`+h` are NOT broken — a head only appears if you also pass `+e`/`+b`, a vector shorter than the head length silently loses its head (fix with `+n<len>`), and `+h` near 1 degenerates the head so the fill vanishes. **Read this when a PyGMT figure misbehaves or errors unexpectedly.**
- [GALLERY.md](GALLERY.md) — 13 ready-to-adapt scenario templates (basemap, multi-panel, inset, classified scatter, velocity field, histogram, rose, 3D, contours, cross-section, dual-axis).
- `scripts/` — runnable, parameterized templates, all style-switchable via `STYLE` in CONFIG: `displacement_map.py`, `seismicity_map.py`, `cross_section.py`, `multipanel_components.py`, `velocity_field_map.py` (GPS velo + error ellipses + ref vector + scale bar), `wrapped_phase_map.py` (InSAR fringes: cyclic CPT + nearest interpolation + moiré guard). Each runs standalone with demo data; edit the CONFIG block at the top. `style_presets.py` defines the styles; `render_style_previews.py` regenerates `previews/`.

## QC 自检回路 (mandatory, read once per session)

**任何图交付前必须走完这个回路，不是可选项**：

```
savefig → Read 成图 → 逐项过下面清单 → 有任何一项不过 → 修复 → 重新渲染 → 再读再核
→ 全部通过 → 对照用户原话核需求覆盖 → 交付
```

最多 3 轮；若同类缺陷第二次出现，说明微调无效——改布局参数量级或换方案（如 gap 一次加够
1.5c，不要 ±0.1c 蹭）。**修复后必须重新 Read 成图确认，"改了代码"不等于"改好了图"。**

## Token 经济策略（QC 要省着做）

1. **每轮只 Read 一次，读缩略图**：`sips -Z 800 fig.png --out fig_qc.png` 后 Read 缩略版
   （全尺寸 PNG 的图像 token 是缩略版的数倍；清单里的缺陷 800px 下全部可见）。只有某个
   细节存疑时才裁局部放大看，不整图重读。
2. **批量修复**：一次 Read 把清单过完、收集**全部**缺陷，一次改完再渲染——严禁一个缺陷
   一轮的挤牙膏循环。目标：多数图 2 次渲染收工（初渲 + 修复渲）。
3. **QC 只重渲染，不重跑数据**：earth_relief 下载、gridding、投影采样等重活放在渲染函数
   外（模板已如此组织）；改布局参数不碰数据段。
4. **模板起步本身就是最大的省法**：实测模板路径 ~5 次工具调用出合格图，手写路径 20+ 次
   还常翻车。QC 是最后一道网，不是给手写代码兜底的许可证。
5. 交付叙述从简：报告改了什么、锚点核了什么即可，不复述清单全文。

## 微缺陷清单（每条都来自实测翻车）

### 1. 压盖 / 重叠 (overlap)
- [ ] colorbar 不压坐标轴标签：笛卡尔面板带 x 轴标题时 `colorbar(offset>=1.4)`（默认 0.8c 必压）
- [ ] colorbar 及其注记不侵入下方/相邻面板（shift_origin 间隙要装得下 bar+注记+标签 ≈ +3.4c）
- [ ] 相邻 subplot 面板的经度刻度不相连（撞了就 `xa30mf` 加粗刻度间隔或加宽 margins）
- [ ] 文字标注互不压盖（如两个板块名重叠）；图例框不盖数据
- [ ] 比例尺/指北针不压海岸线密集区或数据

### 2. 裁切 / 越界 (clipping)
- [ ] 无任何文字/符号被图框切半（帧边标注加 `no_clip=True` 或内移）
- [ ] 面板四边完整（上一面板的底边没被下一面板顶掉）
- [ ] 数据充满 region（地图悬浮在空白大框里 = region 与绘图调用不一致）

### 3. 缺件 (missing elements)
- [ ] **每支矢量都有箭头头**，包括最短的（秃头=尺寸/`+n` 问题，见 GOTCHAS 9）
- [ ] 纬度、经度注记都在（W 与 S 两边各自要有）
- [ ] colorbar 有单位标签；panel label 在图框外左上方可见（inside=True 时才要求方框）
- [ ] 用户点名的元素一件不少（见下"需求覆盖"）

### 4. 冗印 (spurious ink)
- [ ] 轴标签没把引号印出来（`+l"..."` 的引号会原样上图，GOTCHAS 5.4）
- [ ] 无双框（subplot/inset 已画框就别再 basemap(frame=)）
- [ ] 无意外黑块/白块（close 路径错误、fill 默认描边、inset 默认框）
- [ ] 连续场无意外分级色带（想平滑就别给 series inc，或 `continuous=True`）

### 5. 布局 (layout)
- [ ] 定位 inset 叠在主图角内（`fig.inset`），不是脱离主图漂在外面
- [ ] 多面板等宽对齐（`projection="M?"/"X?"`）；共享 colorbar 居中于全体面板
- [ ] 深度/高程轴方向正确：深度正值向下读（负高度投影），剖面横轴是 km 不是度

### 6. 数据锚点 (data anchors) —— 图漂亮但锚点不过 = 错图
- [ ] 条纹数 ≈ 峰值位移 ÷ (λ/2)（25 cm C 波段 ≈ 9 圈，画出 1 圈 = 合成/缠绕环节错了）
- [ ] 台站箭头长度与参考箭头量级相称（差 10 倍 = 单位打滑 mm↔cm）
- [ ] 矢量指向与陈述方位一致（罗盘方位角 az：ve=V·sin az, vn=V·cos az；玫瑰图 E/W 没镜像）
- [ ] 剖面峰值 ≈ 目标已知海拔/深度（差 1500 m+ = 剖面线没穿过目标）
- [ ] 真实地名的地形是真 DEM（earth_relief 本地缓存），不是合成场

## 需求覆盖核对 (requirement echo)

交付前把**用户原话**里的显式要求逐条列出打勾——实测最常被丢的：点名的风格（classic/dark）、
inset、比例尺、参考箭头、"每个面板独立 colorbar"、指定输出路径拼写。列表里任何一项在成图上
找不到就没画完，回去补。
