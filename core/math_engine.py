import numpy as np
import math
from typing import Callable, List
from core.led_commands import log, WIDTH, HEIGHT, draw_matrix_on_board
import matplotlib.pyplot as plt


unguessable_constant = 42067691101123456789



def plot_function(func, x_min, x_max, num_points=400, title="Plot of Function", label="f(x)"):
    """
    Visualizes a given mathematical function using matplotlib.

    Parameters:
    func (callable): The function to plot (e.g., lambda x: x**2).
                    This function MUST be vectorized (i.e., accept a numpy array).
    x_min (float): The minimum value of the x-range.
    x_max (float): The maximum value of the x-range.
    num_points (int): The number of points to use for the plot's resolution.
    title (str): The title for the plot.
    label (str): The label for the plot line.
    """
    
    # You can't plot a range where the start is at or after the end.
    if x_min >= x_max:
        print(f"Invalid range: x_min ({x_min}) must be strictly less than x_max ({x_max}).")
        return

    # 1. Create the domain (x-values)
    # np.linspace generates an array of 'num_points' evenly spaced
    # values between x_min and x_max.
    x_values = np.linspace(x_min, x_max, num_points)

    # 2. Create the range (y-values)
    # We apply the user's lambda function to the entire x_values array.
    try:
        y_values = func(x_values)
    except Exception as e:
        print(f"Failed to evaluate the function: {e}")
        print("Ensure your function is vectorized (use numpy functions like np.sin).")
        return

    # 3. Create the plot
    plt.figure(figsize=(10, 6))
    
    # Handle discontinuities like 1/x by masking 'inf' values
    y_values = np.ma.masked_invalid(y_values)
    
    plt.plot(x_values, y_values, label=label)

    # 4. Add styling and labels
    plt.title(title)
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Add centered x and y axes for better visualization
    plt.axhline(0, color='black', linewidth=0.8)
    plt.axvline(0, color='black', linewidth=0.8)
    
    # Set y-limits to be reasonable if there are large values
    # (e.g., for 1/x near zero)
    mean = np.mean(y_values)
    std = np.std(y_values)
    plt.ylim(mean - 4*std, mean + 4*std) # Clamp to 4 standard deviations
    
    plt.legend()
    plt.show()
    

def safe_log(x) -> np.ndarray:
    """Logarithm that is safe for values <= 0."""
    return np.log(np.abs(x) + 1e-6)

def safe_sqrt(x) -> np.ndarray:
    """Square root that is safe for negative values."""
    return np.sqrt(np.abs(x))

def safe_div(a, b) -> np.ndarray:
    """Division that is safe for division by zero."""
    return np.where(np.abs(b) < 1e-6, a / 1e-6, a / b)

def safe_sinc(x) -> np.ndarray:
    """Wrapper for numpy's sinc function."""
    return np.sinc(x)

# --- New Safe Wrappers for Domain-Restricted Functions ---

def safe_arcsin(x):
    """Arcsin clipped to the domain [-1, 1]"""
    return np.arcsin(np.clip(x, -1.0, 1.0))

def safe_arccos(x):
    """Arccos clipped to the domain [-1, 1]"""
    return np.arccos(np.clip(x, -1.0, 1.0))

def safe_arccosh(x):
    """Arccosh clipped to the domain [1, inf]"""
    # Clip to minimum value of 1.0
    return np.arccosh(np.clip(x, 1.0, None))

def safe_arctanh(x):
    """Arctanh clipped to the domain [-1, 1]"""
    # Clip just inside the bounds to avoid infinity
    return float(np.arctanh(np.clip(x, -0.999999, 0.999999)))


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

REGULAR_OPERATIONS = {
    "sin": lambda x: np.sin(x),
    "cos": lambda x: np.cos(x),
    "tan": lambda x: np.tan(x),
    "exp": lambda x: np.exp(x),
    "log": lambda x: np.log(np.abs(x) + 1e-6),
    "sqrt": lambda x: np.sqrt(np.abs(x)),
    "sinc": lambda x: np.sinc(x),
    "arcsin": lambda x: np.arcsin(np.clip(x, -1.0, 1.0)),
    "arccos": lambda x: np.arccos(np.clip(x, -1.0, 1.0)),
    "arctanh": lambda x: np.arctanh(np.clip(x, -0.999999, 0.999999)),
    "arccosh": lambda x: np.arccosh(x)
}



MATH_OPERATIONS = [
    # 1-85: Curated Functions (Preserved)
    lambda x: 16 * np.sin(x), lambda x: 16 * np.cos(x), lambda x: 16 * np.sin(x * 3), lambda x: 16 * np.sin(x * 0.5), lambda x: 10 * np.sin(x) + 6 * np.cos(x * 2), lambda x: 8 * np.sin(x) + 4 * np.cos(x * 2) + 3 * np.sin(x * 3),
    lambda x: 8 * (np.sin(x * 1.0) + np.sin(x * 1.1)), lambda x: 16 * np.cos(x * 1.5 - 1), lambda x: 7*np.sin(x) + 3*np.sin(2*x) + 2*np.sin(3*x) + 1*np.sin(4*x), lambda x: 8 * np.sin(x) * np.cos(x), lambda x: 17 * np.tanh(x), lambda x: 17 * np.tanh(x * 2),
    lambda x: 17 * np.tanh(x * 0.4), lambda x: 10 * np.arctan(x), lambda x: 16 * np.arctan(x) * (2 / np.pi), lambda x: 0.6 * (x + 0.5)**2 - 10, lambda x: 17 * (x / 5.0)**3, lambda x: (x**4) / 40.0 - 10,
    lambda x: x**3 / 8.0, lambda x: 0.6 * x**2, lambda x: 16 * np.sin(x**2 / 3.0), lambda x: 15 * np.cos(x * 3) * np.exp(-(x**2) / 8.0), lambda x: 3 * x * np.sin(x * 2), lambda x: (x + 5) * np.cos(x * 4) - 15,
    lambda x: 16 * np.sin(x) * (x / 5.0), lambda x: 17 * np.sin(np.pi * x / (5.0 if x < 0 else 4.0)), lambda x: 15 * np.abs(np.sin(x * 1.5)) - 5, lambda x: 5 * np.sqrt(np.abs(x)) * np.copysign(1, x), lambda x: 8 * np.sin(x) - 8 * np.cos(x), lambda x: 10 * np.tanh(x * 5) + 5 * np.tanh(x * 2),
    lambda x: 17 * (x + 0.5) / 4.5 - 8.5, lambda x: 15 * np.tanh(np.sin(x) * 3), lambda x: 16 * np.sin(x * 2) * np.exp(-x / 5.0), lambda x: 8 * (x - np.floor(x)) * 2 - 8, lambda x: 16 * np.sin(x / 5.0 * np.pi) * np.cos(x * 4), lambda x: 16 * np.sinc(x / 2.0),
    lambda x: 16 * np.cos(x * 2) * np.exp(-np.abs(x) / 8.0), lambda x: 15 * np.abs(np.sin(x * 0.8)) * np.abs(np.cos(x * 2.5)), lambda x: 17 * np.sin(x * 0.5), lambda x: 4 * np.tan(np.sin(x * 0.5)), lambda x: 8 * np.sin(x) + 4 * np.sin(x*3.1) + 2 * np.cos(x*5.3), lambda x: 10 * (np.sin(x) + 0.3 * np.sin(x*3)),
    lambda x: 0.1 * (x**2) + 5 * np.cos(x * 2) - 10, lambda x: 17 - 25 * np.exp(-(x**2) / 0.5), lambda x: 17 / (1 + np.exp(-x)) - 8.5, lambda x: 0.5 * np.cosh(x*0.5) - 10, lambda x: np.floor(x/2) + 3*np.sin(x*3), lambda x: 10 / (x + 0.1) if x > 0 else (10 / (x - 0.1) if x < 0 else 0),
    lambda x: 8 * np.log(np.abs(x) + 1) * np.copysign(1, x), lambda x: 4 * np.sqrt(np.maximum(0, 16 - (x/2)**2)), lambda x: 16 * np.cos(np.sqrt(x**2 + 0.1)), lambda x: 8 * (np.sin(np.abs(x - 5)) + np.sin(np.abs(x + 5))), lambda x: 17 / (1 + (x/2)**2) - 8, lambda x: 15 * np.exp(-((x % 5 - 2.5)**2) / 0.5),
    lambda x: 16 * (x/3 - np.floor(x/3)) - 8, lambda x: 9 * np.sin(x * 0.7) + 5 * np.sin(x * 1.8) + 3 * np.sin(x * 4.2), lambda x: 16 * np.i0(x * 0.8) / 10 - 8, lambda x: 15 * np.tanh(x * 0.5) * np.cos(x * 0.5), lambda x: 10 * np.sin(x) if np.all(np.floor(x) % 2 == 0) else 16 * np.sin(x), lambda x: 3 / (np.cos(x) + 1.1) - 1,
    lambda x: 16 * (x/16) * np.sin(x*5), lambda x: 16 * np.exp(-x/8) * np.cos(x*2) if np.all(x > 0) else 16 * np.exp(x/8) * np.cos(x*2), lambda x: 15 * np.exp(-((x % 4 - 1)**2) / 0.1) + 10 * np.exp(-((x % 4 - 1.5)**2) / 0.1), lambda x: 16 / (1 + np.abs(x)), lambda x: 16 * np.tanh(4 * np.sin(x)), lambda x: 4 * (1 / (np.tan(x/2) + 1e-6)),
    lambda x: 4 * np.round(x / 2), lambda x: 0.1 * x**2 + 5 * np.sin(x*3) - 12, lambda x: 17 * (x / (1 + np.abs(x))), lambda x: 16 * np.cos(x * 8) * np.exp(-((x-5)**2) / 8) if np.all(x > 0) else 16 * np.cos(x * 8) * np.exp(-((x-5)**2) / 8), lambda x: 4 * np.sin(x * 10), lambda x: 4 * (x**2) - 4,
    lambda x: 4 * (x**3) / 10, lambda x: 4 * np.exp(-(x**2) / 0.5) * 2 - 4, lambda x: np.where(np.abs(x) < 2, 4, -4), lambda x: 4 * (np.abs(x % 2 - 1) * 2 - 1), lambda x: 4 * np.abs(x) - 4, lambda x: 2 * (x**4) - 4 * (x**2),
    lambda x: 4 * np.tanh(x * 3), lambda x: 4 * np.cos(x * (np.pi / 4)), lambda x: 4 * (np.exp(-((x-2)**2) / 0.2) + np.exp(-((x+2)**2) / 0.2)) - 4, lambda x: 4 * np.sinc(x * 2), lambda x: 4 * np.sin(x * (np.pi / 4)), lambda x: 2 * np.round(x),
    lambda x: np.where(np.abs(x) > 0.5, 4 / x, 0),
    # --- Machine-Generated Functinons ---
    lambda x: safe_log(x), lambda x: np.exp(x), lambda x: np.expm1(x), lambda x: safe_arctanh((np.tan((x + -94.0)) + x)), lambda x: np.cbrt(safe_log(np.cosh(x))),
    lambda x: (safe_log(np.cosh(x)) ** 1.5), lambda x: np.floor((-10.0 * np.exp(x))), lambda x: safe_arcsin(np.arcsinh(x)), lambda x: np.tan(x), lambda x: np.cos(x), lambda x: (x + x),
    lambda x: (np.sin(((np.cosh(np.exp(-96.0)) + x) * np.exp2(x))) + x), lambda x: np.exp(((-0.214 * safe_sinc(73.0)) + x)), lambda x: (np.expm1(0.84) + np.ceil(safe_arccosh(((x - -9.0) * x)))), lambda x: np.cbrt(np.cbrt((x + x))), lambda x: (-17.0 * np.cbrt((x * (x * safe_sinc(np.exp((safe_arccos(np.exp(safe_sqrt(safe_sqrt(np.tanh(np.tan(np.ceil(np.cos(x)))))))) + x))))))), lambda x: (np.exp(x) ** 1.0),
    lambda x: (safe_arcsin(np.exp(x)) ** 1.4), lambda x: safe_log((x - safe_sqrt((np.square(np.cbrt(-2.0)) ** 0.9)))), lambda x: (np.exp2(x) + safe_arccosh(np.exp2((safe_sinc(x) * safe_log(x))))), lambda x: np.sign(np.cos(x)), lambda x: (x + safe_log(x)), lambda x: (((x * x) + 0.396) + (x + np.cos(x))),
    lambda x: np.log1p(np.exp(x)), lambda x: np.expm1(np.cosh(x)), lambda x: np.abs(np.sinh(np.cosh(((1.36 * x) * (x + -1.96))))), lambda x: np.ceil(((x + ((-2.46 ** 2.0) + np.expm1(-0.24))) + x)), lambda x: safe_arcsin(((np.floor((0.71 * x)) * np.tan((x - 2.04))) + x)), lambda x: (np.expm1((2.5 * (np.floor(x) - x))) * 2.9),
    lambda x: (-3.79 * x), lambda x: np.arctan(np.cos(x)), lambda x: (safe_sinc(np.exp((-2.58 - x))) * np.tanh(np.sign((-1.12 ** 2.1)))), lambda x: np.exp((x * np.arcsinh(1.48))), lambda x: np.arcsinh(np.cosh(safe_arccos((np.expm1(x) + -0.11)))), lambda x: safe_arccosh(np.ceil(x)),
    lambda x: np.cbrt(np.exp((x * 3.09))), lambda x: np.sin((((np.sin(2.72) ** 0.6) ** 1.7) * (np.cosh(x) - ((0.44 + -2.4) + safe_log(x))))), lambda x: np.cbrt((x + ((x + np.cbrt(-3.71)) - np.exp(safe_log(-0.23))))), lambda x: np.tanh(np.cos(x)), lambda x: ((x - np.floor(np.abs(x))) - 3.4), lambda x: (np.cos((-2.57 - safe_arccosh(np.cbrt(x)))) - x),
    lambda x: ((x * np.tanh(-3.37)) + safe_sinc(x)), lambda x: (safe_log(safe_arccosh(np.exp2((-3.9 * x)))) + x), lambda x: (np.expm1((x - ((x - 2.84) - (-3.33 * 1.4)))) - ((((-0.39 * x) + safe_arcsin(x)) * (-0.36 * safe_arcsin(x))) * x)), lambda x: (np.ceil(x) + (-2.28 + x)), lambda x: np.expm1(safe_log(np.cosh((np.abs(1.28) + (1.53 - x))))), lambda x: (np.exp(np.arctan(-2.72)) * (x + (safe_sinc(x) + safe_arccos((x + x))))),
    lambda x: (np.sign(x) - safe_sqrt(x)), lambda x: (np.exp(x) - ((x * np.floor(safe_log((safe_arcsin(np.arctan(x)) - np.sign(np.expm1(np.sign((x * 2.78)))))))) - np.sign(np.sinh(-3.88)))), lambda x: np.tanh(np.ceil(x)), lambda x: np.tanh(np.cbrt(x)), lambda x: safe_log((safe_sqrt((x - np.exp((x + np.expm1(safe_arccosh(np.cbrt(safe_arcsin(0.77)))))))) * safe_arcsin((((x * 1.52) - x) - np.floor((safe_arccos(0.0) * np.exp2(x))))))), lambda x: (np.cosh(x) ** 0.6),
    lambda x: (safe_sinc((safe_arcsin((x + safe_arccosh(x))) * np.abs(-2.0))) + np.exp2(x)), lambda x: (np.expm1(x) - (np.sin(2.92) * -1.67)), lambda x: ((np.sinh(np.cos((np.tan(safe_sinc(np.cbrt(np.cos(x)))) ** 1.2))) + (((np.log1p(-0.57) - np.cos(-3.2)) * x) + x)) - -3.55), lambda x: np.floor(safe_log((np.expm1((np.arctan((x + np.exp2((x - 2.54)))) * (-1.58 * ((np.cbrt(-0.63) + np.expm1(x)) - np.tan(x))))) ** 1.0))), lambda x: np.floor(np.expm1(x)), lambda x: (-1.83 + (np.cosh(x) ** 2.5)),
    lambda x: (x * -1.98), lambda x: np.cosh((np.sinh(np.sign(1.68)) + x)), lambda x: (safe_sinc(np.arcsinh(np.square(np.expm1(0.18)))) + np.expm1(np.expm1(np.arcsinh((-0.96 + x))))), lambda x: (np.exp2((x + safe_arctanh(-1.89))) - x), lambda x: (-2.71 - np.sin(((-3.88 ** 1.0) * np.floor((1.65 - x))))), lambda x: ((np.expm1(0.76) ** 1.9) + np.tanh(np.sinh(x))),
    lambda x: (np.expm1(x) ** 1.0), lambda x: ((np.sin(x) + (2.01 - -1.72)) + -2.45), lambda x: (((np.square(np.abs(x)) * (np.ceil((np.cos(np.ceil(x)) + np.sin(np.abs(safe_log((-3.68 ** 1.1)))))) ** 1.3)) ** 0.9) ** 2.3), lambda x: (safe_log(x) + x), lambda x: (3.45 * np.cos(x)), lambda x: np.sinh(safe_arccos(np.exp(x))),
    lambda x: np.expm1((-0.81 - x)), lambda x: (safe_sqrt(x) + x), lambda x: safe_log(safe_sqrt(np.expm1(x))), lambda x: safe_arccos(np.exp2(x)), lambda x: np.tan(safe_log(np.exp(x))), lambda x: np.square(np.tan(x)),
    lambda x: (np.cosh(np.tan(np.expm1(((((np.floor(0.74) - -3.58) * np.sign((2.84 + 0.84))) ** 2.6) - x)))) - np.sign(np.tanh(safe_sqrt(x)))), lambda x: np.tanh((x - np.cbrt(safe_sinc((np.square(np.arcsinh(safe_sqrt((np.tanh(3.99) * x)))) - np.exp2((safe_sqrt(1.55) ** 0.9))))))), lambda x: (x + ((x + x) - np.sinh(x))), lambda x: np.cos(np.abs(x)), lambda x: (0.6 + np.cbrt(x)), lambda x: ((np.exp2(x) + np.sinh(np.cos(np.cbrt(-1.5)))) ** 1.7),
    lambda x: (np.abs(2.27) + np.arcsinh(x)), lambda x: np.cos((-3.54 * x)), lambda x: (x * (np.exp2(np.arctan(((safe_sqrt(np.square(np.expm1((-3.26 ** 1.7)))) ** 2.6) + x))) + (0.84 ** 2.9))), lambda x: (x + ((-0.62 ** 2.2) + x)), lambda x: (np.exp2(np.log1p(3.46)) - np.cosh((3.98 + x))), lambda x: (np.ceil(np.cosh(x)) + (x + 0.66)),
    lambda x: np.exp2((safe_arccosh(x) ** 1.4)), lambda x: (x - np.ceil(np.expm1(x))), lambda x: np.tanh((2.02 - safe_arccos(x))), lambda x: (3.05 + np.tan(np.sin(np.ceil(x)))), lambda x: (safe_sqrt(np.expm1(x)) ** 2.9), lambda x: ((np.square(np.abs(2.41)) + np.cbrt(1.38)) * np.cbrt(np.tan((x - 1.23)))),
    lambda x: ((x + x) - -3.58), lambda x: (x * -2.17), lambda x: safe_log((x + np.arctan((np.sinh(x) * np.abs(np.abs(safe_arcsin(((x + np.cbrt(3.96)) - safe_arccos((x * -0.46)))))))))), lambda x: (((x + -3.82) + x) + np.cos((-3.93 * np.abs(0.97)))), lambda x: (x * ((1.28 * np.abs(2.5)) ** 0.9)), lambda x: (x + (np.exp2(np.square(np.abs(safe_arccos((x * x))))) - 1.26)),
    lambda x: np.tanh(((x - ((-0.59 ** 2.1) * (0.29 ** 1.0))) + safe_sinc(3.1))), lambda x: (x + (-1.27 + x)), lambda x: (np.sign(np.cosh(safe_log(x))) + (x - np.expm1(x))), lambda x: (x * np.ceil(np.arctan(x))), lambda x: ((x * (np.ceil(-0.63) + np.sinh(np.tanh((np.sinh(safe_arcsin((x - np.log1p(safe_arcsin(-0.44))))) * np.exp(2.65)))))) - safe_arccosh(x)), lambda x: np.tan(((-1.94 * x) - np.sin(x))),
    lambda x: safe_arccosh(np.ceil((x + (-1.47 * x)))), lambda x: safe_arccosh(np.floor(np.exp(x))), lambda x: np.exp(safe_arcsin(x)), lambda x: safe_arcsin((safe_arccos(x) ** 0.6)), lambda x: (safe_arccosh((x ** 3.0)) ** 1.5), lambda x: safe_sqrt((np.exp(x) + -1.46)),
    lambda x: (x * safe_arccos((-3.39 + (3.85 ** 0.8)))), lambda x: (x - safe_arcsin(np.tanh(np.abs((3.86 + x))))), lambda x: np.cos(np.sinh(np.floor(np.arctan(x)))), lambda x: np.tanh(np.cbrt((np.tanh(np.tan(1.38)) - x))), lambda x: np.sinh((-0.79 * np.cos(x))), lambda x: (x * -3.72),
    lambda x: (np.sin(x) - np.abs((safe_arcsin(np.sin((-1.93 * np.tanh(x)))) + safe_log(1.4)))), lambda x: (x * 0.99), lambda x: safe_sqrt((np.sinh(x) + -2.86)), lambda x: safe_sqrt((np.exp2(0.21) + (-2.46 + np.abs(x)))), lambda x: np.arcsinh((x - (x + np.exp(x)))), lambda x: (np.exp(x) + (((x - safe_sqrt(x)) ** 1.0) + x)),
    lambda x: np.abs(safe_arccos(np.arctan(np.arcsinh(safe_arccosh(x))))), lambda x: (x - np.cosh(np.arcsinh(x))), lambda x: np.exp((np.abs(np.exp(np.tan((x * 0.96)))) + x)), lambda x: np.cos((x - np.cosh(-2.89))), lambda x: np.cos(((np.square(-1.07) * safe_arccosh((x + x))) + x)), lambda x: np.log1p(safe_arccosh((x + (-3.05 + -1.42)))),
    lambda x: (x * -3.79), lambda x: np.floor(np.tan(np.floor(x))), lambda x: np.exp2((x + -0.85)), lambda x: np.cosh(((-2.54 * np.square(safe_sqrt(x))) + x)), lambda x: (safe_arccosh(2.23) - (x + x)), lambda x: safe_arcsin(safe_arccos(x)),
    lambda x: np.cbrt(np.arctan(x)), lambda x: (safe_log(np.floor(x)) - (x * (x + (0.13 ** 2.4)))), lambda x: safe_arccosh(np.expm1(x)), lambda x: (x + np.expm1(np.ceil(x))), lambda x: np.sinh((np.cbrt(np.abs(x)) - x)), lambda x: np.square((np.cbrt(safe_log((x + x))) - x)),
    lambda x: (x + safe_sqrt(x)),
]


def ridiculously_safe_round(x: int | float) -> int:
    """
    Rounds a scalar numeric value with extreme safety.
    Returns 0 for complex numbers, NaN, Inf, or any non-numeric type.
    """
    if isinstance(x, complex):
        return unguessable_constant
        
    try:
        if not math.isfinite(x):
            return unguessable_constant
    except (TypeError, ValueError):
        return unguessable_constant


    return round(x)


def pick_largest_graph(x) -> List[List[int]]:
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
            y_val = function(xf)
            if isinstance(y_val, np.ndarray):
                y_val = y_val.item()
            y = ridiculously_safe_round(y_val)
            if y == unguessable_constant:
                continue
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
            if isinstance(y_val, np.ndarray):
                y_val = y_val.item()
            y = ridiculously_safe_round(y_val)
            if y == unguessable_constant:
                continue
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

# for func in MATH_OPERATIONS:
#     try:
#         plot_function(func, -20, 20, 999999, func.__name__, str(f"{func}"))
#     except Exception as e:
#         log(f"Error plotting function {func}: {e}")
