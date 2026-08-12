# GMT 中文社区学习材料导航 (docs.gmt-china.org)

社区手册 = GMT 官方文档中文精编 + 地球物理特化 + **官方完全没有的内容**（中文字体方案、
特殊字符对照、社区 gallery）。本文件是导航索引：按需跳转 URL，不整站重爬。
维护方 gmt-china（田冬冬、姚家园），覆盖 GMT 6.6，脚本为 CLI bash 现代模式——转 PyGMT
时对照 REFERENCE.md 的参数别名表（-R→region, -J→projection, -B→frame, -S→style…）。

## Gallery 精选（/6.5/examples/exNNN/，19 例全目录）

高相关 8 例（★ = 本 skill 尚无对应模板，值得抄）：

| 例 | 内容 | 对应关系 |
|---|---|---|
| ex030 | **三维有限断层滑动栅栏图**（plot3d 多边形 CPT 着色 + 3D 视点 -p160/20） | **已移植为 `scripts/fault_slip_3d.py`**（PyGMT + house 规则）；bash 原版在 社区页面 |
| ex011 | **台站中心方位等距投影**（-JE + SE- 同心震心距圈 30°/60°/90°） | **已移植为 `scripts/station_azimuthal_map.py`**；bash 原版同上 |
| ex002 | 地球内部界面 + PcP/PKiKP 射线路径（极坐标叠 basemap） | **已移植为 `scripts/earth_interior.py`** |
| ★ ex031 | 三维速度模型任意垂直切片 | 待移植——需真实速度模型文件（提供即接） |
| ex010/ex012 | 发震时刻着色 / M-T 图 | **已移植为 `time_colored_seismicity.py` / `mt_plot.py`** |
| ex009 | 震级圆圈 + 分段统计小面板 | **已移植**：seismicity_map.py 含 STATS_INSET 统计嵌板 |
| ex015 | GPS 速度场 + 误差椭圆 + inset 图例 | ≈ scripts/velocity_field_map.py |
| ex026 | 地形剖面双图联动 | ≈ scripts/cross_section.py |

中相关：ex003 地形调制纹理、ex004 卫星底图(GCJ-02 纠偏)、ex013 行政区裁剪、
ex017 一般矢量场、ex029 3D draped（其 drapegrid 手法已用于 Sagaing 3D 展示图，拼幅坑见 GOTCHAS 8.7）。5 个精读例的**完整 bash 脚本**已离线存档在
社区页面（ex009/011/015/026/030）。

## 手册章节导航（docs.gmt-china.org/latest/）

| 章节 | 何时去读 |
|---|---|
| `tutorial/advanced/` | subplot/inset/oneliner/配置 的中文教程（与官方等价，中文更快） |
| `basis/` ⭐ | **text 字体语法、special-character 八进制/希腊字母转义、color 663 色名 + `@透明度%`** —— 官方无中文对照 |
| `proj/` | 30+ 投影参数速查（走滑断层用 -JL Lambert、局部用 -JA/-JE） |
| `conf/` | 120+ gmt.conf 参数分类详解 |
| `dataset/` ⭐ | **中国国界/省界 (CN-border-L1.gmt)、中国断层、板块边界 (PB2002)、全球应力/重磁数据下载指引** |
| `chinese/` ⭐ | 中文出图完整方案（官方零提及），配方见下 |
| `module/` | 140+ 模块中文手册（meca/velo/plot3d…） |

## 中文出图配方（chinese/ 章，实测口径）

图内必须出中文时（默认策略仍是图内英文、中文进 caption）：

```bash
# 1. 字体文件: ~/.gmt/winfonts/ 放 simsun.ttc / simhei.ttf 等
# 2. ~/.gmt/cidfmap (Ghostscript CID 映射):
/STSong-Light  <</FileType /TrueType /Path (${HOME}/.gmt/winfonts/simsun.ttc) /SubfontId 0 /CSI [(GB1) 4]>> ;
/STHeiti-Regular <</FileType /TrueType /Path (${HOME}/.gmt/winfonts/simhei.ttf) /SubfontId 0 /CSI [(GB1) 4]>> ;
# 3. ~/.gmt/PSL_custom_fonts.txt:
STSong-Light--UniGB-UTF8-H   0.700   1
STHeiti-Regular--UniGB-UTF8-H  0.700  1
# 4. 脚本内 (PyGMT 用 pygmt.config 同名参数):
gmt set PS_CHAR_ENCODING Standard+        # 6.x 中文 bug 补丁，必须
gmt set FONT_LABEL 12p,STSong-Light--UniGB-UTF8-H,black
```

Windows 走 UTF-8 Beta 区域设置 + Ghostscript ≥10.03 自动 cidfmap（详见 chinese/ 章）。

## 社区技巧摘录（本 skill 其他文档未覆盖的）

- **透明度语法**：`fill="red@50"`、`pen="0.5p,blue@70"`——@后是不透明度百分比，非 RGBA 通道。
- **临时切字体转义**：`@%12%...@%%` 切 Symbol 字体打希腊字母（12 号字体），`@~...@~` 同义；
  八进制 `\NNN` 打特殊符号（对照表在 basis/special-character/）。
- **色名体系**：663 个命名色 + light/dark 前缀（`lightseagreen`），HSV/CMYK 直写均可。
- **oneliner 模式**：`gmt coast ... -pdf map` 单行出图，调试快，生产仍用 begin/end。
- **卫星底图纠偏**：国内 Amap/Google 瓦片是 GCJ-02 坐标，叠 WGS84 数据前必须纠偏（ex004）。

地震分区其余卡片移植：meca 专图 = `focal_mechanisms.py`；sac 波形 = `record_section.py`（真实 IU/II LHZ 数据打包）；grdshake 震动图 = `shaking_intensity.py`（模型场，图上明示 MODELED）。
