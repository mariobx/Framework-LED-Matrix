from led_matrix_commands import log, draw_greyscale_on_board, set_led, clear_graph, start_animation, stop_animation, draw_matrix_on_board, reset_modules, WIDTH, HEIGHT
from BihamMiddletonLevineTrafficModel import run_bml_traffic_model
from gameOfLife import run_game_of_life, STARTING_STATES_GOF
from anagrams import draw_anagram_on_matrix, anagrams_game_of_life, words
from mathFunctions import MATH_OPERATIONS, pick_largest_graph
import random
import time


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
        anagrams_game_of_life(word, generations=generations, delay_sec=delay_sec, which=which)

def run_draw_anagram_on_matrix(word_limit: int = 3, which: str = 'both'):
    log("runtime.py: run_draw_anagram_on_matrix() entry")

    eligible_words = [word for word in words.words() if len(word) <= 7]

    actual_limit = min(word_limit, len(eligible_words))

    for word in random.sample(eligible_words, actual_limit):
        draw_anagram_on_matrix(word, which=which, animate=True)
def run_math_funs_game_of_life(generations: int = 100, delay_sec: float = 0.1, which: str = 'both'):
    for func in random.sample(MATH_OPERATIONS, len(MATH_OPERATIONS)):
        func = pick_largest_graph(func)
        draw_matrix_on_board(func)
        time.sleep(3)
        run_game_of_life(
            initial_board=func,
            generations=generations,
            delay_sec=delay_sec,
            which=which
        )

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
    random_greyscale_animation(animate=True, duration_seconds=10)
    run_draw_anagram_on_matrix(word_limit=4, which='both')
finally:
    reset_modules()
