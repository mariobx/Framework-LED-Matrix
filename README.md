# Framework 16 LED Matrix Modules

I remember how surprised I was at the lack of tools for the LED matrix 16. I had gotten them knowing they were programmable and I could do cool things, yet no one yet has made a tool for them to do much (at least to my research).

This should allow programming novices to run cool simulations of their own on the Framework 16 LED matrix besides the simple boot animations.

The `core/` directory defines the core API of the tool, such as creating a simpler way to interact with the defined LED functions, the path of the LEDs, sending of both greyscale and regular payloads, clearing the matricies, etc.

This suite allows you to run a variety of visual experiments:
* **Anagrams & Text:** Anagrams of random words gliding across the screen or custom text rendered vertically and horizontally.
* **Cellular Automata:** Complex simulations including Conway’s Game of Life, the Biham-Middleton-Levine (BML) traffic model, and Hardy-Pomeau-Pazzis (HPP) lattice gas collisions.
* **Mathematical Visualizations:** Plotting math functions like `sin`, `cos`, `exp`, and `tanh` directly onto the matrix.
* **Hybrid Simulations:** Seeding Game of Life or HPP simulations using math function graphs or anagrammed text as the initial starting states.
* **Noise & Hardware Effects:** Generating hardware-level greyscale noise and controlling internal hardware animations.

---

## Global Options
* `-v, --verbose`: Enable detailed verbose logging for all commands.

---

## Commands & Sub-arguments

### [1] `background` (aliases: `bg`)
Run the background runner (screensaver mode).

---

### [2] `led`
* `version`: Get firmware version from modules.
* `clear`: Clear both displays (all LEDs OFF).
* `fill`: 
    * `--hold <float>`: Seconds to hold the filled screen (default: `0`).
* `start-anim`: Start hardware animation (e.g., fades).
* `stop-anim`: Stop hardware animation.
* `reset`: Clear display and stop animation.
* `ports`: Show available serial ports (for debugging).

---

### [3] `text`
* **`vertical <text>`**
    * `--font-size <int>`: Force a specific font size (default: `auto`).
    * `--which <choice>`: Which module: `left`, `right`, `both` (default: `both`).
    * `--row-offset <int>`: Row offset from the top (default: `0`).
    * `--hold <float>`: Seconds to hold the text on screen (default: `0`).
* **`horizontal <text>`**
    * `--font-size <int>`: Force a specific font size (default: `auto`).
    * `--which <choice>`: Which module: `left`, `right`, `both` (default: `both`).
    * `--x-offset <int>`: Horizontal scroll offset (default: `0`).
    * `--y-offset <int>`: Vertical position offset (default: `centered`).
    * `--hold <float>`: Seconds to hold the text on screen (default: `0`).

---

### [4] `anagram`
* **`draw <word>`**
    * `--which <choice>`: Which module: `left`, `right`, `both` (default: `both`).
    * `--no-animate`: Disable animation between words.

---

### [5] `sim`
* **`bml`**: Run Biham-Middleton-Levine traffic model (cars moving on a grid).
    * `--density <float>`: Car density 0.0 to 1.0 (default: `0.35`).
    * `--steps <int>`: Total half-steps to simulate (default: `500`).
    * `--delay <float>`: Delay in seconds between frames (default: `0.05`).
* **`bml-local`**: Run BML traffic model locally in a Matplotlib window.
* **`hpp`**: Run Hardy-Pomeau-Pazzis lattice gas (particle collision simulation).
    
    * `--density <float>`: Particle density 0.0 to 1.0 (default: `0.5`).
    * `--steps <int>`: Simulation steps (default: `500`).
    * `--delay <float>`: Delay in seconds between frames (default: `0.05`).
    * `--which <choice>`: Which module: `left`, `right`, `both` (default: `both`).
* **`hpp-math`**: Run HPP simulation seeded with math function graphs as the initial state.
    * `--density <float>`: Particle density 0.0 to 1.0 (default: `0.3`).
    * `--steps <int>`: Simulation steps per graph (default: `500`).
    * `--delay <float>`: Delay in seconds between frames (default: `0.05`).
    * `--graphs <int>`: Number of math graphs to run (default: `5`).
* **`outer`**: Run generic Outer-Totalistic CA using Birth/Survival rules.
    * `--b-rule <list>`: Birth rule, comma-separated (e.g., `'3,6'`).
    * `--s-rule <list>`: Survival rule, comma-separated (e.g., `'2,3'`).
    * `--steps <int>`: Simulation steps (default: `200`).
    * `--delay <float>`: Delay in seconds between frames (default: `0.1`).
    * `--oscil-max <int>`: Steps to detect oscillation (default: `20`).
    * `--still-max <int>`: Steps to detect still life (default: `10`).
    * `--empty-max <int>`: Steps to detect empty board (default: `5`).
* **`gof`**: Run Conway's Game of Life (B3/S23).
    
    * `--board <choice>`: Initial state: `random` or named pattern (`glider`, `acorn`, etc.).
    * `--steps <int>`: Simulation steps (default: `200`).
    * `--delay <float>`: Delay in seconds between frames (default: `0.1`).
    * `--which <choice>`: Which module: `left`, `right`, `both` (default: `both`).
* **`inner`**: Run Inner-Totalistic CA (Wolfram NKS style).
    * `<rule> <int>`: The rule number (e.g., `777`).
    * `--steps <int>`: Simulation steps (default: `200`).
    * `--delay <float>`: Delay in seconds between frames (default: `0.1`).
* **`random-grey`**: Display hardware-level greyscale noise.
    * `--duration <int>`: Duration in seconds (default: `10`).
    * `--no-animate`: Disable hardware animation (for pure noise).
* **`anagram-gof`**: Finds anagrams for random words and uses the text as the Game of Life starting state.
    * `--words <int>`: Number of random words to use (default: `4`).
    * `--steps <int>`: GoL steps per anagram (default: `100`).
    * `--delay <float>`: Delay in seconds between GoL frames (default: `0.1`).
    * `--which <choice>`: Which module: `left`, `right`, `both` (default: `both`).
* **`anagram-draw`**: Sequentially find and draw anagrams for random words.
    * `--words <int>`: Number of random words to use (default: `3`).
    * `--which <choice>`: Which module: `left`, `right`, `both` (default: `both`).
* **`math-gof`**: Plot math graphs and use them as the Game of Life starting state.
    * `--steps <int>`: GoL steps per graph (default: `100`).
    * `--delay <float>`: Delay in seconds between GoL frames (default: `0.1`).
* **`math-graphs`**: Show a cycling sequence of random math graphs.
    * `--num <int>`: Number of graphs to show (default: `5`).
    * `--delay <float>`: Delay in seconds between graphs (default: `2.0`).
    * `--which <choice>`: Which module: `left`, `right`, `both` (default: `both`).
    * `--hold <float>`: Seconds to hold the *final* graph on screen (default: `0`).

---

### [6] `math`
* **`plot <function>`**: Plot a function locally and on the matrix.
    * `<function>`: Predefined function: `sin`, `cos`, `tan`, `exp`, `log`, `tanh`, etc.
    * `--points <int>`: Number of points to plot (default: `500`).
