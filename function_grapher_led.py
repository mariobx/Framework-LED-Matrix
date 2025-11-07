import subprocess
import re
import time
import serial
from const import *
import numpy as np
from typing import List, Optional
from typing import Callable
from PIL import Image, ImageDraw, ImageFont

log = VerboseLogger()
log.verbose = verbose
modules = {'left': None, 'right': None}

def get_module_paths():
    """
    Finds the stable /dev/ttyACM* paths for the left and right LED matrix modules
    by matching their known physical PCI paths.

    Returns:
        dict: A dictionary mapping 'left' and 'right' to their /dev/ file paths.
            e.g., {'left': '/dev/ttyACM1', 'right': '/dev/ttyACM0'}
            Values will be None if a path is not found.
    """
    log("get_module_paths: starting module discovery")
    if modules['left'] is not None and modules['right'] is not None:
        log("get_module_paths: using cached module paths")
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
        # payload[0] is the column index, used for logging
        log(f"draw_greyscale_on_board: staging column {payload[0]}")
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

    log(f"send_command: resolved paths -> {paths_to_send}")
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


def create_graph_with_horizontal_x_axis(axis: bool = False, function: Callable[[float], float] = lambda x: x**2, draw_function: bool = True):
    """
    Creates a graph on the LED matrix.
    axis (bool): If True, draws the X and Y axes.
    function (Callable[[float], float]): The mathematical function to graph.
    """
    log(f"create_graph_with_horizontal_x_axis: start axis={axis} function={function}")
    matrix = [[0] * WIDTH for _ in range(HEIGHT)]
    if function:
        matrix = [[0] * WIDTH for _ in range(HEIGHT)]
        if axis:
            log("create_graph_with_horizontal_x_axis: drawing axes")
            for i in range(0, WIDTH):
                matrix[17][i] = 1
            for i in range(0, HEIGHT):
                matrix[i][4] = 1
        points_plotted = 0
        for x in np.arange(-4,5, 0.01):
            xf = float(x)
            y = round(function(xf))
            xi = round(xf)
            if abs(y) > (HEIGHT//2)-1 or abs(xi) > (WIDTH//2):
                continue
            else:
                matrix[Y_AXIS_HORIZONTAL[y]][X_AXIS_HORIZONTAL[xi]] = 1
                points_plotted += 1
        if draw_function:
            draw_matrix_on_board(matrix, 'both')
            log(f"create_graph_with_horizontal_x_axis: drawbw sent, plotted {points_plotted} points")
        return matrix

def create_graph_with_vertical_x_axis(axis: bool = False, function: Callable[[float], float] = lambda x: x**2, draw_function: bool = True):
    """
    Creates a graph on the LED matrix. (Rotated 90 degrees)
    X-Axis: long (34 rows)
    Y-Axis: short (9 cols)
    """
    log(f"create_graph_with_vertical_x_axis: start axis={axis} function={function}")
    matrix = [[0] * WIDTH for _ in range(HEIGHT)]
    if function:
        if axis:
            log("create_graph_with_vertical_x_axis: drawing axes")
            for i in range(0, HEIGHT):
                matrix[i][4] = 1
            for i in range(0, WIDTH):
                matrix[17][i] = 1
        points_plotted = 0
        for x_val in np.arange(-16, 17, 0.01):
            xf = float(x_val)
            y_val = function(xf)
            if np.isnan(y_val):
                log(f"create_graph_with_vertical_x_axis: skip NaN at x={xf}")
                continue
            y = round(y_val)
            xi = round(xf)
            if y not in Y_AXIS_VERTICAL or xi not in X_AXIS_VERTICAL:
                continue
            else:
                matrix[X_AXIS_VERTICAL[xi]][Y_AXIS_VERTICAL[y]] = 1
                points_plotted += 1
        if draw_function:
            draw_matrix_on_board(matrix, 'both')
            log(f"create_graph_with_vertical_x_axis: drawbw sent, plotted {points_plotted} points")
        return matrix

def draw_text_vertical(text: str, font_size: int = 12, which: str = 'both', row_offset: int = 0):
    log(f"draw_text_vertical: rendering '{text}' size={font_size} which={which} row_offset={row_offset}")
    font = None
    if font_size is None:
        current_size = 1
        while True:
            try:
                font = ImageFont.truetype(DEFAULT_FONT_PATH, current_size)
                try:
                    bbox = font.getbbox(text)
                    text_width = bbox[2]
                    text_height = bbox[3]
                except AttributeError:
                    text_width, text_height = font.getsize(text) # type: ignore
                
                if text_height > WIDTH or text_width > (HEIGHT - row_offset):
                    font_size = current_size - 1
                    break
                current_size += 1
            except IOError:
                font = ImageFont.load_default()
                break
        
        if font_size is not None and font_size <= 0: font_size = 1
        try:
            font = ImageFont.truetype(DEFAULT_FONT_PATH, font_size)
            log(f"draw_text_vertical: truetype font loaded at size {font_size}")
        except IOError:
            font = ImageFont.load_default()
            log("draw_text_vertical: fallback to default font")

    else:
        try:
            font = ImageFont.truetype(DEFAULT_FONT_PATH, font_size)
            log(f"draw_text_vertical: truetype font loaded at size {font_size}")
        except IOError:
            font = ImageFont.load_default()
            log("draw_text_vertical: fallback to default font")
    
    try:
        bbox = font.getbbox(text)
        text_width = bbox[2]
        text_height = bbox[3]
    except AttributeError:
        text_width, text_height = font.getsize(text) # type: ignore

    log(f"draw_text_vertical: text bounding box w={text_width} h={text_height}")
    temp_image = Image.new('1', (text_width, text_height), 0) # type: ignore
    draw = ImageDraw.Draw(temp_image)
    draw.text((0, 0), text, font=font, fill=1)

    matrix = [[0] * WIDTH for _ in range(HEIGHT)]
    
    col_offset = (WIDTH - text_height) // 2
    pixels_mapped = 0
    
    for x in range(text_width): # type: ignore
        for y in range(text_height): # type: ignore
            matrix_row = (text_width - 1 - x) + row_offset
            matrix_col = col_offset + y
            
            if not (0 <= matrix_row < HEIGHT and 0 <= matrix_col < WIDTH):
                continue

            matrix[matrix_row][matrix_col] = temp_image.getpixel((x, y)) # type: ignore
            pixels_mapped += 1

    log(f"draw_text_vertical: mapped {pixels_mapped} pixels to matrix")
    draw_matrix_on_board(matrix, which)
    log("draw_text_vertical: drawbw sent")

def draw_text_horizontal(text: str, font_size: int = 12, which: str = 'both', x_offset: int = 0, y_offset: int = 0):
    log(f"draw_text_horizontal: rendering '{text}' size={font_size} which={which} x_offset={x_offset} y_offset={y_offset}")
    font = None
    if font_size is None:
        current_size = 1
        while True:
            try:
                font = ImageFont.truetype(DEFAULT_FONT_PATH, current_size)
                try:
                    text_height = font.getbbox(text)[3]
                except AttributeError:
                    text_height = font.getsize(text)[1] # type: ignore
                
                if text_height > HEIGHT:
                    font_size = current_size - 1
                    break
                current_size += 1
            except IOError:
                font = ImageFont.load_default()
                break

        if font_size is not None and font_size <= 0: font_size = 1
        try:
            font = ImageFont.truetype(DEFAULT_FONT_PATH, font_size)
            log(f"draw_text_horizontal: truetype font loaded at size {font_size}")
        except IOError:
            font = ImageFont.load_default()
            log("draw_text_horizontal: fallback to default font")
    else:
        try:
            font = ImageFont.truetype(DEFAULT_FONT_PATH, font_size)
            log(f"draw_text_horizontal: truetype font loaded at size {font_size}")
        except IOError:
            font = ImageFont.load_default()
            log("draw_text_horizontal: fallback to default font")

    try:
        bbox = font.getbbox(text)
        text_width = bbox[2]
        text_height = bbox[3]
    except AttributeError:
        text_width, text_height = font.getsize(text) # type: ignore

    log(f"draw_text_horizontal: text bounding box w={text_width} h={text_height}")
    temp_image = Image.new('1', (text_width, text_height), 0) # type: ignore
    draw = ImageDraw.Draw(temp_image)
    draw.text((0, 0), text, font=font, fill=1)
    
    matrix = [[0] * WIDTH for _ in range(HEIGHT)]

    if y_offset == 0:
         y_offset = (HEIGHT - text_height) // 2 # type: ignore
    
    pixels_mapped = 0
    for matrix_col in range(WIDTH):
        for matrix_row in range(HEIGHT):
            source_x = matrix_col + x_offset
            source_y = matrix_row - y_offset
            
            if not (0 <= source_x < text_width and 0 <= source_y < text_height):
                continue
            matrix[matrix_row][matrix_col] = temp_image.getpixel((source_x, source_y)) # type: ignore
            pixels_mapped += 1

    log(f"draw_text_horizontal: mapped {pixels_mapped} pixels to matrix")
    draw_matrix_on_board(matrix, which)
    log("draw_text_horizontal: drawbw sent")


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

    


