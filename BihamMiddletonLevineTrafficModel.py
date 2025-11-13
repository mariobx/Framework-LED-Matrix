import cellpylib as cpl
import numpy as np
import time
import random
from led_matrix_commands import log, clear_graph, WIDTH, HEIGHT, draw_greyscale_on_board
from typing import List


BML_EMPTY = 0
BML_RED_RIGHT = 1
BML_BLUE_DOWN = 2


def draw_bml_board(board: List[List[int]], which: str):
    """
    Converts the 3-state BML board (0,1,2) to a greyscale
    matrix (0, 255, 128) and draws it.
    """
    # We must use greyscale for three states
    greyscale_matrix = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for r in range(HEIGHT):
        for c in range(WIDTH):
            state = board[r][c]
            if state == BML_RED_RIGHT:
                greyscale_matrix[r][c] = 255 # Bright
            elif state == BML_BLUE_DOWN:
                greyscale_matrix[r][c] = 128 # Grey
            # else: 0 (Empty)
            
    draw_greyscale_on_board(greyscale_matrix, which)

def bml_rule(neighbourhood: np.ndarray, c_coord: tuple, t: int):
    """
    The BML rule for cellpylib's evolve2d.
    
    Args:
        neighbourhood: The 2D (3x3) NumPy array for the Moore neighborhood (r=1).
                        [[0,0(NW), 0,1(N), 0,2(NE)],
                        [1,0(W),  1,1(C), 1,2(E) ],
                        [2,0(SW), 2,1(S), 2,2(SE)]]
        c_coord (tuple): The (row, col) coordinate. We don't use this.
        t (int): The current timestep.
    """
    
    # --- Get the neighbors we care about from the 3x3 array ---
    # The (0,0) coordinate of the 3x3 grid is NW
    
    N = neighbourhood[0, 1]  # North neighbor
    W = neighbourhood[1, 0]  # West neighbor
    c = neighbourhood[1, 1]  # The CURRENT cell's value (Center)
    E = neighbourhood[1, 2]  # East neighbor
    S = neighbourhood[2, 1]  # South neighbor
    
    # t=0 is the initial state.
    # t=1, 3, 5... should be Red's turn
    # t=2, 4, 6... should be Blue's turn
    
    # On t=0 (initial state), do nothing, just return the current state.
    if t == 0:
        return c
        
    is_red_turn = (t % 2 == 1)
    
    if is_red_turn:
        # --- Red Turn Logic (Blue cars are static) ---
        
        # 1. Am I a RED car?
        if c == BML_RED_RIGHT:
            # Check my EAST neighbor. If it's EMPTY, I move out.
            return BML_EMPTY if E == BML_EMPTY else BML_RED_RIGHT
        
        # 2. Am I an EMPTY spot?
        if c == BML_EMPTY:
            # Check my WEST neighbor. If it's RED, it will move into me.
            return BML_RED_RIGHT if W == BML_RED_RIGHT else BML_EMPTY

        # 3. Am I a BLUE car?
        # if c == BML_BLUE_DOWN:
        return BML_BLUE_DOWN # Blue cars don't move on red turns

    else:
        # --- Blue Turn Logic (Red cars are static) ---
        
        # 1. Am I a BLUE car?
        if c == BML_BLUE_DOWN:
            # Check my SOUTH neighbor. If it's EMPTY, I move out.
            return BML_EMPTY if S == BML_EMPTY else BML_BLUE_DOWN
            
        # 2. Am I an EMPTY spot?
        if c == BML_EMPTY:
            # Check my NORTH neighbor. If it's BLUE, it will move into me.
            return BML_BLUE_DOWN if N == BML_BLUE_DOWN else BML_EMPTY
            
        # 3. Am I a RED car?
        # if c == BML_RED_RIGHT:
        return BML_RED_RIGHT # Red cars don't move on blue turns
    
def create_bml_board_np(density: float = 0.35) -> np.ndarray:
    """
    Creates a new random board for the BML traffic model as a NumPy array.
    (Adapted from your BihamMiddletonLevineTrafficModel.py)
    """
    log(f"BML (cpl): Creating new NumPy board with density {density}")
    board = np.full((HEIGHT, WIDTH), BML_EMPTY, dtype=int)
    
    total_cells = WIDTH * HEIGHT
    num_cars = int(total_cells * density)
    num_red = num_cars // 2
    num_blue = num_cars - num_red
    
    cells = [(r, c) for r in range(HEIGHT) for c in range(WIDTH)]
    random.shuffle(cells)
    
    # Place red (right-moving) cars
    for i in range(num_red):
        r, c = cells.pop()
        board[r, c] = BML_RED_RIGHT
        
    # Place blue (down-moving) cars
    for i in range(num_blue):
        r, c = cells.pop()
        board[r, c] = BML_BLUE_DOWN
        
    log(f"BML (cpl): Seeded board with {num_red} red and {num_blue} blue cars.")
    return board

def run_bml(
    density: float = 0.35,
    steps: int = 500, # Total half-steps (same as your original function)
    delay_sec: float = 0.1,
    which: str = 'both'
):
    """
    Runs the BML Traffic Model simulation using cellpylib.
    """
    log(f"BML (cpl): Starting simulation. density={density}, steps={steps}")
    
    initial_state_2d = create_bml_board_np(density)
    initial_state_3d = np.array([initial_state_2d]) 
    
    log(f"BML (cpl): Evolving {steps} half-steps...")
    
    all_half_steps = cpl.evolve2d(
        cellular_automaton=initial_state_3d,
        timesteps=steps,
        neighbourhood='Moore',
        apply_rule=bml_rule,
        r=1 
    )
    
    log(f"BML (cpl): Evolution complete. Result shape: {all_half_steps.shape}")
    
    try:
        stable_counter = 0
        total_frames = all_half_steps.shape[0]
        for i in range(total_frames):            
            current_board_np = all_half_steps[i]            
            current_board_list = current_board_np.tolist()            
            draw_bml_board(current_board_list, which)
            time.sleep(delay_sec)
            if i == 0:
                turn_name = "Initial State"
            else:
                turn_name = "Red (Right)" if (i % 2 == 1) else "Blue (Down)"
            if i % 20 == 0 or i == total_frames - 1:
                log(f"BML (cpl): Step {i}/{steps} ({turn_name}).")
            if i > 2:
                if np.array_equal(current_board_np, all_half_steps[i-2]):
                    stable_counter += 1
                else:
                    stable_counter = 0
            
            if stable_counter >= 20:
                log("BML (cpl): GRIDLOCK. State stable for 10 full cycles. Halting.")
                time.sleep(2)
                break
                
    except KeyboardInterrupt:
        log("BML (cpl): KeyboardInterrupt received, stopping.")
    finally:
        log(f"BML (cpl): simulation finished.")
        clear_graph()
        log("BML (cpl): cleared display.")

if __name__ == "__main__":
    try:
        run_bml(
            density=0.35, 
            steps=1000, 
            delay_sec=0.1, 
            which='both'
        )
    finally:
        clear_graph()
