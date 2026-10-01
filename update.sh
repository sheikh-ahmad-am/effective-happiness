#!/bin/bash
# World Happiness Analytics — live refresh pipeline.
# Pulls the latest WHR data; if anything changed, re-runs the analysis,
# refreshes the README live-stamp, commits, and pushes.
# Run manually: ./update.sh
# Runs automatically: monthly cron (see README "How the live update works").
set -e
cd "$(dirname "$0")"

echo "==> [1/4] Pulling latest World Happiness Report data..."
PULL_OUT=$(cd data && python3 pull_data.py 2>&1)
echo "$PULL_OUT" | tail -3

if ! echo "$PULL_OUT" | grep -q "^CHANGED$"; then
    echo "==> No new data. Nothing to update."
    exit 0
fi

echo "==> [2/4] Data changed — re-running analysis..."
(cd python && python3 happiness_analysis.py > /dev/null 2>&1)

echo "==> [3/4] Refreshing README live-stamp..."
python3 - <<'EOF'
import pandas as pd, datetime, re
df = pd.read_csv("data/happiness.csv")
years = f"{int(df['year'].min())}–{int(df['year'].max())}"
today = datetime.date.today().isoformat()
stamp = ("> 🔄 **This project is live.** Data is re-pulled automatically and every\n"
         "> chart, KPI, and ranking refreshes whenever a new report lands.\n"
         f"> Last data pull: **{today}** — covering **{years}**.")
path = "README.md"
text = open(path).read()
text = re.sub(r"<!-- LIVE-STAMP -->\n>.*?\n>.*?\n>.*?\n",
              "<!-- LIVE-STAMP -->\n" + stamp + "\n", text, count=1, flags=re.S)
open(path, "w").write(text)
print(f"    stamped: {today} — {years}")
EOF

echo "==> [4/4] Committing and pushing..."
git add -A
git commit -m "Live refresh: WHR data updated ($(date +%Y-%m-%d))" --quiet
git push origin main --quiet
echo "==> Done. Live update pushed to GitHub."
