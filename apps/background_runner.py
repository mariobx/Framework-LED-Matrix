#!/usr/bin/env python3
"""
Background Runner (Screensaver) for LED Matrix.
Cycles through various scenes randomly.
"""
import time
import random
import sys
from typing import List

try:
    from core.led_commands import log, reset_modules
    from apps.runtime import (
        game_of_life_totalistic_sim,
        run_outer_totalistic_simulation,
        run_inner_totalistic_simulation,
        run_bml_simulation,
        run_draw_anagram_on_matrix,
        run_math_funs_game_of_life,
        show_random_graphs,
        random_greyscale_animation
    )
    from simulations.HardyPomeauPazzis import run_hpp_simulation
except ImportError as e:
    print(f"Background Runner Import Error: {e}")
    sys.exit(1)

def scene_game_of_life():
    steps = random.randint(100, 300)
    initial_board = None
    log(f"[BG] Starting Game of Life for {steps} steps...")
    game_of_life_totalistic_sim(initial_board, timesteps=steps, delay_sec=0.05, which='both')

def scene_outer_totalistic():
    b_rule = [random.randint(1, 8) for _ in range(random.randint(1, 3))]
    s_rule = [random.randint(1, 8) for _ in range(random.randint(1, 3))]
    steps = random.randint(100, 200)
    log(f"[BG] Starting Outer-Totalistic (B{b_rule}/S{s_rule}) for {steps} steps...")
    run_outer_totalistic_simulation(None, b_rule, s_rule, timesteps=steps, delay_sec=0.05)

def scene_inner_totalistic():
    rule = random.randint(100, 1000)
    steps = random.randint(100, 200)
    log(f"[BG] Starting Inner-Totalistic Rule {rule} for {steps} steps...")
    run_inner_totalistic_simulation(None, rule, timesteps=steps, delay_sec=0.05)

def scene_bml_traffic():
    density = random.uniform(0.3, 0.45)
    steps = random.randint(400, 800)
    log(f"[BG] Starting BML Traffic (density={density:.2f}) for {steps} steps...")
    run_bml_simulation(density, timesteps=steps, delay_sec=0.02)

def scene_hpp_gas():
    density = random.uniform(0.4, 0.6)
    steps = random.randint(300, 600)
    log(f"[BG] Starting HPP Lattice Gas (density={density:.2f}) for {steps} steps...")
    run_hpp_simulation(None, density, steps, 0.03, 'both')

def scene_anagrams():
    words = random.randint(2, 4)
    log(f"[BG] Drawing anagrams for {words} random words...")
    run_draw_anagram_on_matrix(words, 'both')

def scene_math_gof():
    steps = random.randint(50, 150)
    log(f"[BG] Starting Math-GoL for {steps} steps...")
    run_math_funs_game_of_life(steps, 0.05)

def scene_math_graphs():
    num = random.randint(3, 7)
    log(f"[BG] Showing {num} random math graphs...")
    show_random_graphs(num, 3.0, 'both')

def scene_random_noise():
    duration = random.randint(5, 15)
    log(f"[BG] Showing random noise for {duration} seconds...")
    random_greyscale_animation(animate=True, duration_sec=duration)

SCENES = [
    scene_game_of_life,
    scene_outer_totalistic,
    scene_inner_totalistic,
    scene_bml_traffic,
    scene_hpp_gas,
    scene_anagrams,
    scene_math_gof,
    scene_math_graphs,
    scene_random_noise
]

def run_background_mode():
    """
    Main loop for background runner.
    """
    log("--- Starting Background Runner ---")
    log("Press Ctrl+C to stop.")
    
    try:
        while True:
            # Pick a random scene
            scene = random.choice(SCENES)
            
            try:
                scene()
                # Brief pause between scenes
                time.sleep(1.0)
                reset_modules()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                log(f"[BG] Error in scene {scene.__name__}: {e}")
                # Log traceback for debugging if needed
                # import traceback
                # traceback.print_exc()
                time.sleep(2.0)
                reset_modules()

    except KeyboardInterrupt:
        log("\nBackground runner stopped by user.")
    finally:
        reset_modules()
        log("Modules reset.")

if __name__ == "__main__":
    run_background_mode()
