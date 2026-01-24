#!/usr/bin/env python3

"""
hpp_lga_model.py

Implements the HPP (Hardy-Pomeau-Pazzis) Lattice Gas Automaton (LGA)
for the 34x9 LED matrix, using the cellpylib library.

This automaton models fluid dynamics using 4-bit particle states
and specific collision/propagation rules. It is NOT a totalistic
automaton and requires a custom 'apply_rule' function.
"""

import cellpylib as cpl
import numpy as np
import time
import random
from typing import List, Optional
from led_matrix_commands import log, clear_graph, WIDTH, HEIGHT, draw_matrix_on_board, reset_modules

# --- HPP Particle States (Bitmasks) ---
# A cell's state is the bitwise OR of the particles it contains.
EMPTY      = 0b0000  # 0
W_PARTICLE = 0b0001  # 1 (West-moving)
E_PARTICLE = 0b0010  # 2 (East-moving)
S_PARTICLE = 0b0100  # 4 (South-moving)
N_PARTICLE = 0b1000  # 8 (North-moving)

# --- HPP Collision States ---
# These are the only two states that result in a collision
WE_COLLIDE = W_PARTICLE | E_PARTICLE # 3 (West + East)
NS_COLLIDE = N_PARTICLE | S_PARTICLE # 12 (North + South)


def draw_hpp_board(board: List[List[int]], which: str):
    """
    Converts the 16-state HPP board to a regular matrix
    (0-1) and draws it.
    """
    matrix = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for r in range(HEIGHT):
        for c in range(WIDTH):
            state = board[r][c]
            if state != EMPTY:
                matrix[r][c] = 1  # Occupied
            else:
                matrix[r][c] = 0  # Empty
    draw_matrix_on_board(matrix, which)


def hpp_collide(state: int) -> int:
    """
    Computes the post-collision state for a single HPP cell.
    This is the first half of the HPP rule.
    """
    # N+S collision (12)
    if state == NS_COLLIDE: 
        return WE_COLLIDE  # Becomes E+W (3)
        
    # E+W collision (3)
    if state == WE_COLLIDE:
        return NS_COLLIDE  # Becomes N+S (12)
        
    # All other states (0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15)
    # pass through unchanged.
    return state


def hpp_lga_rule(neighbourhood: np.ndarray, c_coord: tuple, t: int) -> int:
    """
    The HPP rule function for cellpylib's evolve2d.
    This is the "Propagation" step. It calculates the new state of
    the center cell (1,1) by "gathering" all particles that will
    propagate *into* it from its 4 neighbors' *post-collision* states.
    
    Args:
        neighbourhood: The 2D (3x3) NumPy array (Moore neighborhood).
        c_coord (tuple): The (row, col) coordinate (unused).
        t (int): The current timestep (unused).
    """
    
    # 1. Get the pre-collision state of the 4 neighbors we care about.
    north_cell_pre_collide = neighbourhood[0, 1]
    south_cell_pre_collide = neighbourhood[2, 1]
    east_cell_pre_collide  = neighbourhood[1, 2]
    west_cell_pre_collide  = neighbourhood[1, 0]
    
    # 2. Compute the post-collision state for each neighbor.
    # This determines what particles are *available to move*
    n_post_collide = hpp_collide(north_cell_pre_collide)
    s_post_collide = hpp_collide(south_cell_pre_collide)
    e_post_collide = hpp_collide(east_cell_pre_collide)
    w_post_collide = hpp_collide(west_cell_pre_collide)
    
    # 3. "Gather" the particles that will arrive at the center cell.
    
    # The new North particle comes from the South neighbor's post-collision North particle.
    from_south = s_post_collide & N_PARTICLE
    
    # The new South particle comes from the North neighbor's post-collision South particle.
    from_north = n_post_collide & S_PARTICLE
    
    # The new West particle comes from the East neighbor's post-collision West particle.
    from_east = e_post_collide & W_PARTICLE
    
    # The new East particle comes from the West neighbor's post-collision East particle.
    from_west = w_post_collide & E_PARTICLE
    
    # The new state of the center cell is the bitwise OR 
    # of all particles that have propagated into it.
    new_center_state = from_north | from_south | from_east | from_west
    
    return new_center_state


def create_hpp_board_np(density: float = 0.5, initial_state: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Creates a new random board for the HPP model, or uses a provided one.
    
    If initial_state is provided, it is used directly.
    If initial_state is None, a new random board is generated
    based on the density.
    """
    if initial_state is not None:
        #take initial board, provide random particles movements
        for r in range(HEIGHT):
            for c in range(WIDTH):
                if initial_state[r, c] != EMPTY:
                    #random particle type to the occupied cell
                    initial_state[r, c] = random.choice([W_PARTICLE, E_PARTICLE, S_PARTICLE, N_PARTICLE])
        return initial_state

    log(f"HPP: Creating new NumPy board with particle density {density}")
    board = np.full((HEIGHT, WIDTH), EMPTY, dtype=int)
    
    total_cells = WIDTH * HEIGHT
    num_particles = int(total_cells * density)
    
    # Get a list of all possible single-particle states
    particle_types = [W_PARTICLE, E_PARTICLE, S_PARTICLE, N_PARTICLE]
    
    # Get a list of unique cells to populate
    cells_to_populate = random.sample(
        [(r, c) for r in range(HEIGHT) for c in range(WIDTH)], 
        num_particles
    )
    
    for r, c in cells_to_populate:
        # Assign a random particle type to the chosen cell
        board[r, c] = random.choice(particle_types)
        
    log(f"HPP: Seeded board with {num_particles} random particles.")
    return board


def run_hpp_simulation(
    initial_state: Optional[np.ndarray] = None,
    density: float = 0.5,
    timesteps: int = 500,
    delay_sec: float = 0.1,
    which: str = 'both'
):
    """
    Runs the HPP Lattice Gas Automaton simulation using cellpylib.
    """
    log(f"HPP: Starting simulation. density={density}, steps={timesteps}")
    
    # Use the create function, which respects the initial_state override
    initial_state_2d = create_hpp_board_np(density, initial_state)
    
    # Wrap in 3D array for cellpylib's evolve2d function
    initial_state_3d = np.array([initial_state_2d]) 
    
    log(f"HPP: Evolving {timesteps} steps...")
    
    # Evolve the cellular automaton
    all_generations = cpl.evolve2d(
        cellular_automaton=initial_state_3d,
        timesteps=timesteps,
        neighbourhood='Moore', # We need N,S,E,W neighbors
        apply_rule=hpp_lga_rule,
        r=1 # Radius 1
    )
    
    log(f"HPP: Evolution complete. Result shape: {all_generations.shape}")
    
    try:
        stable_counter = 0
        total_frames = all_generations.shape[0]

        for i in range(total_frames):            
            current_board_np = all_generations[i]            
            current_board_list = current_board_np.tolist()            
            
            # Draw the state to the LED matrix
            draw_hpp_board(current_board_list, which)
            time.sleep(delay_sec)
            
            if i % 20 == 0 or i == total_frames - 1:
                log(f"HPP: Step {i}/{timesteps}.")

            # Check for stable state (gridlock or empty)
            if i > 0:
                if np.array_equal(current_board_np, all_generations[i-1]):
                    stable_counter += 1
                else:
                    stable_counter = 0
            
            if stable_counter >= 20:
                log("HPP: State stable for 20 steps. Halting.")
                time.sleep(2)
                break
                
    except KeyboardInterrupt:
        log("HPP: KeyboardInterrupt received, stopping.")
    finally:
        log(f"HPP: simulation finished.")
        clear_graph()
        log("HPP: cleared display.")

def run_test_hpp():
    """
    Test function to run a sample HPP simulation.
    """
    matrix = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
    matrix[HEIGHT // 2][WIDTH // 2] = N_PARTICLE | S_PARTICLE
    matrix[HEIGHT // 2][(WIDTH // 2) - 1] = E_PARTICLE | W_PARTICLE
    board = create_hpp_board_np(initial_state=np.array(matrix))
    try:
        run_hpp_simulation(
            initial_state=board,
            density=0.3, 
            timesteps=200, 
            delay_sec=0.05, 
            which='both'
        )
    finally:
        reset_modules()

if __name__ == "__main__":
    run_test_hpp()