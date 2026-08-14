#!/usr/bin/env python
"""Programmatic QC gate for rendered figures. Not advice — assertions.

Called automatically at the end of every template (and usable standalone:
`python qc_check.py fig.png`). Raises/exits non-zero on failure, so a broken
figure can NOT be delivered silently. Checks are image-level and calibrated
against the skill's corpus of real passes and real failures:

  blank      most-common-color share of the interior. Catches "two dots on a
             white canvas" (a real shipped failure).
  hollow     content bounding box vs canvas. Catches half-empty layouts.
  flatline   color entropy. Catches single-color / dead renders.

Data-side guards (call from scripts before plotting):
  assert_real_field(arr, name)   finite fraction + variance sanity for grids.
"""
import sys

import numpy as np
from PIL import Image

# thresholds calibrated on the blind-test corpus (see CALIBRATION note below).
# Line-art figures (record sections, rose diagrams) are legitimately blank-heavy,
# so "near-empty" requires blank AND low entropy together.
BLANK_MAX = 0.90      # interior share of the single most common color ...
ENTROPY_NEAR = 0.95   # ... combined with entropy below this -> near-empty
ENTROPY_DEAD = 0.60   # entropy below this alone -> dead render
BBOX_MIN = 0.42       # content bbox area / canvas area


def _metrics(path):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im.resize((min(im.width, 900),
                              max(1, int(im.height * min(im.width, 900) / im.width)))))
    h, w = a.shape[:2]
    # interior = drop a 4% border frame (axes/annotations live there)
    bh, bw = max(2, h // 25), max(2, w // 25)
    core = a[bh:h - bh, bw:w - bw]
    q = (core // 24).astype(np.uint16)          # coarse color quantization
    key = q[..., 0] * 121 + q[..., 1] * 11 + q[..., 2]
    _, counts = np.unique(key, return_counts=True)
    blank = counts.max() / key.size
    # content bbox: pixels that differ from the canvas' modal color
    modal = np.bincount(key.ravel()).argmax()
    diff = key != modal
    ys, xs = np.where(diff)
    bbox = 0.0
    if ys.size:
        bbox = ((ys.max() - ys.min()) * (xs.max() - xs.min())) / key.size
    lum = (0.299 * core[..., 0] + 0.587 * core[..., 1] + 0.114 * core[..., 2])
    hist, _ = np.histogram(lum, bins=64, range=(0, 255))
    p = hist / hist.sum()
    p = p[p > 0]
    entropy = float(-(p * np.log2(p)).sum())
    return {"blank": float(blank), "bbox": float(bbox), "entropy": entropy}


def qc_image(path, strict=True):
    """Hard gate. Returns metrics dict on PASS; raises SystemExit on FAIL."""
    m = _metrics(path)
    fails = []
    if m["blank"] > BLANK_MAX and m["entropy"] < ENTROPY_NEAR:
        fails.append(f"near-empty: {m['blank']:.2f} one-color interior with "
                     f"entropy {m['entropy']:.2f} — almost nothing was drawn")
    if m["bbox"] < BBOX_MIN:
        fails.append(f"hollow: content bbox covers {m['bbox']:.2f} of the canvas "
                     f"(min {BBOX_MIN}) — layout mostly empty")
    if m["entropy"] < ENTROPY_DEAD:
        fails.append(f"dead: luminance entropy {m['entropy']:.2f} bits — flat render")
    tag = "QC-PASS" if not fails else "QC-FAIL"
    print(f"[{tag}] {path}  blank={m['blank']:.2f} bbox={m['bbox']:.2f} "
          f"entropy={m['entropy']:.2f}")
    if fails and strict:
        for f in fails:
            print("  -", f)
        print("  Figure NOT deliverable. Fix the layout/data and re-render.")
        raise SystemExit(1)
    return m


def assert_in_region(lon, lat, region, name="target", margin=0.05):
    """The resolved event/place MUST sit inside the map region (with margin as a
    fraction of the span). A real shipped failure framed the 2025 Dingri map
    half a degree south of the epicenter."""
    w, e, sth, nth = region[:4]
    mx, my = (e - w) * margin, (nth - sth) * margin
    if not (w + mx <= lon <= e - mx and sth + my <= lat <= nth - my):
        raise SystemExit(f"[QC-FAIL] {name} ({lon:.3f}, {lat:.3f}) is outside or on "
                         f"the edge of region {region[:4]} — re-center the region on "
                         "the resolved coordinates before rendering.")


def assert_real_field(arr, name="field"):
    """Grid sanity before plotting: enough finite data, non-constant."""
    a = np.asarray(arr, dtype=float)
    finite = np.isfinite(a)
    frac = finite.mean() if a.size else 0.0
    if frac < 0.02:
        raise SystemExit(f"[QC-FAIL] {name}: only {frac:.1%} finite values — "
                         "the dataset is empty; do NOT substitute synthetic data, "
                         "report the fetch/parse failure instead.")
    if finite.any() and np.nanstd(a) == 0:
        raise SystemExit(f"[QC-FAIL] {name}: constant field — likely a parse error.")


if __name__ == "__main__":
    ok = True
    for p in sys.argv[1:]:
        try:
            qc_image(p)
        except SystemExit:
            ok = False
    sys.exit(0 if ok else 1)

# CALIBRATION (2026-08, 20 real passes + shipped failures): passes span
# blank 0.17-0.91 / bbox 0.98-1.00 / entropy 1.03-5.5 (record sections are the
# legitimate blank-heavy extreme). Shipped blank-interferogram failure:
# blank 0.93 + entropy 0.79 -> caught by the combined rule. SCOPE: image checks
# catch EMPTY/BROKEN renders only; fabricated-but-rich figures are prevented at
# the data layer (assert_real_field + the synthetic-fallback ban in SKILL.md).
