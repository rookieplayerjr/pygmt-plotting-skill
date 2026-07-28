# PyGMT 出版级制图实战 (Publication Craft)

社区一手来源（PyGMT Tutorials/Gallery、GMT 官方文档、Crameri 科学配色站、FOSS4G/EarthScope
workshop、GMT 中文社区）提炼的"把图从能用到好看、到投稿规范"的工作流与审美经验。
API 签名见 [REFERENCE.md](REFERENCE.md)，报错避坑见 [GOTCHAS.md](GOTCHAS.md)。

---

## 1. 图层叠放顺序（画家模型）

GMT 是画家模型——**后画的盖先画的，调用顺序 = 叠放顺序**。出版级地图标准流水线：

1. **底图框架** `fig.basemap()`/`fig.coast()`：先定 region + projection
2. **地形底层** `fig.grdimage(shading=...)`：shaded relief（灰度或彩色）
3. **海陆** `fig.coast(land=, water=, shorelines=)`
4. **数据层**：散点 `fig.plot` / 半透明栅格叠加 / 等值线 `fig.grdcontour`
5. **构造要素**：断层线、板块边界（`fig.plot` 线）、震源机制 `fig.meca`
6. **注记** `fig.text`：标签、剖面线 A–A′
7. **装饰**（最后）：`fig.colorbar` → 比例尺/指北针 `fig.basemap(map_scale=, rose=)` → 定位图 `fig.inset`

理由：colorbar/scale/inset 必须最后画，否则被数据层盖住；数据点要在地形之上才可见。
重复调 `fig.basemap()` 只加装饰（scale/rose）而不重画框，是合法常用手法。

## 2. 科学配色（最被强调、最易错）

**弃用 jet/rainbow**：非感知均匀，制造虚假梯度与边界，黑白打印和色盲下失效。

| 类型 | 推荐 cmap (Crameri SCM) | 用途 |
|---|---|---|
| Sequential | `batlow`(旗舰)、`roma`、`oslo`、`lajolla` | 单向递增（速度、深度、温度） |
| Diverging | `vik`、`broc`、`cork`、`berlin` | 有零点的差值（位移、异常、形变） |
| 地形 | `oleron`、`bukavu` | 陆海色带分明 |
| Cyclic | `romaO`、`vikO`、`brocO` | 相位、方位角、经度 |

**三条硬规则**：① 感知均匀（每档色差=等量数据差）；② 色觉友好（SCM 内置承诺）；
③ **diverging 必须零值居中且 series 对称** —— `series=[-5, 5, 0.5]` 而非 `[0, 10, …]`，
否则零点偏移、视觉偏向一端，这是 diverging 图最常见错误。
```python
pygmt.makecpt(cmap="vik", series=[-5, 5, 0.5], continuous=True)   # 形变：对称居中
pygmt.makecpt(cmap="batlow", series=[0, 4000, 100])              # 地形：单向
```

## 3. 地形 Hillshade（光照）

光源方位角惯例：**azimuth 300° 或 -45°（西北光）** —— 人眼默认"光从左上来"才把凸起读对，
这是审美惯例非物理真实。太阳高度角常用 30°。

```python
# A. grdimage 自带 shading（一步到位，推荐）
fig.grdimage(grid=dem, cmap="oleron", shading="+a300+nt1")   # +nt1=累积分布拉伸
# B. 单独算梯度网格
dgrid = pygmt.grdgradient(grid=dem, radiance=[300, 30])      # [方位角, 高度角]
fig.grdimage(grid=dem, cmap="oleron", shading=dgrid)
```

**"灰度地形 + 半透明彩色数据"叠加**（出版图最好看的做法）：
```python
fig.grdimage(grid=dem, cmap="gray", shading=True)            # 底：灰度浮雕
fig.grdimage(grid=data, cmap="vik", transparency=40)         # 叠：半透明数据，透出地形
```

## 4. 比例尺 / 指北针 / 经纬网

```python
# 比例尺（墨卡托等投影比例随纬度变，+c<lat> 必须指定计算纬度）
fig.basemap(map_scale="jBR+w500k+f+u+o1c/1c+c35")   # +f 火车轨样式, +u 加单位
# 方向玫瑰 / 磁罗盘
fig.basemap(rose="jTR+w1.5c+f2+lW,E,S,N")           # +f1~3 详略, +l 自定义标签
fig.basemap(compass="jTR+w2c+d11")                   # +d 磁偏角
```
经纬网 frame：三档 `a`(注记)/`f`(刻度)/`g`(网格)；**只在左 W、下 S 注记**（大写带注记，
小写仅刻度）→ `frame=["WSne","af"]`。配 `MAP_FRAME_TYPE="plain"` 去掉默认 fancy 黑白边框。

## 5. 多面板组图

```python
with fig.subplot(nrows=2, ncols=2, figsize=("15c","12c"), autolabel=True,
                 frame=["af","WSne"], margins=["0.3c","0.3c"],
                 sharex="b", sharey="l", title="Main"):   # 仅底/左显注记，省空间且统一
    fig.basemap(region=..., projection="X?", panel=[0,0]); fig.grdimage(...)
    fig.basemap(panel=True)                                # panel=True 自动推进
```
- `projection="X?"/"M?"` 让宽度由 subplot 自动算 → 面板等宽对齐。
- **共享 colorbar**：在 subplot 块**外**画完所有面板后调一次 `fig.colorbar(position="JBC+w10c/0.4c+h+o0c/1.5c")`。
- subplot **不支持嵌套**；复杂版面用多块 subplot + `fig.shift_origin()` 手动拼。

## 6. 导出选择

- **投稿首选矢量 PDF/EPS**：无分辨率问题，文字/线条无限缩放清晰，字体经 ghostscript 默认嵌入。
- **含大量栅格**（InSAR 形变、shaded relief）：PNG/TIFF，**dpi≥300**（投稿常要 300–600）。
- `crop=True`(默认) 裁多余画布；`transparent=True` 仅 PNG；混合时整图导 PDF（栅格内嵌为图像）。

## 7. 地震 / 构造图组合

典型 seismotectonic 叠层（按 §1 顺序）：灰度 shaded relief → 海岸线 → 断层线（粗实线）→
震中散点（按深度配色、按震级定 size）→ 震源机制 beachball（`fig.meca`，按深度 cmap 着色）→
剖面线 A–A′ → 深度 colorbar → 比例尺+指北针 → inset 定位图。
范例脚本见 `scripts/seismicity_map.py` 与 `scripts/cross_section.py`。

## 8. 定位图 inset

```python
with fig.inset(position="jTL+w3.5c+o0.2c", box="+gwhite+p1.5p,gold"):
    fig.coast(region=[-130,-65,24,50], projection="M3.5c", land="gray",
              borders=[1,2], shorelines="1/thin", dcw="US.CA+gred")   # dcw 高亮主图所在区
```
小图用小投影（如 `M3.5c`），或在 inset 里画矩形框标主图范围。

## 9. "从能用到好看"的零散经验

- **pen 层级**：断层粗实线 `1.5p,black`、次级细线、边界虚线——用粗细+实虚建立视觉层级，别全同宽。
- **海岸线只画 1 级** `shorelines="0.5p,black"`，避免内陆细碎湖线（共 4 级）干扰。
- **coastline resolution 按出图尺寸选**：小图 `low` 足够，`full` 拖慢且无意义。
- **统一字号**：`pygmt.config(FONT_ANNOT_PRIMARY="9p", FONT_LABEL="10p", FONT_TITLE="12p")` 全局设，别每处单设。
- **交互迭代**：workshop 共识——Jupyter 里 `fig.show()` 边改边看，出版图靠多轮微调；
  收尾必做自检（读回成图查双框、裁切、标签一致）。
