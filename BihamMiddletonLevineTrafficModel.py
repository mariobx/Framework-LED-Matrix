from led_matrix_commands import log, draw_greyscale_on_board, clear_graph, WIDTH, HEIGHT
import copy
import random
import time
from typing import List

BML_EMPTY = 0
BML_RED_RIGHT = 1
BML_BLUE_DOWN = 2


def create_bml_board(density: float = 0.35) -> List[List[int]]:
    """
    Creates a new random board for the BML traffic model.
    
    Args:
        density (float): 0.0 to 1.0. Total percentage of cars.
                        Half will be red, half blue.
                        
    Returns:
        List[List[int]]: A 34x9 matrix with 0=Empty, 1=Red, 2=Blue.
    """
    log(f"BML: Creating new board with density {density}")
    board = [[BML_EMPTY for _ in range(WIDTH)] for _ in range(HEIGHT)]
    
    total_cells = WIDTH * HEIGHT
    num_cars = int(total_cells * density)
    num_red = num_cars // 2
    num_blue = num_cars - num_red
    
    cells = [(r, c) for r in range(HEIGHT) for c in range(WIDTH)]
    random.shuffle(cells)
    
    # Place red (right-moving) cars
    for i in range(num_red):
        r, c = cells.pop()
        board[r][c] = BML_RED_RIGHT
        
    # Place blue (down-moving) cars
    for i in range(num_blue):
        r, c = cells.pop()
        board[r][c] = BML_BLUE_DOWN
        
    log(f"BML: Seeded board with {num_red} red and {num_blue} blue cars.")
    return board

def step_bml_board(board: List[List[int]], move_red: bool) -> int:
    """
    Performs a single half-step (a "turn") of the BML model.
    Modifies the board in-place.
    
    Args:
        board: The 34x9 game board.
        move_red (bool): If True, moves red cars. If False, moves blue cars.
        
    Returns:
        int: The number of cars that successfully moved.
    """
    cars_moved = 0
    
    if move_red:
        board_before = copy.deepcopy(board)
        
        for r in range(HEIGHT):
            for c in range(WIDTH):
                if board_before[r][c] == BML_RED_RIGHT:
                    target_c = (c + 1) % WIDTH
                    if board_before[r][target_c] == BML_EMPTY:
                        board[r][c] = BML_EMPTY
                        board[r][target_c] = BML_RED_RIGHT
                        cars_moved += 1
                        
    else:
        board_before = copy.deepcopy(board)

        for r in range(HEIGHT):
            for c in range(WIDTH):
                if board_before[r][c] == BML_BLUE_DOWN:
                    target_r = (r + 1) % HEIGHT
                    if board_before[target_r][c] == BML_EMPTY:
                        board[r][c] = BML_EMPTY
                        board[target_r][c] = BML_BLUE_DOWN
                        cars_moved += 1
                        
    return cars_moved

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

def run_bml_traffic_model(
    density: float = 0.35,
    steps: int = 500,
    delay_sec: float = 0.1,
    which: str = 'both'
):
    """
    Runs the BML Traffic Model simulation.
    
    Args:
        density (float): Total car density (0.0 - 1.0).
        steps (int): Total number of half-steps to run.
        delay_sec (float): Time to pause between steps.
    """
    log(f"BML: Starting simulation. density={density}, steps={steps}")
    board = create_bml_board(density)
    
    # Start by moving red
    move_red_turn = True 
    
    try:
        for i in range(steps):
            # 1. Draw the current state
            draw_bml_board(board, which)
            time.sleep(delay_sec)
            
            # 2. Calculate the next state
            cars_moved = step_bml_board(board, move_red_turn)
            
            # 3. Log and swap turns
            turn_name = "Red (Right)" if move_red_turn else "Blue (Down)"
            log(f"BML: Step {i+1}/{steps} ({turn_name}). Moved {cars_moved} cars.")
            
            # If no cars moved, the model is in gridlock.
            if cars_moved == 0:
                log("BML: GRIDLOCK. No cars moved. Halting.")
                # Pause on the gridlocked state
                time.sleep(2)
                break
                
            # Swap to the other car color's turn
            move_red_turn = not move_red_turn
            
    except KeyboardInterrupt:
        log("BML: KeyboardInterrupt received, stopping.")
    finally:
        log(f"BML: simulation finished.")
        clear_graph()
        log("BML: cleared display.")

