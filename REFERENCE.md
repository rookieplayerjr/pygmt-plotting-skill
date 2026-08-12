# PyGMT API Reference

Complete reference distilled from the official PyGMT docs (pygmt.org/latest). Every method
parameter accepts a Python full name (used here) and a GMT single-letter alias (shown in
tables). Grid-processing functions return `xarray.DataArray` when `outgrid=None`.

---

## 1. Figure lifecycle

```python
import pygmt
fig = pygmt.Figure()              # canvas; all plotting methods hang off fig
fig.basemap(...); fig.coast(...)  # build layers bottom → top
fig.show()                        # preview (external viewer / notebook inline)
fig.savefig("map.png", dpi=300)   # export; extension decides format
```

**`fig.savefig(fname, transparent=False, crop=True, anti_alias=True, show=False, worldfile=False, **kwargs)`**
- Extension → format: raster `PNG/JPG/BMP/TIFF/PPM`, vector `PDF/EPS`, `KML` (+companion PNG).
- `dpi=` (raster resolution), `transparent=True` (PNG/KML), `crop=True` (trim to artwork), `worldfile=True` (georeferenced raster).
- `fig.show(method=..., dpi=300, width=500)`: `method="external"` (PDF viewer) / `"notebook"` (inline PNG). Global default via `pygmt.set_display()`.

---

## 2. region / projection / frame

### region (R) — `[W, E, S, N]`
```python
region=[10, 20, 35, 45]   # list (preferred), = West,East,South,North
region="10/20/35/45"      # string
region="g"                # global 0–360 / 90S–90N (center 180)
region="d"                # global 180W–180E (center 0)
region="JP"               # ISO 3166-1 alpha-2 country code
region="10/35/20/45+r"    # +r → the two values are lower-left / upper-right corners (oblique)
region="JP+r3"            # +r on a country code → pad by 3°
```

### projection (J) — `code[params/]width` (width **must** carry unit c/i/p)
| Code | Projection | Syntax |
|---|---|---|
| `X` | Linear/Cartesian (non-geo) | `Xw[/h]`; suffix `l`=log, `p`=power, `T`=time |
| `M` | Mercator | `M[lon0/[lat0/]]w` |
| `Q` | Cylindrical equidistant (Plate Carrée) | `Q[lon0/[lat0/]]w` |
| `L` | Lambert conformal conic | `Llon0/lat0/lat1/lat2/w` |
| `B` | Albers equal-area conic | `Blon0/lat0/lat1/lat2/w` |
| `D` | Equidistant conic | `Dlon0/lat0/lat1/lat2/w` |
| `G` | Orthographic / perspective | `Glon0/lat0[/horizon]/w` |
| `E` | Azimuthal equidistant | `Elon0/lat0[/horizon]/w` |
| `A` | Lambert azimuthal equal-area | `Alon0/lat0[/horizon]/w` |
| `S` | Stereographic (polar: lat0=±90) | `Slon0/lat0[/horizon]/w` |
| `T` | Transverse Mercator | `Tlon0[/lat0]/w` |
| `U` | UTM | `Uzone/w` |
| `W` | Mollweide | `W[lon0/]w` |
| `N` | Robinson | `N[lon0/]w` |
| `H` | Hammer | `H[lon0/]w` |
| `R` | Winkel Tripel | `R[lon0/]w` |
| `Kf`/`Ks` | Eckert IV / VI | `Kf[lon0/]w` |
| `I` | Sinusoidal | `I[lon0/]w` |
| `Y` | Cylindrical equal-area | `Ylon0/lat0/w` |
| `P` | Polar (r-θ, non-geo) | `Pw[+a][+fflip][+roffset][+torigin]` |

### frame (B) — `bool` / `str` / `list`
- Edge letters: `WSNE` (axis+ticks+annotations), `wsne` (no annotations), `lbtr` (axis only).
- Interval letters after axis name: `a`=annotation/major, `f`=minor tick, `g`=grid → `xa30f7.5g15`.
- Modifiers: `+lLabel` (axis label — **Cartesian only**), `+tTitle`, `+uUnit`.
- **GMT 6.6 strictness**: frame *settings* (edge letters, `+t`, `+g`) may appear in only ONE list entry. `["WSne", "af", "+tTitle"]` hard-fails (`Option -B parsing failure … Offending option -BWSne`) because `WSne` and `+tTitle` are two frame-settings invocations → write `["WSne+tTitle", "af"]`. A lone `["af", "+tTitle"]` (no edge letters) is still legal.
```python
frame=True                                       # = "af" auto
frame=["WSne", "xaf", "yaf"]                     # annotate left+bottom only (house style)
frame=["WSne+tTitle", "xa30f7.5g15", "yaf"]      # title MUST ride the edge-letters entry
```

---

## 3. fig.basemap & fig.coast

**`fig.basemap`** draws the frame/axes/title and optional embellishments:
- `map_scale` (L): `"jBL+w100k+o0.5c"` (anchor BL, 100 km bar, offset).
- `rose` (Td) / `compass` (Tm); `box` (F) frames a scale/rose with fill/pen.

**`fig.coast`** — coastlines, land/water fill, political boundaries:
| Param (alias) | Use | Example |
|---|---|---|
| `shorelines` (W) | coastline pen | `"0.5p,black"` |
| `land` (G) / `water` (S) | fills | `"gray90"` / `"lightblue"` |
| `resolution` (D) | `f/h/i/l/c` (full→crude) | `"i"` |
| `borders` (N) | `1`=national, `2`=state, `3`=marine | `"1/1p,black"` |
| `rivers` (I) | | `"1/0.5p,blue"` |
| `dcw` (E) | fill by country code | `"JP+gred"` |
| `area_thresh` (A) | min feature area km² | `1000` |

---

## 4. fig.plot / fig.plot3d / fig.text

**`fig.plot`** — points, lines, symbols. Input via `x=/y=` (+`size=`/`symbol=` arrays) or `data=` (file/ndarray/DataFrame/xarray/GeoDataFrame).

| Param (alias) | Use |
|---|---|
| `style` (S) | symbol code + size: `c`circle `s`square `t`triangle `i`inv-tri `d`diamond `h`hexagon `a`star `+`plus → `"c0.2c"`. `"cc"` = circle, size column in cm |
| `pen` (W) | `"1p,black"` line/outline |
| `fill` (G) | color, or value array with `cmap=True` |
| `cmap` (C) | CPT name or `True` (use session CPT) |
| `error_bar` (E) | `"y+w3p"` |
| `close` (L) | close polygon: `"+y-8000"` (close down to y) |
| `label` (l) | legend entry; `transparency` (t) 0–100; `no_clip` |

```python
fig.plot(x=lon, y=lat, style="c0.2c", fill="red", pen="0.5p,black")     # scatter
pygmt.makecpt(cmap="viridis", series=[0, 100])
fig.plot(x=x, y=y, style="c0.3c", fill=vals, cmap=True)                 # value-colored
fig.plot(x=x, y=y, pen="1.5p,blue,--")                                  # line
fig.plot(x=x, y=y, style="cc", size=0.02*2**mag, fill=dep, cmap=True)   # size∝mag, color∝depth
```

**`fig.plot3d`**: `region` needs 6 values `[xmin,xmax,ymin,ymax,zmin,zmax]`, plus `zscale=`/`zsize=` and `perspective=[azimuth, elevation]`.

**`fig.text`** — labels:
| Param | Use |
|---|---|
| `x`/`y` or `position` | coords, or corner code `TL TC TR ML MC MR BL BC BR` |
| `font` | `"12p,Helvetica-Bold,black"` |
| `justify` | which point of the text anchors (nine-cell code) |
| `angle` | CCW rotation; `offset` `"j0.2c"` (j = away from anchor) |
| `fill`/`pen`/`clearance` | text box bg / border / padding |
```python
fig.text(position="TL", text="A", font="12p,Helvetica-Bold,black",
         justify="TL", offset="j0.2c", fill="white", pen="0.8p,black", clearance="1.5p/1.5p")
```

---

## 5. Pen / fill / CPT syntax

- **Pen** `width,color,style`: `"1p,black,--"`; styles `-`/`dashed`, `.`/`dotted`, `.-` dash-dot, or custom `"4p,2p"`. Width also named `thin`/`thick`/`fat`.
- **Fill/color**: name (`darkgreen`), `R/G/B` (`255/128/0`), gray `0–255`, hex `#RRGGBB`, or `@NN` transparency suffix (`white@30`).

**`pygmt.makecpt(cmap, series, reverse, continuous, truncate, background, categorical, cyclic, color_model, output)`**
| Param (alias) | Use |
|---|---|
| `cmap` (C) | master CPT name |
| `series` (T) | `[min, max, inc]` or value list |
| `reverse` (I) | `True`/`"c"` flip colors, `"z"` flip z |
| `continuous` (Z) | smooth interpolation |
| `truncate` (G) | `(zlow, zhigh)` clip endpoints |
| `background` (D) | bg/fg colors at extremes |
| `categorical` | discrete classes; `color_model="+cA,B,C"` names them |
| `cyclic` | wrapped colormap |
| `output` (H) | save `.cpt`; **omit → becomes session CPT** (auto-used by later grdimage/plot/colorbar) |

**`pygmt.grd2cpt(grid, cmap, nlevels, ...)`** — histogram-equalized CPT from a grid's data distribution.

### CPT names by type
- **Diverging** (zero-centered: displacement/velocity/anomaly): `vik roma broc cork lisbon berlin bam polar`
- **Sequential** (scalar): `inferno magma plasma viridis turbo batlow hawaii oslo lajolla hot haxby`
- **Topography**: `geo` (land), `oleron`/`relief`/`etopo1` (land+ocean), `srtm/terra`, `gray` (hillshade)
- **Cyclic** (suffix `O`): `romaO vikO bamO` — wrapped phase, azimuth
- Scientific Colour Maps (Crameri) are perceptually uniform & print-safe → prefer them.

---

## 6. Grids: grdimage / grdcontour / grdview / colorbar

**`fig.grdimage(grid, cmap, shading, nan_transparent, dpi=100, monochrome)`**
```python
grid = pygmt.datasets.load_earth_relief("30m")
shade = pygmt.grdgradient(grid=grid, azimuth=315, normalize=True)   # hillshade intensity
fig.grdimage(grid=grid, shading=shade, cmap="geo", projection="M12c")
```
- `shading`: intensity grid (−1…+1), `True` (auto), or `"+a45"` azimuth.
- `nan_transparent=True` masks NaNs (or pass a color).

**`fig.grdcontour(grid, levels, annotation, limit, pen)`**
```python
fig.grdcontour(grid=grid, levels=250, annotation=1000, limit=[0, 5000], pen="0.5p,black")
```
`levels`=interval/list/CPT; `annotation`=annotated-contour interval; `limit=[low,high]` clips.

**`fig.grdview(grid, perspective, surftype, zscale/zsize, cmap, drape_grid, shading, plane)`**
```python
fig.grdview(grid=grid, perspective=[130, 30], zsize="2c", surftype="s",
            cmap="geo", frame=["xa", "ya", "wSnE"])
```
`surftype`: `s`=surface, `m`=mesh, `i`=image, `c`=transparent image. `drape_grid` colors one grid by another. `region` may take 6 values incl. zmin/zmax.

**`fig.colorbar(cmap, position, frame, box, ...)`** — `position` uses GMT `-D` modifiers:
| Modifier | Meaning |
|---|---|
| `J<anchor>` / `j<anchor>` | anchor to map edge, e.g. `JBC` bottom-center, `JMR` mid-right |
| `+w<len>/<width>` | bar length/width `+w8c/0.4c` |
| `+h` / `+v` | horizontal / vertical (default v) |
| `+o<dx>/<dy>` | offset from anchor |
| `+e` / `+eb` / `+ef` | triangle ends (out-of-range) both/back/front |
| `+m` | move annotations/label to other side |
```python
fig.colorbar(position="JBC+w8c/0.4c+h+o0c/0.8c",
             frame=["x+lVelocity", "y+lmm/yr"], box="+gwhite@30+p0.8p,black")
```

---

## 7. Datasets & grid processing

**Datasets** (`from pygmt.datasets import ...`):
- `load_earth_relief(resolution="01d", region=None, registration=None, data_source="igpp", use_srtm=False)` — resolutions `01d 30m 20m 15m 10m 06m 05m 04m 03m 02m 01m 30s 15s 03s 01s`; **resolutions finer than 05m require `region`**.
- `load_earth_age`, `load_earth_geoid`, `load_earth_magnetic_anomaly` (same signature shape).
- `load_sample_data("name")` — e.g. `"ocean_ridge_points"`, `"fractures"`, `"japan_quakes"`.
- **Plate boundaries (Bird 2003 PB2002)**: NOT on the GMT remote server (`@PB2002_boundaries.txt` 404s — verified). Download the PB2002 boundary file once (Bird 2003 supplementary data; the GMT-format `pb2002_boundaries.gmt` ships with several open finite-fault packages) and plot it directly: `fig.plot(data="pb2002_boundaries.gmt", pen="0.8p,firebrick")` — multi-segment GMT file. Never sketch synthetic "boundaries" on real maps.

**Grid → grid** (return DataArray when `outgrid=None`):
| Function | Purpose |
|---|---|
| `grdcut(grid, region)` | crop subregion |
| `grdgradient(grid, azimuth=315, normalize=True)` | directional gradient / hillshade intensity |
| `grdsample(grid, spacing, registration)` | resample to new grid spacing |
| `grdfilter(grid, filter="g50", distance)` | spatial filter/smooth (`g`=Gaussian width) |
| `grdproject(grid, projection)` | forward/inverse projection of a grid |

**Grid → table**: `grdtrack(grid, points=df, newcolname="z")` samples grids at points (profile/track); `profile="lonA/latA/lonB/latB+i_inc_"` auto-generates the line.

**Table → grid** (gridding): `xyz2grd` (already-regular), `surface(data, region, spacing, tension)` (adjustable-tension spline), `nearneighbor`, `blockmean`/`blockmedian` (decimate before gridding):
```python
binned = pygmt.blockmedian(data=df, region=region, spacing="1m")
grid   = pygmt.surface(data=binned, region=region, spacing="1m", tension=0.35)
```

**xarray integration**: any `xarray.DataArray`/NetCDF can be passed to grdimage/grdcontour/grdview. The `.gmt` accessor carries metadata — set after reading external NetCDF if projection looks wrong:
```python
grid = xr.open_dataarray("los.nc")
grid.gmt.gtype = 1          # 0=Cartesian, 1=geographic
grid.gmt.registration = 0   # 0=gridline, 1=pixel
```

---

## 8. Seismology / geodesy: meca & velo

**`fig.meca(spec, scale, convention, component, longitude, latitude, depth, plot_longitude, plot_latitude, offset, compressionfill="black", extensionfill="white", pen, cmap, nodal, outline)`** — focal mechanisms (beachballs).

> ⚠️ **v0.17 param naming is mixed**: fill params have NO underscore — `compressionfill`, `extensionfill` (meca), `uncertaintyfill` (velo); the old underscore forms (`compression_fill`…) now **hard-fail** with `Unrecognized parameter`. Position/name params KEEP underscores: `plot_longitude`, `plot_latitude`, `event_name`.

Convention → spec fields (dict keys / DataFrame columns; convention auto-inferred from dict/DataFrame keys):
| convention | fields |
|---|---|
| `aki` | `strike, dip, rake, magnitude` |
| `gcmt` | `strike1,dip1,rake1, strike2,dip2,rake2, mantissa, exponent` |
| `mt` | `mrr,mtt,mff,mrt,mrf,mtf, exponent` |
| `partial` | `strike1,dip1, strike2, fault_type, magnitude` |
| `principal_axis` | T/N/P each (value,azimuth,plunge) + `exponent` |

`scale="1c"` = radius at M=5. Modifiers: `+l` radius ∝ moment, `+m` all same size, `+s6` reference magnitude 6, `+f8p+jTC` label `event_name`.
```python
focal = {"strike": 330, "dip": 30, "rake": 90, "magnitude": 3}
fig.meca(spec=focal, scale="1c", longitude=-124.3, latitude=48.1, depth=12,
         compressionfill="red", extensionfill="cornsilk", pen="0.5p,gray30")

# Many events colored by depth. With a DataFrame spec, longitude/latitude/depth must be
# COLUMNS in df — do NOT also pass them as kwargs (raises "All arrays must have same size").
pygmt.makecpt(cmap="viridis", series=[0, 50])
fig.meca(spec=df, scale="0.4c", cmap=True)   # df has lon/lat/depth/strike/dip/rake/magnitude
# To declutter, plot at offset positions: add plot_longitude/plot_latitude columns to df
# and pass offset="+s0.15c+p0.5p,blue" (tie-line + small circle at the true location).
```

**`fig.velo(data, spec, pen, fill, uncertaintyfill, line, vector, zvalue, cmap)`** — GPS/velocity fields. `spec` prefix sets symbol AND column order:
| prefix | symbol | columns |
|---|---|---|
| `e[scale/]conf[+ffont]` | velocity ellipse (E,N) | `lon lat v_e v_n sig_e sig_n corr_EN [site]` |
| `r...` | ellipse (rotated) | `lon lat v_e v_n major minor azimuth [site]` |
| `n[scale]` | anisotropy bars | `lon lat e n` |
| `w...` | rotational wedge | `lon lat rot σ` |
| `x[scale]` | strain crosses | `lon lat eps1 eps2 azimuth` |
```python
fig.velo(data=df, spec="e0.2/0.39+f18", uncertaintyfill="lightblue1",
         pen="0.6p,red", line=True, vector="0.3c+p1p+e+gred")
```
`e0.2/0.39`: 0.2 = velocity→length scale, 0.39 ≈ 1σ ellipse (0.95 = 95%). Color by magnitude: `cmap="turbo", zvalue="m"`.

---

## 9. Cross-sections: project + grdtrack

**`pygmt.project(data, x, y, z, center, endpoint, azimuth, length, width, generate, convention, unit, output_type="pandas")`** — generate a profile line or project points onto it.
- Define the line by `center+endpoint`, `center+azimuth`, or `center+pole`.
- Output columns via `convention` (subset of `xyzpqrs`): **`p`** = distance along profile, **`q`** = perpendicular distance, `r,s` = nearest point on profile, `x,y` = input coords, `z` = passthrough.
- `unit=True` → p,q in km. `generate="1k"` → equally spaced points every 1 km. `width=[-20,20]` keeps only |q|<20 km.

```python
# Topographic profile: generate points → sample grid → plot distance vs elevation
track = pygmt.project(center=[lonA,latA], endpoint=[lonB,latB], generate="1k", unit=True)
track = pygmt.grdtrack(grid=grid, points=track, newcolname="elevation")
fig.plot(x=track.p, y=track.elevation, pen="1p,red")

# Earthquakes projected onto a depth section (y down via negative height):
proj = pygmt.project(data=eqs, center=[lonA,latA], endpoint=[lonB,latB],
                     convention="pz", unit=True, width=[-20, 20])
fig.plot(x=proj.p, y=proj.z, fill=proj.z, cmap=True, style="cc", size=0.02*2**eqs.mag,
         projection="X12c/-4c", region=[0, 200, 0, 30])
```

---

## 10. Layout: subplot / shift_origin / inset / legend

**`fig.subplot` + `fig.set_panel`** — regular grid, auto-labels:
```python
with fig.subplot(nrows=2, ncols=2, figsize=("15c","12c"), autolabel=True,
                 margins=["0.3c","0.2c"], title="Figure", sharex="b", sharey="l", frame="af"):
    fig.basemap(region=[...], projection="M?", panel=True)   # panel=True advances
    fig.basemap(region=[...], projection="M?", panel=[1,0])  # or [row,col] / index
```
`panel=True` advances sequentially; `panel=[row,col]` (0-based) or `panel=idx` targets. Use `"M?"`/`"X?"` to auto-size per cell. **Frame is managed by subplot — don't re-pass `frame=` inside panels.**

**`fig.shift_origin(xshift, yshift)`** — manual paneling. Reference previous figure size with `"w"`/`"h"`: `yshift="h+1.5c"`, `xshift="w+1c"`. Permanent (standalone call) or temporary (`with`).

**`fig.inset(position, width, height, box)`** — locator map as context manager:
```python
with fig.inset(position="jTR+w3.5c+o0.2c", box="+gwhite+p1p,black"):
    fig.coast(region="g", projection="G-120/40/?", land="gray", water="white")
    fig.plot(x=[W,E,E,W,W], y=[S,S,N,N,S], pen="1p,red")     # study-area box
```

**`fig.legend(spec, position, box)`** — `box="+gwhite+p1p,black"`, default top-right.
- Auto: pass `label=` on plot calls, then `fig.legend()`.
- Manual spec (StringIO/file), symbol codes: `H` header, `S dx symbol size fill pen text_dx label`, `D` divider, `L` text, `N` columns, `G`/`V` spacing.
```python
fig.plot(..., label="Earthquakes"); fig.plot(..., pen="1.5p,black", label="Fault")
fig.legend(position="jTR+o0.2c", box="+gwhite+p1p,black")
```

---

## 11. pygmt.config — GMT defaults

Context manager (temporary, restores on exit) or direct call (session-wide):
```python
with pygmt.config(MAP_FRAME_TYPE="plain", MAP_FRAME_PEN="1p,black"):
    fig.basemap(...)   # house style; avoids drawing the frame twice
```
Common keys: `MAP_FRAME_TYPE` (plain/fancy), `MAP_FRAME_PEN`, `FONT_TITLE`, `FONT_ANNOT_PRIMARY`, `FONT_LABEL`, `FORMAT_GEO_MAP` (`ddd.xx`), `COLOR_NAN`, `MAP_GRID_PEN`, `MAP_TICK_PEN/LENGTH`.

---

## 12. Common pitfalls

1. `region` order is `[W, E, S, N]` — not `[W,S,E,N]`.
2. `projection` width must carry a unit (`M12c`), else error.
3. Axis labels `+l` work **only on Cartesian (X)** projections — geographic maps reject them.
4. `plot3d` needs a 6-value `region` plus `zscale`/`perspective`.
5. meca/velo fill params have **no underscore** in v0.17 (`compressionfill`, `uncertaintyfill`; underscore forms hard-fail), and `velo` `spec` prefix dictates column order — wrong order silently mis-plots.
6. `project` outputs distance as `p`, perpendicular as `q`; need `unit=True` for km.
7. Shared multi-panel colorbar: call `fig.colorbar` **outside** the `subplot` block, anchored with `j<corner>+o`.
8. `makecpt`/`grd2cpt` with no `output=` set the session CPT — later commands don't need `cmap=` again.
9. Newer gallery examples import `from pygmt.params import Box, Pattern` (v0.17 ships exactly these two classes — no `Position`). String modifiers remain fully supported and portable: `position="jTL+o0.2c"`, `box="+p1p,black"`.
