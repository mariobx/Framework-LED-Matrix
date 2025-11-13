from led_matrix_commands import log, draw_greyscale_on_board, set_led, clear_graph, start_animation, stop_animation, draw_matrix_on_board, reset_modules, WIDTH, HEIGHT, coordinates_to_matrix
from BihamMiddletonLevineTrafficModel import run_bml
from anagrams import draw_anagram_on_matrix, words, anagrams
from text import draw_text_vertical
from mathFunctions import MATH_OPERATIONS, pick_largest_graph
from inner_totalistic_ca import run_totalistic_ca
from outer_totalistic import run_outer_totalistic_ca, game_of_life_rules, STARTING_STATES_GOF
from typing import List, Optional
from HardyPomeauPazzis import run_hpp_simulation, create_hpp_board_np
import random
import time
import numpy as np


def run_hpp_with_math(density: float = 0.3, timesteps: int = 500, delay_sec: float = 0.1, graphs_count: int = 5):
    log("HPP: Running HPP simulation with math function graphs.")
    for func in random.sample(MATH_OPERATIONS, graphs_count):
        func = pick_largest_graph(func)
        draw_matrix_on_board(func)
        func = create_hpp_board_np(initial_state=np.array(func))
        time.sleep(3)
        run_hpp_simulation(
            initial_state=func,
            density=density,
            timesteps=timesteps,
            delay_sec=delay_sec,
            which='both'
        )

def run_outer_totalistic_simulation(initial_state: Optional[List[List[int]]] = None, b_rule: Optional[List[int]] = None, s_rule: Optional[List[int]] = None, timesteps: int = 100, delay_sec: float = 0.1, oscilation_max_steps: int = 20, still_board_max_steps: int = 10, empty_board_max_steps: int = 5):
    # normalize defaults to avoid mutable default arguments and satisfy type annotations
    if b_rule is None:
        b_rule = [3]
    if s_rule is None:
        s_rule = [2,3]

    initial_state_np = np.random.randint(0, 2, size=(HEIGHT, WIDTH), dtype=int) if initial_state is None else np.array(initial_state, dtype=int)
    log(f"Running Outer-Totalistic CA: B{b_rule}/S{s_rule} for {timesteps} steps.")
    all_generations = run_outer_totalistic_ca(initial_state_np, timesteps, b_rule, s_rule)
    oscilation_counter = 0
    still_board_counter = 0
    empty_board_counter = 0
    for t in range(all_generations.shape[0]):
        frame_np = all_generations[t] 
        frame_list = frame_np.tolist()
        draw_matrix_on_board(frame_list, which='both')
        time.sleep(delay_sec)
        #oscilation
        if all_generations[t].tolist() == all_generations[t-2].tolist() and t >=2:
            oscilation_counter +=1
            if oscilation_counter >= oscilation_max_steps:
                log(f"oscillation at step {t-oscilation_max_steps}. Ending simulation.")
                break
        else:
            oscilation_counter = 0

        # still life
        if np.all(frame_np == 0):
            still_board_counter += 1
            if still_board_counter >= still_board_max_steps:
                log(f"still life detected at step {t-still_board_max_steps}. Ending simulation.")
                break
        else:
            still_board_counter = 0

        # empty board
        if np.all(frame_np == 0):
            empty_board_counter += 1
            if empty_board_counter >= empty_board_max_steps:
                log(f"empty board detected at step {t-empty_board_max_steps}. Ending simulation.")
                break
        else:
            empty_board_counter = 0


def game_of_life_totalistic_sim(initial_board: Optional[List[List[int]]] = None, generations: int = 200, delay_sec: float = 0.1, which: str = 'both'):
    initial_state_np = np.array(initial_board, dtype=int) if initial_board is not None else np.random.randint(0, 2, size=(HEIGHT, WIDTH), dtype=int)
    b_rule = game_of_life_rules['Original']['B']
    s_rule = game_of_life_rules['Original']['S']
    run_outer_totalistic_simulation(initial_state_np.tolist(), b_rule, s_rule, generations, delay_sec)
        

def run_bml_simulation(density: float = 0.3, timesteps: int = 100, delay_sec: float = 0.1):
    run_bml(density=density, steps=timesteps, delay_sec=delay_sec)

def run_inner_totalistic_simulation(initial_state: Optional[List[List[int]]] = None, rule_number: int = 777, timesteps: int = 200, delay_sec: float = 0.1):
    initial_state_np = np.array(initial_state, dtype=int) if initial_state is not None else np.random.randint(0, 2, size=(HEIGHT, WIDTH), dtype=int)
    log(f"Running Inner-Totalistic CA: rule={rule_number} for {timesteps} steps.")
    all_generations = run_totalistic_ca(initial_state_np, timesteps, rule_number)

    try:
        for t in range(all_generations.shape[0]):
            frame_np = all_generations[t]
            frame_list = frame_np.tolist()
            draw_matrix_on_board(frame_list, which='both')
            time.sleep(delay_sec)

    except KeyboardInterrupt:
        log("Animation stopped by user.")
        clear_graph()

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

def run_anagrams_game_of_life(word_limit: int = 4, generations: int = 100, delay_sec: float = 0.1, which: str = 'both'):
    log("runtime.py: run_anagrams_game_of_life() entry")
    eligible_words = [word for word in words.words() if len(word) <= 7]
    actual_limit = min(word_limit, len(eligible_words))
    for word in random.sample(eligible_words, actual_limit):
        ana_lst = anagrams(word)
        ana_lst.add(word)
        ana_lst = list(ana_lst)
        for w in ana_lst:
            log(f"runtime.py: run_anagrams_game_of_life() rendering word '{w}'")
            matrix = draw_text_vertical(w, which=which)
            time.sleep(2)
            start_animation()
            time.sleep(5)
            stop_animation()
            draw_text_vertical(w, which=which)
            game_of_life_totalistic_sim(initial_board=matrix, generations=generations, delay_sec=delay_sec, which=which)

def run_draw_anagram_on_matrix(word_limit: int = 3, which: str = 'both'):
    log("runtime.py: run_draw_anagram_on_matrix() entry")
    eligible_words = [word for word in words.words() if len(word) <= 7]
    actual_limit = min(word_limit, len(eligible_words))
    for word in random.sample(eligible_words, actual_limit):
        draw_anagram_on_matrix(word, which=which, animate=True)


def run_math_funs_game_of_life(generations: int = 100, delay_sec: float = 0.1):
    for func in random.sample(MATH_OPERATIONS, len(MATH_OPERATIONS)):
        func = pick_largest_graph(func)
        draw_matrix_on_board(func)
        time.sleep(3)
        game_of_life_totalistic_sim(initial_board=func, generations=generations, delay_sec=delay_sec, which='both')

def show_random_graphs(num_graphs: int = 5, delay_sec: float = 2.0, which: str = 'both'):
    log(f"show_random_graphs: start num_graphs={num_graphs} delay_sec={delay_sec} which={which}")
    for i in range(num_graphs):
        func = random.choice(MATH_OPERATIONS)
        log(f"show_random_graphs: graph {i+1}/{num_graphs}, selected function {func.__name__}")
        graph_matrix = pick_largest_graph(func)
        draw_matrix_on_board(graph_matrix, which=which)
        time.sleep(delay_sec)
    log("show_random_graphs: completed all graphs, clearing display")
    clear_graph()


try:
    run_outer_totalistic_simulation(initial_state=STARTING_STATES_GOF['lwss'], b_rule=game_of_life_rules['Original']['B'], s_rule=game_of_life_rules['Original']['S'], timesteps=500, delay_sec=0.001)
finally:
    reset_modules()
