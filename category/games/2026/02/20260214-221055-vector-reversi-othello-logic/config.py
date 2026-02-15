"""Configuration for Vector Reversi Othello Logic."""

import os

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 900
BOARD_SIZE = 800
SIDE_PANEL_HEIGHT = 100

# Grid configuration
GRID_SIZE = 8
CELL_SIZE = BOARD_SIZE // GRID_SIZE

# Colors (R, G, B)
COLOR_BG = (30, 30, 30)
COLOR_GRID = (100, 100, 100)
COLOR_BLACK = (20, 20, 20)
COLOR_WHITE = (240, 240, 240)
COLOR_HINT = (50, 150, 50)
COLOR_HINT_HOVER = (70, 180, 70)
COLOR_VALID_MOVE = (0, 255, 0)
COLOR_PANEL = (40, 40, 40)
COLOR_TEXT = (200, 200, 200)

# Game states
EMPTY = 0
BLACK = 1
WHITE = 2

# Directions for checking flanks (dx, dy)
DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),          (0, 1),
    (1, -1),  (1, 0),  (1, 1)
]

# Font sizes
FONT_SIZE_LARGE = 36
FONT_SIZE_MEDIUM = 24
FONT_SIZE_SMALL = 18

# Animation settings
FLIP_DELAY = 100  # ms between piece flips in animation
