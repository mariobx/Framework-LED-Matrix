#!/usr/bin/env python3

helper = """
Master Command-Line Interface (CLI) for the LED Matrix project.

This script provides a centralized way to run various functions
from the different modules of the project.

USAGE:
    python3 cli.py [COMMAND] [SUBCOMMAND] [OPTIONS]
    ./cli.py [COMMAND] [SUBCOMMAND] [OPTIONS] (if executable)

--- EXAMPLES BY COMMAND ---

[1] led: Basic hardware commands
    # Get firmware version from modules
    ./cli.py led version

    # Clear both displays (all LEDs OFF)
    ./cli.py led clear

    # Fill both displays and hold for 3 seconds
    ./cli.py led fill --hold 3

    # Start hardware fade/etc animation
    ./cli.py led start-anim

    # Stop hardware animation
    ./cli.py led stop-anim

    # Clear display and stop animation
    ./cli.py led reset

    # Show available serial ports (for debugging)
    ./cli.py led ports

[2] text: Render text on the matrix
    # Draw text vertically and hold for 5 seconds
    ./cli.py text vertical "HELLO" --hold 5

    # Draw text horizontally with a specific font size and offset
    ./cli.py text horizontal "Scrolling" --font-size 8 --x-offset 10

[3] anagram: Run anagram-related functions
    # Find and draw all anagrams for the word "post"
    ./cli.py anagram draw post

    # Do the same, but disable the animation between words
    ./cli.py anagram draw post --no-animate

[4] sim: Run complex cellular automata and simulations
    # Run Conway's Game of Life (B3/S23) from a random start
    ./cli.py sim gof

    # Run Game of Life with a specific pattern (glider)
    ./cli.py sim gof --board glider --steps 300 --delay 0.05

    # Run a CUSTOM Outer-Totalistic CA (e.g., "HighLife" B3,6/S2,3)
    # NOTE: Rules are now comma-separated.
    ./cli.py sim outer --b-rule "3,6" --s-rule "2,3"

    # Run a CUSTOM Inner-Totalistic CA (e.t., rule 777)
    # This takes a single number, so double/triple digits are fine.
    ./cli.py sim inner 777 --steps 100
    ./cli.py sim inner 1024 --steps 100

    # Run the BML traffic simulation
    ./cli.py sim bml --density 0.4 --steps 1000 --delay 0.02

    # Run the BML simulation LOCALLY (in a Matplotlib window)
    ./cli.py sim bml-local --density 0.4 --steps 1000

    # Run the HPP Lattice Gas simulation
    ./cli.py sim hpp --density 0.5 --steps 500

    # Run HPP, but seed the board with math function graphs
    ./cli.py sim hpp-math --graphs 3

    # Show random greyscale noise for 15 seconds
    ./cli.py sim random-grey --duration 15

    # Draw anagrams for 3 words, then run GoL on each
    ./cli.py sim anagram-gof --words 3

    # Show 10 random math graphs, pausing 3 sec each, and hold the last one
    ./cli.py sim math-graphs --num 10 --delay 3 --hold 5

[5] math: Run local math visualization tools
    # Plot a predefined function LOCALLY and on the MATRIX
    ./cli.py math plot sin
"""

import argparse
import sys
import time
import numpy as np
from typing import List, Optional

# --- Import All Necessary Functions ---
# We import from the new package structure.

try:
    # LED Matrix Core Commands
    from framework_led_matrix.core.led_commands import (
        log,
        reset_modules,
        get_firmware_version,
        clear_graph,
        fill_graph,
        start_animation,
        stop_animation,
        output_ports,
        WIDTH,
        HEIGHT,
        coordinates_to_matrix,
        draw_matrix_on_board
    )

    # Text Rendering
    from framework_led_matrix.utils.text_rendering import draw_text_vertical, draw_text_horizontal

    # Anagrams
    from framework_led_matrix.utils.anagrams import draw_anagram_on_matrix

    # Math Functions
    from framework_led_matrix.core.math_engine import (
        plot_function, 
        MATH_OPERATIONS, 
        pick_largest_graph, 
        REGULAR_OPERATIONS
    )
    
    # Simulation Models
    from framework_led_matrix.simulations.BihamMiddletonLevineTrafficModel import run_bml, show_bml_local_animation
    from framework_led_matrix.simulations.HardyPomeauPazzis import run_hpp_simulation, create_hpp_board_np
    from framework_led_matrix.simulations.outer_totalistic import STARTING_STATES_GOF, game_of_life_rules
    
    # Runtime Simulation Functions
    from framework_led_matrix.apps.runtime import (
        run_hpp_with_math,
        run_outer_totalistic_simulation,
        game_of_life_totalistic_sim,
        run_bml_simulation,
        run_inner_totalistic_simulation,
        random_greyscale_animation,
        run_anagrams_game_of_life,
        run_draw_anagram_on_matrix,
        run_math_funs_game_of_life,
        show_random_graphs
    )
    
    # Background Runner
    from framework_led_matrix.apps.background_runner import run_background_mode

except ImportError as e:
    print(f"Error: Failed to import a necessary module: {e}", file=sys.stderr)
    print("Please ensure you are running cli.py from the root directory", file=sys.stderr)
    print("of the graph_functions_on_matrix project.", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred during import: {e}", file=sys.stderr)
    sys.exit(1)


# --- Type-Parsing Helper Functions ---

def parse_int_list(list_str: str) -> List[int]:
    """Parses a comma-separated list of ints (e.g., '3,6,7') into a list."""
    if not list_str:
        return []
    try:
        # Allow empty strings to return empty lists
        if not list_str.strip():
            return []
        return [int(x.strip()) for x in list_str.split(',')]
    except Exception as e:
        raise argparse.ArgumentTypeError(f"Invalid integer list format: '{list_str}'. Must be comma-separated (e.g., '3,6,7'). Error: {e}")


# --- CLI Definition ---

def build_cli():
    """
    Builds the entire argparse CLI structure.
    """
    parser = argparse.ArgumentParser(
        description="Master CLI for LED Matrix controllers and simulations.",
        formatter_class=argparse.RawTextHelpFormatter,
        # Updated main epilog
        epilog="Run a command with -h for more specific help (e.g., ./cli.py sim gof -h)"
    )
    
    # --- ADDED: Top-level verbose flag ---
    parser.add_argument(
        '-v', '--verbose', 
        action='store_true', 
        help='Enable detailed verbose logging for all commands.'
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True, help='Main command category')

    # --- 0. Background Sub-parser ---
    subparsers.add_parser(
        'background', 
        aliases=['bg'],
        help='Run the background runner (screensaver mode).',
        epilog="Example: ./cli.py background"
    )

    # --- 1. LED Sub-parser ---
    led_parser = subparsers.add_parser(
        'led', 
        help='Basic hardware commands.',
        epilog="Example: ./cli.py led clear"
    )
    led_subparsers = led_parser.add_subparsers(dest='led_command', required=True, help='Specific LED command')
    
    led_subparsers.add_parser('version', help='Get firmware version from modules.', epilog="Example: ./cli.py led version")
    led_subparsers.add_parser('clear', help='Clear both displays (all LEDs OFF).', epilog="Example: ./cli.py led clear")
    
    # Add 'fill' command with hold argument
    led_fill = led_subparsers.add_parser(
        'fill', 
        help='Fill both displays (all LEDs ON).', 
        epilog="Example: ./cli.py led fill --hold 2"
    )
    led_fill.add_argument('--hold', type=float, default=0, help='Seconds to hold the filled screen (default: 0).')
    
    led_subparsers.add_parser('start-anim', help='Start hardware animation (e.g., fades).', epilog="Example: ./cli.py led start-anim")
    led_subparsers.add_parser('stop-anim', help='Stop hardware animation.', epilog="Example: ./cli.py led stop-anim")
    led_subparsers.add_parser('reset', help='Clear display and stop animation.', epilog="Example: ./cli.py led reset")
    led_subparsers.add_parser('ports', help='Show available serial ports (for debugging).', epilog="Example: ./cli.py led ports")

    # --- 2. Text Sub-parser ---
    text_parser = subparsers.add_parser(
        'text', 
        help='Render text on the matrix.',
        epilog="Example: ./cli.py text vertical \"HELLO\" --hold 3"
    )
    text_subparsers = text_parser.add_subparsers(dest='text_command', required=True, help='Specific text command')

    # 'text vertical' command
    text_vert = text_subparsers.add_parser(
        'vertical', 
        help='Draw text vertically.',
        epilog="Example: ./cli.py text vertical \"MY TEXT\" --font-size 10 --hold 3"
    )
    text_vert.add_argument('text', type=str, help='The text string to render.')
    text_vert.add_argument('--font-size', type=int, default=None, help='Force a specific font size (default: auto).')
    text_vert.add_argument('--which', type=str, default='both', choices=['left', 'right', 'both'], help='Which module to draw on.')
    text_vert.add_argument('--row-offset', type=int, default=0, help='Row offset from the top (default: 0).')
    text_vert.add_argument('--hold', type=float, default=0, help='Seconds to hold the text on screen after drawing (default: 0).')

    # 'text horizontal' command
    text_horiz = text_subparsers.add_parser(
        'horizontal', 
        help='Draw text horizontally.',
        epilog="Example: ./cli.py text horizontal \"SCROLL\" --x-offset 5 --hold 3"
    )
    text_horiz.add_argument('text', type=str, help='The text string to render.')
    text_horiz.add_argument('--font-size', type=int, default=None, help='Force a specific font size (default: auto).')
    text_horiz.add_argument('--which', type=str, default='both', choices=['left', 'right', 'both'], help='Which module to draw on.')
    text_horiz.add_argument('--x-offset', type=int, default=0, help='Horizontal scroll offset (default: 0).')
    text_horiz.add_argument('--y-offset', type=int, default=0, help='Vertical position offset (default: centered).')
    text_horiz.add_argument('--hold', type=float, default=0, help='Seconds to hold the text on screen after drawing (default: 0).')

    # --- 3. Anagram Sub-parser ---
    anagram_parser = subparsers.add_parser(
        'anagram', 
        help='Run anagram-related functions.',
        epilog="Example: ./cli.py anagram draw post"
    )
    anagram_subparsers = anagram_parser.add_subparsers(dest='anagram_command', required=True, help='Specific anagram command')

    # 'anagram draw' command
    ana_draw = anagram_subparsers.add_parser(
        'draw', 
        help='Find and draw anagrams for a word.',
        epilog="Example: ./cli.py anagram draw listen"
    )
    ana_draw.add_argument('word', type=str, help='The word to find anagrams for.')
    ana_draw.add_argument('--which', type=str, default='both', choices=['left', 'right', 'both'], help='Which module to draw on.')
    ana_draw.add_argument('--no-animate', action='store_false', dest='animate', help='Disable animation between words.')

    # --- 4. Simulation Sub-parser ---
    sim_parser = subparsers.add_parser(
        'sim', 
        help='Run complex simulations.',
        epilog="Example: ./cli.py sim gof --board glider --steps 100"
    )
    sim_subparsers = sim_parser.add_subparsers(dest='sim_command', required=True, help='Specific simulation to run')

    # 'sim bml' command
    sim_bml = sim_subparsers.add_parser(
        'bml', 
        help='Run BML traffic simulation on LED matrix.',
        epilog="Example: ./cli.py sim bml --density 0.4 --steps 1000 --delay 0.02"
    )
    sim_bml.add_argument('--density', type=float, default=0.35, help='Car density (0.0 to 1.0).')
    sim_bml.add_argument('--steps', type=int, default=500, help='Total half-steps to simulate.')
    sim_bml.add_argument('--delay', type=float, default=0.05, help='Delay in seconds between frames.')

    # 'sim bml-local' command
    sim_bml_local = sim_subparsers.add_parser(
        'bml-local', 
        help='Run BML sim locally in a Matplotlib window.',
        epilog="Example: ./cli.py sim bml-local --density 0.35 --steps 500"
    )
    sim_bml_local.add_argument('--density', type=float, default=0.35, help='Car density (0.0 to 1.0).')
    sim_bml_local.add_argument('--steps', type=int, default=500, help='Total half-steps to simulate.')

    # 'sim hpp' command
    sim_hpp = sim_subparsers.add_parser(
        'hpp', 
        help='Run HPP Lattice Gas simulation on LED matrix.',
        epilog="Example: ./cli.py sim hpp --density 0.5 --steps 500"
    )
    sim_hpp.add_argument('--density', type=float, default=0.5, help='Particle density (0.0 to 1.0).')
    sim_hpp.add_argument('--steps', type=int, default=500, help='Simulation steps.')
    sim_hpp.add_argument('--delay', type=float, default=0.05, help='Delay in seconds between frames.')
    sim_hpp.add_argument('--which', type=str, default='both', choices=['left', 'right', 'both'], help='Which module to draw on.')

    # 'sim hpp-math' command
    sim_hpp_math = sim_subparsers.add_parser(
        'hpp-math', 
        help='Run HPP sim, seeded with math graphs.',
        epilog="Example: ./cli.py sim hpp-math --graphs 3 --steps 200"
    )
    sim_hpp_math.add_argument('--density', type=float, default=0.3, help='Particle density (0.0 to 1.0).')
    sim_hpp_math.add_argument('--steps', type=int, default=500, help='Simulation steps per graph.')
    sim_hpp_math.add_argument('--delay', type=float, default=0.05, help='Delay in seconds between frames.')
    sim_hpp_math.add_argument('--graphs', type=int, default=5, help='Number of math graphs to run.')

    # 'sim outer' command
    sim_outer = sim_subparsers.add_parser(
        'outer', 
        help="Run a generic Outer-Totalistic (B/S) CA.",
        epilog="Example (HighLife rule): ./cli.py sim outer --b-rule \"3,6\" --s-rule \"2,3\""
    )
    sim_outer.add_argument('--b-rule', type=parse_int_list, default=[3], help="Birth rule, comma-separated (e.g., '3,6').")
    sim_outer.add_argument('--s-rule', type=parse_int_list, default=[2, 3], help="Survival rule, comma-separated (e.g., '2,3').")
    sim_outer.add_argument('--steps', type=int, default=200, help='Simulation steps.')
    sim_outer.add_argument('--delay', type=float, default=0.1, help='Delay in seconds between frames.')
    sim_outer.add_argument('--oscil-max', type=int, default=20, help='Steps to detect oscillation.')
    sim_outer.add_argument('--still-max', type=int, default=10, help='Steps to detect still life.')
    sim_outer.add_argument('--empty-max', type=int, default=5, help='Steps to detect empty board.')

    # 'sim gof' command
    sim_gof = sim_subparsers.add_parser(
        'gof', 
        help="Run Conway's Game of Life (B3/S23).",
        epilog="Example: ./cli.py sim gof --board glider --steps 300 --delay 0.05"
    )
    sim_gof.add_argument('--board', type=str, default='random', choices=['random'] + list(STARTING_STATES_GOF.keys()), help='Initial board state (default: random).')
    sim_gof.add_argument('--steps', type=int, default=200, help='Simulation steps.')
    sim_gof.add_argument('--delay', type=float, default=0.1, help='Delay in seconds between frames.')
    sim_gof.add_argument('--which', type=str, default='both', choices=['left', 'right', 'both'], help='Which module to draw on.')

    # 'sim inner' command
    sim_inner = sim_subparsers.add_parser(
        'inner', 
        help="Run an Inner-Totalistic (NKS) CA.",
        epilog="Example: ./cli.py sim inner 777 --steps 100"
    )
    sim_inner.add_argument('rule', type=int, help="The NKS-style rule number (e.g., 777). This is a single integer.")
    sim_inner.add_argument('--steps', type=int, default=200, help='Simulation steps.')
    sim_inner.add_argument('--delay', type=float, default=0.1, help='Delay in seconds between frames.')

    # 'sim random-grey' command
    sim_grey = sim_subparsers.add_parser(
        'random-grey', 
        help='Display random greyscale noise.',
        epilog="Example: ./cli.py sim random-grey --duration 15"
    )
    sim_grey.add_argument('--duration', type=int, default=10, help='Duration in seconds.')
    sim_grey.add_argument('--no-animate', action='store_false', dest='animate', help='Disable hardware animation (for pure noise).')

    # 'sim anagram-gof' command
    sim_ana_gof = sim_subparsers.add_parser(
        'anagram-gof', 
        help='Draw anagrams, then run GoL on them.',
        epilog="Example: ./cli.py sim anagram-gof --words 3 --steps 50"
    )
    sim_ana_gof.add_argument('--words', type=int, default=4, help='Number of random words to use.')
    sim_ana_gof.add_argument('--steps', type=int, default=100, help='GoL steps per anagram.')
    sim_ana_gof.add_argument('--delay', type=float, default=0.1, help='Delay in seconds between GoL frames.')
    sim_ana_gof.add_argument('--which', type=str, default='both', choices=['left', 'right', 'both'], help='Which module to draw on.')

    # 'sim anagram-draw' command
    sim_ana_draw = sim_subparsers.add_parser(
        'anagram-draw', 
        help='Find and draw anagrams for random words.',
        epilog="Example: ./cli.py sim anagram-draw --words 2"
    )
    sim_ana_draw.add_argument('--words', type=int, default=3, help='Number of random words to use.')
    sim_ana_draw.add_argument('--which', type=str, default='both', choices=['left', 'right', 'both'], help='Which module to draw on.')

    # 'sim math-gof' command
    sim_math_gof = sim_subparsers.add_parser(
        'math-gof', 
        help='Draw math graphs, then run GoL on them.',
        epilog="Example: ./cli.py sim math-gof --steps 50"
    )
    sim_math_gof.add_argument('--steps', type=int, default=100, help='GoL steps per graph.')
    sim_math_gof.add_argument('--delay', type=float, default=0.1, help='Delay in seconds between GoL frames.')

    # 'sim math-graphs' command
    sim_math_graphs = sim_subparsers.add_parser(
        'math-graphs', 
        help='Show a sequence of random math graphs.',
        epilog="Example: ./cli.py sim math-graphs --num 5 --delay 3 --hold 5"
    )
    sim_math_graphs.add_argument('--num', type=int, default=5, help='Number of graphs to show.')
    sim_math_graphs.add_argument('--delay', type=float, default=2.0, help='Delay in seconds between graphs.')
    sim_math_graphs.add_argument('--which', type=str, default='both', choices=['left', 'right', 'both'], help='Which module to draw on.')
    sim_math_graphs.add_argument('--hold', type=float, default=0, help='Seconds to hold the *final* graph on screen (default: 0).')


    # --- 5. Math Sub-parser (User's modified version) ---
    math_parser = subparsers.add_parser(
        'math', 
        help='Run local math visualization tools.',
        epilog="Example: ./cli.py math plot sin"
    )
    math_subparsers = math_parser.add_subparsers(dest='math_command', required=True, help='Specific math command')

    # 'math plot' command
    math_plot = math_subparsers.add_parser(
        'plot', 
        help='Plot a predefined function locally and on the matrix.',
        epilog="""
Examples:
    ./cli.py math plot sin
    ./cli.py math plot tanh
"""
    )
    # Create the list of available function names for the help message
    try:
        func_names = list(REGULAR_OPERATIONS.keys())
        choices_help = f"Picks from this predefined list: {', '.join(func_names)}"
    except NameError:
        # Fallback if REGULAR_OPERATIONS isn't loaded yet (shouldn't happen)
        func_names = ['sin', 'cos', 'tan', 'exp', 'log', 'tanh', 'sqrt', 'arcsin', 'arccos', 'arctanh']
        choices_help = "Picks from a predefined list (e.g., 'sin', 'cos')."

    math_plot.add_argument(
        'function_string', 
        type=str, 
        choices=func_names + [""], # Add "" to handle empty list during build
        help=choices_help
    )
    math_plot.add_argument('--points', type=int, default=500, help='Number of points to plot. Determines resolution (default: 500).')

    return parser

# --- Main Execution ---

def main():
    """
    Main function to parse arguments and dispatch commands.
    Includes a try...finally block to reset modules on exit.
    """
    # Note: parser.parse_args() reads directly from sys.argv
    parser = build_cli()
    
    # If no commands are given, print main help
    if len(sys.argv) == 1:
        print(helper)
        return

    args = parser.parse_args()

    # --- Set verbose flag from new top-level argument ---
    log.verbose = args.verbose 
    # --- Removed hardcoded log.verbose = True ---

    try:
        # --- 0. Background Command Dispatch ---
        if args.command in ['background', 'bg']:
            run_background_mode()

        # --- 1. LED Command Dispatch ---
        elif args.command == 'led':
            if args.led_command == 'version':
                get_firmware_version()
            elif args.led_command == 'clear':
                clear_graph()
            elif args.led_command == 'fill':
                fill_graph()
                if args.hold > 0:
                    log(f"Holding fill for {args.hold} seconds...")
                    time.sleep(args.hold)
            elif args.led_command == 'start-anim':
                start_animation()
            elif args.led_command == 'stop-anim':
                stop_animation()
            elif args.led_command == 'reset':
                reset_modules()
            elif args.led_command == 'ports':
                output_ports()

        # --- 2. Text Command Dispatch ---
        elif args.command == 'text':
            if args.text_command == 'vertical':
                draw_text_vertical(args.text, args.font_size, args.which, args.row_offset)
                if args.hold > 0:
                    log(f"Holding text for {args.hold} seconds...")
                    time.sleep(args.hold)
            elif args.text_command == 'horizontal':
                draw_text_horizontal(args.text, args.font_size, args.which, args.x_offset, args.y_offset)
                if args.hold > 0:
                    log(f"Holding text for {args.hold} seconds...")
                    time.sleep(args.hold)
        
        # --- 3. Anagram Command Dispatch ---
        elif args.command == 'anagram':
            if args.anagram_command == 'draw':
                draw_anagram_on_matrix(args.word, args.which, args.animate)
                # Note: This function has its own internal delays.
                # We don't add --hold here as it would be ambiguous.

        # --- 4. Simulation Command Dispatch ---
        elif args.command == 'sim':
            if args.sim_command == 'bml':
                run_bml_simulation(args.density, args.steps, args.delay)
            elif args.sim_command == 'bml-local':
                print(f"Starting local BML simulation (density={args.density}, steps={args.steps})...")
                print("Close the Matplotlib window to exit.")
                show_bml_local_animation(args.density, args.steps)
            elif args.sim_command == 'hpp':
                run_hpp_simulation(None, args.density, args.steps, args.delay, args.which)
            elif args.sim_command == 'hpp-math':
                run_hpp_with_math(args.density, args.steps, args.delay, args.graphs)
            elif args.sim_command == 'outer':
                run_outer_totalistic_simulation(
                    initial_state=None, 
                    b_rule=args.b_rule, 
                    s_rule=args.s_rule, 
                    timesteps=args.steps, 
                    delay_sec=args.delay,
                    oscilation_max_steps=args.oscil_max,
                    still_board_max_steps=args.still_max,
                    empty_board_max_steps=args.empty_max
                )
            elif args.sim_command == 'gof':
                initial_board = None
                if args.board != 'random':
                    initial_board = STARTING_STATES_GOF[args.board]
                game_of_life_totalistic_sim(initial_board, args.steps, args.delay, args.which)
            elif args.sim_command == 'inner':
                # 'rule' is already an int thanks to type=int in add_argument
                run_inner_totalistic_simulation(None, args.rule, args.steps, args.delay)
            elif args.sim_command == 'random-grey':
                random_greyscale_animation(args.animate, args.duration)
            elif args.sim_command == 'anagram-gof':
                run_anagrams_game_of_life(args.words, args.steps, args.delay, args.which)
            elif args.sim_command == 'anagram-draw':
                run_draw_anagram_on_matrix(args.words, args.which)
            elif args.sim_command == 'math-gof':
                run_math_funs_game_of_life(args.steps, args.delay)
            elif args.sim_command == 'math-graphs':
                show_random_graphs(args.num, args.delay, args.which)
                if args.hold > 0:
                    time.sleep(args.hold)

        # --- 5. Math Command Dispatch (User's modified version) ---
        elif args.command == 'math':
            if args.math_command == 'plot':
                try:
                    op = args.function_string.strip()
                    if op in REGULAR_OPERATIONS:
                        func = REGULAR_OPERATIONS[op]
                        log(f"Plotting predefined function: '{op}'")
                    else:
                        print(f"Error: '{op}' not found in REGULAR_OPERATIONS.", file=sys.stderr)
                        print("Available functions are:", list(REGULAR_OPERATIONS.keys()), file=sys.stderr)
                        return

                    log("Generating graph for matrix...")
                    graph_matrix = pick_largest_graph(func)
                    draw_matrix_on_board(graph_matrix, which='both')
                    
                    log("Generating local plot window...")
                    plot_function(func, -40, 40, args.points, f'Plot of {op}', label=op) # type: ignore
                
                except Exception as e:
                    print(f"Error during math plot: {e}", file=sys.stderr)
                    sys.exit(1)

    except KeyboardInterrupt:
        print("\nCaught KeyboardInterrupt. Exiting and resetting modules.")
    except Exception as e:
        print(f"\nAn unhandled error occurred: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
    finally:
        # Check if 'args' exists, as it wouldn't if no args were given
        if 'args' in locals():
            # Don't reset if the command *was* reset
            if not (args.command == 'led' and args.led_command == 'reset'):
                log("Cleaning up... resetting modules.")
                reset_modules()
        
        # Always print done
        print("Done.")

# --- Built-in Test Suite ---

def run_tests():
    """
    Runs a built-in test suite by simulating command-line arguments.
    This is triggered by running: ./cli.py --test
    """
    original_argv = list(sys.argv)
    print("--- STARTING BUILT-IN TEST SUITE ---")
    
    # Find a valid function name from REGULAR_OPERATIONS for the test
    # Default to 'sin' if the import failed for some reason
    try:
        math_test_func = list(REGULAR_OPERATIONS.keys())[0]
    except (NameError, IndexError):
        math_test_func = 'sin' # Fallback
    
    # Define test commands (as lists of strings, just like sys.argv)
    test_commands = [
        ['cli.py', 'led', 'version'],
        ['cli.py', '-v', 'text', 'vertical', 'TEST', '--hold', '1.5'], # Test verbose flag
        ['cli.py', 'sim', 'gof', '--board', 'blinker', '--steps', '25', '--delay', '0.05'],
        ['cli.py', 'sim', 'outer', '--b-rule', '3,6', '--s-rule', '2,3', '--steps', '25', '--delay', '0.05'],
        ['cli.py', 'sim', 'inner', '777', '--steps', '25', '--delay', '0.05'],
        ['cli.py', 'sim', 'bml-local', '--steps', '50'], # Will pause for user
        # --- FIXED TEST CASE ---
        ['cli.py', 'math', 'plot', math_test_func], # Will pause for user
    ]

    try:
        for i, cmd in enumerate(test_commands):
            print(f"\n--- TEST {i+1}/{len(test_commands)}: {' '.join(cmd)} ---")
            sys.argv = cmd # Overwrite sys.argv
            
            try:
                main() # Run the main function with the new sys.argv
            except SystemExit:
                print(f"Test {i+1} completed with SystemExit (expected for -h or plot).")
            except Exception as e:
                print(f"--- TEST {i+1} FAILED: {e} ---")
            
            # Pause briefly for visual tests on the matrix
            # (The --hold test will pause itself)
            if (cmd[1] == 'sim' and 'local' not in cmd[2]):
                print("Pausing 2 seconds for visual check...")
                time.sleep(2)

    except Exception as e:
        print(f"\n--- TEST SUITE ABORTED: {e} ---")
    finally:
        print("\n--- TEST SUITE FINISHED ---")
        sys.argv = original_argv # Restore original sys.argv
        reset_modules()
        print("Original argv restored. Modules reset.")


if __name__ == "__main__":
    # Check for the special --test flag
    if len(sys.argv) == 2 and sys.argv[1] == '--test':
        run_tests()
    else:
        # Run normal operation
        main()
