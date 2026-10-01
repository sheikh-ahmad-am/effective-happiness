"""World Happiness Analytics — synthetic panel data generator.

Produces data/happiness.csv: ~150 countries x 6 years (2019-2024) with
World-Happiness-Report-style columns. Seeded RNG (seed=42) -> fully
reproducible. Ladder scores are constructed from the six factors so that
correlations with GDP / social support / health hold BY CONSTRUCTION.

Calibrated roughly to real WHR ranges (Nordics ~7.5-7.8 top,
Afghanistan ~1.8 bottom). All data is synthetic.
"""

import numpy as np
import pandas as pd

SEED = 42
YEARS = list(range(2019, 2025))
rng = np.random.default_rng(SEED)

# (country, anchor_offset_on_ladder) — anchors keep headline rankings sane.
REGIONS = {
    "Western Europe": {
        "trend": 0.015,
        "factors": dict(log_gdp=10.8, social=0.92, hle=72.5, freedom=0.88,
                        generosity=0.30, corruption=0.30),
        "countries": ["Finland", "Denmark", "Iceland", "Sweden", "Netherlands",
                      "Norway", "Switzerland", "Luxembourg", "Austria",
                      "Ireland", "Germany", "Belgium", "United Kingdom",
                      "France", "Spain", "Italy", "Portugal", "Greece",
                      "Malta", "Cyprus"],
        "anchors": {"Finland": 0.56, "Denmark": 0.50, "Iceland": 0.28,
                    "Sweden": 0.17, "Netherlands": 0.17, "Norway": 0.21,
                    "Greece": -0.39},
    },
    "North America": {
        "trend": -0.010,
        "factors": dict(log_gdp=11.0, social=0.90, hle=71.0, freedom=0.85,
                        generosity=0.40, corruption=0.35),
        "countries": ["Canada", "United States"],
        "anchors": {"Canada": 0.07, "United States": -0.1},
    },
    "Latin America": {
        "trend": -0.045,
        "factors": dict(log_gdp=9.4, social=0.82, hle=68.0, freedom=0.75,
                        generosity=0.20, corruption=0.65),
        "countries": ["Costa Rica", "Mexico", "Uruguay", "Chile", "Panama",
                      "Brazil", "Argentina", "Colombia", "Peru", "Ecuador",
                      "Bolivia", "Paraguay", "Guatemala", "Honduras",
                      "El Salvador", "Nicaragua", "Dominican Republic",
                      "Jamaica", "Trinidad and Tobago", "Haiti", "Cuba",
                      "Bahamas", "Barbados", "Belize", "Guyana", "Suriname",
                      "Grenada"],
        "anchors": {"Costa Rica": 0.32, "Haiti": -0.56, "Venezuela": 0.0},
    },
    "Middle East": {
        "trend": 0.020,
        "factors": dict(log_gdp=10.0, social=0.80, hle=69.0, freedom=0.60,
                        generosity=0.15, corruption=0.60),
        "countries": ["Israel", "United Arab Emirates", "Saudi Arabia",
                      "Qatar", "Kuwait", "Bahrain", "Oman", "Jordan",
                      "Lebanon", "Turkey", "Iran", "Iraq", "Yemen", "Syria"],
        "anchors": {"Israel": 0.24, "Lebanon": -0.91, "Yemen": -0.77,
                    "Syria": -0.63},
    },
    "Sub-Saharan Africa": {
        "trend": 0.005,
        "factors": dict(log_gdp=8.0, social=0.70, hle=58.0, freedom=0.65,
                        generosity=0.25, corruption=0.70),
        "countries": ["Mauritius", "South Africa", "Ghana", "Nigeria",
                      "Kenya", "Ethiopia", "Tanzania", "Uganda", "Rwanda",
                      "Senegal", "Ivory Coast", "Cameroon", "DR Congo",
                      "Zambia", "Zimbabwe", "Mozambique", "Angola", "Sudan",
                      "Chad", "Niger", "Mali", "Burkina Faso", "Somalia",
                      "Madagascar", "Malawi", "Botswana", "Namibia", "Gabon",
                      "Congo", "Sierra Leone", "Benin", "Togo", "Guinea",
                      "Liberia", "Mauritania", "Burundi", "Djibouti",
                      "Eritrea", "Lesotho", "Eswatini", "Comoros",
                      "Seychelles", "Cabo Verde", "Gambia",
                      "Central African Republic", "South Sudan"],
        "anchors": {"Mauritius": 0.39, "Rwanda": 0.1, "Somalia": -0.24,
                    "South Sudan": -0.49, "Central African Republic": -0.42},
    },
    "South Asia": {
        "trend": 0.010,
        "factors": dict(log_gdp=8.3, social=0.68, hle=64.0, freedom=0.65,
                        generosity=0.25, corruption=0.68),
        "countries": ["India", "Pakistan", "Bangladesh", "Nepal",
                      "Sri Lanka", "Bhutan", "Maldives", "Afghanistan"],
        "anchors": {"Bhutan": 0.39, "Afghanistan": -1.90, "India": -0.07},
    },
    "East Asia": {
        "trend": 0.030,
        "factors": dict(log_gdp=10.0, social=0.85, hle=72.0, freedom=0.65,
                        generosity=0.10, corruption=0.55),
        "countries": ["Singapore", "Japan", "South Korea", "Taiwan", "China",
                      "Hong Kong", "Mongolia", "Thailand", "Vietnam",
                      "Philippines", "Indonesia", "Malaysia", "Cambodia",
                      "Laos", "Myanmar", "Brunei", "Timor-Leste"],
        "anchors": {"Singapore": 0.21, "Myanmar": -0.35},
    },
    "Central/Eastern Europe": {
        "trend": 0.055,
        "factors": dict(log_gdp=9.8, social=0.85, hle=69.0, freedom=0.70,
                        generosity=0.15, corruption=0.65),
        "countries": ["Czechia", "Slovenia", "Estonia", "Lithuania",
                      "Latvia", "Poland", "Slovakia", "Hungary", "Romania",
                      "Bulgaria", "Croatia", "Serbia", "Bosnia and Herzegovina",
                      "Albania", "North Macedonia", "Montenegro", "Moldova",
                      "Ukraine", "Belarus", "Georgia", "Armenia",
                      "Azerbaijan", "Kazakhstan", "Kyrgyzstan", "Uzbekistan"],
        "anchors": {"Czechia": 0.21, "Ukraine": -0.32},
    },
}

# Ladder construction weights (standardized-factor space) — by construction
# GDP, social support and health dominate the ladder score.
W = dict(log_gdp=0.34, social=0.30, hle=0.24, freedom=0.18,
         generosity=0.08, corruption=-0.14)
LADDER_MEAN, LADDER_SD = 5.30, 1.00

rows = []
for region, spec in REGIONS.items():
    f = spec["factors"]
    for country in spec["countries"]:
        anchor = spec["anchors"].get(country, 0.0)
        # Stable country-level factor baselines (fixed effects).
        c_log_gdp = rng.normal(f["log_gdp"], 0.55)
        c_social = np.clip(rng.normal(f["social"], 0.07), 0.25, 1.0)
        c_hle = np.clip(rng.normal(f["hle"], 3.2), 48.0, 78.0)
        c_freedom = np.clip(rng.normal(f["freedom"], 0.09), 0.15, 1.0)
        c_gener = np.clip(rng.normal(f["generosity"], 0.09), 0.0, 0.9)
        c_corrupt = np.clip(rng.normal(f["corruption"], 0.10), 0.05, 0.95)
        # Random-walk drift so 2019->2024 movers emerge naturally.
        drift = rng.normal(0, 0.05)
        for yi, year in enumerate(YEARS):
            t = yi  # 0..5
            log_gdp = c_log_gdp + rng.normal(0, 0.05) + 0.012 * t
            social = np.clip(c_social + rng.normal(0, 0.015), 0.25, 1.0)
            hle = np.clip(c_hle + rng.normal(0, 0.25) + 0.08 * t, 48.0, 78.0)
            freedom = np.clip(c_freedom + rng.normal(0, 0.02), 0.15, 1.0)
            gener = np.clip(c_gener + rng.normal(0, 0.02), 0.0, 0.9)
            corrupt = np.clip(c_corrupt + rng.normal(0, 0.02), 0.05, 0.95)
            rows.append(dict(
                country=country, region=region, year=year,
                log_gdp_per_capita=round(log_gdp, 3),
                social_support=round(social, 3),
                healthy_life_expectancy=round(hle, 1),
                freedom=round(freedom, 3),
                generosity=round(gener, 3),
                corruption_perception=round(corrupt, 3),
                _drift=drift, _trend=spec["trend"], _anchor=anchor, _t=t,
            ))

df = pd.DataFrame(rows)

# --- ladder score from standardized factors (computed globally) -----------
z = lambda s: (s - s.mean()) / s.std(ddof=0)
ladder_raw = (W["log_gdp"] * z(df["log_gdp_per_capita"])
              + W["social"] * z(df["social_support"])
              + W["hle"] * z(df["healthy_life_expectancy"])
              + W["freedom"] * z(df["freedom"])
              + W["generosity"] * z(df["generosity"])
              + W["corruption"] * z(df["corruption_perception"]))
ladder = (LADDER_MEAN + LADDER_SD * ladder_raw
          + df["_anchor"]
          + df["_trend"] * df["_t"]          # regional rise/fall over 2019-2024
          + df["_drift"] * df["_t"]          # country random walk
          + rng.normal(0, 0.22, len(df)))    # noise
df["ladder_score"] = ladder.clip(1.0, 8.4).round(3)
df = df.drop(columns=["_drift", "_trend", "_anchor", "_t"])

df = df[["country", "region", "year", "ladder_score", "log_gdp_per_capita",
         "social_support", "healthy_life_expectancy", "freedom",
         "generosity", "corruption_perception"]]
df.to_csv("happiness.csv", index=False)
print(f"wrote happiness.csv: {len(df)} rows "
      f"({df['country'].nunique()} countries x {df['year'].nunique()} years)")
print(df[df.year == 2024].nlargest(3, "ladder_score")
      [["country", "ladder_score"]].to_string(index=False))
print(df[df.year == 2024].nsmallest(3, "ladder_score")
      [["country", "ladder_score"]].to_string(index=False))
