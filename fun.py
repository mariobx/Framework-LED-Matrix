from typing import List
from function_grapher_led import *
import nltk
import time
import math
import copy
from nltk.corpus import words
from math_funs import math_operations, STARTING_STATES_GOF
import random

log = VerboseLogger()
log.verbose = verbose

def random_greyscale_animation(animate: bool = True, duration_seconds: int = 10):
    log(f"random_greyscale_animation: start animate={animate} duration_seconds={duration_seconds}")
    matrix = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
    if animate:
        log("random_greyscale_animation: starting hardware animation")
        start_animation()
    else:
        log("random_greyscale_animation: ensuring animation stopped")
        stop_animation()

    timeout_start = time.time()
    frames = 0
    while time.time() < timeout_start + duration_seconds:
        frames += 1
        # fill matrix with random brightness
        for row in range(HEIGHT):
            for col in range(WIDTH):
                brightness = int(random.triangular(0, 255, 0))
                set_led(matrix, row, col, brightness)
        draw_greyscale_on_board(matrix, which='both')
        # log periodically to avoid overwhelming logs
        if frames % 10 == 0:
            remaining = max(0, timeout_start + duration_seconds - time.time())
            log(f"random_greyscale_animation: frames={frames} time_remaining={remaining:.1f}s")
    log(f"random_greyscale_animation: completed frames={frames}")
    stop_animation()
    clear_graph()
    log("random_greyscale_animation: stopped animation and cleared display")


def anagrams(word):
    log(f"anagrams: finding anagrams for '{word}'")
    word_sorted = sorted(word)
    result = set(w for w in words.words() if sorted(w) == word_sorted)
    log(f"anagrams: found {len(result)} candidates")
    return result

def draw_anagram_on_matrix(word: str, which: str = 'both'):
    """Draws an anagram of the given word on the LED matrix."""
    log(f"draw_anagram_on_matrix: start word='{word}' which={which}")
    log("draw_anagram_on_matrix: ensuring 'words' corpus is available")
    nltk.download('words', quiet=True)
    ana_lst = anagrams(word)
    ana_lst.add(word)
    ana_lst = list(ana_lst)
    log(f"draw_anagram_on_matrix: will render {len(ana_lst)} strings: {ana_lst}")
    for w in ana_lst:
        log(f"draw_anagram_on_matrix: rendering '{w}' on matrix (vertical)")
        draw_text_vertical(w, font_size=7, which=which)
        log(f"draw_anagram_on_matrix: rendered '{w}', toggling animation briefly")
        stop_animation()
        time.sleep(2)
        start_animation()
        time.sleep(5)
    log("draw_anagram_on_matrix: finished rendering all anagrams, resetting modules")
    reset_modules()

def calculate_next_gen(board: List[List[int]]) -> None:
    """
    Calculates the next generation of the Game of Life using a toroidal
    (wrapping) grid.
    Modifies the board in-place.
    """
    reading_board = copy.deepcopy(board)
    
    dead = 0
    live = 1
    
    # Get the dimensions of the board
    num_rows = len(board)
    num_cols = len(board[0])

    for r in range(num_rows):
        for c in range(num_cols):            
            neighbor_count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue

                    # Calculate neighbor coordinates using the modulo operator for wrapping
                    nr = (r + dr) % num_rows
                    nc = (c + dc) % num_cols
                    
                    if reading_board[nr][nc] == live:
                        neighbor_count += 1

            status = reading_board[r][c]
            if status == live and neighbor_count < 2:
                board[r][c] = dead
            elif status == live and (neighbor_count == 2 or neighbor_count == 3):
                board[r][c] = live
            elif status == live and neighbor_count > 3:
                board[r][c] = dead
            elif status == dead and neighbor_count == 3:
                board[r][c] = live


def run_game_of_life(
    pattern_name: Optional[str] = None, 
    initial_board: Optional[List[List[int]]] = None,
    generations: int = 200, 
    delay_sec: float = 0.1, 
    which: str = 'both'
):
    """
    Runs Conway's Game of Life on the LED matrix.
    
    You MUST provide ONE of pattern_name or initial_board.
    
    Args:
        pattern_name (str, optional): The key of the pattern in STARTING_STATES_GOF.
        initial_board (list[list[int]], optional): A 34x9 matrix to start from.
        generations (int): Number of generations to run.
        delay_sec (float): Time to pause between generations.
        which (str): Which module to draw on ('left', 'right', 'both').
    """
    log(f"run_game_of_life: starting generations={generations}.")
    
    board = [] # Initialize board

    if initial_board is not None:
        log("run_game_of_life: using provided initial_board.")
        board = copy.deepcopy(initial_board)
        
    elif pattern_name is not None:
        log(f"run_game_of_life: loading pattern_name='{pattern_name}'")
        if pattern_name not in STARTING_STATES_GOF:
            log(f"run_game_of_life: Error - pattern '{pattern_name}' not found.")
            print(f"Error: Pattern '{pattern_name}' not found.")
            print(f"Available patterns: {list(STARTING_STATES_GOF.keys())}")
            return
            
        starting_coords = STARTING_STATES_GOF[pattern_name]
        board = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        
        pixels_seeded = 0
        for r, c in starting_coords:
            if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                board[r][c] = 1  # 1 = live
                pixels_seeded += 1
        log(f"run_game_of_life: seeded {pixels_seeded} live cells.")
        
    else:
        log("run_game_of_life: Error - You must provide 'pattern_name' or 'initial_board'.")
        print("Error: run_game_of_life requires 'pattern_name' or 'initial_board'.")
        return

    # --- NEW: Counters and history for all stop conditions ---
    stable_counter = 0
    oscillator_counter = 0
    board_previous = [] # Will store Gen N
    board_two_ago = []  # Will store Gen N-1
    # --------------------------------------------------------

    try:
        for i in range(generations):
            draw_matrix_on_board(board, which=which)
            time.sleep(delay_sec)
            calculate_next_gen(board)
            # --- Check for empty board (Stop Condition 1) ---
            if not any(1 for row in board for cell in row if cell == 1):
                log(f"run_game_of_life: Board is empty after generation {i+1}. Halting.")
                draw_matrix_on_board(board, which=which)
                time.sleep(0.5)
                break
            # --- Check for stable board (Stop Condition 2) ---
            if board == board_previous:
                stable_counter += 1
                oscillator_counter = 0 # Reset other counter
                log(f"run_game_of_life: Board state stable. Count: {stable_counter}")
            # --- Check for oscillator (Stop Condition 3) ---
            elif board == board_two_ago:
                oscillator_counter += 1
                stable_counter = 0 # Reset other counter
                log(f"run_game_of_life: Board state oscillating (P=2). Count: {oscillator_counter}")
            else:
                stable_counter = 0
                oscillator_counter = 0
            # --- Check counters for halting ---
            if stable_counter >= 10:
                log(f"run_game_of_life: Board state stable for 10 generations. Halting.")
                time.sleep(0.5)
                break
            
            if oscillator_counter >= 10:
                log(f"run_game_of_life: Board state oscillating for 10 generations (20 cycles). Halting.")
                time.sleep(0.5)
                break
            board_two_ago = copy.deepcopy(board_previous)
            board_previous = copy.deepcopy(board)
            if i % 20 == 0:
                log(f"run_game_of_life: generation {i+1}/{generations}")

    except KeyboardInterrupt:
        log("run_game_of_life: KeyboardInterrupt received, stopping.")
    finally:
        log(f"run_game_of_life: simulation finished.")
        clear_graph()
        log("run_game_of_life: cleared display.")

def run_stuff():
    for n in math_operations:
        create_graph_with_horizontal_x_axis(False, n, True)
        time.sleep(3)
        run_game_of_life(
            initial_board=create_graph_with_horizontal_x_axis(False, n, True),
            generations=100,
            delay_sec=0.2,
            which='both'
        )
        clear_graph()
        time.sleep(1)

if __name__ == "__main__":
    log("fun.py: __main__ entry - running run_stuff()")
    try:
        run_stuff()
    finally:
        log("fun.py: __main__ exit - resetting modules")
        reset_modules()
