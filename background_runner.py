import time
import random
import sys
import traceback
import nltk
from nltk.corpus import words

# Import existing modules
from led_matrix_commands import log, clear_graph, reset_modules, WIDTH, HEIGHT
from outer_totalistic import run_outer_totalistic_ca, game_of_life_rules, STARTING_STATES_GOF
from inner_totalistic_ca import run_totalistic_ca, INTERESTING_RULES
from BihamMiddletonLevineTrafficModel import run_bml
from HardyPomeauPazzis import run_hpp_simulation, get_hpp_starting_state
from mathFunctions import MATH_OPERATIONS, pick_largest_graph
from led_matrix_commands import draw_matrix_on_board
from text import draw_text_vertical
from anagrams import anagrams

def run_background_mode():
    """
    Runs the background mode, cycling through various simulations indefinitely.
    """
    # Force verbose logging off for background mode to keep console clean
    log.verbose = False
    print("Starting Background Mode. Press Ctrl+C to exit.")

    # Ensure NLTK words are available
    try:
        nltk.data.find('corpora/words')
    except LookupError:
        print("Downloading NLTK words corpus...")
        nltk.download('words', quiet=True)

    while True:
        try:
            # Randomly select a scene type
            scene_type = random.choice([
                'outer_ca', 
                'inner_ca', 
                'bml', 
                'hpp', 
                'math_gol', 
                'scrolling_words'
            ])
            
            print(f"\n--- Switching to scene: {scene_type} ---")
            
            if scene_type == 'outer_ca':
                _run_outer_ca_scene()
            elif scene_type == 'inner_ca':
                _run_inner_ca_scene()
            elif scene_type == 'bml':
                _run_bml_scene()
            elif scene_type == 'hpp':
                _run_hpp_scene()
            elif scene_type == 'math_gol':
                _run_math_gol_scene()
            elif scene_type == 'scrolling_words':
                _run_scrolling_words_scene()
            
            # Transition delay
            time.sleep(1)
            clear_graph()
            
        except KeyboardInterrupt:
            print("\nBackground mode interrupted by user.")
            break
        except Exception as e:
            print(f"Error in background scene '{scene_type}': {e}")
            traceback.print_exc()
            # Wait a bit before retrying to avoid rapid error loops
            time.sleep(2)
            reset_modules()

    reset_modules()
    print("Background mode exited.")

def _run_outer_ca_scene():
    # Pick a random rule
    rule_name = random.choice(list(game_of_life_rules.keys()))
    rule = game_of_life_rules[rule_name]
    b_rule = rule['B']
    s_rule = rule['S']
    
    # Pick a random start state
    # 50% chance of random noise, 50% chance of a named pattern (if applicable)
    initial_state = None
    if random.random() < 0.5:
        # Use a named pattern if available, otherwise random
        pattern_name = random.choice(list(STARTING_STATES_GOF.keys()))
        # Note: STARTING_STATES_GOF values are lists of coords, need to convert to matrix if used directly
        # But run_outer_totalistic_simulation handles conversion if passed as list of lists
        # However, run_outer_totalistic_ca expects a numpy array.
        # Let's use the helper from runtime.py logic or just build it here.
        # For simplicity, let's just use random noise mostly, or specific patterns for standard GoL
        if rule_name == 'Original' or random.random() < 0.3:
             # Convert coord list to matrix
             coords = STARTING_STATES_GOF[pattern_name]
             import numpy as np
             initial_state = np.zeros((HEIGHT, WIDTH), dtype=int)
             for r, c in coords:
                 if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                     initial_state[r, c] = 1
             print(f"Rule: {rule_name}, Pattern: {pattern_name}")
        else:
             print(f"Rule: {rule_name}, Pattern: Random Noise")
    else:
        print(f"Rule: {rule_name}, Pattern: Random Noise")

    # Run simulation
    # We need to manually run the loop to handle the display, similar to runtime.py
    # but we want to keep it contained here.
    import numpy as np
    if initial_state is None:
        initial_state = np.random.randint(0, 2, size=(HEIGHT, WIDTH), dtype=int)
    
    steps = random.randint(100, 300)
    delay = 0.05
    
    # Using the low-level function from outer_totalistic
    generations = run_outer_totalistic_ca(initial_state, steps, b_rule, s_rule)
    
    for t in range(generations.shape[0]):
        frame = generations[t].tolist()
        draw_matrix_on_board(frame, which='both')
        time.sleep(delay)

def _run_inner_ca_scene():
    rule = random.choice(INTERESTING_RULES)
    steps = random.randint(100, 200)
    delay = 0.05
    print(f"Rule: {rule}")
    
    import numpy as np
    initial_state = np.zeros((HEIGHT, WIDTH), dtype=int)
    initial_state[HEIGHT // 2, WIDTH // 2] = 1 # Center seed
    
    # Or sometimes random row
    if random.random() < 0.3:
         initial_state = np.random.randint(0, 2, size=(HEIGHT, WIDTH), dtype=int)
    
    generations = run_totalistic_ca(initial_state, steps, rule)
    
    for t in range(generations.shape[0]):
        frame = generations[t].tolist()
        draw_matrix_on_board(frame, which='both')
        time.sleep(delay)

def _run_bml_scene():
    density = random.uniform(0.57, 0.8) # User requested >= 0.57
    steps = random.randint(300, 600)
    delay = 0.01 # User requested <= 0.01
    print(f"Density: {density:.2f}")
    
    run_bml(density=density, steps=steps, delay_sec=delay)

def _run_hpp_scene():
    state_names = [
        'Random', 'Central Block', 'Colliding Blocks', 'Four Corners', 
        'Central Void', 'Horizontal Stripe', 'Vertical Stripe', 
        'Checkerboard', 'Shear Flow', 'Explosion'
    ]
    name = random.choice(state_names)
    density = random.uniform(0.3, 0.7)
    steps = random.randint(300, 600)
    delay = 0.05
    print(f"State: {name}, Density: {density:.2f}")
    
    initial_state = get_hpp_starting_state(name, density)
    run_hpp_simulation(initial_state=initial_state, density=density, timesteps=steps, delay_sec=delay, which='both')

def _run_math_gol_scene():
    func = random.choice(MATH_OPERATIONS)
    print(f"Function: {func.__name__}")
    
    graph = pick_largest_graph(func)
    draw_matrix_on_board(graph, which='both')
    time.sleep(1)
    
    # Evolve with Game of Life
    steps = 100
    delay = 0.05
    import numpy as np
    initial_state = np.array(graph, dtype=int)
    rule = game_of_life_rules['Original']
    
    generations = run_outer_totalistic_ca(initial_state, steps, rule['B'], rule['S'])
    
    for t in range(generations.shape[0]):
        frame = generations[t].tolist()
        draw_matrix_on_board(frame, which='both')
        time.sleep(delay)

def _run_scrolling_words_scene():
    # Get random words
    eligible_words = [w for w in words.words() if 3 <= len(w) <= 7]
    # Pick 1-2 words
    num_words = random.randint(1, 2)
    selected_words = random.sample(eligible_words, num_words)
    print(f"Words: {selected_words}")
    
    for word in selected_words:
        # Vertical, auto font, low delay
        draw_text_vertical(word, font_size=None, which='both', row_offset=0)
        time.sleep(0.5)
        # Maybe flash it?
        time.sleep(1.5)
