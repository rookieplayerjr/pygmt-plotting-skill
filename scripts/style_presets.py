"""Selectable visual styles for PyGMT figures.

Six presets grounded in GMT's built-in themes (classic/modern/minimal, see
`gmt.conf` GMT_THEME), the GMT China community conventions, and the house
publication style. Import next to the template scripts:

    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from style_presets import style, panel_label, colorbar, list_styles

    fig = pygmt.Figure()
    with style("dark"):                      # or "house" (default), "journal", ...
        fig.basemap(...)
        ...
        panel_label(fig, "A", style_name="dark")
        colorbar(fig, "LOS displacement (mm)", style_name="dark")

Every preset keeps the two house hard rules: tick labels only on W/S edges
(pass frame=["WSne", ...] yourself) and horizontal bottom colorbar via the
colorbar() helper. Depth axes must still read positive-down (see SKILL.md).
"""

import pygmt

# Each style: `config` -> pygmt.config keys; `label_font`/`label_box` -> panel
# label; `cbar` -> colorbar position template; `land`/`water`/`shore` ->
# suggested coast colors (per-call params, cannot live in gmt.conf).
STYLES = {
    # Default publication style (user's house rules). Plain thin frame,
    # compact Helvetica, boxed uppercase panel letters.
    "house": {
        "config": {
            "MAP_FRAME_TYPE": "plain",
            "MAP_FRAME_PEN": "1p,black",
            "FONT_ANNOT_PRIMARY": "9p,Helvetica,black",
            "FONT_LABEL": "10p,Helvetica,black",
            "FONT_TITLE": "12p,Helvetica-Bold,black",
            "MAP_TICK_PEN": "0.8p,black",
        },
        "label_font": "12p,Helvetica-Bold,black",
        "label_box": {"fill": "white", "pen": "0.8p,black"},
        "cbar": "JBC+w{w}c/0.4c+h+o0c/0.8c",
        "land": "gray90", "water": "white", "shore": "0.5p,black",
        "use": "default for all scientific figures",
    },
    # Two-column journal submission: same skeleton as house, one notch
    # smaller/thinner so an 8.5 cm single-column figure stays legible.
    "journal": {
        "config": {
            "MAP_FRAME_TYPE": "plain",
            "MAP_FRAME_PEN": "0.8p,black",
            "FONT_ANNOT_PRIMARY": "8p,Helvetica,black",
            "FONT_LABEL": "9p,Helvetica,black",
            "FONT_TITLE": "10p,Helvetica-Bold,black",
            "MAP_TICK_PEN": "0.6p,black",
            "MAP_TICK_LENGTH_PRIMARY": "3p/1.5p",
            "MAP_ANNOT_OFFSET_PRIMARY": "3p",
        },
        "label_font": "10p,Helvetica-Bold,black",
        "label_box": {"fill": "white", "pen": "0.6p,black"},
        "cbar": "JBC+w{w}c/0.3c+h+o0c/0.6c",
        "land": "gray92", "water": "white", "shore": "0.4p,black",
        "use": "final submission figures at true column width; export PDF",
    },
    # Traditional GMT look: fancy black/white ruled frame, classic-theme
    # fonts, ddd:mm:ss annotations. Matches GMT_THEME=classic defaults.
    "classic": {
        "config": {
            "MAP_FRAME_TYPE": "fancy",
            "MAP_FRAME_WIDTH": "5p",
            "FONT_ANNOT_PRIMARY": "12p,Helvetica,black",
            "FONT_LABEL": "14p,Helvetica,black",
            "FONT_TITLE": "18p,Helvetica-Bold,black",
            "FORMAT_GEO_MAP": "ddd:mm:ssF",
            "MAP_VECTOR_SHAPE": "0",
        },
        "label_font": "14p,Helvetica-Bold,black",
        "label_box": {"fill": "white", "pen": "0.8p,black"},
        "cbar": "JBC+w{w}c/0.5c+h+o0c/1.0c",
        "land": "burlywood", "water": "lightblue", "shore": "0.5p,black",
        "use": "classic cartographic look (theses, reports, wall maps)",
    },
    # GMT_THEME=minimal: plain frame, AvantGarde-Book, light gray grid.
    # Airy look for web pages and slide decks on white background.
    "minimal": {
        "config": {
            "MAP_FRAME_TYPE": "plain",
            "MAP_FRAME_PEN": "0.8p,gray30",
            "FONT_ANNOT_PRIMARY": "9p,AvantGarde-Book,gray20",
            "FONT_LABEL": "10p,AvantGarde-Book,gray20",
            "FONT_TITLE": "13p,AvantGarde-Book,gray10",
            "MAP_TICK_PEN": "0.6p,gray30",
            "MAP_GRID_PEN_PRIMARY": "0.25p,gray85",
        },
        "label_font": "12p,AvantGarde-Book,gray10",
        "label_box": {"fill": "white", "pen": "0.6p,gray50"},
        "cbar": "JBC+w{w}c/0.35c+h+o0c/0.8c",
        "land": "gray95", "water": "white", "shore": "0.4p,gray40",
        "use": "clean modern look; add g to frame for the light grid",
    },
    # Slides/talks: everything one-third bigger and thicker so it reads
    # from the back of the room.
    "presentation": {
        "config": {
            "MAP_FRAME_TYPE": "plain",
            "MAP_FRAME_PEN": "1.5p,black",
            "FONT_ANNOT_PRIMARY": "14p,Helvetica,black",
            "FONT_LABEL": "16p,Helvetica,black",
            "FONT_TITLE": "20p,Helvetica-Bold,black",
            "MAP_TICK_PEN": "1.2p,black",
            "MAP_TICK_LENGTH_PRIMARY": "6p/3p",
        },
        "label_font": "18p,Helvetica-Bold,black",
        "label_box": {"fill": "white", "pen": "1.2p,black"},
        "cbar": "JBC+w{w}c/0.6c+h+o0c/1.0c",
        "land": "gray90", "water": "white", "shore": "0.6p,black",
        "use": "conference slides; pair with thick data pens (>=1.5p)",
    },
    # Dark background for slide decks / posters on black. Only page,
    # frame, font, tick and grid colors change — never CPT extremes.
    "dark": {
        "config": {
            "MAP_FRAME_TYPE": "plain",
            "PS_PAGE_COLOR": "16/16/20",
            "MAP_FRAME_PEN": "1p,gray95",
            "FONT_ANNOT_PRIMARY": "11p,Helvetica,gray90",
            "FONT_LABEL": "12p,Helvetica,gray90",
            "FONT_TITLE": "14p,Helvetica-Bold,white",
            "MAP_TICK_PEN": "0.8p,gray90",
            "MAP_GRID_PEN_PRIMARY": "0.25p,gray40",
            "COLOR_NAN": "gray25",
        },
        "label_font": "13p,Helvetica-Bold,white",
        "label_box": {"fill": "gray15", "pen": "0.8p,gray80"},
        "cbar": "JBC+w{w}c/0.4c+h+o0c/0.8c",
        "land": "gray25", "water": "gray10", "shore": "0.5p,gray70",
        "use": "dark slide decks; bright CPTs (turbo, vik, batlow) read best",
    },
}


def list_styles():
    """Name -> one-line purpose, for quick discovery."""
    return {name: s["use"] for name, s in STYLES.items()}


def style(name="house", **overrides):
    """Context manager: `with style("dark"): fig.basemap(...)`.

    Extra pygmt.config keys can be passed as overrides, e.g.
    style("house", FORMAT_GEO_MAP="ddd.x").
    """
    cfg = dict(STYLES[name]["config"])
    cfg.update(overrides)
    return pygmt.config(**cfg)


def panel_label(fig, text, style_name="house", position="TL"):
    """House-rule panel letter: uppercase, boxed, no parentheses."""
    s = STYLES[style_name]
    fig.text(position=position, text=text, font=s["label_font"],
             justify=position, offset="j0.2c", no_clip=True,
             clearance="1.5p/1.5p", **s["label_box"])


def colorbar(fig, label, style_name="house", width=8, frame_extra=None, offset=None):
    """Horizontal bottom colorbar with unit label (house hard rule).

    offset (cm): vertical drop below the frame. Default comes from the style;
    RAISE it (>=1.4) when the panel above is Cartesian with an x-axis label —
    annotations + label stack deeper than a map frame and the bar overprints them.
    """
    s = STYLES[style_name]
    frame = [f"x+l{label}"]
    if frame_extra:
        frame += list(frame_extra)
    pos = s["cbar"].format(w=width)
    if offset is not None:
        head, _, _ = pos.rpartition("+o")
        pos = f"{head}+o0c/{offset}c"
    fig.colorbar(position=pos, frame=frame)


def coast_colors(style_name="house"):
    """Suggested per-call coast colors: dict(land=, water=, shorelines=)."""
    s = STYLES[style_name]
    return {"land": s["land"], "water": s["water"], "shorelines": s["shore"]}


if __name__ == "__main__":
    for k, v in list_styles().items():
        print(f"{k:13s} {v}")
