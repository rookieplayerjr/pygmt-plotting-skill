# PyGMT 实战避坑清单 (Community Gotchas)

社区一手来源（GMT 论坛、PyGMT GitHub、changelog）提炼的踩坑经验。每条：现象 → 原因 → 正确写法。
官方 API 签名见 [REFERENCE.md](REFERENCE.md)；本文件只收录文档里不会明说、但实战必踩的坑。

---

## 1. region / 投影

### 1.1 region 顺序是 [W, E, S, N]，不是 [W, S, E, N]
- **现象**：地图范围错乱、空白、或报 "Region exceeds limits"。
- **原因**：误用 matplotlib 的 `[xmin, xmax, ymin, ymax]` 习惯顺序是对的，但很多人写成 `[W, S, E, N]`（经纬交错）。
- **正确**：`region=[-125, -114, 32, 42]`（西、东、南、北）。

### 1.2 `"d"` vs `"g"` 全球范围 —— 决定地图中心
- `"d"` = -180/180，中心在本初子午线 (0,0)。
- `"g"` = 0/360，中心在国际日期变更线 (180,0)。
- **太平洋/跨日期线研究区**：用 `"g"`（0/360），避免数据被 ±180 边界切成两半。
- 来源：<https://www.pygmt.org/latest/tutorials/basics/regions.html>

### 1.3 跨 ±180° 日期线
- **现象**：跨日期线的线/多边形被拉到整个地图宽度，或要素被边界裁掉。
- **原因**：GMT 对日期线 wrapping 的检测在某些情况下失效；笛卡尔区域 ±180 跳变。
- **正确**：研究区跨日期线时统一用 0/360 经度约定（数据和 region 都转到 0–360），region 用 `"g"` 系。周期性地图上靠近边界的符号可能需要画两次（GMT 会在 repeating boundary 两侧各画一次）。

### 1.4 投影宽度必须带单位
- **现象**：报错或尺寸异常。
- **原因**：`projection="M12"` 缺单位。
- **正确**：`"M12c"`（厘米）/`"M5i"`（英寸）/`"M300p"`（点）。Mercator `M`、linear `X`、Lambert `L lon0/lat0/lat1/lat2/w`、orthographic `G lon0/lat0/w`。

### 1.5 ISO 国家码 + `+r`/`+e` 自动取范围
- `region="JP"` 自动取日本范围；`region="JP+r2"` 向外扩 2 度。
- `+r` = 圆整到 increment 倍数；`+R` = 加 increment 不圆整；`+e` = 至少扩 0.25×increment。
- corner 形式：`"10/35/20/45+r"` = 左下 (10E,35N)、右上 (20E,45N)（注意此处是对角点，不是 W/E/S/N）。

### 1.6 地理 vs 笛卡尔 gtype 导致错位（见 §3.1）

---

## 2. 颜色 / CPT

### 2.1 makecpt 无 `output=` → 设为「会话 CPT」，会被后续 makecpt 覆盖
- **现象**：colorbar 用错了颜色范围，或多 panel 颜色串台。
- **原因**：`pygmt.makecpt(...)` 不带 `output=` 时设置的是当前会话 CPT，后续 `grdimage`/`plot(cmap=True)`/`colorbar` 自动使用它；下一次 `makecpt` 会覆盖它。
- **正确**：多色标场景，要么每个 panel 紧贴 `makecpt` 后立即 `grdimage`+`colorbar`，要么存文件用 `output=` 再以文件名引用（见 2.2、5.1）。

### 2.2 存了 CPT 文件后 `colorbar(cmap=True)` 报 "CPT has no z-slices"
- **现象**：`pygmt.makecpt(..., output="x.cpt")` 后 `fig.colorbar(cmap=True)` 报错 `CPT <stdin> has no z-slices`。
- **原因**：`cmap=True` 取的是会话 CPT，但你存到了文件、没设会话 CPT。
- **正确**：`fig.colorbar(cmap="x.cpt")`（传文件名，不要 True）。
- 来源：<https://forum.generic-mapping-tools.org/t/pygmt-makecpt-error-cpt-stdin-has-no-z-slices/2964>

### 2.3 series 第三个值（increment）决定离散/连续
- **现象**：colorbar 出现意外的分级色块（banded）而非平滑渐变，或反之。
- **原因**：`series=[min, max]`（无 inc）→ 连续 CPT；`series=[min, max, inc]` → 按 inc 分级（离散）。想要平滑渐变却写了 inc，就会出现色块。
- **正确**：
  - 平滑（位移/速度场）：`pygmt.makecpt(cmap="vik", series=[-10, 10])`
  - 分级（等高线、分类）：`pygmt.makecpt(cmap="batlow", series=[0, 5000, 500])`
- 从颜色列表构建时，`continuous=True` 才强制连续（默认离散）。

### 2.4 数据超出 series 范围 → 取 background/foreground 色
- **现象**：超界数据显示成奇怪的端点色或缺失。
- **原因**：CPT 含 B（< 最低值）、F（> 最高值）、N（NaN）三个额外色；超界数据落到 B/F。
- **正确**：用 `background`/`overrule_bg`/`no_bg` 控制；或扩大 series 范围。NaN 区域用 N 色（默认 `gmt.conf` 的 `COLOR_NAN`）。
- 来源：<https://forum.generic-mapping-tools.org/t/series-argument-in-pygmt-makecpt/3865>

### 2.5 NaN 透明 / 掩膜
- grid 中 NaN 想透明：`fig.grdimage(grid, nan_transparent=True)`（PostScript Level 3 color-masking）。
- 想把非 NaN 的某个值也设透明：`nan_transparent="+z<value>"`。
- makecpt 透明度：`transparency=50`（0–100）；加 `+a` 同时作用于 F/B/N。
- colorbar 想显示 NaN 色块：用 colorbar 的 NaN label 选项。
- 来源：<https://forum.generic-mapping-tools.org/t/how-to-create-grid-and-mask-nan-areas-with-gray-color/1577>

### 2.6 直方图均衡化颜色用 grd2cpt
- 数据分布极不均匀（如地形）时 `makecpt` 线性 series 会浪费色域；改用 `pygmt.grd2cpt(grid=g, cmap="geo")` 按数据分位数分配颜色。

---

## 3. 网格 / xarray

### 3.1 外部 NetCDF 读入后 gtype/registration 不对 → 地图错位或当成笛卡尔
- **现象**：地理网格被当成笛卡尔画，投影错乱、坐标错位；或 warning "Guessing of registration in conflict between x and y"。
- **原因**：自建/外部 xarray DataArray 的 `gmt.gtype`、`gmt.registration` 没设对。
- **正确**：显式设置（值的含义：registration `GRIDLINE=0` / `PIXEL=1`；gtype `CARTESIAN=0` / `GEOGRAPHIC=1`）：
  ```python
  da.gmt.gtype = 1          # geographic
  da.gmt.registration = 0   # gridline
  ```
- 来源：<https://github.com/GenericMappingTools/pygmt/issues/1172>

### 3.2 算术运算会重置 gmt 属性，切片不会
- **现象**：`grid * 2` 后画图突然错位。
- **原因**：xarray accessor 限制 —— 算术运算（`grid*2`、`grid+offset`）后 `gmt` accessor 重新初始化为默认（gridline/cartesian）；**切片**（`grid[0:30, 50:80]`）则保留。
- **正确**：算术后手动搬回：
  ```python
  g2 = grid * 2.0
  g2.gmt.registration = grid.gmt.registration
  g2.gmt.gtype = grid.gmt.gtype
  ```
- 来源：<https://www.pygmt.org/dev/api/generated/pygmt.GMTDataArrayAccessor.html>

### 3.3 从 Dataset 取 DataArray 设属性不生效
- **现象**：`ds.zval.gmt.registration = ...` 不持久。
- **正确**：先赋给变量再设：
  ```python
  zval = ds.zval
  zval.gmt.registration = 0   # 这样才持久
  ```

### 3.4 grdimage 全黑（全球网格缺冗余 360°E）
- **现象**：全球网格 `grdimage` 输出全黑。
- **原因**：网格经度只到 359° / 缺 0°E 与 360°E 的冗余重复点。
- **正确**：构建全球网格时让经度含冗余端点 `lon = np.arange(0, 361, 1)`（0 到 360 闭区间）。
- 来源：<https://github.com/GenericMappingTools/pygmt/issues/3331>、<https://github.com/GenericMappingTools/pygmt/issues/375>

### 3.5 pixel vs gridline registration
- earth_relief 默认 gridline，但 `"15s"` 只有 pixel。混用会有半格偏移。
- `load_earth_relief(resolution=..., registration="pixel"/"gridline")` 显式指定。

### 3.6 高分辨率网格下载慢 / 必须给 region
- 分辨率高于 `05m` 时 **必须**传 `region=`，否则拒绝（避免下载全球高分网格）。
- 大区域用高分辨率前先估数据量，能用 `01m`/`03s` 就不用 `01s`。

---

## 4. 性能 / 缓存 / 文件大小

### 4.1 earth_relief 缓存位置 `~/.gmt`
- 首次需联网下载，缓存到 `~/.gmt/server/earth/earth_relief/`（还有 earth_gebco 等），之后离线复用。
- 想换缓存盘：设环境变量 `GMT_USERDIR` / `GMT_CACHEDIR`。
- 来源：<https://www.pygmt.org/dev/api/generated/pygmt.datasets.load_earth_relief.html>

### 4.2 矢量 PDF 太大
- **现象**：含大量散点/等高线/grdimage 的 PDF 几十上百 MB，打开卡。
- **原因**：PDF 默认把所有元素矢量化；grdimage 投影到非 linear/Mercator 时按 `dpi`（默认 100）栅格化。
- **正确**：
  - PDF 内栅格分辨率默认 720 dpi，可降：`fig.savefig("f.pdf", dpi=300)`。
  - 底图（relief/影像）天生是栅格，矢量化的是上层点线 → 海量散点直接导出 PNG/TIFF（`dpi=300`）而非 PDF。
  - 投影栅格化分辨率：grdimage 的 `dpi=` 参数。

### 4.3 海量散点慢
- GMT 画几十万散点本身比 matplotlib 快，但每点不同大小/颜色（`fill=`数组 + `cmap=True`）会变慢。
- 能用单一 size/单色就不传数组；密集点考虑先做密度网格 (`pygmt.blockmean`/`xyz2grd`) 再 `grdimage`。

---

## 5. 文本 / 图例 / colorbar 排版

### 5.1 多 panel 共享 / 独立 colorbar
- **每 panel 独立色标**：在 `with fig.set_panel(panel=i):` 内紧接 `makecpt` → `grdimage` → `colorbar`，各自独立。
  ```python
  with fig.subplot(nrows=1, ncols=2, figsize=("15c","8c")):
      with fig.set_panel(panel=0):
          pygmt.makecpt(cmap="geo", series=[-8000, 8000])
          fig.grdimage(grid=g0); fig.colorbar(frame="x+lElevation (m)")
      with fig.set_panel(panel=1):
          pygmt.makecpt(cmap="globe", series=[-6000, 3000])
          fig.grdimage(grid=g1); fig.colorbar(frame="x+lElevation (m)")
  ```
- **全图一个共享 colorbar**：subplot 结束后（退出 with 块），用绝对定位画一次 `fig.colorbar(position="JBC+w8c/0.4c+h+o0c/1c")`。
- 注意 issue #2426：subplot 模式下 colorbar 定位 PyGMT 与 CLI 行为曾不一致，定位异常时改用绝对 `position=`。
- 来源：<https://www.pygmt.org/dev/gallery/embellishments/colorbars_multiple.html>

### 5.2 colorbar offset 单位 & 与轴标签重叠
- `position` 修饰符 `+o<dx>/<dy>` 的偏移要带足够距离，否则 colorbar 标签压到坐标轴标签上。
- 房规：`position="JBC+w8c/0.4c+h+o0c/0.8c"`（水平、底部居中、向下偏 0.8c）。

### 5.3 FONT 字号「改了没反应」
- **现象**：`pygmt.config(FONT_LABEL=...)` 似乎无效。
- **原因/真相**：必须把绘图操作放进 `with pygmt.config(...)` 上下文里；config 块可以包住 `Figure()` 创建和所有绘图。另外**投影宽度也影响字号相对大小**（同样 12p 在 `X10c` 和 `X20c` 上视觉占比不同）。
  ```python
  with pygmt.config(FONT_LABEL="14p", FONT_ANNOT_PRIMARY="12p"):
      fig = pygmt.Figure()
      fig.basemap(region=[0,10,0,10], projection="X10c",
                  frame=["WSen","x+lXlabel","y+lYlabel"])
  ```
- `FONT` 是总开关，`FONT_ANNOT_PRIMARY`/`FONT_LABEL`/`FONT_TITLE` 分项覆盖。
- 来源：<https://forum.generic-mapping-tools.org/t/font-size-doesnt-change-regardless-of-what-i-do/3983>

### 5.4 轴标签 `+l` 只在笛卡尔 (X) 投影上有效
- 地理投影（M/L/G…）的 frame 不支持 `x+lLabel` 轴标题，要用 `fig.text` 自己加。

---

## 6. 版本迁移（0.x 参数改名）

PyGMT 0.x 持续重命名参数，老博客/老脚本会报 `unexpected keyword`。对照表（旧 → 新 / 起始版本）：

| 旧写法 | 新写法 | 版本 |
|---|---|---|
| `color=` | `fill=`（plot/plot3d/rose/velo） | ≤0.8 |
| `uncertaintycolor=` | `uncertaintyfill=`（velo） | ≤0.8 |
| wiggle `color=` | `fillpositive=`/`fillnegative=` | ≤0.8 |
| grdimage `bit_color=` | `bitcolor=` | ≤0.8 |
| `fig.xshift/yshift` | `fig.shift_origin()` | ≤0.8 |
| timestamp `justification=` | `justify=` | 0.11 |
| grdfill `no_data=` | `hole=` | 0.15 |
| grdclip `new=` | `replace=` | 0.15 |
| `GMTInvalidInput` | `GMTValueError`/`GMTTypeError` | 0.17 |
| `separator=` | `sep=` | 0.17 |
| histogram `barwidth=` | `bar_width=` | 0.18 |
| `margin=` | `clearance=` | 0.18 |

其他要点：
- `interval`→`levels`、`annotation` 处理方式：grdcontour/contour 的等值线参数在多版本间调整过，等值线不出来时核对 `levels=`/`annotation=`。
- 新版引入 `Position`/`Box` 等对象式参数（colorbar `position=`/`box=`、`frame=Axis(...)`），但**字符串写法仍兼容**，老代码无需立刻改。
- `region`/`projection` 与单字母 `R`/`J` 始终等价并存。
- 来源：<https://www.pygmt.org/dev/changes.html>

---

## 7. 安装 / 环境

### 7.1 用 conda/mamba 装，避免版本不匹配
- PyGMT 要 **GMT ≥ 6.5.0**。conda-forge 提供 Linux/macOS/Windows 预编译 GMT。
- 推荐 `mamba install -c conda-forge pygmt`，让 GMT + Ghostscript + GDAL 等依赖一并装齐。
- 排查：`pygmt.show_versions()` 打印 GMT / Ghostscript / 各依赖版本。

### 7.2 savefig/show 报 Ghostscript (gs) 找不到或版本旧
- **现象**：`psconvert [ERROR]: Cannot execute Ghostscript (gs)`，或找到了旧版 gs。
- **原因（Win）**：GMT 通过系统调用 gs，Win 上 psconvert 从注册表找 gs；conda 装的 gs 不写注册表，于是用到旧的 32 位 gs。Unix 上则是 gs 不在 PATH。
- **正确**：
  - 临时：`fig.savefig("f.png", G="<path>/gs")` 直接指定（`fig.show()` 不支持此参数）。
  - 长久（Win）：用官方安装器装 64 位 Ghostscript ≥ 9.54，会写更高优先级注册表项。
  - Unix：确保 gs 在 PATH（conda 环境已激活）。
  - 透明度异常也多半是 GMT/Ghostscript 版本组合问题 → 升级。
- 来源：<https://forum.generic-mapping-tools.org/t/pygmt-finding-old-ghostscript-with-conda-on-windows/3174>、<https://forum.generic-mapping-tools.org/t/pygmt-error-with-savefig-show-because-of-psconvert/1127>

---

## 8. inset / meca / grdimage 实战坑（实战验证）

### 8.1 `fig.inset` 内 basemap 不画 annotations 和 label
- **现象**：inset 内 `fig.basemap(frame=["WSne","xa..+l..","ya..+l.."])` 只画框线 + 刻度线（ticks），**刻度数字和轴标题全部不显示**。
- **原因**：inset 上下文里 basemap 的 annotation/label 被抑制（GMT inset 机制）。
- **解法**：
  - 手动用 `fig.text` 画刻度数字 + 轴标题（自己定位，向内或向外）。
  - 或彻底不用 inset，改 `fig.shift_origin(xshift=..,yshift=..)` 画独立面板 → annotations 正常，画完 shift 回。

### 8.2 `fig.inset` 强制画默认黑框；`box="+p..."` 会叠成双框
- **现象**：不传 box 也有一圈黑框；再传 `box="+p1p,black"` 出现**两个边框**。
- **解法**：单框 → `box="+gwhite"`（只白底，复用默认框）；想让容器框当坐标轴框就别再画自己的框。真要无框只能 `shift_origin`。白边 `box="+p1p,white"` **盖不住**默认黑框。

### 8.3 `meca` 的 `+m` 震级缩放在 M5–M7 几乎看不出差别
- **现象**：`scale="0.6c+m5"` 下 M5/M6/M7 beachball 大小肉眼无区别。
- **解法**：要按 Mw 明显区分，逐个事件手动算固定尺寸（不带 `+m`）：
  ```python
  bs = 0.30 + 0.17*(Mw - 5)        # M5=0.30c, M7=0.64c
  fig.meca(spec=..., scale=f"{bs:.2f}c", ...)
  ```

### 8.4 `meca(cmap=True)` 用负/小值当 depth 着色 → segfault
- **现象**：想按某连续量（如相关系数）给 beachball 上色，塞进 `depth` 字段 + `cmap=True`，GMT **段错误 exit 139**。
- **解法**：逐个 beachball 用 matplotlib 把值映射成 hex，传 `compressionfill`：
  ```python
  import matplotlib.cm as mcm, matplotlib.colors as mc
  col = mc.to_hex(mcm.get_cmap("RdBu_r")(mc.Normalize(-0.8,0.8)(val)))
  fig.meca(spec=..., compressionfill=col, ...)
  ```

### 8.5 手写 rasterio GeoTIFF 传 `grdimage` → segfault
- **现象**：用 `rasterio` 手动 `transform` 写出的 tif 给 `grdimage`，常直接 segfault。
- **解法**：别落地成手写 tif，直接用 xarray：在已知好坐标的 grid 上替换数据 `relief.copy(data=computed)`，传给 `grdimage`（保留正确 registration/坐标轴）。

### 8.6 `grdimage(shading=...)` 要求强度网格与数据网格同维度
- **现象**：`grdimage [ERROR]: Dimensions of intensity grid do not match that of the data grid!`
- **解法**：数据和地形梯度分辨率不同时，先 `pygmt.grdsample` 把两者采样到**同一 region + spacing + registration**，再画。

### 8.7 内嵌 colorbar 的 label 伸出主图框 → `+mal`
- **现象**：`position="jBR/jBL+..+h"` 内嵌水平 colorbar，annotations + label 默认在色条**下方**，会超出主图边框。
- **解法**：position 末尾加 `+mal`，把 annotations/label 移到色条**上方**；色条本身贴近内框底即可。

### 8.8 `fig.plot(fill="white")` 自带黑色描边（意外的"最外框"）
- **现象**：只想用白矩形盖背景，却多出一圈黑边框。
- **解法**：纯填充无边 → 显式 `pen="white"`（同色隐藏）；GMT psxy 给了 `-G` 默认仍画 `-W`。

### 8.9 inset 骑在主图角上（一半内一半外）
- 用负 offset 把 inset 中心推到主图角：`position="jTR+w<W>/<H>+o-<W/2>c/-<H/2>c"`（offset 正=向内，负=向外）。要"大部分在内、角探出"就用小负值。

### 8.10 密集标签/beachball 防重叠：偏移 + 引线
- 聚集事件：beachball 画到**偏移位置**，`fig.plot` 画细线连回真实震中，真实点画小圆点。两行标签合并成一行可显著减重叠；放大整图（增大 `W`）也直接拉开标签间距。

### 8.11 出版尺寸适配 A4
- 图宽由地图 `projection="M<W>c"` 的 W 决定；横向图配 A4 横向用 **W≈24cm**（总图含标注 ~25cm < 29.7cm 留边距）。`fig.savefig(dpi=360)` 给足栅格分辨率。

### 8.12 `grdimage(nan_transparent=True)` + 自定义 grayscale CPT → panel 下方多一条红/品红条带
- **现象**：用 hand-crafted grayscale CPT（如 `0 black 1 white`）画 coherence、相干图等含 nodata 的灰度数据，开 `nan_transparent=True` 后 panel border 下方出现一条整 panel 宽的**红色 / 品红条**，紧贴 colorbar 上方。
- **本质**：`nan_transparent` flag 强制 GMT 在 colorbar 上方/panel 下方渲染 CPT 的 N (NaN) 条目作为提示带；如果你的 CPT 没显式 `N -` (透明) 或 GMT 默认 NaN 是红色，就显示成红条。即使 CPT 写了 `N -`，PyGMT `makecpt` 重生成 session CPT 时可能 strip 掉该条目。
- **解法**：grayscale + 没有真 NaN 的数据**直接关掉** `nan_transparent`：
  ```python
  fig.grdimage(grid=g_coh, cmap=True, interpolation="n")   # no nan_transparent
  ```
  Coherence 的 `coh==0` 区域在 GMT 灰度上自然显示为黑（"decorrelated = no signal"），符合 InSAR 惯例，不需要透明化。
- **副作用**：若数据真有 NaN 必须透明（如裁掉海面），就别用自定义 CPT；改用 GMT master `gray` cmap 或写 NetCDF 时用 `_FillValue` 让 GMT 走 NaN 路径（PyGMT 0.13 实测 NetCDF NaN 透明化不稳，更稳是 GeoTIFF + rasterio nodata）。

### 8.13 `grdimage` 默认双线性插值 → cyclic colormap (wrapped phase) 在 ±π 边界出灰带
- **现象**：用 `romaO`/`vikO` 等 cyclic colormap 画 wrapped phase（InSAR、orientation 等 [-π, π] 数据），相邻 input pixel 一个 +π、一个 -π → grdimage 默认 bilinear/bicubic 插值算出**平均=0**，cyclic colormap 上 0 落在中性色（灰/白）→ wrap 边界一圈**伪灰带**。
- **本质**：cyclic 数据线性距离≠相位距离；GMT 插值器不知道 ±π 是同一个相位。
- **解法**：插值器换 nearest-neighbor，每个 input pixel 渲染为均匀色块、不跨 wrap 边界平滑：
  ```python
  fig.grdimage(grid=wrapped_nc, cmap=True, nan_transparent=True,
               interpolation="n")   # GMT -n 标志：no smoothing
  ```
- **副作用**：高 dpi 输出时 input pixel 边界肉眼可见（小马赛克）；如要既无 wrap 伪带又看不出马赛克，先把 source grid `grdsample` 上采样 2-4×（仍用 nearest），让物理像素小于 1 px@output dpi。
- **同坑**：用 `vik` 等 zero-centered 但**非** cyclic 的 diverging cmap 画相位类数据时一样出问题（更明显，因 vik 中点是白色）。InSAR wrapped phase **必须** cyclic cmap (`romaO`/`vikO`/`brocO`)。
- **物理分辨率瓶颈** 仍受 multi-look 限制（如 rng-looks 8×2 → 100 m posting）；要更细 fringe 需重处理用 rng-looks 4×1。

---

## 9. 矢量箭头 `fig.plot(style="v...")`（GMT 6.6.0 / PyGMT 0.17.0 实测）

> 结论先行：`+g<fill>` 和 `+h<shape>` **没有 bug，都正常生效**。「只画出线段没有箭头头」的真实原因是下面三条，全部**静默失败**（不报错、不警告），所以极易被误判为 GMT bug。

### 9.1 `+g`/`+h` 看似「不生效」→ 其实是没开箭头头 `+e`/`+b`
- **现象**：`style="v0.5c+gred"` 或 `style="v0.5c+h0.5+gred"` 只画出一条线段，没有箭头头。
- **本质**：GMT 6 的 `v` 样式**默认两端都不画头**。`+e`（末端）/`+b`（起端）才是**开关**；`+g`（填色）、`+h`（形状）只是在描述「头长什么样」，没有头时被静默忽略。
- **解法**：必须显式给 `+e`（或 `+b`，或两者兼有画双头）。修饰符**顺序无关**，`+gred+e` 与 `+e+gred` 等价。
- 只给 `+e` 不给 `+g`/`fill=` → 画出**空心头**（白底黑边），不是没画。

### 9.2 矢量总长 < 箭头头长度 → 整个头被静默丢弃
- **现象**：速度场 / 滑移矢量图里长矢量箭头正常，几根小矢量退化成**短横线**。量级跨度大的图必踩。
- **本质**：`v<size>` 里的 size 是**箭头头的长度**，不是矢量长度。当矢量总长短于头长，GMT 直接不画头。
- **解法**：加 `+n<length>` 归一化——短于该长度的矢量整体等比缩小，头也跟着缩、不会消失；或按数据里**最短**那根矢量来定头的尺寸。
- **实测**：头 `0.5c`、矢量实长 ≈0.64 cm → 无头；加 `+n2c` 后箭头恢复。

### 9.3 `+h` 接近 1 → 头退化成无面积 V 形，`+g` 填色几乎看不见
- `+h` 是 headshape（后掠程度，0=平底三角，1=纯 V 形燕尾）。`+h1` 时头几乎没有面积，填色被压没 → 又一次被误判成「`+g` 不生效」。
- **安全值 `+h0.5`**，兼顾美观与可见性。

### 9.4 安全写法
```python
fig.plot(x=x, y=y, direction=[azimuth, length],
         style="v0.35c+e+gred+h0.5+n1c", pen="1.2p,red")
```
`+e` 开末端头 · `+g` 填色 · `+h0.5` 适度后掠 · `+n1c` 保证短矢量不掉头。
`plot(fill="red")` 与 style 里的 `+gred` **等价**，二选一即可，不必都写。
