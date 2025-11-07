WIDTH = 9
HEIGHT = 34
verbose = True

RIGHT_PCI_PATH = 'pci-0000:c2:00.3-usb-0:3.3:1.0'
LEFT_PCI_PATH = 'pci-0000:c2:00.3-usb-0:4.2:1.0'

TRUE = [1]
FALSE = [0]

COMMANDS = {
    # --- Write Commands ---
    "brightness": 0x00,
    "pattern": 0x01,
    "bootloader": 0x02,
    "sleep": 0x03,
    "animate": 0x04,
    "panic": 0x05,
    "drawbw": 0x06,
    "stagecol": 0x07,
    "flushcols": 0x08,
    "startgame": 0x10,
    "gamecontrol": 0x11,
    
    # --- Read Commands (Same ID, no params) ---
    "getsleep": 0x03,
    "getanimate": 0x04,
    "gamestatus": 0x12,
    "version": 0x20
}

PATTERNS = {
    "percentage": [0x00],
    "gradient": [0x01],
    "doublegradient": [0x02],
    "lotush": [0x03],
    "zigzag": [0x04],
    "full": [0x05],
    "panic": [0x06],
    "lotusv": [0x07]
}

GAMES = {
    "snake": [0],
    "pong": [1],
}

GAME_CONTROLS = {
    "pong": {
        "far_player": {
            "left": [2],
            "right": [3]
        },
        "close_player": {
            "left": [5],
            "right": [6],
        },
        "stop": [4]
    },
    "snake": {
        "up": [0],
        "down": [1],
        "left": [2],
        "right": [3],
        "stop": [4]
    },
}

# row 33 col 8 is last dot

X_AXIS_HORIZONTAL = {
    -4: 0, -3: 1, -2: 2, -1: 3, 0: 4, 1: 5, 2: 6, 3: 7, 4: 8
}
Y_AXIS_HORIZONTAL = {
    -16: 33, -15: 32, -14: 31, -13: 30, -12: 29, -11: 28, -10: 27, -9: 26,
    -8: 25, -7: 24, -6: 23, -5: 22, -4: 21, -3: 20, -2: 19, -1: 18, 0: 17,
    1: 16, 2: 15, 3: 14, 4: 13, 5: 12, 6: 11, 7: 10, 8: 9, 9: 8, 10: 7,
    11: 6, 12: 5, 13: 4, 14: 3, 15: 2, 16: 1, 17: 0
}

X_AXIS_VERTICAL = {
    -16: 33, -15: 32, -14: 31, -13: 30, -12: 29, -11: 28, -10: 27, -9: 26,
    -8: 25, -7: 24, -6: 23, -5: 22, -4: 21, -3: 20, -2: 19, -1: 18, 0: 17,
    1: 16, 2: 15, 3: 14, 4: 13, 5: 12, 6: 11, 7: 10, 8: 9, 9: 8, 10: 7,
    11: 6, 12: 5, 13: 4, 14: 3, 15: 2, 16: 1, 17: 0
}
Y_AXIS_VERTICAL = {
    -4: 0, -3: 1, -2: 2, -1: 3, 0: 4, 1: 5, 2: 6, 3: 7, 4: 8
}

DEFAULT_FONT_PATH = "/usr/share/fonts/TTF/DejaVuSansMono.ttf"

class VerboseLogger:
    """
    A simple, callable logger.
    Acts just like print() if self.verbose is True,
    otherwise does nothing.
    """
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __call__(self, *args, **kwargs):
        """
        This makes the instance itself callable.
        e.g., v_print("Hello")
        """
        if self.verbose:
            print(*args, **kwargs)