#!/usr/bin/env python
"""Frame/inset helpers for the '-B cannot say axis-without-ticks' family of traps
(GOTCHAS 8.14/8.15/8.16, pixel-verified on the Venezuela Figure 1 rebuild).

Usage:
    from frame_helpers import sides_WS, close_box, mercator_height

    fig.basemap(..., frame=sides_WS(["WSne", "xaf", "yaf"]))  # annotate W/S only,
    ...                                                        # NO top/right ticks
    close_box(fig)            # after ALL panel content: 4-side axis, zero ticks
"""
import numpy as np
import pygmt


def sides_WS(frame):
    """Strip top/right side letters from a frame list.

    GMT -B side letters: UPPER = axis+ticks+annotations, lower = axis+ticks
    (annotations off, ticks STILL drawn); absent = nothing. There is no
    "axis line without ticks" spelling — so drop n/e entirely here and add
    the box back later with close_box().
    """
    f = list(frame)
    f[0] = "".join(c for c in f[0] if c not in "neNE")
    return f


def close_box(fig, pen="1p,black"):
    """Redraw all four axis lines with zero-length ticks (no annotations).

    MUST run AFTER every content layer of the panel/inset: coast land fill or
    grdimage painted to the region edge overpaints the inner half of any
    earlier border (GOTCHAS 8.15 — measured 5 px -> 2 px at 300 dpi).
    Inherits the current region/projection.
    """
    with pygmt.config(MAP_TICK_LENGTH_PRIMARY="0p",
                      MAP_FRAME_PEN=pen, MAP_FRAME_TYPE="plain"):
        fig.basemap(frame=["wsne"])


def mercator_height(width_cm, region):
    """True Mercator panel height for a region at a given width.

    Use for inset +w<W>c/<H>c — a hard-coded height that is short by even
    0.1 cm lets the map spill below the white box (GOTCHAS 8.16).
    """
    w, e, s, n = region[:4]
    y = lambda p: np.degrees(np.log(np.tan(np.radians(45 + p / 2))))
    return width_cm * (y(n) - y(s)) / (e - w)
