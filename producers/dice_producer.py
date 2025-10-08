# producers/dice_producer.py

"""
Simple dice event producer.

Generates an infinite stream of dice-roll events as dictionaries:
{
    "trial_id": int,           # 1, 2, 3, ...
    "event_type": "dice",
    "outcome": 1..6,           # uniform RNG
    "timestamp": ISO-8601 UTC  # e.g., "2025-10-07T01:23:45.678901+00:00"
}

Args:
    delay_sec (float): Sleep between events (default 0.2 s).
    seed (int | None): RNG seed for reproducible outcomes.

Yields:
    dict: One event per iteration.
"""


import random
import time
from datetime import datetime, timezone

def dice_stream(delay_sec=0.2, seed=None):
    rng = random.Random(seed)
    trial_id = 0
    while True:
        trial_id += 1
        yield {
            "trial_id": trial_id,
            "event_type": "dice",
            "outcome": rng.randint(1, 6),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        time.sleep(delay_sec)

if __name__ == "__main__":
    s = dice_stream(delay_sec=0.1, seed=42)
    for _ in range(5):
        print(next(s))
