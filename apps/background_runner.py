import time
import random
import sys
import traceback
from core.led_commands import log, reset_modules, clear_graph
from simulations.outer_totalistic import NAMED_RULES, STARTING_STATES_GOF

# Import simulation functions
from apps.runtime import (
    run_hpp_with_math,
    run_outer_totalistic_simulation,
    game_of_life_totalistic_sim,
    run_bml_simulation,
    run_inner_totalistic_simulation,
    random_greyscale_animation,
    run_anagrams_game_of_life,
    run_draw_anagram_on_matrix,
    run_math_funs_game_of_life,
    show_random_graphs
)
from utils.text_rendering import draw_text_horizontal

# --- SCENE DEFINITIONS ---

def scene_game_of_life():
    """Runs Game of Life with a random starting pattern."""
    pattern_name = random.choice(list(STARTING_STATES_GOF.keys()))
    log(f"Background: Running Game of Life ({pattern_name})")
    initial_board = STARTING_STATES_GOF[pattern_name]
    steps = random.randint(100, 300)
    game_of_life_totalistic_sim(initial_board, steps=steps, delay_sec=0.05, which='both')

def scene_outer_totalistic():
    """Runs a random Outer-Totalistic CA rule."""
    rule_name = random.choice(list(NAMED_RULES.keys()))
    b_rule, s_rule = NAMED_RULES[rule_name]
    log(f"Background: Running Outer-Totalistic CA ({rule_name})")
    steps = random.randint(100, 300)
    run_outer_totalistic_simulation(
        initial_state=None, # Random start
        b_rule=b_rule,
        s_rule=s_rule,
        timesteps=steps,
        delay_sec=0.05
    )

def scene_inner_totalistic():
    """Runs a random Inner-Totalistic (NKS) CA rule."""
    # Pick a random rule number. Some are boring, but that's part of the fun?
    # Let's stick to some known "interesting" ones or just random.
    # Rule 30, 90, 110, 184 are classics for 1D, but this is 2D totalistic.
    # Let's just pick a random int.
    rule = random.randint(1, 1000)
    log(f"Background: Running Inner-Totalistic CA (Rule {rule})")
    steps = random.randint(100, 200)
    run_inner_totalistic_simulation(None, rule, steps=steps, delay_sec=0.05)

def scene_bml_traffic():
    """Runs BML Traffic Model."""
    density = random.uniform(0.2, 0.6)
    log(f"Background: Running BML Traffic (density={density:.2f})")
    steps = random.randint(200, 500)
    run_bml_simulation(density=density, steps=steps, delay=0.02)

def scene_hpp_gas():
    """Runs HPP Lattice Gas simulation."""
    log("Background: Running HPP Lattice Gas")
    steps = random.randint(200, 400)
    # We don't have a direct run_hpp_simulation in imports, let's check runtime.py again or use run_hpp_with_math
    # Actually run_hpp_simulation is in HardyPomeauPazzis, but runtime has run_hpp_with_math.
    # Let's use run_hpp_with_math for more variety.
    graphs = random.randint(1, 3)
    run_hpp_with_math(density=0.3, steps=steps, delay=0.05, graphs=graphs)

def scene_math_graphs():
    """Shows random math graphs."""
    log("Background: Showing Math Graphs")
    num_graphs = random.randint(3, 6)
    show_random_graphs(num=num_graphs, delay=2.0, which='both')

def scene_random_words():
    """Scrolls random words."""
    words = ["HELLO", "WORLD", "PYTHON", "CODE", "MATRIX", "LED", "HACK", "MAKE", "BUILD", "CREATE"]
    word = random.choice(words)
    log(f"Background: Scrolling word '{word}'")
    draw_text_horizontal(word, font_size=None, which='both', x_offset=0, y_offset=0)
    time.sleep(2)

def scene_random_noise():
    """Shows random greyscale noise."""
    log("Background: Random Noise")
    duration = random.randint(5, 10)
    random_greyscale_animation(animate=True, duration=duration)

# List of available scenes
SCENES = [
    scene_game_of_life,
    scene_outer_totalistic,
    scene_inner_totalistic,
    scene_bml_traffic,
    scene_hpp_gas,
    scene_math_graphs,
    scene_random_words,
    scene_random_noise
]

def run_background_mode():
    """
    Main loop for the background runner.
    Cycles through scenes indefinitely until interrupted.
    """
    print("--- Starting Background Runner ---")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            # Pick a random scene
            scene = random.choice(SCENES)
            
            try:
                # Run the scene
                scene()
                
                # clear graph between scenes
                clear_graph()
                
                # Small pause between scenes
                time.sleep(1.0)
                
            except Exception as e:
                log(f"Error running scene {scene.__name__}: {e}")
                traceback.print_exc()
                # Wait a bit before trying next scene so we don't spam errors
                time.sleep(2.0)
                
    except KeyboardInterrupt:
        print("\nBackground runner stopped by user.")
    finally:
        reset_modules()
        print("Modules reset.")

if __name__ == "__main__":
    run_background_mode()
