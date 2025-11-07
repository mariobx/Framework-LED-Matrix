import math

STARTING_STATES_GOF = {
    # --- Classic Oscillators (Blinkers) ---
    "blinker": [
        # The simplest period-2 oscillator
        (17, 3), (17, 4), (17, 5)
    ],
    "toad": [
        # A period-2 oscillator
        (17, 3), (17, 4), (17, 5),
        (18, 2), (18, 3), (18, 4)
    ],
    "pentadecathlon": [
        # A period-15 oscillator, fits perfectly.
        (12, 4),
        (13, 4),
        (14, 2), (14, 4), (14, 6),
        (15, 4),
        (16, 4),
        (17, 4),
        (18, 4),
        (19, 2), (19, 4), (19, 6),
        (20, 4),
        (21, 4)
    ],

    # --- Spaceships (Travelers) ---
    "glider": [
        # The classic. Will now travel diagonally forever.
        (1, 2), 
        (2, 3), 
        (3, 1), (3, 2), (3, 3)
    ],
    "lwss": [
        # "Lightweight Spaceship", travels horizontally.
        # It will wrap the 9-column width very quickly.
        (17, 3), (17, 5),
        (18, 2),
        (19, 2), (19, 5),
        (20, 2), (20, 3), (20, 4), (20, 5)
    ],

    # --- Methuselahs (Long-Running) ---
    "r_pentomino": [
        # Stabilizes after 1103 generations
        (17, 4), (17, 5),
        (18, 3), (18, 4),
        (19, 4)
    ],
    "diehard": [
        # Dies after 130 generations
        (17, 7),
        (18, 1), (18, 2),
        (19, 2), (19, 5), (19, 6), (19, 7)
    ],
    "acorn": [
        # Runs for 5206 generations
        (17, 2),
        (18, 4),
        (19, 1), (19, 2), (19, 5), (19, 6), (19, 7)
    ],
    
    # --- Still Lifes (Stable) ---
    "block": [
        # The simplest stable pattern
        (17, 3), (17, 4),
        (18, 3), (18, 4)
    ],
    "beehive": [
        # Another common still life
        (17, 3), (17, 4),
        (18, 2), (18, 5),
        (19, 3), (19, 4)
    ]
}


math_operations = [
    # --- Trigonometric (Basic & Harmonics) ---

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

    # --- S-Curves & Bounded Functions (tanh, atan) ---

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

    # --- Polynomials (Scaled to Fit) ---
    # Note: x^2 range [0, 25], x^3 range [-125, 64]

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

    # --- Combinations & Exotic Shapes ---

    # 21. Chirped wave (frequency increases with |x|)
    lambda x: 16 * math.sin(x**2 / 3.0),

    # 22. Gaussian-modulated wave (a "wavelet") (max amp 15)
    lambda x: 15 * math.cos(x * 3) * math.exp(-(x**2) / 8.0),

    # 23. Growing oscillation (well-behaved in range)
    lambda x: 3 * x * math.sin(x * 2),

    # 24. Linear ramp envelope (range `~[-15.3, 0]`)
    lambda x: (x + 5) * math.cos(x * 4) - 15, # Shifted down, x=-5 is 0-15=-15

    # 25. Sine wave with a linear ramp envelope (range `~[-15.3, 10.2]`)
    lambda x: 16 * math.sin(x) * (x / 5.0),

    # 26. Asymmetric frequency sine wave (max 17, -17)
    lambda x: 17 * math.sin(math.pi * x / (5.0 if x < 0 else 4.0)),

    # 27. Bouncing ball / absolute value sine
    lambda x: 15 * abs(math.sin(x * 1.5)) - 5, # Range [-5, 10]

    # 28. Square-root "ramps" (range ~[-11.1, 10])
    lambda x: 5 * math.sqrt(abs(x)) * math.copysign(1, x),

    # 29. Rotated sine/cosine (max amp ~11.3)
    lambda x: 8 * math.sin(x) - 8 * math.cos(x),

    # 30. Step-like function from steep tanh
    lambda x: 10 * math.tanh(x * 5) + 5 * math.tanh(x * 2),

    # 31. Linear ramp (range [-8.5, 8.5])
    lambda x: 17 * (x + 0.5) / 4.5 - 8.5, # Scaled for [-5, 4] -> [-8.5, 8.5]
    
    # 32. Clipped sine wave (soft clip) (range ~[-15, 15])
    lambda x: 15 * math.tanh(math.sin(x) * 3),
    
    # 33. Exponentially decaying sine wave (range ~[-11.8, 16])
    lambda x: 16 * math.sin(x * 2) * math.exp(-x / 5.0),
    
    # 34. Sawtooth-like (using modulo, range [0, 16])
    lambda x: 16 * (x % 1.0) - 8, # `x % 1.0` gives range [0, 1]... oh wait, not for negatives.
    # 34. (Corrected) Sawtooth (range [-8, 8])
    lambda x: 8 * (x - math.floor(x)) * 2 - 8,

    # 35. Slow envelope * fast wave (max amp 16)
    lambda x: 16 * math.sin(x / 5.0 * math.pi) * math.cos(x * 4),
]