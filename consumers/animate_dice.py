# consumers/animate_dice.py
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from consumers.stream_consumer import consume_forever

def animate_live(delay_sec=0.1, seed=None):
    faces = [1, 2, 3, 4, 5, 6]
    gen = consume_forever(delay_sec=delay_sec, seed=seed)

    # prime one frame
    counts, props, n = next(gen)

    fig, ax = plt.subplots()
    bars = ax.bar([str(f) for f in faces], [props.get(f, 0.0) for f in faces])
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Proportion")
    ax.set_xlabel("Dice Face")
    exp_line = ax.axhline(1/6, linestyle="--", linewidth=1)
    title = ax.set_title(f"Dice Proportions (n={n})")

    paused = {"value": False}  # mutable container so inner func can modify

    def update(_frame):
        if paused["value"]:
            return bars  # no updates while paused
        counts, props, n = next(gen)
        for i, f in enumerate(faces):
            bars[i].set_height(props.get(f, 0.0))
        title.set_text(f"Dice Proportions (n={n})")
        return bars

    anim = FuncAnimation(
        fig, update,
        interval=100,
        blit=False,
        cache_frame_data=False
    )

    # --- key bindings: space = pause/resume, q = stop updates (leave last frame)
    def on_key(event):
        if event.key == " ":
            paused["value"] = not paused["value"]
            if paused["value"]:
                anim.event_source.stop()
                title.set_text(f"Dice Proportions (n={n}) — PAUSED")
                fig.canvas.draw_idle()
            else:
                anim.event_source.start()
        elif event.key == "q":
            paused["value"] = True
            anim.event_source.stop()
            title.set_text(f"Dice Proportions (n={n}) — STOPPED")
            fig.canvas.draw_idle()
            # window stays open until you close it

    fig.canvas.mpl_connect("key_press_event", on_key)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    animate_live(delay_sec=0.1, seed=7)
