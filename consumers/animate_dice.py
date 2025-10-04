# consumers/animate_dice.py
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from consumers.stream_consumer import consume_forever

def animate_live(delay_sec=0.1, seed=None):
    faces = [1, 2, 3, 4, 5, 6]
    gen = consume_forever(delay_sec=delay_sec, seed=seed)

    # Prime one frame
    counts, props, n = next(gen)

    fig, ax = plt.subplots()
    
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
    ax.set_ylim(0, 1.0)  # fixed y-axis to prevent jitter
    ax.set_ylabel("Proportion")
    ax.set_xlabel("Dice Face")
    exp_line = ax.axhline(1/6, linestyle="--", linewidth=1)
    title = ax.set_title(f"Dice Proportions (n={n})")

    # Track latest state so pause/stop shows accurate n
    state = {"paused": False, "stopped": False, "n": n}

    def update(_frame):
        if state["paused"] or state["stopped"]:
            return bars  # no updates while paused/stopped
        counts, props, n_now = next(gen)
        for i, f in enumerate(faces):
            bars[i].set_height(props.get(f, 0.0))
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
            # (Leave 'q' alone to close the window if you want to exit.)

    fig.canvas.mpl_connect("key_press_event", on_key)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    animate_live(delay_sec=0.1, seed=7)
