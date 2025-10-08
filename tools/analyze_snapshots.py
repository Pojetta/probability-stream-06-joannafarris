# tools/analyze_snapshots.py

"""
Dice snapshot analysis.

Reads the snapshot CSV and generates two PNG figures and a summary table.

Input
- CSV path from environment variable SNAPSHOT_PATH (default: "data/snapshots.csv").

Columns (expected in the CSV)
- ts           : timestamp string "YYYY-MM-DDTHH:MM:SS".
- n            : total number of rolls observed at this snapshot.
- chi2         : Pearson chi-square against a fair die (df = 5; expected = n/6).
- max_abs_dev  : max absolute deviation of any face’s proportion from 1/6.
- p1 .. p6     : cumulative proportions per face at this snapshot (c_i / n).
- c1 .. c6     : cumulative counts per face at this snapshot.

Output (written to ./reports/)
- faces_distribution.png — final snapshot bar chart of cumulative proportions (with counts optional).
- faces_trend.png        — cumulative proportions over time vs. expected 1/6.
- summary.csv            — one row per run with final stats.

Notes
- A new “run” is inferred when n decreases relative to the previous row.
- The ./reports directory is created if missing.

Run
- From the repository root:
    python tools/analyze_snapshots.py
- Or as a module:
    python -m tools.analyze_snapshots
- Custom CSV path:
    SNAPSHOT_PATH=path/to/snapshots.csv python -m tools.analyze_snapshots
"""


import os
import pandas as pd
import matplotlib.pyplot as plt


CSV_PATH = os.getenv("SNAPSHOT_PATH", "data/snapshots.csv")
OUTDIR = "reports"
CHI2_CRIT_5PCT = 11.07  # df=5

os.makedirs(OUTDIR, exist_ok=True)

# Load snapshots
df = pd.read_csv(CSV_PATH, parse_dates=["ts"])

# Identify runs: whenever n drops, a new run started
df["run"] = (df["n"].diff().fillna(0) < 0).cumsum()

# Build cumulative proportions from counts (robust even if CSV p1..p6 were per-batch)
for i in range(1, 7):
    df[f"p{i}_cum"] = df[f"c{i}"] / df["n"]

# Focus plots on the latest run only (change to df to show all runs)
latest = df[df["run"] == df["run"].max()].copy()

# ---------------------------
# 1) Faces distribution (final snapshot)
# ---------------------------
row = latest.iloc[-1] if not latest.empty else df.iloc[-1]
heights = [row[f"p{i}_cum"] for i in range(1, 7)]
labels  = [str(i) for i in range(1, 7)]
counts  = [int(row[f"c{i}"]) for i in range(1, 7)]

hex_colors = [
    "#bedfdd", "#fcc2b3", "#fc917b",
    "#d0b97e", "#b89e46", "#365d59",
]

fig1, ax1 = plt.subplots(figsize=(7, 4))
bars = ax1.bar(labels, heights, color=hex_colors, edgecolor="black")

# Put proportions inside bars for readability
for rect, p in zip(bars, heights):
    ax1.text(
        rect.get_x() + rect.get_width() / 2,
        rect.get_height() / 1.1,
        f"{p:.3f}",
        ha="center", va="center",
        color="black", fontsize=11
    )

# ax1.set_facecolor("#FFF8EB")          # axes background
fig1.patch.set_facecolor("#FFFAF0")
fig1.patch.set_edgecolor("black")     # figure border
fig1.patch.set_linewidth(1.5)

ax1.set_title(f"Cumulative Dice Face Proportions — n={int(row['n'])}", pad=14)
ax1.set_xlabel("Dice Face", labelpad=8)
ax1.set_ylabel("Proportion")
ax1.set_ylim(0, 0.20)   # lower bound, upper bound
ax1.axhline(1/6, linestyle="--", linewidth=1, color="#c9a365ff")

#plt.tight_layout()
#plt.savefig(os.path.join(OUTDIR, "faces_distribution.png"),
#            dpi=150, bbox_inches="tight", pad_inches=0.1)
fig1.subplots_adjust(left=0.14, right=0.95, bottom=0.17, top=0.85)
plt.savefig(os.path.join(OUTDIR, "faces_distribution.png"), dpi=150)
plt.close()

# ---------------------------
# 2) Proportions over time
# ---------------------------
fig2, ax2 = plt.subplots(figsize=(7, 4))
src = latest if not latest.empty else df
for i, color in enumerate(hex_colors, start=1):
    ax2.plot(src["n"], src[f"p{i}_cum"], label=f"Face {i}", color=color, linewidth=1.8)

fig2.patch.set_facecolor("#FFFAF0")
fig2.patch.set_edgecolor("black")
fig2.patch.set_linewidth(1.5)

ax2.axhline(1/6, linestyle="--", color="#07322bdb", linewidth=1, label="Expected (1/6)")
ax2.set_title("Dice Face Proportions Over Time (cumulative)")
ax2.set_xlabel("Number of Rolls", labelpad=14)
ax2.set_ylabel("Proportion")
ax2.legend(frameon=True, edgecolor="black", fontsize=8)
# less blank space on the right; higher "right" = smaller margin
fig2.subplots_adjust(left=0.10, right=0.95, bottom=0.20, top=0.88)


#plt.tight_layout()
#plt.savefig(os.path.join(OUTDIR, "faces_trend.png"),
#           dpi=150, bbox_inches="tight", pad_inches=0.1)
plt.savefig(os.path.join(OUTDIR, "faces_trend.png"), dpi=150)
plt.close()

# ---------------------------
# 3) Fairness checkpoint @ 5%
# ---------------------------
df["passes_chi2_5pct"] = df["chi2"] < CHI2_CRIT_5PCT
first_pass = (
    df[df["passes_chi2_5pct"]]
    .groupby("run", as_index=False)["n"].min()
    .rename(columns={"n": "n_at_first_pass"})
)

# ---------------------------
# 4) End-of-run summary CSV
# ---------------------------
last_per_run = (
    df.sort_values(["run", "n"])
      .groupby("run")
      .tail(1)[["run", "n", "max_abs_dev", "chi2", "p1", "p2", "p3", "p4", "p5", "p6"]]
)

summary = last_per_run.merge(first_pass, on="run", how="left").sort_values("run")
summary.to_csv(os.path.join(OUTDIR, "summary.csv"), index=False)

# ---------------------------
# 5) Tiny human summary
# ---------------------------
print("=== Final snapshot per run ===")
print(summary.to_string(index=False))
print("\n=== Snapshot analysis complete ===")
print(f"Read {len(df)} rows from snapshots.csv")
print("Generated files:")
print("Wrote to:", os.path.join(OUTDIR, "faces_distribution.png"))
print("Wrote to:", os.path.join(OUTDIR, "faces_trend.png"))
print("Wrote to:", os.path.join(OUTDIR, "summary.csv"))
