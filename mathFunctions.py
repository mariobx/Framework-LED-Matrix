import numpy as np
import math
from typing import Callable
from led_matrix_commands import log, WIDTH, HEIGHT, draw_matrix_on_board


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

MATH_OPERATIONS = [
    # --- Original 35 Functions ---
    # 1. Simple high-amplitude sine wave
    lambda x: 16 * math.sin(x),
    # 2. Simple high-amplitude cosine wave
    lambda x: 16 * math.cos(x),
    # 3. Fast, high-frequency sine wave
    lambda x: 16 * math.sin(x * 3),
    # 4. Slow, low-frequency sine wave
    lambda x: 16 * math.sin(x * 0.5),
    # 5. Two-frequency interference (max amp 16)
    lambda x: 10 * math.sin(x) + 6 * math.cos(x * 2),
    # 6. Three-frequency harmonic (max amp 15)
    lambda x: 8 * math.sin(x) + 4 * math.cos(x * 2) + 3 * math.sin(x * 3),
    # 7. Beat frequency (slowly modulating) (max amp 16)
    lambda x: 8 * (math.sin(x * 1.0) + math.sin(x * 1.1)),
    # 8. Cosine wave with a phase and frequency shift
    lambda x: 16 * math.cos(x * 1.5 - 1),
    # 9. Complex harmonic series (max amp 13)
    lambda x: 7*math.sin(x) + 3*math.sin(2*x) + 2*math.sin(3*x) + 1*math.sin(4*x),
    # 10. Simple frequency multiplication (max amp 8)
    lambda x: 8 * math.sin(x) * math.cos(x), # Equivalent to 4*sin(2*x)
    # 11. Full-range S-curve (tanh)
    lambda x: 17 * math.tanh(x),
    # 12. Steeper S-curve (compressed horizontally)
    lambda x: 17 * math.tanh(x * 2),
    # 13. Slower S-curve (stretched horizontally)
    lambda x: 17 * math.tanh(x * 0.4),
    # 14. Arctan S-curve (naturally bounded) (range ~[-13.7, 13.2])
    lambda x: 10 * math.atan(x),
    # 15. Scaled arctan to fill range (range ~[-15.6, 15.1])
    lambda x: 16 * math.atan(x) * (2 / math.pi),
    # 16. Shifted parabola (range [-10, 2.15])
    lambda x: 0.6 * (x + 0.5)**2 - 10,
    # 17. Asymmetric cubic (range [-17, 8.7])
    lambda x: 17 * (x / 5.0)**3,
    # 18. Centered "W" shaped quartic (range [-10, 5.6])
    lambda x: (x**4) / 40.0 - 10,
    # 19. Simple scaled cubic (range ~[-15.6, 8])
    lambda x: x**3 / 8.0,
    # 20. Simple scaled quadratic (range [0, 15])
    lambda x: 0.6 * x**2,
    # 21. Chirped wave (frequency increases with |x|)
    lambda x: 16 * math.sin(x**2 / 3.0),
    # 22. Gaussian-modulated wave (a "wavelet") (max amp 15)
    lambda x: 15 * math.cos(x * 3) * math.exp(-(x**2) / 8.0),
    # 23. Growing oscillation (well-behaved in range)
    lambda x: 3 * x * math.sin(x * 2),
    # 24. Linear ramp envelope (range `~[-15.3, 0]`)
    lambda x: (x + 5) * math.cos(x * 4) - 15,
    # 25. Sine wave with a linear ramp envelope (range `~[-15.3, 10.2]`)
    lambda x: 16 * math.sin(x) * (x / 5.0),
    # 26. Asymmetric frequency sine wave (max 17, -17)
    lambda x: 17 * math.sin(math.pi * x / (5.0 if x < 0 else 4.0)),
    # 27. Bouncing ball / absolute value sine
    lambda x: 15 * abs(math.sin(x * 1.5)) - 5,
    # 28. Square-root "ramps" (range ~[-11.1, 10])
    lambda x: 5 * math.sqrt(abs(x)) * math.copysign(1, x),
    # 29. Rotated sine/cosine (max amp ~11.3)
    lambda x: 8 * math.sin(x) - 8 * math.cos(x),
    # 30. Step-like function from steep tanh
    lambda x: 10 * math.tanh(x * 5) + 5 * math.tanh(x * 2),
    # 31. Linear ramp (range [-8.5, 8.5])
    lambda x: 17 * (x + 0.5) / 4.5 - 8.5,
    # 32. Clipped sine wave (soft clip) (range ~[-15, 15])
    lambda x: 15 * math.tanh(math.sin(x) * 3),
    # 33. Exponentially decaying sine wave (range ~[-11.8, 16])
    lambda x: 16 * math.sin(x * 2) * math.exp(-x / 5.0),
    # 34. (Corrected) Sawtooth (range [-8, 8])
    lambda x: 8 * (x - math.floor(x)) * 2 - 8,
    # 35. Slow envelope * fast wave (max amp 16)
    lambda x: 16 * math.sin(x / 5.0 * math.pi) * math.cos(x * 4),

    # --- 50 NEW FUNCTIONS ---

    # --- Vertical Axis Optimized (Wide range, best for x_val in [-16, 17]) ---

    # 36. Sinc function (damped wave)
    lambda x: 16 * np.sinc(x / 2.0), # np.sinc(x) = sin(pi*x)/(pi*x)
    # 37. Damped cosine
    lambda x: 16 * math.cos(x * 2) * math.exp(-abs(x) / 8.0),
    # 38. Bouncing wave (abs(sin) * abs(cos))
    lambda x: 15 * abs(math.sin(x * 0.8)) * abs(math.cos(x * 2.5)),
    # 39. Sharp S-curve from error function
    lambda x: 17 * math.erf(x * 0.5),
    # 40. High-frequency tan applied to sin (creates asymptotes)
    lambda x: 4 * math.tan(math.sin(x * 0.5)),
    # 41. Wood grain / Perlin-like
    lambda x: 8 * math.sin(x) + 4 * math.sin(x*3.1) + 2 * math.cos(x*5.3),
    # 42. Sharp digital-like wave (sign function)
    lambda x: 10 * (math.sin(x) + 0.3 * math.sin(x*3)),
    # 43. Parabolic troughs
    lambda x: 0.1 * (x**2) + 5 * math.cos(x * 2) - 10,
    # 44. Sharp "laser" spike (inverted Gaussian)
    lambda x: 17 - 25 * math.exp(-(x**2) / 0.5),
    # 45. Logistic curve
    lambda x: 17 / (1 + math.exp(-x)) - 8.5,
    # 46. Hyperbolic cosine (catenary curve)
    lambda x: 0.5 * math.cosh(x*0.5) - 10,
    # 47. Steep steps (floor + sin)
    lambda x: math.floor(x/2) + 3*math.sin(x*3),
    # 48. Sharp inverse decay
    lambda x: 10 / (x + 0.1) if x > 0 else (10 / (x - 0.1) if x < 0 else 0),
    # 49. Logarithmic curve (shifted)
    lambda x: 8 * math.log(abs(x) + 1) * math.copysign(1, x),
    # 50. Elliptical shape (top half)
    lambda x: 4 * math.sqrt(max(0, 16 - (x/2)**2)),
    # 51. Ripple tank (cos(r))
    lambda x: 16 * math.cos(math.sqrt(x**2 + 0.1)),
    # 52. Interference pattern (two sources)
    lambda x: 8 * (math.sin(abs(x - 5)) + math.sin(abs(x + 5))),
    # 53. Inverse quadratic
    lambda x: 17 / (1 + (x/2)**2) - 8,
    # 54. Gaussian pulse train
    lambda x: 15 * math.exp(-((x % 5 - 2.5)**2) / 0.5),
    # 55. Sharp sawtooth
    lambda x: 16 * (x/3 - math.floor(x/3)) - 8,
    # 56. Simple fractal noise (sum of sines)
    lambda x: 9 * math.sin(x * 0.7) + 5 * math.sin(x * 1.8) + 3 * math.sin(x * 4.2),
    # 57. Bessel function (J0) - a damped, spreading wave
    lambda x: 16 * np.i0(x * 0.8) / 10 - 8, # np.i0 is a Bessel function
    # 58. Modulated S-curve
    lambda x: 15 * math.tanh(x * 0.5) * math.cos(x * 0.5),
    # 59. Alternating magnitude wave
    lambda x: 10 * math.sin(x) if int(x) % 2 == 0 else 16 * math.sin(x),
    # 60. Sharp peaks (1/cos)
    lambda x: 3 / (math.cos(x) + 1.1) - 1,
    # 61. Fast oscillation in envelope
    lambda x: 16 * (x/16) * math.sin(x*5),
    # 62. Damped spring motion
    lambda x: 16 * math.exp(-x/8) * math.cos(x*2) if x > 0 else 16 * math.exp(x/8) * math.cos(x*2),
    # 63. "Heartbeat" (two Gaussian pulses)
    lambda x: 15 * math.exp(-((x % 4 - 1)**2) / 0.1) + 10 * math.exp(-((x % 4 - 1.5)**2) / 0.1),
    # 64. Power spectrum-like decay
    lambda x: 16 / (1 + abs(x)),
    # 65. Hyperbolic tangent of sine
    lambda x: 16 * math.tanh(4 * math.sin(x)),
    # 66. Sharp, thin spikes (cotangent)
    lambda x: 4 * (1 / (math.tan(x/2) + 1e-6)),
    # 67. "Staircase" function
    lambda x: 4 * round(x / 2),
    # 68. Sine wave on a parabola
    lambda x: 0.1 * x**2 + 5 * math.sin(x*3) - 12,
    # 69. Complex S-curve
    lambda x: 17 * (x / (1 + abs(x))),
    # 70. Wave packet
    lambda x: 16 * math.cos(x * 8) * math.exp(-((x-5)**2) / 8) if x > 0 else 16 * math.cos(x * 8) * math.exp(-((x+5)**2) / 8),
    
    # --- Horizontal Axis Optimized (Narrow range, best for x_val in [-4, 4]) ---
    
    # 71. Very fast wave
    lambda x: 4 * math.sin(x * 10),
    # 72. Steep parabola
    lambda x: 4 * (x**2) - 4,
    # 73. Steep cubic
    lambda x: 4 * (x**3) / 10,
    # 74. Sharp central spike (Gaussian)
    lambda x: 4 * math.exp(-(x**2) / 0.5) * 2 - 4,
    # 75. Box function (square pulse)
    lambda x: 4 if abs(x) < 2 else -4,
    # 76. Triangle wave (narrow)
    lambda x: 4 * (abs(x % 2 - 1) * 2 - 1),
    # 77. V-Shape (absolute value)
    lambda x: 4 * abs(x) - 4,
    # 78. W-Shape (quartic)
    lambda x: 2 * (x**4) - 4 * (x**2),
    # 79. Rapid S-curve
    lambda x: 4 * math.tanh(x * 3),
    # 80. Cosine (full range in 9 pixels)
    lambda x: 4 * math.cos(x * (math.pi / 4)),
    # 81. Two sharp spikes
    lambda x: 4 * (math.exp(-((x-2)**2) / 0.2) + math.exp(-((x+2)**2) / 0.2)) - 4,
    # 82. Narrow sinc function
    lambda x: 4 * np.sinc(x * 2),
    # 83. Sine (full period)
    lambda x: 4 * math.sin(x * (math.pi / 4)),
    # 84. Steep steps
    lambda x: 2 * round(x),
    # 85. Sharp inverse (1/x)
    lambda x: 4 / x if abs(x) > 0.5 else 0,
]


def pick_largest_graph(x):
    vert_graph = create_graph_with_vertical_x_axis(False, x, False)
    horiz_graph = create_graph_with_horizontal_x_axis(False, x, False)
    vert_count = sum(1 for row in vert_graph for cell in row if cell == 1)
    horiz_count = sum(1 for row in horiz_graph for cell in row if cell == 1)
    return horiz_graph if horiz_count >= vert_count else vert_graph



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