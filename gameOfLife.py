#I could not get the game of life command that was built in to work so I remade the game of life
from led_matrix_commands import log, draw_matrix_on_board, clear_graph, WIDTH, HEIGHT
import copy
import time
from typing import List, Optional
import random

STARTING_STATES_GOF = {
    # --- Classic Oscillators (Blinkers) ---
    "blinker": [
        # The simplest period-2 oscillator
        (17, 3), (17, 4), (17, 5)
    ],
    "toad": [
        # A period-2 oscillator
        (17, 3), (17, 4), (17, 5),
        (18, 2), (18, 3), (18, 4)
    ],
    "pentadecathlon": [
        # A period-15 oscillator, fits perfectly.
        (12, 4),
        (13, 4),
        (14, 2), (14, 4), (14, 6),
        (15, 4),
        (16, 4),
        (17, 4),
        (18, 4),
        (19, 2), (19, 4), (19, 6),
        (20, 4),
        (21, 4)
    ],

    # --- Spaceships (Travelers) ---
    "glider": [
        # The classic. Will now travel diagonally forever.
        (1, 2), 
        (2, 3), 
        (3, 1), (3, 2), (3, 3)
    ],
    "lwss": [
        # "Lightweight Spaceship", travels horizontally.
        # It will wrap the 9-column width very quickly.
        (17, 3), (17, 5),
        (18, 2),
        (19, 2), (19, 5),
        (20, 2), (20, 3), (20, 4), (20, 5)
    ],

    # --- Methuselahs (Long-Running) ---
    "r_pentomino": [
        # Stabilizes after 1103 generations
        (17, 4), (17, 5),
        (18, 3), (18, 4),
        (19, 4)
    ],
    "diehard": [
        # Dies after 130 generations
        (17, 7),
        (18, 1), (18, 2),
        (19, 2), (19, 5), (19, 6), (19, 7)
    ],
    "acorn": [
        # Runs for 5206 generations
        (17, 2),
        (18, 4),
        (19, 1), (19, 2), (19, 5), (19, 6), (19, 7)
    ],
    
    # --- Still Lifes (Stable) ---
    "block": [
        # The simplest stable pattern
        (17, 3), (17, 4),
        (18, 3), (18, 4)
    ],
    "beehive": [
        # Another common still life
        (17, 3), (17, 4),
        (18, 2), (18, 5),
        (19, 3), (19, 4)
    ]
}


def calculate_next_gen(board: List[List[int]]) -> None:
    """
    Calculates the next generation of the Game of Life using a toroidal
    (wrapping) grid.
    Modifies the board in-place.
    """
    reading_board = copy.deepcopy(board)
    
    dead = 0
    live = 1
    
    num_rows = len(board)
    num_cols = len(board[0])

    for r in range(num_rows):
        for c in range(num_cols):            
            neighbor_count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue

                    #neighbor coordinates using the modulo operator for wrapping
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
    
    board = []

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

    stable_counter = 0
    oscillator_counter = 0
    board_previous = []
    board_two_ago = []

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
                stable_counter = 0
                log(f"run_game_of_life: Board state oscillating (P=2). Count: {oscillator_counter}")
            else:
                stable_counter = 0
                oscillator_counter = 0
            # --- Check counters for halting ---
            if stable_counter >= 10:
                log(f"run_game_of_life: Board state stable for 10 generations. Halting.")
                time.sleep(0.5)
                break
            
            if oscillator_counter >= 20:
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

def show_preset_gol():
    """Picks a random preset GoL pattern and displays its name first."""
    log("runtime.show: 'show_preset_gol_with_title'")
    
    # Pick a random preset
    pattern_name = random.choice(list(STARTING_STATES_GOF.keys()))
    log(f"show_preset_gol_with_title: selected '{pattern_name}'")

    # Run the pattern
    run_game_of_life(
        pattern_name=pattern_name,
        generations=300,
        delay_sec=0.2,
        which='both'
    )
    time.sleep(1)
    



