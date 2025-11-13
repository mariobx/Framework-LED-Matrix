import numpy as np
import cellpylib as cpl
from led_matrix_commands import log, WIDTH, HEIGHT



def create_simple_state(k: int = 2, val: int = 1) -> np.ndarray:
    """Creates a 2D (HEIGHT, WIDTH) array of zeros with a single 'val' at the center."""
    log(f"CPL Helpers: Creating simple center-seed state (val={val})")
    board = np.zeros((HEIGHT, WIDTH), dtype=int)
    board[HEIGHT // 2, WIDTH // 2] = val
    return board

def run_totalistic_ca(initial_state: np.ndarray, timesteps: int, rule_number: int) -> np.ndarray:
    """
    Runs a k=2 (binary) totalistic CA for 'timesteps'.
    
    The rule is based on the *sum* of the 8 'Moore' neighbors + center.
    'rule_number' is the NKS-style rule number for k=2.
    
    Returns:
        A 3D NumPy array of shape (timesteps + 1, HEIGHT, WIDTH)
    """
    k = 2
    log(f"Totalistic CA (k=2): Running (rule={rule_number}) for {timesteps} steps.")
    
    rule_func = lambda n, c_coord, t: cpl.totalistic_rule(n, k=k, rule=rule_number)
    
    initial_state_3d = np.array([initial_state])
    
    all_generations = cpl.evolve2d(
        cellular_automaton=initial_state_3d,
        timesteps=timesteps,
        neighbourhood='Moore',
        apply_rule=rule_func
    )
    return all_generations


if __name__ == "__main__":
    # Test block
    log("--- Testing Totalistic CA ---")
    init_state = create_simple_state(k=3, val=1)
    # Rule 777 is a 3-color replicator
    history = run_totalistic_ca(init_state, timesteps=50, rule_number=777)
    log(f"History shape: {history.shape}")
    log("Test complete.")