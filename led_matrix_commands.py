import subprocess
import re
import serial
import serial.tools.list_ports
from typing import List, Optional, Tuple
import sys

WIDTH = 9
HEIGHT = 34
verbose = True
linux = bool(sys.platform == "linux")

class VerboseLogger:
    def __init__(self, verbose=False):
        self.verbose = verbose
    def __call__(self, *args, **kwargs):
        if self.verbose:
            print(*args, **kwargs)

def find_matching_ports_windows(target_description):
    """Finds COM ports with descriptions containing the target_description."""
    matching_ports = {
        'left': '',
        'right': ''
    }
    for port in serial.tools.list_ports.comports():
        if target_description in port.description:
            # Check the device name, not the description
            if port.device == 'COM3':
                matching_ports['left'] = port.device
            elif port.device == 'COM4':
                matching_ports['right'] = port.device
    return matching_ports

log = VerboseLogger()
log.verbose = verbose

modules = {'left': None, 'right': None}

# --- HARDWARE CONSTANTS ---
RIGHT_PCI_PATH_WINDOWS = ''
LEFT_PCI_PATH_WINDOWS = ''
RIGHT_PCI_PATH_LINUX = 'pci-0000:c2:00.3-usb-0:3.3:1.0'
LEFT_PCI_PATH_LINUX = 'pci-0000:c2:00.3-usb-0:4.2:1.0'
RIGHT_PCI_PATH = RIGHT_PCI_PATH_LINUX if linux else RIGHT_PCI_PATH_WINDOWS
LEFT_PCI_PATH = LEFT_PCI_PATH_LINUX if linux else LEFT_PCI_PATH_WINDOWS

DEFAULT_FONT_PATH = "/usr/share/fonts/TTF/DejaVuSansMono.ttf"

# --- COMMAND CONSTANTS ---
COMMANDS = {
    "brightness": 0x00, "pattern": 0x01, "bootloader": 0x02, "sleep": 0x03,
    "animate": 0x04, "panic": 0x05, "drawbw": 0x06, "stagecol": 0x07,
    "flushcols": 0x08, "startgame": 0x10, "gamecontrol": 0x11,
    "getsleep": 0x03, "getanimate": 0x04, "gamestatus": 0x12, "version": 0x20
}
PATTERNS = {
    "percentage": [0x00], "gradient": [0x01], "doublegradient": [0x02],
    "lotush": [0x03], "zigzag": [0x04], "full": [0x05], "panic": [0x06], "lotusv": [0x07]
}
GAMES = { "snake": [0], "pong": [1] }
GAME_CONTROLS = {
    "pong": {
        "far_player": {"left": [2], "right": [3]},
        "close_player": {"left": [5], "right": [6]}, "stop": [4]
    },
    "snake": {
        "up": [0], "down": [1], "left": [2], "right": [3], "stop": [4]
    },
}


def get_module_paths():
    """
    Finds the stable /dev/ttyACM* paths for the left and right LED matrix modules
    by matching their known physical PCI paths.

    Returns:
        dict: A dictionary mapping 'left' and 'right' to their /dev/ file paths.
            e.g., {'left': '/dev/ttyACM1', 'right': '/dev/ttyACM0'}
            Values will be None if a path is not found.
    """
    if not linux:
        if modules['left'] is not None and modules['right'] is not None:
            return modules
        else:
            found_ports = find_matching_ports_windows("USB Serial Device")
            modules['left'] = found_ports['left']
            modules['right'] = found_ports['right']
            log(f"get_module_paths: found ports -> {modules}")
            return modules

    if modules['left'] is not None and modules['right'] is not None:
        log("get_module_paths: using cached module paths", modules)
        return modules
    
    try:
        result = subprocess.run(
            ['ls', '-l', '/dev/serial/by-path/'], 
            capture_output=True, 
            text=True,
            check=True
        )
        log("get_module_paths: ls output captured")
        lines = result.stdout.strip().split('\n')
        for line in lines:
            # Find the 'ttyACM*' device name in the line
            match = re.search(r'ttyACM\d+', line)
            if not match:
                continue  # Skip lines that aren't ttyACM devices
            device_path = f"/dev/{match.group(0)}"
            log(f"get_module_paths: found device {device_path} in line: {line.strip()}")
            if RIGHT_PCI_PATH in line:
                modules['right'] = device_path # type: ignore
                log(f"get_module_paths: mapped RIGHT -> {device_path}")
            elif LEFT_PCI_PATH in line:
                modules['left'] = device_path # type: ignore
                log(f"get_module_paths: mapped LEFT -> {device_path}")
    except FileNotFoundError:
        log("get_module_paths: Error: 'ls' command not found. Please ensure coreutils are installed.")
    except subprocess.CalledProcessError as e:
        log(f"get_module_paths: Error listing serial devices: {e.stderr}")
    except Exception as e:
        log(f"get_module_paths: unexpected error: {e}")
    log(f"get_module_paths: result -> {modules}")
    return modules

def create_matrix(matrix_data):
    """
    Converts a 2D matrix (34 rows, 9 cols) into a 39-byte payload.
    
    Args:
        matrix_data (list[list[int]]): 2D array of 34x9. 1 = ON, 0 = OFF.
    """
    log(f"create_matrix: building payload")
    
    # 1. Initialize the 39-byte payload with all zeros (LEDs off)
    vals = [0] * 39

    # 2. Pack the 2D matrix data into the 39-byte list
    pixels_set = 0
    for row in range(HEIGHT):
        for col in range(WIDTH):
            
            # Check the cell value. 
            # We assume 1 is ON, 0 is OFF.
            cell = matrix_data[row][col]
            if cell == 1:
                # Convert [row][col] to 1D index
                i = col + row * WIDTH
                
                # Find the byte index (i // 8)
                # Find the bit index (i % 8)
                # Set the corresponding bit to 1
                vals[i // 8] |= (1 << (i % 8))
                pixels_set += 1
    log(f"draw_matrix: packed {pixels_set} pixels into payload")
    return vals

def draw_matrix_on_board(matrix_data, which='both'):
    send_command(COMMANDS['drawbw'], create_matrix(matrix_data), which=which)


def create_greyscale_payloads(matrix_data: List[List[int]]) -> List[List[int]]:
    """
    Prepares the 9 separate column-payloads for the 'stagecol' command.
    
    Args:
        matrix_data (list[list[int]]): 2D array of 34x9 with brightness 0-255.

    Returns:
        list[list[int]]: A list of 9 payloads. Each payload is
                        [col_index] + [34 bytes of brightness].
    """
    all_payloads = []
    log("create_greyscale_payloads: preparing 9 column payloads")
    
    # Iterate by COLUMN (0 to 8)
    for col in range(WIDTH):
        column_brightness_data = []
        for row in range(HEIGHT):
            # Get brightness, ensure it's an int and clamp (0-255)
            brightness = matrix_data[row][col]
            brightness = max(0, min(255, int(brightness)))
            column_brightness_data.append(brightness)
        
        # Create the final parameters: [col_index] + [34 bytes]
        parameters = [col] + column_brightness_data
        all_payloads.append(parameters)
        
    log(f"create_greyscale_payloads: created {len(all_payloads)} payloads.")
    return all_payloads

def draw_greyscale_on_board(matrix_data: List[List[int]], which: str = 'both'):
    """
    Creates and draws a greyscale matrix on the board.
    This version does NOT track global state.
    
    Args:
        matrix_data (list[list[int]]): 2D array of 34x9 (brightness 0-255).
        which (str): 'left', 'right', 'both'.
    """
    log(f"draw_greyscale_on_board: starting (which={which})")

    # 1. Create the payloads
    all_column_payloads = create_greyscale_payloads(matrix_data)
    
    # 2. Send all the staged column data
    for payload in all_column_payloads:
        send_command(COMMANDS['stagecol'], payload, which)
    
    # 3. After all columns are staged, flush them to the display
    send_command(COMMANDS['flushcols'], [], which)
    log("draw_greyscale_on_board: flushed staged columns")

def set_led(matrix, row, col, brightness):
    """
    Helper function to safely set a pixel's brightness in a matrix.
    This function DOES NOT send any commands.
    """
    if 0 <= row < HEIGHT and 0 <= col < WIDTH:
        matrix[row][col] = int(max(0, min(255, int(brightness))))
        log(f"set_led: set ({row},{col}) -> {matrix[row][col]}")
    else:
        log(f"set_led: Warning: Pixel ({row}, {col}) is out of bounds.")
        print(f"Warning: Pixel ({row}, {col}) is out of bounds.")

def send_command(command_id, parameters, which='both', with_response=False):
    log(f"send_command: enter command_id={command_id} which={which} with_response={with_response}")
    if which == 'both' and with_response:
        log("send_command: Error - cannot request response from both modules")
        print("Error: Cannot request response from 'both' modules simultaneously.")
        print("Please call separately for 'left' and 'right' if responses are needed.")
        return None

    modules = get_module_paths()
    paths_to_send = []
    if which == 'left':
        paths_to_send.append(modules.get('left'))
    elif which == 'right':
        paths_to_send.append(modules.get('right'))
    elif which == 'both':
        paths_to_send.append(modules.get('left'))
        paths_to_send.append(modules.get('right'))
    else:
        log(f"send_command: Error - invalid which parameter '{which}'")
        print(f"Error: 'which' can only be 'left', 'right', or 'both', not '{which}'")
        return None

    # log(f"send_command: resolved paths -> {paths_to_send}")
    response_data = None
    for path in paths_to_send:
        if path is None:
            module_name = "unknown"
            if path == modules.get('left'): module_name = 'left'
            if path == modules.get('right'): module_name = 'right'
            log(f"send_command: Error - Path for '{module_name}' module not found. Skipping.")
            print(f"Error: Path for '{module_name}' module not found. Skipping.")
            continue
            
        try:
            log(f"send_command: opening serial {path} at 115200")
            with serial.Serial(path, 115200, timeout=1.0) as s:
                
                payload = [0x32, 0xAC, command_id] + (parameters or [])
                log(f"send_command: writing payload to {path}: {payload[:16]}{'...' if len(payload)>16 else ''}")
                
                s.write(bytes(payload))
                s.flush()
                
                if with_response:
                    response_data = s.read(3) # Read 3 bytes, not 32
                    log(f"send_command: received response from {path}: {response_data}")
                else:
                    log(f"send_command: write completed to {path} (no response requested)")
                    
        except serial.SerialException as e:
            log(f"send_command: SerialException for {path}: {e}")
            print(f"Error connecting to {path}: {e}")
        except Exception as e:
            log(f"send_command: unexpected error for {path}: {e}")
            print(f"An unexpected error occurred with {path}: {e}")

    log("send_command: exiting")
    return response_data

def coordinates_to_matrix(coordinates: List[Tuple[int, int]] | List[List[int]]) -> List[List[int]]:
    """
    Translates a list of (row, col) tuples into a full 34x9 2D matrix.
    
    Args:
        coordinates: A list of (row, col) tuples to mark as '1'.
        
    Returns:
        A 34x9 2D matrix (List[List[int]]).
    """
    log("coordinates_to_matrix: creating new 34x9 matrix")
    # 1. Create the initial board (all 0s)
    matrix = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
    
    # 2. Seed the board with the coordinates
    pixels_seeded = 0
    for r, c in coordinates:
        if 0 <= r < HEIGHT and 0 <= c < WIDTH:
            matrix[r][c] = 1  # 1 = live
            pixels_seeded += 1
    
    log(f"coordinates_to_matrix: seeded {pixels_seeded} pixels.")
    return matrix


def parse_version_string(response_bytes: Optional[bytes]) -> str:
    """Helper to parse the 3-byte version response."""
    log("parse_version_string: parsing response")
    if not response_bytes or len(response_bytes) < 3:
        log("parse_version_string: invalid or missing response")
        return "v?.?.? (Error: No response)"
    
    try:
        major = response_bytes[0]
        lsb = response_bytes[1]
        pre_release_flag = response_bytes[2]
        
        # LSB is mmmmPPPP
        minor = (lsb & 0xF0) >> 4  # Get top 4 bits
        patch = lsb & 0x0F          # Get bottom 4 bits
        
        pre_release_str = "-pre" if pre_release_flag == 1 else ""
        version = f"v{major}.{minor}.{patch}{pre_release_str}"
        log(f"parse_version_string: parsed version {version}")
        return version
        
    except Exception as e:
        log(f"parse_version_string: error parsing response: {e}")
        return f"v?.?.? (Error: {e})"

def get_firmware_version():
    """
    Gets, parses, and prints the firmware version for both modules.
    """
    log("get_firmware_version: querying modules for version")
    print("Querying modules for version...")
    
    right_response = send_command(
        COMMANDS["version"], 
        parameters=None, 
        which='right', 
        with_response=True
    )
    
    left_response = send_command(
        COMMANDS["version"], 
        parameters=None, 
        which='left', 
        with_response=True
    )
    
    right_parsed = parse_version_string(right_response)
    left_parsed = parse_version_string(left_response)
    log(f"get_firmware_version: right={right_parsed} left={left_parsed}")
    print(f"Right LED Module: {right_parsed}")
    print(f"Left LED Module:  {left_parsed}")


def clear_graph():
    """
    Clears the LED matrix.
    """
    log("clear_graph: clearing matrix")
    draw_matrix_on_board([[0] * WIDTH for _ in range(HEIGHT)], 'both')
    
def fill_graph():
    """
    Fills the LED matrix.
    """
    log("fill_graph: filling matrix")
    draw_matrix_on_board([[1] * WIDTH for _ in range(HEIGHT)], 'both')

def start_animation():
    """Starts the LED animation."""
    log("start_animation: starting animation on both modules")
    send_command(COMMANDS["animate"], [1], 'both')
    
def stop_animation():
    """Stops the LED animation."""
    log("stop_animation: stopping animation on both modules")
    send_command(COMMANDS["animate"], [0], 'both')
    
def reset_modules():
    """Resets both LED matrix modules."""
    log("reset_modules: resetting modules (clear + stop animation)")
    clear_graph()
    stop_animation()
    
def output_ports():
    """
    Outputs the current module paths for debugging.
    """
    for port in serial.tools.list_ports.comports():
        print(f"Device: {port.device}")
        print(f"  Name: {port.name}")
        print(f"  Description: {port.description}")
        print(f"  HWID: {port.hwid}")
        print(f"  VID: {port.vid}")
        print(f"  PID: {port.pid}")
                  


