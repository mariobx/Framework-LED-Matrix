## LED Matrix Graph & Simulation Suite
This project provides a comprehensive toolkit for rendering mathematical functions, complex cellular automata simulations, and text animations on a dual 34x9 LED matrix system. It includes a modular core for hardware communication, a suite of simulation engines (BML, HPP, GoL), and a robust CLI for local and remote visualization.

# Workflow:
  1. Initialize hardware modules (left/right) via serial PCI paths.
  2. Select a mode: Math Plotting, CA Simulation, Text Rendering, or Anagram discovery.
  3. (Math) Sample high-resolution functions (step 0.01) and map them to the 34x9 discrete grid.
  4. (Simulation) Evolve cellular automata states using cellpylib and push frames to hardware.
  5. (Background) Cycle through "scenes" indefinitely for a screensaver-like experience.

# Arguments:
  - `led`: Basic hardware commands (version, clear, fill, start-anim, stop-anim, reset, ports).
  - `text`: Render text on the matrix (vertical, horizontal) with customizable hold times and offsets.
  - `anagram`: Find and draw anagrams for a target word on the matrix.
  - `sim`: Run complex simulations:
    - `gof`: Conway's Game of Life with named patterns (glider, acorn, etc.).
    - `outer`: Custom Outer-Totalistic CA with B/S rules.
    - `inner`: Custom Inner-Totalistic CA with NKS rule numbers.
    - `bml`: Biham-Middleton-Levine traffic model (includes `bml-local` for Matplotlib).
    - `hpp`: Hardy-Pomeau-Pazzis lattice gas (includes `hpp-math` for graph seeding).
    - `random-grey`: Random greyscale noise generation.
  - `math`: Plot predefined functions (sin, cos, exp, etc.) locally and on the matrix.
  - `-v`, `--verbose`: Enable detailed logging for debugging hardware communication.

# Examples:
  1. **Run a Game of Life "Diehard" pattern:** \
  ./cli.py sim gof --board diehard --delay 0.05

  2. **Plot a sine wave locally and on the matrix:** \
  ./cli.py math plot sin --points 1000

  3. **Run the background screensaver mode with verbose logging:** \
  ./cli.py -v background

  4. **Render horizontal scrolling text on the left module:** \
  ./cli.py text horizontal "FRAMEWORK" --which left --x-offset 2

  5. **Run a custom CA rule (Seeds) on the matrix:** \
  ./cli.py sim outer --b-rule "2" --s-rule "" --steps 500

  6. **Discover anagrams for "binary" and render them:** \
  ./cli.py anagram draw binary
