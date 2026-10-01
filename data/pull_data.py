"""Pull real World Happiness Report data and build data/happiness.csv.

Downloads the yearly WHR CSVs (2015 -> latest available) from a public
mirror, normalizes columns to one schema, and writes the merged panel.
Probes future years too, so when a new report lands the next run picks it
up automatically — that is what makes this project "live".

Usage:
    cd data && python3 pull_data.py
Prints CHANGED or UNCHANGED (based on content hash) and writes
data/LAST_UPDATED.txt with the refresh timestamp.

Schema written to happiness.csv:
    country, region, year, ladder_score, gdp, social_support,
    health, freedom, generosity, trust
where gdp/social_support/health/freedom/generosity/trust are the WHR
explanatory components (their modelled contribution to the ladder score),
and `trust` = Trust (Government Corruption): higher = cleaner institutions.
"""

import hashlib
import sys
import urllib.request
from datetime import datetime, timezone
from io import StringIO

import pandas as pd

BASE_URL = ("https://raw.githubusercontent.com/3112aastikg/"
            "Minor-Project-World-Happiness-Report-Analysis/main/{year}.csv")
# Fallback mirror tried if the primary fails for a given year.
FALLBACK_URL = None  # add a second mirror here if one is ever needed

COLUMN_MAP = {
    "Country": "country",
    "Region": "region",
    "Happiness Score": "ladder_score",
    "Economy (GDP per Capita)": "gdp",
    "Social Support": "social_support",
    "Health (Life Expectancy)": "health",
    "Freedom": "freedom",
    "Generosity": "generosity",
    "Trust (Government Corruption)": "trust",
}
KEEP = list(COLUMN_MAP.values())


def fetch(year):
    last_err = None
    for url in [u for u in (BASE_URL.format(year=year),
                            FALLBACK_URL.format(year=year) if FALLBACK_URL else None)
                if u]:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                if r.status == 200:
                    return r.read().decode("utf-8-sig")
        except Exception as e:  # noqa: BLE001 - try next mirror
            last_err = e
    if last_err:
        print(f"  year {year}: unavailable ({last_err})", file=sys.stderr)
    return None


def main():
    frames = []
    # Probe 2015..2030; keep every year that returns a valid CSV.
    for year in range(2015, 2031):
        raw = fetch(year)
        if raw is None:
            continue
        df = pd.read_csv(StringIO(raw))
        missing = [c for c in COLUMN_MAP if c not in df.columns]
        if missing:
            print(f"  year {year}: unexpected columns, skipped (missing {missing})",
                  file=sys.stderr)
            continue
        df = df.rename(columns=COLUMN_MAP)[KEEP]
        df["year"] = year
        # normalize text fields
        df["country"] = df["country"].astype(str).str.strip()
        df["region"] = df["region"].astype(str).str.strip()
        frames.append(df)
        print(f"  year {year}: {len(df)} countries")

    if not frames:
        print("ERROR: no yearly files could be downloaded.", file=sys.stderr)
        sys.exit(1)

    panel = pd.concat(frames, ignore_index=True)
    panel = panel.dropna(subset=["ladder_score"])
    panel = panel.sort_values(["year", "country"]).reset_index(drop=True)

    csv_bytes = panel.to_csv(index=False).encode("utf-8")
    new_hash = hashlib.sha256(csv_bytes).hexdigest()[:16]

    changed = True
    try:
        with open("happiness.csv", "rb") as f:
            old_hash = hashlib.sha256(f.read()).hexdigest()[:16]
        changed = old_hash != new_hash
    except FileNotFoundError:
        pass

    with open("happiness.csv", "wb") as f:
        f.write(csv_bytes)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    with open("LAST_UPDATED.txt", "w") as f:
        f.write(f"last_data_pull: {stamp}\n"
                f"years: {panel['year'].min()}-{panel['year'].max()}\n"
                f"rows: {len(panel)}\n"
                f"content_hash: {new_hash}\n"
                f"source: {BASE_URL.format(year='{YYYY}')}\n")

    yrs = sorted(panel["year"].unique())
    print(f"years {yrs[0]}-{yrs[-1]} | {len(panel)} rows | "
          f"{panel['country'].nunique()} countries | {panel['region'].nunique()} regions")
    print("CHANGED" if changed else "UNCHANGED")
    sys.exit(0)


if __name__ == "__main__":
    main()
