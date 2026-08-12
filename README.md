# pygmt-plotting

[![License: MIT](https://img.shields.io/github/license/rookieplayerjr/pygmt-plotting-skill)](LICENSE)
[![PyGMT](https://img.shields.io/badge/PyGMT-%E2%89%A50.13%20·%20tested%200.17.0-2e6b8a)](https://www.pygmt.org)
[![GMT](https://img.shields.io/badge/GMT-6.6.0-2e6b8a)](https://www.generic-mapping-tools.org)
[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-agentskills.io-b3552e)](https://agentskills.io/specification)

An [Agent Skill](https://agentskills.io/specification) that turns [PyGMT](https://www.pygmt.org)
into a figure production line: copy a template, edit one CONFIG block, pick a style,
ship a publication-ready map.

<p align="center"><img src="previews/displacement_map.png" width="720"></p>
<p align="center"><i>Unmodified demo output of <code>scripts/displacement_map.py</code> —
coseismic LOS field over SRTM terrain, fault trace, locator inset.</i></p>

## Features

- **Six runnable templates.** Displacement map, seismicity map with focal mechanisms,
  map + depth section, E/N/U component panels, GPS velocity field, wrapped interferogram.
  Each runs standalone in seconds; you edit only the CONFIG block and the data section.
- **Six styles, one switch.** `house` · `journal` · `classic` · `minimal` ·
  `presentation` · `dark` — `STYLE = "dark"` restyles the entire figure.
- **Condensed reference + symptom-indexed gotchas.** The failures that cost an afternoon
  because nothing errors out, each with symptom → cause → fix.
- **Pre-delivery QC checklist.** Overlap, clipping, missing arrowheads, wrong data anchors.
  Every checklist item and gotcha corresponds to a failure observed in testing.

## Installation

Clone into your agent's skills directory (target folder must be named `pygmt-plotting`):

```bash
# Claude Code
git clone https://github.com/rookieplayerjr/pygmt-plotting-skill.git ~/.claude/skills/pygmt-plotting
# Codex ($CODEX_HOME/skills if set)
git clone https://github.com/rookieplayerjr/pygmt-plotting-skill.git ~/.codex/skills/pygmt-plotting
# Tencent WorkBuddy
git clone https://github.com/rookieplayerjr/pygmt-plotting-skill.git ~/.workbuddy/skills/pygmt-plotting
```

The skill is discovered automatically from `SKILL.md`; start a new session afterwards.
Rendering requires PyGMT/GMT (`conda install -c conda-forge pygmt`); the reference material
is useful without them.

## Templates

Every image below is the direct, unedited output of its script:

| | |
|---|---|
| <img src="previews/seismicity_map.png" width="420"> | <img src="previews/cross_section.png" width="420"> |
| `seismicity_map.py` — Japan-trench catalog (real PyGMT sample data), depth-colored, magnitude-sized, GCMT-style beachballs | `cross_section.py` — profile on relief + events projected onto a depth section, depth reading positive down |
| <img src="previews/multipanel_components.png" width="420"> | <img src="previews/velocity_field_map.png" width="420"> |
| `multipanel_components.py` — E/N/U decomposition sharing one CPT and colorbar | `velocity_field_map.py` — GPS vectors, 1σ ellipses, reference arrow, scale bar |
| <img src="previews/wrapped_phase_map.png" width="420"> | <img src="previews/displacement_map.png" width="420"> |
| `wrapped_phase_map.py` — wrapped fringes with cyclic CPT + nearest-neighbor guard, π-annotated colorbar | `displacement_map.py` — gridded LOS over terrain, fault trace, locator inset |

## Styles

<p align="center"><img src="previews/styles_all.png" width="860"></p>

Same data, six looks — set `STYLE = "..."` in any template. All styles keep the same hard
rules (annotations on W/S only, bottom colorbar with units, depth axes positive-down).
`style_presets.py` also exposes `style()`, `panel_label()`, `colorbar()`, `coast_colors()`
for standalone scripts.

## Documentation

| File | Contents |
|---|---|
| `SKILL.md` | Entry point: template routing, style routing, house rules, load discipline |
| `REFERENCE.md` | Condensed PyGMT API (verified against 0.17.0) |
| `GOTCHAS.md` | Symptom-indexed pitfalls: region/CPT/grids/layout/meca/velo/vectors |
| `GALLERY.md` | 13 ready-to-adapt scenario snippets |
| `STYLES.md` | The six styles: configs, previews, dark-mode notes, how to extend |
| `CRAFT.md` | Publication craft: layer order, colormaps, hillshade, export |
| `QC.md` | Pre-delivery checklist loop with a token-economy protocol |
| `COMMUNITY.md` | Curated navigation of the GMT China community manual, incl. CJK labels |
| `MANUAL.html` | Self-contained handbook (Chinese) covering all of the above |

## A sample of the gotchas

- `frame=["WSne", "af", "+tTitle"]` hard-fails on GMT 6.6 — frame settings may appear in
  only one list entry: `["WSne+tTitle", "af"]`.
- `velo` with `+n` silently deletes every arrowhead on geographic maps. Omit `+n`; size
  `VSCALE` so the smallest meaningful velocity clears the head length.
- Bilinear interpolation destroys cyclic colormaps: ±π pixels average to the neutral
  color and wrapped interferograms grow a false gray seam. Use `interpolation="n"`.
- `makecpt` without `output=` sets a session-global CPT that the next `makecpt` silently
  overwrites — multi-panel figures get cross-contaminated colors.
- Scatter fed straight to `xyz2grd` renders vertical stripes; it bins, it does not
  interpolate. Use `blockmean` + `surface`.

## Acknowledgements

The community-sourced material references the [GMT China community manual](https://docs.gmt-china.org)
(CC BY-NC-SA); colormaps follow Crameri's [Scientific Colour Maps](https://www.fabiocrameri.ch/colourmaps/).

## License

MIT — see [LICENSE](LICENSE).
