# World Happiness Analytics 🔄 Live

**Video walkthrough:** [60-second demo on LinkedIn](https://www.linkedin.com/feed/update/urn:li:ugcPost:7511301668160987137)

A data-analyst project answering one question: **which country-level
factors — wealth, social support, health, freedom — best explain national
happiness, and which regions are rising or falling?**

Built on the **real World Happiness Report, 2015–2025** (1,657 country-year
rows, 197 countries, 10 regions): correlation analysis, an OLS regression
that ranks the six happiness factors by effect size, regional trend lines,
and the biggest country climbers and fallers. Every number below comes from
a real run of `python/happiness_analysis.py`.

<!-- LIVE-STAMP -->
> 🔄 **This project is live.** Data is re-pulled automatically and every
> chart, KPI, and ranking refreshes whenever a new report lands.
> Last data pull: **2026-10-01** — covering **2015–2025**.

## Why, how, what

**Why** — every year the World Happiness Report ranks 150+ countries, but a
ranking alone doesn't tell a policymaker *what to fix*. If social support
moves happiness more than GDP, that changes where a country should invest.
And a one-off analysis goes stale — so this one updates itself.

**How** — (1) `data/pull_data.py` downloads the yearly WHR files
(2015 → latest available) and merges them into one panel. (2) Measure the
headline KPIs: global average, top/bottom countries, regional rankings.
(3) Correlate each of the six WHR explanatory factors with the ladder
score. (4) Fit an OLS regression on standardized factors to rank drivers
by effect size. (5) Track regional trajectories and flag the biggest
country-level climbers and fallers. (6) Reproduce every headline KPI in
SQL. (7) `update.sh` re-runs the whole pipeline whenever new data appears.

**What** — a self-updating happiness-analysis toolkit: live panel dataset,
one script that runs the full analysis, five charts, a SQL query pack
(`sql/queries.sql`) reproducing every headline KPI, and a written answer to
which factors matter most.

## Analytics type

| Type | How this project uses it |
|---|---|
| **Descriptive** (primary) | Rankings and trends: top/bottom countries, regional averages, the 2015–2025 trajectory of world happiness. |
| **Diagnostic** | Explains *why* happiness differs: correlations and the OLS regression rank the six factors by effect size. |
| **Predictive** | The regression model predicts a country's ladder score from its six factors (R² = 0.831) — the same equation scores any new country-year. |
| **Prescriptive** | Points *where to invest*: a 1-SD lift in social support (+0.464) moves happiness more than three times as much as a 1-SD lift in GDP (+0.137). |

## SQL analysis layer

Every headline KPI is also computed directly in SQL — the same aggregations
an analyst would run against a production country-statistics table.
[`sql/queries.sql`](sql/queries.sql) (MySQL 8 compatible) reproduces, all exact.
The queries use `MAX(year)` / `MIN(year)` instead of hardcoded years, so they
keep returning the right answer as new yearly data arrives:

- **global average ladder (2025)** — 5.578 across 147 countries
- **top 10 countries** — Finland 7.736, Denmark 7.521, Iceland 7.515
- **bottom 5 countries** — Afghanistan 1.364, Sierra Leone 2.998, Lebanon 3.188
- **avg ladder by region** — Australia and New Zealand 6.963 (best) → Southern Asia 3.929 (worst)
- **avg ladder by GDP quartile** — Q1 (poorest) 4.365 · Q2 5.265 · Q3 5.958 · Q4 (richest) 6.757
- **biggest climber / faller 2015→2025** — Serbia +1.483, Afghanistan -2.211
- **YoY global trend** — 2015 5.376 → 2025 5.578 (slowly up, +0.202)

SQL handles the extraction, aggregation, and KPI computation; Python handles
the statistical modelling (correlations, OLS regression), charts, and the
written findings.

## Dataset

`data/happiness.csv` — 1,657 rows (197 countries × 2015–2025), built by
`data/pull_data.py` from the yearly World Happiness Report files.
Source: World Happiness Report yearly releases (via public mirror;
see `data/pull_data.py` for the URL).

| Column | Description |
|---|---|
| country | Country name |
| region | 10 WHR regions (Western Europe, North America, Latin America and Caribbean, Middle East and Northern Africa, Sub-Saharan Africa, Southern Asia, Eastern Asia, Southeastern Asia, Central and Eastern Europe, Australia and New Zealand) |
| year | 2015–2025 (grows as new reports are pulled) |
| ladder_score | Cantril ladder happiness score (0–10) |
| gdp | Economy: GDP per capita (WHR explanatory component) |
| social_support | Social support (WHR explanatory component) |
| health | Health / life expectancy (WHR explanatory component) |
| freedom | Freedom to make life choices (WHR explanatory component) |
| generosity | Generosity (WHR explanatory component) |
| trust | Trust in government — higher = cleaner institutions (WHR explanatory component) |

> The six factors are the WHR's own explanatory components — their modelled
> contribution to each country's ladder score. A high regression R² is
> therefore expected; the insight is in the *relative* weights.

## Results

All figures are the actual output of `python/happiness_analysis.py` on the
2026-10-01 data pull:

**Headline:** global average ladder score **5.578** in 2025 (147 countries,
10 regions) — up +0.202 since 2015 (5.376): the world is slowly getting
happier.

| Rank | Country | Region | Ladder |
|---|---|---|---|
| 1 | **Finland** | Western Europe | **7.736** |
| 2 | Denmark | Western Europe | 7.521 |
| 3 | Iceland | Western Europe | 7.515 |
| 4 | Sweden | Western Europe | 7.345 |
| 5 | Netherlands | Western Europe | 7.306 |
| … | | | |
| 143 | Zimbabwe | Sub-Saharan Africa | 3.396 |
| 144 | Malawi | Sub-Saharan Africa | 3.260 |
| 145 | Lebanon | Middle East and Northern Africa | 3.188 |
| 146 | Sierra Leone | Sub-Saharan Africa | 2.998 |
| 147 | **Afghanistan** | Southern Asia | **1.364** |

| Region | Avg ladder 2025 |
|---|---|
| Australia and New Zealand | **6.963** |
| Western Europe | 6.818 |
| North America | 6.764 |
| Latin America and Caribbean | 6.271 |
| Eastern Asia | 6.017 |
| Central and Eastern Europe | 6.002 |
| Southeastern Asia | 5.642 |
| Middle East and Northern Africa | 5.278 |
| Sub-Saharan Africa | 4.360 |
| Southern Asia | **3.929** |

- **Correlations with ladder (all years):** GDP component **0.712** ·
  health 0.679 · social support 0.667 · freedom 0.521 ·
  trust (low corruption) 0.417 · generosity 0.071 (essentially none).
- **OLS regression (standardized, n = 147, 2025):** **R² = 0.831**. Effect
  of a +1 SD move in each factor: social support **+0.464** · freedom
  **+0.278** · health +0.205 · GDP component +0.137 · trust +0.094 ·
  generosity -0.025. **Social support is the strongest driver** — more than
  three times the effect of GDP per SD. Money matters, but belonging
  matters more.
- **Wealth vs happiness:** GDP–ladder Pearson r = 0.763 in 2025, but the
  scatter shows wide vertical spread at every income level — money explains
  a lot, not everything.
- **Regional trajectories 2015→2025:** Central and Eastern Europe rose most
  (**+0.669**); Southern Asia fell most (**-0.652**, driven by Afghanistan).
  North America fell notably too (-0.509).
- **Biggest climbers:** Serbia **+1.483** · Togo +1.476 · Ivory Coast
  +1.447 · Romania +1.439 · Bulgaria +1.336.
- **Biggest fallers:** Afghanistan **-2.211** · Lebanon -1.651 ·
  Sierra Leone -1.509 · Zambia -1.217 · Zimbabwe -1.214.
- **GDP quartiles:** poorest-quartile countries average 4.365 vs 6.757 for
  the richest — a 2.39-point happiness gap by wealth.

### What a policymaker should take away (prescriptive)

1. **Social support is the high-ROI lever** — the largest effect per SD
   (+0.464), and community is cheaper to build than GDP.
2. **Freedom matters more than income here** (+0.278 vs +0.137): agency
   over one's life shows up strongly in ladder scores.
3. **Health buys happiness** (+0.205 per SD): life-expectancy gains show up
   directly in scores.
4. **Clean institutions help** (+0.094): lower corruption lifts scores even
   at fixed income.
5. **Generosity barely registers** (-0.025) — don't build a national
   strategy on it.

## How the live update works

```
data/pull_data.py   → downloads yearly WHR CSVs (2015 → newest available),
                      merges them into data/happiness.csv,
                      writes data/LAST_UPDATED.txt, prints CHANGED/UNCHANGED
python/happiness_analysis.py → re-runs every KPI, chart, and the summary
update.sh           → pull → if CHANGED: re-run analysis, refresh the
                      README timestamp, commit, and push
```

A scheduled check runs monthly: if a new yearly report has landed, the
pipeline refreshes everything and pushes the update — charts, README
numbers, and SQL results all move together. The SQL queries use
`MAX(year)`/`MIN(year)`, so they never need editing when new data arrives.

## Charts

| File | Shows |
|---|---|
| `images/top10_bar.png` | Top 10 happiest countries, latest year |
| `images/correlation_heatmap.png` | Correlation matrix: six factors vs ladder |
| `images/gdp_vs_ladder_scatter.png` | GDP component vs ladder by region, with trend line |
| `images/regional_trends.png` | Regional average ladder, 2015–2025 |
| `images/climbers_fallers.png` | Biggest country climbers and fallers, 2015–2025 |

All charts render in the portfolio dark theme (near-black `#121212`, neon-lime `#6fff54` accent, rust `#c96a5e` for negatives) to match [the author's site](https://sheikh-ahmad-am.github.io/portfolio/).

## Methods

- **Panel EDA** — global average, rankings, regional means, YoY trend.
- **Pearson correlations** — each factor vs ladder across all 1,657 rows.
- **OLS regression** (`sklearn.linear_model.LinearRegression`) on
  standardized factors; standardized coefficients rank drivers by effect
  size; R² measures explanatory power.
- **Regional panel trends** — yearly regional means; first→latest change
  flags risers and fallers.
- **Country movers** — per-country ladder change first→latest year via pivot.
- **GDP quartiles** — `NTILE(4)` over the GDP component (MySQL 8), the
  classic wealth-vs-outcome cut.

## Tech stack

Python 3.12 · pandas · NumPy · matplotlib · seaborn · scikit-learn
(LinearRegression) · MySQL 8 (verification queries)

## How to run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Pull the latest WHR data (2015 -> newest available -> data/happiness.csv)
cd data
python3 pull_data.py

# 3. Run the full analysis, print results, save charts + results_summary.txt
cd ../python
python3 happiness_analysis.py

# 4. (Optional) Verify headline KPIs in MySQL Workbench with sql/queries.sql

# Or do it all at once whenever new data may exist:
./update.sh
```

## Project structure

```
effective-happiness/
├── data/
│   ├── pull_data.py        # downloads yearly WHR CSVs, builds happiness.csv
│   ├── happiness.csv       # merged panel (1,657 rows, 2015-2025)
│   └── LAST_UPDATED.txt    # last pull timestamp + content hash
├── python/
│   └── happiness_analysis.py  # full analysis + charts + summary
├── sql/
│   └── queries.sql         # MySQL 8 queries reproducing every KPI
├── images/                 # 5 charts (regenerated each run)
├── update.sh               # pull → re-run → stamp README → commit → push
├── results_summary.txt     # headline numbers from the latest run
├── requirements.txt
└── README.md
```

## Limitations

- The WHR explanatory components are model-based, not raw survey
  measures — the regression decomposes the WHR's own model, it doesn't
  independently discover these drivers.
- The OLS model is associational, not causal: happier countries differ on
  many unmeasured dimensions.
- Source data comes from a public mirror of the WHR releases; if the
  mirror moves, `BASE_URL` in `pull_data.py` needs updating.
- Year coverage depends on the source repo being updated with each new
  annual report.
