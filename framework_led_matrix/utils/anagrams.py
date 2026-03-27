from framework_led_matrix.simulations.outer_totalistic import run_outer_totalistic_ca
from framework_led_matrix.core.led_commands import start_animation, stop_animation, reset_modules, log
from framework_led_matrix.utils.text_rendering import draw_text_vertical
import nltk
import time

def ensure_nltk_words():
    """Ensures the 'words' corpus is downloaded."""
    try:
        nltk.data.find('corpora/words')
    except (LookupError, AttributeError):
        log("NLTK 'words' corpus not found. Downloading...")
        nltk.download('words', quiet=True)

def draw_anagram_on_matrix(word: str, which: str = 'both', animate: bool = True):
    """Draws an anagram of the given word on the LED matrix."""
    log(f"draw_anagram_on_matrix: start word='{word}' which={which}")
    ensure_nltk_words()
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

def anagrams(word):
    log(f"anagrams: finding anagrams for '{word}'")
    word_sorted = sorted(word)
    result = set(w for w in words.words() if sorted(w) == word_sorted)
    log(f"anagrams: found {len(result)} candidates")
    return result