from led_matrix_commands import log, draw_matrix_on_board, WIDTH, HEIGHT
from PIL import Image, ImageDraw, ImageFont



DEFAULT_FONT_PATH = "/usr/share/fonts/TTF/DejaVuSansMono.ttf"

def get_font_size(word_length: int) -> int:
    """
    Gets an appropriate font size for rendering a word vertically
    on the 34-pixel-tall matrix.
    
    This is based on two constraints:
    1. Font height must be <= 9 (the matrix width).
    2. Total word length (as pixels) must be <= 34 (the matrix height).
    
    Args:
        word_length (int): The length of the word.
        
    Returns:
        int: The calculated font size.
    """
    SIZE_MAP = {
        2: 10,
        3: 10,
        4: 10,
        5: 9,
        6: 8,
        7: 7,
        8: 7,
        9: 6,
        10: 5,
        11: 5,
        12: 5,
        13: 5,
        14: 5,
    }
    
    if word_length < 2:
        return 10
    elif word_length > 14:
        return 4
        
    return SIZE_MAP.get(word_length, 4)


def get_matrix_from_text_vertical(text: str, font_size: int | None = None, row_offset: int = 0):
    log(f"get_matrix_from_text_vertical: rendering '{text}' requested_size={font_size} row_offset={row_offset}")
    if font_size is None:
        font_size = get_font_size(len(text))
        log(f"get_matrix_from_text_vertical: computed font_size={font_size} using get_font_size(len(text)={len(text)})")
    try:
        font = ImageFont.truetype(DEFAULT_FONT_PATH, font_size)
        log(f"get_matrix_from_text_vertical: truetype font loaded at size {font_size}")
    except IOError:
        font = ImageFont.load_default()
        log("get_matrix_from_text_vertical: fallback to default font")

    #text width must be <= HEIGHT-row_offset, text height <= WIDTH
    try:
        bbox = font.getbbox(text)
        text_width = bbox[2]
        text_height = bbox[3]
    except AttributeError:
        text_width, text_height = font.getsize(text) # type: ignore

    # If it doesn't fit, reduce font_size until it does (or reaches 1)
    while (text_height > WIDTH or text_width > (HEIGHT - row_offset)) and font_size > 1:
        font_size -= 1
        try:
            font = ImageFont.truetype(DEFAULT_FONT_PATH, font_size)
        except IOError:
            font = ImageFont.load_default()
        try:
            bbox = font.getbbox(text)
            text_width = bbox[2]
            text_height = bbox[3]
        except AttributeError:
            text_width, text_height = font.getsize(text) # type: ignore

    log(f"get_matrix_from_text_vertical: final font_size={font_size} bbox_w={text_width} bbox_h={text_height}")
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

    log(f"get_matrix_from_text_vertical: mapped {pixels_mapped} pixels to matrix")
    return matrix

def get_matrix_from_text_horizontal(text: str, font_size: int | None = None, x_offset: int = 0, y_offset: int = 0):
    log(f"get_matrix_from_text_horizontal: rendering '{text}' requested_size={font_size} x_offset={x_offset} y_offset={y_offset}")
    if font_size is None:
        font_size = get_font_size(len(text))
        log(f"get_matrix_from_text_horizontal: computed font_size={font_size} using get_font_size(len(text)={len(text)})")

    try:
        font = ImageFont.truetype(DEFAULT_FONT_PATH, font_size)
        log(f"get_matrix_from_text_horizontal: truetype font loaded at size {font_size}")
    except IOError:
        font = ImageFont.load_default()
        log("get_matrix_from_text_horizontal: fallback to default font")

    try:
        bbox = font.getbbox(text)
        text_width = bbox[2]
        text_height = bbox[3]
    except AttributeError:
        text_width, text_height = font.getsize(text) # type: ignore

    #If text height is too tall for the matrix, reduce font_size until it fits
    while text_height > HEIGHT and font_size > 1:
        font_size -= 1
        try:
            font = ImageFont.truetype(DEFAULT_FONT_PATH, font_size)
        except IOError:
            font = ImageFont.load_default()
        try:
            bbox = font.getbbox(text)
            text_width = bbox[2]
            text_height = bbox[3]
        except AttributeError:
            text_width, text_height = font.getsize(text) # type: ignore

    log(f"get_matrix_from_text_horizontal: final font_size={font_size} bbox_w={text_width} bbox_h={text_height}")
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

    log(f"get_matrix_from_text_horizontal: mapped {pixels_mapped} pixels to matrix")
    return matrix

def draw_text_vertical(text: str, font_size: int | None = None, which: str = 'both', row_offset: int = 0):
    log(f"draw_text_vertical: rendering '{text}' requested_size={font_size} which={which} row_offset={row_offset}")
    if font_size is None:
        font_size = get_font_size(len(text))
        log(f"draw_text_vertical: computed font_size={font_size} using get_font_size(len(text)={len(text)})")
    try:
        font = ImageFont.truetype(DEFAULT_FONT_PATH, font_size)
        log(f"draw_text_vertical: truetype font loaded at size {font_size}")
    except IOError:
        font = ImageFont.load_default()
        log("draw_text_vertical: fallback to default font")

    #text width must be <= HEIGHT-row_offset, text height <= WIDTH
    try:
        bbox = font.getbbox(text)
        text_width = bbox[2]
        text_height = bbox[3]
    except AttributeError:
        text_width, text_height = font.getsize(text) # type: ignore

    # If it doesn't fit, reduce font_size until it does (or reaches 1)
    while (text_height > WIDTH or text_width > (HEIGHT - row_offset)) and font_size > 1:
        font_size -= 1
        try:
            font = ImageFont.truetype(DEFAULT_FONT_PATH, font_size)
        except IOError:
            font = ImageFont.load_default()
        try:
            bbox = font.getbbox(text)
            text_width = bbox[2]
            text_height = bbox[3]
        except AttributeError:
            text_width, text_height = font.getsize(text) # type: ignore

    log(f"draw_text_vertical: final font_size={font_size} bbox_w={text_width} bbox_h={text_height}")
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
    return matrix

def draw_text_horizontal(text: str, font_size: int | None = None, which: str = 'both', x_offset: int = 0, y_offset: int = 0):
    log(f"draw_text_horizontal: rendering '{text}' requested_size={font_size} which={which} x_offset={x_offset} y_offset={y_offset}")
    if font_size is None:
        font_size = get_font_size(len(text))
        log(f"draw_text_horizontal: computed font_size={font_size} using get_font_size(len(text)={len(text)})")

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

    #If text height is too tall for the matrix, reduce font_size until it fits
    while text_height > HEIGHT and font_size > 1:
        font_size -= 1
        try:
            font = ImageFont.truetype(DEFAULT_FONT_PATH, font_size)
        except IOError:
            font = ImageFont.load_default()
        try:
            bbox = font.getbbox(text)
            text_width = bbox[2]
            text_height = bbox[3]
        except AttributeError:
            text_width, text_height = font.getsize(text) # type: ignore

    log(f"draw_text_horizontal: final font_size={font_size} bbox_w={text_width} bbox_h={text_height}")
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
    return matrix
