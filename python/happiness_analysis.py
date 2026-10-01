"""World Happiness Analytics — full analysis (REAL DATA edition).

Reads data/happiness.csv (built by data/pull_data.py from the yearly World
Happiness Report CSVs), runs the analysis, saves charts to images/, and
writes results_summary.txt with every headline number (used for the README).

Sections: headline KPIs -> correlations -> OLS regression -> GDP scatter ->
regional trends -> climbers & fallers -> SQL cross-check values.

The six factors are the WHR's explanatory components (each factor's modelled
contribution to the ladder score), so a high regression R^2 is expected —
the interesting part is the *relative* weight of each driver.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression

sns.set_theme(style="whitegrid")

df = pd.read_csv("../data/happiness.csv")
LATEST = int(df["year"].max())
BASE = int(df["year"].min())
FACTORS = ["gdp", "social_support", "health", "freedom", "generosity", "trust"]
FACTOR_LABELS = {"gdp": "GDP component",
                 "social_support": "social support",
                 "health": "health",
                 "freedom": "freedom",
                 "generosity": "generosity",
                 "trust": "trust (low corruption)"}
dL = df[df["year"] == LATEST].copy()

out = []
def log(line=""):
    print(line)
    out.append(line)

# ================================================== 1. Headline KPIs ===
log(f"=== Headline KPIs ({LATEST}) ===")
global_avg = dL["ladder_score"].mean()
log(f"Global average ladder score ({LATEST}): {global_avg:.3f}")
log(f"Countries: {dL['country'].nunique()} | Regions: {dL['region'].nunique()}")

top10 = dL.nlargest(10, "ladder_score")[["country", "region", "ladder_score"]]
log("\nTop 10 countries:")
log(top10.to_string(index=False))
bottom5 = dL.nsmallest(5, "ladder_score")[["country", "region", "ladder_score"]]
log("\nBottom 5 countries:")
log(bottom5.to_string(index=False))

region_avg = dL.groupby("region")["ladder_score"].mean().sort_values(ascending=False)
log(f"\nAverage ladder by region ({LATEST}):")
log(region_avg.round(3).to_string())
log(f"\nBest region: {region_avg.index[0]} ({region_avg.iloc[0]:.3f})")
log(f"Worst region: {region_avg.index[-1]} ({region_avg.iloc[-1]:.3f})")

fig, ax = plt.subplots(figsize=(10, 6))
t10 = top10.iloc[::-1]
ax.barh(t10["country"], t10["ladder_score"], color="#2a7f62")
ax.set_xlabel("Ladder score (0-10)")
ax.set_title(f"Top 10 happiest countries ({LATEST})")
for i, v in enumerate(t10["ladder_score"]):
    ax.text(v + 0.03, i, f"{v:.2f}", va="center", fontsize=9)
ax.set_xlim(0, t10["ladder_score"].max() * 1.12)
plt.tight_layout(); plt.savefig("../images/top10_bar.png", dpi=120); plt.close()

# ================================================= 2. Correlations ===
log("\n=== Correlations with ladder score (all years) ===")
corr = df[FACTORS + ["ladder_score"]].corr()["ladder_score"].drop("ladder_score")
log(corr.round(3).to_string())

fig, ax = plt.subplots(figsize=(9, 7))
cm = df[FACTORS + ["ladder_score"]].corr()
sns.heatmap(cm, annot=True, fmt=".2f", cmap="RdYlGn", vmin=-0.6, vmax=1.0,
            square=True, ax=ax, cbar_kws={"label": "Pearson r"})
ax.set_title("Correlation matrix: happiness factors vs ladder score")
ax.set_xticklabels([FACTOR_LABELS.get(c, c) for c in cm.columns], rotation=30, ha="right")
ax.set_yticklabels([FACTOR_LABELS.get(c, c) for c in cm.index], rotation=0)
plt.tight_layout(); plt.savefig("../images/correlation_heatmap.png", dpi=120); plt.close()

# =========================================== 3. OLS regression ===
log(f"\n=== OLS regression: ladder ~ 6 factors (standardized, {LATEST}) ===")
X = dL[FACTORS].values
y = dL["ladder_score"].values
Xz = (X - X.mean(0)) / X.std(0, ddof=0)
yz = (y - y.mean()) / y.std(ddof=0)
model = LinearRegression().fit(Xz, yz)
r2 = model.score(Xz, yz)
std_coefs = pd.Series(model.coef_, index=FACTORS).sort_values(ascending=False,
    key=lambda s: s.abs())
log(f"R² = {r2:.3f}  (n = {len(dL)} countries, {LATEST})")
log("Standardized coefficients (|coef| = effect of +1 SD in factor):")
for f, c in std_coefs.items():
    log(f"  {FACTOR_LABELS[f]:24s} {c:+.3f}")
top_factor = std_coefs.index[0]
log(f"Strongest driver: {FACTOR_LABELS[top_factor]} ({std_coefs.iloc[0]:+.3f})")

# ====================================== 4. GDP vs ladder scatter ===
log("\n=== GDP component vs ladder ===")
fig, ax = plt.subplots(figsize=(10, 6))
regions = sorted(dL["region"].unique())
palette = dict(zip(regions, sns.color_palette("tab10", len(regions))))
for r in regions:
    sub = dL[dL["region"] == r]
    ax.scatter(sub["gdp"], sub["ladder_score"], s=28,
               label=r, color=palette[r], alpha=0.8, edgecolor="white",
               linewidth=0.4)
xs = np.linspace(dL["gdp"].min(), dL["gdp"].max(), 100)
b, a = np.polyfit(dL["gdp"], dL["ladder_score"], 1)
ax.plot(xs, a + b * xs, color="black", lw=1.6, ls="--",
        label=f"trend (slope {b:.2f})")
ax.set_xlabel("GDP component (WHR explanatory contribution)")
ax.set_ylabel("Ladder score (0-10)")
ax.set_title(f"Wealth vs happiness ({LATEST}) — one dot per country")
ax.legend(fontsize=8, loc="upper left", ncol=2)
plt.tight_layout(); plt.savefig("../images/gdp_vs_ladder_scatter.png", dpi=120); plt.close()
log(f"GDP-ladder Pearson r = {dL['gdp'].corr(dL['ladder_score']):.3f}")

# ========================================= 5. Regional trends ===
log(f"\n=== Regional trends {BASE}-{LATEST} ===")
trend = df.groupby(["region", "year"])["ladder_score"].mean().unstack("year")
change = (trend[LATEST] - trend[BASE]).sort_values(ascending=False)
log(f"Change in regional avg ladder, {BASE} -> {LATEST}:")
log(change.round(3).to_string())
log(f"\nBiggest riser: {change.index[0]} ({change.iloc[0]:+.3f})")
log(f"Biggest faller: {change.index[-1]} ({change.iloc[-1]:+.3f})")

fig, ax = plt.subplots(figsize=(10, 6))
for r in trend.index:
    ax.plot(trend.columns, trend.loc[r], marker="o", ms=4, label=r,
            color=palette.get(r, "gray"), lw=2)
ax.set_xlabel("Year"); ax.set_ylabel("Average ladder score")
ax.set_title(f"Happiness trends by region, {BASE}-{LATEST}")
ax.legend(fontsize=8, loc="center left", bbox_to_anchor=(1, 0.5))
plt.tight_layout(); plt.savefig("../images/regional_trends.png", dpi=120); plt.close()

# ==================================== 6. Climbers & fallers ===
log(f"\n=== Biggest climbers & fallers ({BASE} -> {LATEST}) ===")
piv = df.pivot_table(index=["country", "region"], columns="year",
                     values="ladder_score")
piv = piv.dropna(subset=[BASE, LATEST])
piv["change"] = piv[LATEST] - piv[BASE]
piv = piv.reset_index()
climbers = piv.nlargest(5, "change")
fallers = piv.nsmallest(5, "change")
log("Top 5 climbers:")
log(climbers[["country", "region", "change"]].to_string(index=False,
    formatters={"change": "{:+.3f}".format}))
log("\nTop 5 fallers:")
log(fallers[["country", "region", "change"]].to_string(index=False,
    formatters={"change": "{:+.3f}".format}))
biggest_climber = (climbers.iloc[0]["country"], climbers.iloc[0]["change"])
biggest_faller = (fallers.iloc[0]["country"], fallers.iloc[0]["change"])

fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=False)
c5 = climbers.iloc[::-1]
axes[0].barh(c5["country"], c5["change"], color="#2a7f62")
axes[0].set_title(f"Biggest climbers {BASE}-{LATEST}")
axes[0].set_xlabel("Ladder change")
f5 = fallers.iloc[::-1]
axes[1].barh(f5["country"], f5["change"], color="#b03a2e")
axes[1].set_title(f"Biggest fallers {BASE}-{LATEST}")
axes[1].set_xlabel("Ladder change")
for axi in axes:
    for i, v in enumerate(axi.patches):
        w = v.get_width()
        axi.text(w + (0.02 if w > 0 else -0.02), v.get_y() + v.get_height()/2,
                 f"{w:+.2f}", va="center", ha="left" if w > 0 else "right",
                 fontsize=9)
plt.tight_layout(); plt.savefig("../images/climbers_fallers.png", dpi=120); plt.close()

# ============================ 7. SQL cross-check values (GDP quartiles) ===
# Quartiles computed the NTILE(4) way (row-count buckets), exactly matching
# the MySQL NTILE(4) OVER (ORDER BY gdp) in sql/queries.sql.
log(f"\n=== GDP quartile avgs {LATEST} (for SQL Q5 cross-check) ===")
dLq = dL.sort_values("gdp").reset_index(drop=True)
n = len(dLq)
dLq["gdp_quartile"] = (np.arange(n) * 4 // n + 1)
dLq["gdp_quartile"] = dLq["gdp_quartile"].map(
    {1: "Q1 (poorest)", 2: "Q2", 3: "Q3", 4: "Q4 (richest)"})
qavg = dLq.groupby("gdp_quartile", observed=True)["ladder_score"].mean()
log(qavg.round(3).to_string())

log("\n=== YoY global trend (for SQL Q7 cross-check) ===")
yoy = df.groupby("year")["ladder_score"].mean()
log(yoy.round(3).to_string())

with open("../results_summary.txt", "w") as f:
    f.write("\n".join(out) + "\n")
log("\nwrote ../results_summary.txt and 5 charts to ../images/")
