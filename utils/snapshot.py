# utils/snapshot.py

"""
Snapshot writer for the dice stream.

Purpose
- Append a summary row to a CSV every SNAPSHOT_EVERY rolls.
- Each row stores: timestamp, total rolls (n), chi-square, max abs deviation,
  cumulative proportions p1..p6 (counts / n), and cumulative counts c1..c6.

Environment
- SNAPSHOT_EVERY: write interval (default: 50)
- SNAPSHOT_PATH : output CSV path (default: data/snapshots.csv)
"""


import os
import csv
import time
from typing import Dict, Iterable, List, Union

SNAPSHOT_EVERY = int(os.getenv("SNAPSHOT_EVERY", "50"))
SNAPSHOT_PATH  = os.getenv("SNAPSHOT_PATH", "data/snapshots.csv")

FIELDS = [
    "ts", "n", "max_abs_dev", "chi2",
    "p1","p2","p3","p4","p5","p6",
    "c1","c2","c3","c4","c5","c6",
]

Faces = range(1, 7)
CountsType = Union[Dict[int, int], Iterable[int]]

def _counts_vec(counts: CountsType) -> List[int]:
    """
    Normalize counts into a list [c1..c6].

    Supports:
      - dict keyed 1..6
      - list/tuple of length 6 (c1..c6)
    """
    if isinstance(counts, dict):
        return [int(counts.get(i, 0)) for i in Faces]
    # Assume ordered iterable [c1..c6]
    vals = list(counts)
    if len(vals) != 6:
        raise ValueError(f"Expected 6 counts, got {len(vals)}")
    return [int(v) for v in vals]

def _proportions(counts: CountsType, n: int) -> List[float]:
    """Cumulative proportions p_i = c_i / n; returns [p1..p6]."""
    if n <= 0:
        return [0.0] * 6
    vec = _counts_vec(counts)
    return [c / n for c in vec]

def _chi2(counts: CountsType, n: int) -> float:
    """Pearson chi-square against a fair die (df=5; expected = n/6)."""
    if n <= 0:
        return 0.0
    vec = _counts_vec(counts)
    exp = n / 6
    return sum(((c - exp) ** 2) / exp for c in vec)

def _max_abs_dev(props: List[float]) -> float:
    """Max |p(face) - 1/6| across faces."""
    return max(abs(p - 1/6) for p in props) if props else 0.0

def init() -> None:
    """Ensure the output directory exists and the CSV has a header."""
    os.makedirs(os.path.dirname(SNAPSHOT_PATH) or ".", exist_ok=True)
    if not os.path.exists(SNAPSHOT_PATH):
        with open(SNAPSHOT_PATH, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writeheader()

def maybe_write(n: int, counts: CountsType) -> None:
    """
    Append a snapshot row every SNAPSHOT_EVERY rolls.

    Expects cumulative counts (totals so far). If you accidentally pass
    per-batch counts, proportions will not represent convergence.
    """
    if SNAPSHOT_EVERY <= 0 or (n % SNAPSHOT_EVERY) != 0:
        return

    vec = _counts_vec(counts)
    # Optional safety: ensure counts sum to n (cumulative totals).
    # Comment this back in if you want a hard guarantee.
    # if sum(vec) != n:
    #     raise AssertionError(f"Expected cumulative counts: sum={sum(vec)}, n={n}")

    ps = _proportions(vec, n)
    row = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "n": n,
        "max_abs_dev": round(_max_abs_dev(ps), 6),
        "chi2": round(_chi2(vec, n), 6),
        "p1": ps[0], "p2": ps[1], "p3": ps[2],
        "p4": ps[3], "p5": ps[4], "p6": ps[5],
        "c1": vec[0], "c2": vec[1], "c3": vec[2],
        "c4": vec[3], "c5": vec[4], "c6": vec[5],
    }
    with open(SNAPSHOT_PATH, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=FIELDS).writerow(row)
