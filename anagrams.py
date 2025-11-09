from gameOfLife import run_game_of_life
from led_matrix_commands import start_animation, stop_animation, reset_modules
import nltk
import time
from nltk.corpus import words
from led_matrix_commands import log
from text import draw_text_vertical

def draw_anagram_on_matrix(word: str, which: str = 'both', animate: bool = True):
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
        draw_text_vertical(w, which=which)
        log(f"draw_anagram_on_matrix: rendered '{w}', toggling animation briefly")
        stop_animation()
        time.sleep(2)
        start_animation() if animate else stop_animation()
        time.sleep(5)
    log("draw_anagram_on_matrix: finished rendering all anagrams, resetting modules")
    reset_modules()
    

def anagrams_game_of_life(word: str, generations: int = 100, delay_sec: float = 0.1, which: str = 'both'):
    """Runs Game of Life using an anagram of the given word as the starting pattern."""
    log(f"anagrams_game_of_life: start word='{word}' generations={generations} delay_sec={delay_sec} which={which}")
    log("anagrams_game_of_life: ensuring 'words' corpus is available")
    nltk.download('words', quiet=True)
    ana_lst = anagrams(word)
    ana_lst.add(word)
    ana_lst = list(ana_lst)
    log(f"anagrams_game_of_life: will run GoL for {len(ana_lst)} strings: {ana_lst}")
    for w in ana_lst:
        log(f"anagrams_game_of_life: running GoL for '{w}'")
        matrix = draw_text_vertical(w)
        time.sleep(2)
        run_game_of_life(
            initial_board=matrix,
            generations=generations,
            delay_sec=delay_sec,
            which=which
        )
        log(f"anagrams_game_of_life: completed GoL for '{w}', resetting modules briefly")
        reset_modules()
        time.sleep(2)
    log("anagrams_game_of_life: finished all anagrams, resetting modules")
    reset_modules()

def anagrams(word):
    log(f"anagrams: finding anagrams for '{word}'")
    word_sorted = sorted(word)
    result = set(w for w in words.words() if sorted(w) == word_sorted)
    log(f"anagrams: found {len(result)} candidates")
    return result