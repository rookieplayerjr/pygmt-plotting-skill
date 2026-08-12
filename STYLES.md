# Style Presets — 一套图形，六种风格

`scripts/style_presets.py` 提供 6 个可切换的视觉风格。模板脚本 CONFIG 里改一行
`STYLE = "..."` 即整图换装；自写脚本用法：

```python
import sys; sys.path.insert(0, "<skill>/scripts")
from style_presets import style, panel_label, colorbar, coast_colors, list_styles

fig = pygmt.Figure()
with style("dark"):                          # pygmt.config 上下文，出块即恢复
    fig.basemap(..., frame=["WSne", "xaf", "yaf"])
    fig.coast(**coast_colors("dark"))
    ...
    panel_label(fig, "A", style_name="dark")             # 方框面板字母
    colorbar(fig, "LOS (mm)", style_name="dark", width=8) # 底部水平色标
with style("house", FORMAT_GEO_MAP="ddd.x"):  # 任意 gmt.conf 键可临时覆盖
    ...
```

所有风格都保留两条房规硬约束：**注记只在 W/S 两边**（frame 自己传 `WSne`）、
**colorbar 水平置底带单位**（用 `colorbar()` helper）。深度轴正值向下规则不变。

## 风格总表

| 风格 | 预览 | 一句话 | 何时用 |
|---|---|---|---|
| `house` | ![house](previews/style_house.png) | plain 细框 + Helvetica 9p + vik/inferno | **默认**。日常科研图、报告、组会 |
| `journal` | ![journal](previews/style_journal.png) | house 收紧一号（8p、0.8p 框、短刻度） | 投稿终稿，单栏 8.5 cm 版面；导出 PDF |
| `classic` | ![classic](previews/style_classic.png) | GMT fancy 黑白花边框 + ddd:mm:ss + 传统配色 | 经典制图风：学位论文、挂图、站位图 |
| `minimal` | ![minimal](previews/style_minimal.png) | AvantGarde 灰调 + 浅灰网格（frame 加 `g`） | 网页、幻灯浅底、现代简洁风 |
| `presentation` | ![presentation](previews/style_presentation.png) | 全部大一档粗一档（14p 注记、1.5p 框） | 会议幻灯；数据 pen 也配粗（≥1.5p） |
| `dark` | ![dark](previews/style_dark.png) | 深页底 + 白框白字 + 灰网格 | 深色幻灯/海报。亮色 CPT（turbo/batlow/vik）最清楚 |

来源锚点：`classic`/`minimal` 对应 GMT 官方 `GMT_THEME` 的 classic/minimal 主题参数
（见 gmt.conf 文档），`house`/`journal` 是用户房规，`dark` 综合社区暗色图配方。

## dark 风格的注意事项（仅它有坑）

- 预设只改页面/框线/字体/刻度/网格颜色，**不动 COLOR_BACKGROUND/FOREGROUND**（那会改数据渲染）。
- 海陆底色是逐调用参数，记得用 `coast_colors("dark")`（land gray25 / water gray10 / 岸线 gray70）。
- 近零发白的 diverging CPT（vik 中心）在深底上会"发光"，属正常；纯亮序列色
  （turbo、batlow、hawaii）观感最佳。灰度 hillshade 底图照常可用。
- 导出 PNG 别开 `transparent=True`（页面色就是设计的一部分）。

## 扩展 / 自定义

- 新风格：往 `style_presets.py` 的 `STYLES` dict 加一个 entry（config + label/cbar/coast 五件套），
  然后跑 `python scripts/render_style_previews.py` 重新生成预览图并目检。
- 单图微调不建新风格：`style("house", MAP_FRAME_PEN="1.2p,black")` 直接覆盖。
- 多面板 subplot 的面板字母由 autolabel 画，样式化写法见
  `scripts/multipanel_components.py`（从 `STYLES[STYLE]["label_box"]` 拼 autolabel 串 + `FONT_TAG`）。

## 中文标注（CJK）

GMT 原生 PostScript 字体不含 CJK；中文出图两条路：
1. 完整配方（cidfmap + PSL_custom_fonts + `PS_CHAR_ENCODING Standard+`）见
   [COMMUNITY.md](COMMUNITY.md) 的"中文出图配方"节；
2. **更稳**：图内一律英文，中文放论文 caption / 幻灯页面文字（house 默认做法）。
