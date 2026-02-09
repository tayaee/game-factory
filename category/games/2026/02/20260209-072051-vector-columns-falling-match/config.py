"""Game configuration constants for Vector Columns Falling Match."""

import pygame

# Display settings
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 650
FPS = 60

# Grid settings
GRID_COLS = 6
GRID_ROWS = 13
CELL_SIZE = 40
GRID_OFFSET_X = 130
GRID_OFFSET_Y = 50

# Colors (RGB)
BLACK = (10, 10, 20)
WHITE = (240, 240, 250)
GRID_BG = (30, 30, 45)
GRID_BORDER = (60, 60, 80)

# Gem colors (6 types)
GEM_COLORS = [
    (255, 50, 50),    # Red
    (50, 255, 50),    # Green
    (50, 100, 255),   # Blue
    (255, 255, 50),   # Yellow
    (255, 100, 200),  # Magenta
    (50, 255, 255),   # Cyan
]

GEM_BORDER = (255, 255, 255)

# Game timing
INITIAL_FALL_DELAY = 800  # ms
MIN_FALL_DELAY = 100
SOFT_DROP_DELAY = 50
LOCK_DELAY = 300

# Scoring
BASE_SCORE = 100
CHAIN_MULTIPLIER = 1.5

# Speed thresholds
LEVEL_LINES = [5, 10, 15, 20, 30, 40, 50, 70, 100]
SPEED_DECREASE = 80

# Empty cell value
EMPTY = 0
