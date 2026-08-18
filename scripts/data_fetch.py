#!/usr/bin/env python
"""USGS FDSN catalog fetch for the templates — so figure scripts never hand-roll
download/parse code (the step where runs historically died or fell back to
fabricated data).

    from data_fetch import usgs_catalog
    cat = usgs_catalog(region=[96, 98.5, 33.5, 35.5], minmag=2.5,
                       start="2021-05-21", end="2021-07-22")

Returns a DataFrame with lon/lat/depth/mag/time. Results are cached under
scripts/data/ so a repeated run is offline. On failure or an implausibly empty
result it STOPS with a clear message — fabricating a stand-in catalog is
banned (SKILL.md rule 8).
"""
import hashlib
import io
import os
import urllib.request

import pandas as pd

BASE = ("https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv"
        "&orderby=time-asc")
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def usgs_catalog(region, minmag=4.0, start="2000-01-01", end="2030-01-01",
                 min_expected=3, cache=True):
    """Fetch (or read cached) USGS events for [W, E, S, N] region."""
    w, e, s, n = region[:4]
    url = (f"{BASE}&starttime={start}&endtime={end}&minmagnitude={minmag}"
           f"&minlongitude={w}&maxlongitude={e}&minlatitude={s}&maxlatitude={n}")
    tag = hashlib.md5(url.encode()).hexdigest()[:10]
    path = os.path.join(CACHE_DIR, f"usgs_{tag}.csv")
    if cache and os.path.exists(path):
        cat = pd.read_csv(path, parse_dates=["time"])
    else:
        try:
            raw = urllib.request.urlopen(url, timeout=60).read().decode()
        except Exception as exc:
            raise SystemExit(
                f"[QC-FAIL] USGS fetch failed ({exc}). STOP and report this — "
                "do NOT substitute a synthetic catalog (SKILL.md rule 8).")
        d = pd.read_csv(io.StringIO(raw))
        if not {"longitude", "latitude", "depth", "mag"}.issubset(d.columns):
            raise SystemExit("[QC-FAIL] USGS response missing expected columns — "
                             "report the failure, do not fabricate data.")
        cat = d[["time", "longitude", "latitude", "depth", "mag"]].dropna()
        cat.columns = ["time", "lon", "lat", "depth", "mag"]
        cat["time"] = pd.to_datetime(cat.time.str[:19])
        if cache:
            os.makedirs(CACHE_DIR, exist_ok=True)
            cat.to_csv(path, index=False)
            cat = pd.read_csv(path, parse_dates=["time"])
    if len(cat) < min_expected:
        raise SystemExit(
            f"[QC-FAIL] only {len(cat)} events returned for {region[:4]} "
            f"M>={minmag} {start}..{end} — widen the query or report the gap; "
            "never pad with synthetic events.")
    print(f"[data] USGS catalog: {len(cat)} events "
          f"(M{cat.mag.min():.1f}-{cat.mag.max():.1f}, "
          f"depth {cat.depth.min():.0f}-{cat.depth.max():.0f} km)")
    return cat
