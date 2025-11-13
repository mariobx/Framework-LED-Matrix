import numpy as np
import cellpylib as cpl
from led_matrix_commands import log, WIDTH, HEIGHT, coordinates_to_matrix

STARTING_STATES_GOF = {
    "blinker": coordinates_to_matrix([[17, 3], [17, 4], [17, 5]]),
    "toad": coordinates_to_matrix([[17, 3], [17, 4], [17, 5], [18, 2], [18, 3], [18, 4]]),
    "pentadecathlon": coordinates_to_matrix([
        [12, 4], [13, 4], [14, 2], [14, 4], [14, 6], [15, 4], [16, 4],
        [17, 4], [18, 4], [19, 2], [19, 4], [19, 6], [20, 4], [21, 4]
    ]),
    "glider": coordinates_to_matrix([[1, 2], [2, 3], [3, 1], [3, 2], [3, 3]]),
    "lwss": coordinates_to_matrix([
        [17, 3], [17, 5], [18, 2], [19, 2], [19, 5],
        [20, 2], [20, 3], [20, 4], [20, 5]
    ]),
    "r_pentomino": coordinates_to_matrix([[17, 4], [17, 5], [18, 3], [18, 4], [19, 4]]),
    "diehard": coordinates_to_matrix([
        [17, 7], [18, 1], [18, 2], [19, 2], [19, 5], [19, 6], [19, 7]
    ]),
    "acorn": coordinates_to_matrix([
        [17, 2], [18, 4], [19, 1], [19, 2], [19, 5], [19, 6], [19, 7]
    ]),
    "block": coordinates_to_matrix([[17, 3], [17, 4], [18, 3], [18, 4]]),
    "beehive": coordinates_to_matrix([[17, 3], [17, 4], [18, 2], [18, 5], [19, 3], [19, 4]]),
    "r_pentomino": coordinates_to_matrix([[17, 4], [17, 5], [18, 3], [18, 4], [19, 4]]),
}


game_of_life_rules = {
    'Original': {'B': [3], 'S': [2, 3]},
    'HighLife': {'B': [3, 6], 'S': [2, 3]},
    'Day & Night': {'B': [3, 6, 7, 8], 'S': [3, 4, 6, 7, 8]},
    'Seeds': {'B': [2], 'S': []},
}
    

def run_outer_totalistic_ca(
    initial_state: np.ndarray, 
    timesteps: int, 
    b_rule: list[int], 
    s_rule: list[int]
) -> np.ndarray:
    """
    Runs a general binary Outer-Totalistic (B/S) CA for 'timesteps'.
    This is the system used by Conway's Game of Life.
    
    Args:
        initial_state: The 2D (H, W) NumPy array to start with.
        timesteps: The number of generations to evolve.
        b_rule: A list of neighbor counts to "Birth" a dead cell (e.g., [3]).
        s_rule: A list of neighbor counts to "Survive" a live cell (e.g., [2, 3]).
    
    Returns:
        A 3D NumPy array of shape (timesteps + 1, HEIGHT, WIDTH)
    """
    log(f"Outer-Totalistic CA: Running B{b_rule}/S{s_rule} for {timesteps} steps.")
    
    # Use sets for fast 'in' lookups
    b_set = set(b_rule)
    s_set = set(s_rule)
    
    def outer_totalistic_rule(neighbourhood: np.ndarray, c_coord: tuple, t: int) -> int:
        """
        The custom 'apply_rule' function that implements B/S logic.
        
        Args:
            neighbourhood: The 2D (3x3) NumPy array (Moore neighborhood).
            c_coord (tuple): The (row, col) coordinate (unused).
            t (int): The current timestep (unused).
        """
        
        # Get the 8-neighbor sum (total sum - center cell)
        neighbor_sum = np.sum(neighbourhood) - neighbourhood[1, 1]
        
        # Get the center cell's current state
        center_val = neighbourhood[1, 1]
        
        if center_val == 1:
            # Cell is ALIVE, check SURVIVAL rule
            if neighbor_sum in s_set:
                return 1  # Survive
            else:
                return 0  # Die
        else:
            # Cell is DEAD, check BIRTH rule
            if neighbor_sum in b_set:
                return 1  # Born
            else:
                return 0  # Stay dead
                
    # Wrap initial state into a 3D array (shape [1, H, W])
    initial_state_3d = np.array([initial_state])
    
    # Evolve and return the history
    all_generations = cpl.evolve2d(
        cellular_automaton=initial_state_3d,
        timesteps=timesteps,
        neighbourhood='Moore', # B/S rules require the 8-neighbor Moore
        apply_rule=outer_totalistic_rule
    )
    return all_generations

