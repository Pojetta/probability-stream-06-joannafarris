# consumers/stream_consumer.py

"""
Lightweight dice stream consumer.

- Wraps `producers.dice_producer.dice_stream` and maintains cumulative counts (1–6)
  and total rolls `n`, exposing current proportions on demand.
- Public entrypoint: `consume_forever(delay_sec=0.2, seed=None, max_events=None)`,
  a generator yielding `(counts: dict[int,int], proportions: dict[int,float], n: int)`
  after each event.

Intended use: import `consume_forever` from visualizers (e.g., `animate_dice.py`)
to drive a live chart without re-implementing counting logic.
"""


from producers.dice_producer import dice_stream

print("__name__ in stream_consumer:", __name__)

def init_counts():
    return {face: 0 for face in range(1, 7)}

def proportions(counts):
    total = sum(counts.values())
    return {k: (counts[k] / total if total else 0.0) for k in counts}

class StreamConsumer:
    def __init__(self):
        self.counts = init_counts()
        self.n = 0

    def process_event(self, event):
        if isinstance(event, dict) and event.get("event_type") == "dice":
            outcome = event.get("outcome")
            if isinstance(outcome, int) and 1 <= outcome <= 6:
                self.counts[outcome] += 1
                self.n += 1

    def current(self):
        return self.counts, proportions(self.counts), self.n

def consume_forever(delay_sec=0.2, seed=None, max_events=None):
    sc = StreamConsumer()
    stream = dice_stream(delay_sec=delay_sec, seed=seed)
    i = 0
    while True:
        evt = next(stream)
        sc.process_event(evt)
        i += 1
        yield sc.current()
        if max_events is not None and i >= max_events:
            break

if __name__ == "__main__":
    for counts, props, n in consume_forever(delay_sec=0.05, seed=1, max_events=10):
        print(n, counts, props)
