# PyGMT Gallery — Scenario Templates

13 ready-to-adapt templates distilled from the official PyGMT gallery. Each is minimal and
runnable. Swap `cmap` for house-style palettes (diverging → `vik`, sequential → `inferno`/`roma`)
and wrap drawing in `with pygmt.config(MAP_FRAME_TYPE="plain", MAP_FRAME_PEN="1p,black"):`.

---

## 1. Global / regional basemap (coast)
Quick land/water basemap — the starting point for any geographic figure.
```python
import pygmt
fig = pygmt.Figure()
fig.basemap(region="g", projection="W15c", frame=True)
fig.coast(land="#666666", water="skyblue")
fig.show()
```

## 2. Relief basemap + sampled points (load_earth_relief + grdtrack)
DEM/bathymetry background with observation points colored by an attribute — the standard
"DEM base + observations" pattern.
```python
import pygmt
grid = pygmt.datasets.load_earth_relief()
points = pygmt.datasets.load_sample_data(name="ocean_ridge_points")
track = pygmt.grdtrack(points=points, grid=grid, newcolname="bathymetry")
fig = pygmt.Figure()
fig.basemap(region="g", projection="Cyl_stere/150/-20/15c", frame=True)
fig.grdimage(grid=grid, cmap="gray")
fig.coast(land="#666666")
fig.plot(x=track.longitude, y=track.latitude, style="c0.15c", cmap="terra",
         fill=(track.bathymetry - track.bathymetry.mean()) / track.bathymetry.std())
fig.show()
```

## 3. Multi-panel grid (subplot + autolabel)
Regular grid of panels (e.g. East/North/Up components) with automatic A/B/C labels.
```python
import pygmt
fig = pygmt.Figure()
with fig.subplot(nrows=2, ncols=3, figsize=("15c", "6c"), frame="lrtb", autolabel=True):
    for i in range(2):
        for j in range(3):
            with fig.set_panel(panel=[i, j]):
                fig.text(position="MC", text=f"row {i}, col {j}", region=[0, 1, 0, 1])
fig.show()
# subplot manages the frame — do NOT re-pass frame= inside panels (avoids double frames).
```

## 4. Locator inset (fig.inset)
Embed a small "where on Earth" map highlighting the study area.
```python
import pygmt
fig = pygmt.Figure()
fig.coast(region="MG+r2", land="brown", water="lightblue", shorelines="thin", frame="a")
with fig.inset(position="jTL+w3.5c+o0.2c", box="+p1.5p,gold"):
    fig.coast(region="g", projection="G47/-20/?", land="gray", water="white", dcw="MG+gred")
fig.show()
```

## 5. Grouped scatter + legend
Multiple populations as scatter with variable size, semi-transparent overlap, auto legend.
```python
import numpy as np, pygmt
rng = np.random.default_rng(seed=42); n = 200
fig = pygmt.Figure()
fig.basemap(region=[-1, 1, -1, 1], projection="X10c/10c", frame=["xa0.5fg", "ya0.5fg", "WSrt"])
for fill in ["gray73", "darkorange", "slateblue"]:
    x = rng.normal(0, 0.5, n); y = rng.normal(0, 0.5, n); size = rng.normal(0, 0.5, n) * 0.5
    fig.plot(x=x, y=y, style="c", size=size, fill=fill, label=f"{fill}+S0.25c", transparency=50)
fig.legend(transparency=30)
fig.show()
```

## 6. Classified scatter (categorical CPT)
Color by a category column, size by a third variable, categorical colorbar.
```python
import pandas as pd, pygmt
df = pd.read_csv("https://github.com/mwaskom/seaborn-data/raw/master/penguins.csv")
df.species = df.species.astype("category")
cats = list(df.species.cat.categories)
region = pygmt.info(data=df[["bill_length_mm", "bill_depth_mm"]], per_column=True, spacing=(3, 2))
fig = pygmt.Figure()
fig.basemap(region=region, projection="X10c/10c",
            frame=["xafg+lBill length (mm)", "yafg+lBill depth (mm)", "WSen"])
pygmt.makecpt(cmap="inferno", series=(df.species.cat.codes.min(), df.species.cat.codes.max(), 1),
              color_model="+c" + ",".join(cats))
fig.plot(x=df.bill_length_mm, y=df.bill_depth_mm, size=df.body_mass_g * 7.5e-5,
         fill=df.species.cat.codes.astype(int), cmap=True, no_clip=True, style="cc", transparency=40)
fig.colorbar()
fig.show()
```

## 7. Velocity field + confidence ellipses (fig.velo)
GPS / deformation vectors with error ellipses — interseismic velocity standard.
```python
import pandas as pd, pygmt
df = pd.DataFrame({
    "x": [0, -8, 0, -5, 5, 0], "y": [-8, 5, 0, -5, 0, -5],
    "east_velocity": [0, 3, 4, 6, -6, 6], "north_velocity": [0, 3, 6, 4, 4, -4],
    "east_sigma": [4, 0, 4, 6, 6, 6], "north_sigma": [6, 0, 6, 4, 4, 4],
    "correlation_EN": [0.5, 0.5, 0.5, 0.5, -0.5, -0.5],
    "SITE": ["0x0", "3x3", "4x6", "6x4", "-6x4", "6x-4"]})
fig = pygmt.Figure()
fig.velo(data=df, region=[-10, 8, -10, 6], projection="x0.8c", frame=["WSne", "2g2f"],
         spec="e0.2/0.39+f18", uncertaintyfill="lightblue1", pen="0.6p,red",
         line=True, vector="0.3c+p1p+e+gred")
fig.show()
```

## 8. Histogram (fig.histogram)
Single-variable distribution (residuals, elevations) with fixed bin width.
```python
import numpy as np, pygmt
data = np.random.default_rng(seed=100).normal(100, 25, 521)
fig = pygmt.Figure()
fig.histogram(data=data, frame=["WSne", "x+lElevation (m)", "y+lCounts"],
              series=5, fill="red3", pen="1p", histtype=0)  # histtype=0 = counts
fig.show()
```

## 9. Rose diagram (fig.rose)
Directional data statistics (fault strikes, joint azimuths, wave directions).
**Use fig.rose, not matplotlib polar**: rose is azimuth-native (0° = North, clockwise);
matplotlib polar defaults to counterclockwise-from-East, and hand-relabeled compasses
routinely come out MIRRORED (E/W swapped) — a silently wrong structural figure.
```python
import pygmt
data = pygmt.datasets.load_sample_data(name="fractures")  # length + azimuth
fig = pygmt.Figure()
fig.rose(length=data.length, azimuth=data.azimuth, region=[0, 1, 0, 360], diameter="7.5c",
         sector="10+r", norm=True, fill="red3", frame=["x0.2g0.2", "y30g30", "+glightgray"], pen="1p")
fig.show()
```

## 10. 3D perspective surface (fig.grdview)
Three-dimensional rendering of a grid (topography, potential field, inversion result).
**Real DEMs**: use `zsize="3c"` NOT `zscale` (zscale × thousands of meters = runaway canvas,
GOTCHAS 8.6), and `load_earth_relief("15s"/"03s", region=...)` so the volcano keeps its ridges.
```python
import numpy as np, pygmt, xarray as xr
def ackley(x, y):
    return (-20*np.exp(-0.2*np.sqrt(0.5*(x**2+y**2)))
            - np.exp(0.5*(np.cos(2*np.pi*x)+np.cos(2*np.pi*y))) + np.exp(1) + 20)
INC = 0.05; x = np.arange(-5, 5+INC, INC); y = np.arange(-5, 5+INC, INC)
data = xr.DataArray(ackley(*np.meshgrid(x, y)), coords=(x, y))
fig = pygmt.Figure()
fig.grdview(data, frame=["a5f1g5", "za5f1g5"], projection="x0.5c", zscale="0.5c",
            surftype="s", cmap="roma", perspective=[135, 30], shading="+a45")
fig.colorbar(frame="a2f1")
fig.show()
```

## 11. Contours from scattered z (fig.contour)
Interpolate (x,y,z) triples into a contour map; can overlay on a basemap.
```python
import numpy as np, pygmt
X, Y = np.meshgrid(np.linspace(-10, 10, 50), np.linspace(-10, 10, 50)); Z = X**2 + Y**2
fig = pygmt.Figure()
fig.contour(region=[-10, 10, -10, 10], projection="X10c/10c", frame="ag", pen="0.5p",
            x=X.flatten(), y=Y.flatten(), z=Z.flatten(), levels=10, annotation=20)
fig.show()
```

## 12. Map + topographic cross-section (project + grdtrack + shift_origin)
Draw line A–B, sample DEM along it, plot the elevation profile above the map. The full
"map + profile" pattern (also used for depth sections).
```python
import pygmt
region_map = [122, 149, 30, 49]; lonA, latA, lonB, latB = 126, 42, 146, 40
fig = pygmt.Figure()
fig.basemap(region=region_map, projection="M12c", frame="af")
grid = pygmt.datasets.load_earth_relief(resolution="10m", region=region_map)
fig.grdimage(grid=grid, cmap="oleron")
fig.plot(x=[lonA, lonB], y=[latA, latB], pen="1p,red")
fig.text(x=[lonA, lonB], y=[latA, latB], text=["A", "B"], offset="0c/0.3c", font="15p,red")
fig.shift_origin(yshift="h+1.5c")
fig.basemap(region=[0, 15, -8000, 6000], projection="X12c/3c", frame=0)
track = pygmt.project(center=[lonA, latA], endpoint=[lonB, latB], generate=0.1)
track = pygmt.grdtrack(grid=grid, points=track, newcolname="elevation")
fig.plot(x=track.p, y=track.elevation, fill="gray", pen="1p,red", close="+y-8000")
fig.basemap(frame=["WSrt", "xa2f1+lDistance", "ya4000+lElevation / m"])
fig.show()
```

## 13. Dual Y-axis line plot (config-colored axes)
Two y-scales on one frame (e.g. displacement vs rate), left/right axes colored to match.
```python
import numpy as np, pygmt
x = np.linspace(1, 9, 9); y1 = x; y2 = x**2 + 110
fig = pygmt.Figure()
fig.basemap(region=[0, 10, 0, 10], projection="X15c/15c", frame=["St", "xaf+lx"])
with pygmt.config(MAP_FRAME_PEN="blue", MAP_TICK_PEN="blue", FONT_ANNOT_PRIMARY="blue", FONT_LABEL="blue"):
    fig.basemap(frame=["W", "yaf+ly1"])
fig.plot(x=x, y=y1, pen="1p,blue"); fig.plot(x=x, y=y1, style="c0.2c", fill="blue", label="y1")
with pygmt.config(MAP_FRAME_PEN="red", MAP_TICK_PEN="red", FONT_ANNOT_PRIMARY="red", FONT_LABEL="red"):
    fig.basemap(region=[0, 10, 100, 200], frame=["E", "yaf+ly2"])
fig.plot(x=x, y=y2, pen="1p,red"); fig.plot(x=x, y=y2, style="s0.28c", fill="red", label="y2")
fig.legend(position="jTL+o0.1c", box=True)
fig.show()
```

---

**Focal mechanisms (meca)** are covered in `scripts/seismicity_map.py` and REFERENCE.md §8.
**Version note**: newer gallery code may use `from pygmt.params import Box, Pattern` (the only two
classes in v0.17); string modifiers (`position="jTL+o0.2c"`, `box="+p1p,black"`) work on all versions.
