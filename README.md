# probability-stream-06-joannafarris

Plan and draft a custom streaming data project.

---

## P6: Probability Stream

This project simulates dice rolls as a continuous data stream using a Python generator.  

The consumer reads each event as it arrives, updates running counts, and calculates live proportions for all six faces.  

A Matplotlib animation displays these proportions as an updating bar chart, showing how the distribution of rolls gradually converges toward the expected probability of **1/6 per face**.

---

### Insight and Focus

The main insight is observing **probability stabilization** — how random outcomes begin unevenly but converge toward a predictable distribution over time.  

By tracking proportions in real time, this stream demonstrates the **Law of Large Numbers** in a visual and interactive way.

Each message (a single dice roll) is processed as follows:
1. **Producer (Generator):** emits a dice face (1–6) as a JSON event.  
2. **Consumer:** receives the event, updates running totals for each face, and recalculates proportions.  
3. **Visualization:** redraws the bar chart live, displaying both proportions and running counts.

This process turns an abstract probability principle into a streaming, data-driven visualization.

---

### Run Instructions

#### 1. Activate your virtual environment
```bash
source .venv/bin/activate
```

#### 2. Run the producer
```bash
python -m producers.dice_producer
```
### 3. Run the consumer (with animation) 
```bash 
python -m consumers.animate_dice 
```  

---

### Dynamic Visualization

The live Matplotlib animation displays:

- Six color-coded bars (one for each dice face)  
- Real-time count labels above each bar  
- A dashed reference line at the expected probability (1/6)  
- Keyboard controls for interaction:  
  - **Space** — Pause / Resume  
  - **X** — Stop (freeze chart)  
  - **Q** — Quit  

The chart background uses warm, muted tones for visual balance, and proportions are scaled from **0 to 0.5** to reduce whitespace while keeping the trend readable.

---

### Example Visualization

![Dice Roll Stream Animation](images/dice_roll_stream_animation.png)

---

### Future Extensions

- Add **bias detection** to flag when one face appears unusually often.  
- Introduce a **coin flip stream** for side-by-side comparison.  
- Include **alert triggers** (email or text) when proportions deviate significantly from expectation.

