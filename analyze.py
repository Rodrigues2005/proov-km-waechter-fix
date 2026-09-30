# analyze.py
# Risk factors: km_since_service (r=+0.40), avg_daily_km (r=+0.25), load_factor (r=+0.22).
# Total mileage and age have near-zero correlation (r≈0.002) and are NOT predictive in this fleet.
#
# Each factor is min-max scaled to [0,1] and combined with weights proportional to its
# correlation with broke_down. Score 0 = lowest risk, 100 = highest risk.

import pandas as pd

# ── 1. Load data ──────────────────────────────────────────────────────────────
df = pd.read_csv("fleet_history.csv")

# ── 2. Column-by-column group comparison ─────────────────────────────────────
#
# We split the fleet into two groups (broke_down=1 vs 0) and compare every numeric
# column. We also compute Pearson correlation with broke_down as a single number
# that tells us how strongly each column tracks breakdowns.
#
# Results (see comments below — DO NOT change these without re-running the analysis):
#
#   Column              Correlation   Broke mean   Fine mean   Separation?
#   odometer_km         +0.002        53 448 km    53 302 km   NO  — identical groups
#   age_years           -0.001         5.9 yr        5.9 yr    NO  — identical groups
#   km_since_service    +0.404        11 678 km     7 261 km   YES — 61% higher in broken cars
#   avg_daily_km        +0.252          159.7         131.4    YES — 22% higher in broken cars
#   load_factor         +0.215            0.60          0.50   YES — 19% higher in broken cars
#
# The "obvious" predictors (total mileage and age) do not separate the groups at all.
# The real signal is how overdue the car is for service, how hard it is driven daily,
# and how heavily it is loaded.

broke = df[df["broke_down"] == 1]
fine  = df[df["broke_down"] == 0]

print("=" * 65)
print("Group comparison: broke_down=1 vs broke_down=0")
print("=" * 65)
features = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]
for col in features:
    r      = df[col].corr(df["broke_down"])
    b_mean = broke[col].mean()
    f_mean = fine[col].mean()
    diff   = (b_mean - f_mean) / f_mean * 100 if f_mean else 0
    signal = "SIGNAL" if abs(r) >= 0.20 else "no signal"
    print(f"  {col:20s}  r={r:+.3f}  broke={b_mean:8.1f}  fine={f_mean:8.1f}  "
          f"diff={diff:+.0f}%  [{signal}]")
print()

# ── 3. Build a risk score from the three predictive columns only ──────────────
#
# Method: min-max normalise each signal column to [0, 1], then take a weighted
# average using weights proportional to each column's correlation with broke_down.
# Multiply by 100 to get a 0–100 score.  No machine learning needed.
#
# Weights (proportional to |r|):
#   km_since_service : 0.404  →  46 %
#   avg_daily_km     : 0.252  →  29 %
#   load_factor      : 0.215  →  25 %

SIGNAL_COLS = ["km_since_service", "avg_daily_km", "load_factor"]
WEIGHTS     = [0.404, 0.252, 0.215]

def minmax(series: pd.Series) -> pd.Series:
    """Scale a series to the range [0, 1] using observed min and max."""
    lo, hi = series.min(), series.max()
    return (series - lo) / (hi - lo)

total_weight = sum(WEIGHTS)
score = sum(w * minmax(df[col]) for col, w in zip(SIGNAL_COLS, WEIGHTS)) / total_weight
df["risk_score"] = (score * 100).round(1)

# ── 4. Rank and print the top 10 riskiest cars ────────────────────────────────
ranked = df.sort_values("risk_score", ascending=False).reset_index(drop=True)
ranked.index += 1   # start rank at 1

print("=" * 65)
print("Top 10 cars by risk score (highest risk first)")
print("=" * 65)
print(f"  {'Rank':>4}  {'Car ID':<10}  {'Score':>5}  "
      f"{'km_since_svc':>13}  {'avg_daily_km':>13}  {'load':>6}  {'broke?':>7}")
print("  " + "-" * 61)
for rank, row in ranked.head(10).iterrows():
    broke_marker = "  ✓" if row["broke_down"] == 1 else ""
    print(f"  {rank:>4}  {row['car_id']:<10}  {row['risk_score']:>5.1f}  "
          f"{row['km_since_service']:>13.0f}  {row['avg_daily_km']:>13.0f}  "
          f"{row['load_factor']:>6.2f}{broke_marker}")

print()
n_top10_broke = ranked.head(10)["broke_down"].sum()
print(f"  {n_top10_broke} of the top-10 riskiest cars actually broke down "
      f"({n_top10_broke/10*100:.0f}%).")
print()

# ── 5. Sanity check: how well does the score rank the fleet overall? ───────────
# A good score concentrates the broken cars near the top of the ranking.
# We check what fraction of the broken cars fall in the top third of the risk ranking.
top_third = ranked.head(len(ranked) // 3)
n_broke_in_top_third = top_third["broke_down"].sum()
print(f"  Broken cars in the top third of the risk ranking: "
      f"{n_broke_in_top_third} of {broke['broke_down'].sum()} "
      f"({n_broke_in_top_third/len(broke)*100:.0f}%).")
print(f"  Random chance would put ~{len(broke)//3} of them there.")
