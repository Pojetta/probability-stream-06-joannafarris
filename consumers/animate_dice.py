# consumers/animate_dice.py

"""
Animate live dice-roll proportions.

Summary
- Streams die rolls from `consumers.stream_consumer.consume_forever` and renders
  a live bar chart of cumulative face proportions with an expected 1/6 reference line.
- Displays running counts as labels; title shows current sample size n.
- Writes periodic snapshot rows to CSV via `utils.snapshot` (sidecar; no visual impact).

Behavior
- Fixed y-axis (0–0.5) to reduce jitter while proportions converge.
- Bars recolor consistently by face; labels reposition for readability.
- Title updates each frame with the latest n.

Snapshots
- `utils.snapshot.init()` ensures the CSV exists; `maybe_write(n, counts)` appends
  a row every `SNAPSHOT_EVERY` rolls.
- Fields: ts, n, max_abs_dev, chi2, p1..p6 (cumulative proportions), c1..c6 (cumulative counts).
- Environment:
    SNAPSHOT_EVERY (default: 50)
    SNAPSHOT_PATH  (default: data/snapshots.csv)

Controls
- Space: pause / resume (title reflects PAUSED state with last n)
- X:     stop (freeze last frame; window remains open)
- Q:     close the window (standard Matplotlib behavior)

Run
- From the repository root:
    python -m consumers.animate_dice
- Optional parameters (via code or wrapper):
    animate_live(delay_sec=0.1, seed=7)

Dependencies
- Matplotlib for animation and plotting.
- `consumers.stream_consumer` for the roll stream.
- `utils.snapshot` for sidecar CSV snapshots.
"""


import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from consumers.stream_consumer import consume_forever
from utils import snapshot as snap  # NEW: sidecar snapshots; no visual impact


def animate_live(delay_sec=0.1, seed=None):
    faces = [1, 2, 3, 4, 5, 6]
    gen = consume_forever(delay_sec=delay_sec, seed=seed)

    # Prime one frame
    counts, props, n = next(gen)

    snap.init()                 # NEW: ensure snapshots file exists
    snap.maybe_write(n, counts) # NEW: write snapshot if interval

    #fig, ax = plt.subplots()
    fig, ax = plt.subplots(figsize=(7, 4), constrained_layout=True)
    fig.patch.set_facecolor("#ffeed247")  # background around the plot
    ax.set_facecolor("#ffeed2a5")  
    

    labels  = [str(f) for f in faces]
    heights = [props.get(f, 0.0) for f in faces]
    hex_colors = [
        "#bedfdd", 
        "#fcc2b3", 
        "#fc917b", 
        "#d0b97e", 
        "#b89e46", 
        "#365d59", 
    ]
    bars = ax.bar(labels, heights, color=hex_colors, edgecolor="black")

    ax.set_ylim(0, .5)  # fixed y-axis to prevent jitter
    ax.set_ylabel("Proportion", fontsize=11)

    ax.set_xlabel("Dice Face", fontsize=11)
    for label in ax.get_xticklabels():
        label.set_fontweight("bold")
    ax.tick_params(axis="x", labelsize=12)  # bump size up (try 14 if you want larger)

    exp_line = ax.axhline(1/6, linestyle="--", linewidth=.8, color="#c9a365ff", label="Expected Probability (1/6)")
    ax.legend(loc="upper right", frameon=True)

    title = ax.set_title(f"Dice Proportions (n={n})", fontsize=16)

    # --- ADDED: running count labels for each bar ---
    count_labels = []
    for i, f in enumerate(faces):
        cnt = counts.get(f, 0)
        x = bars[i].get_x() + bars[i].get_width() / 2
        h = heights[i]
        # place just above the bar initially
        txt = ax.text(x, h + 0.02, str(cnt), ha="center", va="bottom", fontsize=9)
        count_labels.append(txt)

    def _place_label(i, h, cnt):
        """Reposition label based on bar height; keep it readable."""
        x = bars[i].get_x() + bars[i].get_width() / 2
        # If the bar is tall, put the label inside near the top in white
        if h > 0.85:
            count_labels[i].set_position((x, h - 0.05))
            count_labels[i].set_va("top")
            count_labels[i].set_color("white")
        else:
            # Otherwise, keep it above the bar in black
            count_labels[i].set_position((x, h + 0.02))
            count_labels[i].set_va("bottom")
            count_labels[i].set_color("black")
        count_labels[i].set_text(str(cnt))
    # --- END ADDED ---

    # Track latest state so pause/stop shows accurate n
    state = {"paused": False, "stopped": False, "n": n}

    def update(_frame):
        if state["paused"] or state["stopped"]:
            return bars  # no updates while paused/stopped

        counts, props, n_now = next(gen)
        for i, f in enumerate(faces):
            h = props.get(f, 0.0)
            bars[i].set_height(h)
            # ADDED: update the label position/text with current count
            _place_label(i, h, counts.get(f, 0))

        snap.maybe_write(n_now, counts)  # NEW: sidecar snapshot; chart unchanged

        title.set_text(f"Dice Proportions (n={n_now})")
        state["n"] = n_now  # remember latest n for pause/stop display
        return bars  # return value ignored when blit=False

    # Keep a reference; no blit; disable frame cache
    anim = FuncAnimation(
        fig, update,
        interval=100,
        blit=False,
        cache_frame_data=False
    )

    # Keys:
    #   Space = pause/resume (accurate n in title)
    #   X     = stop (freeze last frame; window stays open)
    #   q     = default Matplotlib quit/close (unchanged)
    def on_key(event):
        if event.key == " ":
            state["paused"] = not state["paused"]
            if state["paused"]:
                anim.event_source.stop()
                title.set_text(f"Dice Proportions (n={state['n']}) — PAUSED")
                fig.canvas.draw_idle()
            else:
                anim.event_source.start()
        elif event.key in ("x", "X"):
            if not state["stopped"]:
                state["stopped"] = True
                anim.event_source.stop()
                title.set_text(f"Dice Proportions (n={state['n']}) — STOPPED")
                fig.canvas.draw_idle()
                print("Animation stopped. Close window to exit.")   

    fig.canvas.mpl_connect("key_press_event", on_key)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    animate_live(delay_sec=0.1, seed=7)