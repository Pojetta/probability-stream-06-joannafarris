# producers/dice_producer.py
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
