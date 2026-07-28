# pygmt-plotting

An [Agent Skill](https://agentskills.io/specification) for producing publication-quality
scientific maps and figures with [PyGMT](https://www.pygmt.org/).

It bundles three things that are usually scattered: a condensed API reference, an
opinionated house style for journal figures, and — the part that took the longest to
accumulate — a catalogue of field-tested traps that the official docs do not mention.

## Install

Drop it into your agent's skills directory:

```bash
git clone https://github.com/rookieplayerjr/pygmt-plotting-skill.git ~/.claude/skills/pygmt-plotting
```

Claude Code discovers it automatically from the `SKILL.md` frontmatter. For other agent
runtimes, see your platform's skill-loading documentation.

## What's inside

| File | Contents |
|---|---|
| `SKILL.md` | Entry point: quick start, the three universal parameters (`region`/`projection`/`frame`), projection & CPT cheat sheets, and the house style rules. |
| `REFERENCE.md` | Condensed API: figure lifecycle, `coast`/`plot`/`text`, `grdimage`/`grdcontour`/`grdview`, `makecpt`/`colorbar`, grid processing, `meca`, `velo`, `project`, and multi-panel layout. |
| `GOTCHAS.md` | Nine sections of pitfalls with symptom → cause → fix, sourced from the GMT forum, PyGMT issues, and hard-won practice. |
| `CRAFT.md` | Publication craft: layer order, colormap choice, hillshade conventions, multi-panel alignment, vector vs raster export. |
| `GALLERY.md` | 13 ready-to-adapt scenario templates. |
| `scripts/` | Four runnable, parameterized templates. Each runs standalone on synthetic or GMT-hosted data — edit the `CONFIG` block at the top. |

All four scripts are verified to run against PyGMT 0.17.0 / GMT 6.6.0. They produce the
figures below directly, with no data files to fetch:

| `displacement_map.py` | `seismicity_map.py` |
|---|---|
| ![](previews/displacement_map.png) | ![](previews/seismicity_map.png) |
| Shaded relief under a diverging displacement field, with a horizontal colorbar. | Earthquake catalogue scaled by magnitude and colored by depth, with focal mechanisms. |

| `cross_section.py` | `multipanel_components.py` |
|---|---|
| ![](previews/cross_section.png) | ![](previews/multipanel_components.png) |
| A profile line on a map plus events projected onto a depth section, depth reading positive downward. | Three-component panel row sharing one CPT, laid out with `subplot`. |

## A sample of the gotchas

These are the kind of failures that cost an afternoon because nothing errors out:

- **Vector arrowheads never appear.** `style="v0.5c+gred"` draws a bare line. `+g` (fill)
  and `+h` (shape) only describe what a head looks like — `+e`/`+b` is what actually turns
  one on. Separately, a vector shorter than the head length silently loses its head
  entirely, which is why velocity fields lose arrows on exactly the small vectors you
  cared about.
- **`makecpt` without `output=` sets a session-global CPT** that the next `makecpt`
  silently overwrites, so multi-panel figures get cross-contaminated colors.
- **xarray arithmetic resets `gmt.gtype`/`gmt.registration`,** so `grid * 2` quietly turns
  a geographic grid into a Cartesian one and your map shifts. Slicing preserves them.
- **Bilinear interpolation destroys cyclic colormaps.** Adjacent +π and −π pixels average
  to 0, which is the neutral color, so wrapped interferograms grow a false gray seam along
  every fringe boundary. Use `interpolation="n"`.

## House style

The skill enforces an opinionated default for journal figures: plain frames, tick labels
only on the left and bottom edges, boxed uppercase panel labels, horizontal colorbars with
units, `vik` for diverging data and `inferno`/`roma` for sequential, and depth axes that
read positive downward. Override any of it when a target journal disagrees — the rules are
stated in one place at the top of `SKILL.md` precisely so they are easy to change.

One rule is worth calling out because violating it is subtle: when imaging dense fringe or
speckle data, the rendered panel must have at least as many pixels as the grid has columns
(`panel_cm × dpi / 2.54 ≥ n_columns`). Undersampled fringes alias into moiré ripples that
look like real signal.

## Requirements

PyGMT ≥ 0.13 (developed and verified against 0.17.0) and GMT ≥ 6.4 (verified against 6.6.0).
Install via conda-forge, which is the only reliable way to keep the GMT C library and the
Python wrapper in sync:

```bash
conda install -c conda-forge pygmt
```

## License

MIT — see [LICENSE](LICENSE).
