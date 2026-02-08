"""Configuration constants for Vector Tetris Grid Logic."""

# Screen dimensions
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 650
UI_HEIGHT = 80

# Grid configuration
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 28
GRID_OFFSET_X = 50
GRID_OFFSET_Y = UI_HEIGHT + 20

# Preview box (next piece)
PREVIEW_OFFSET_X = 360
PREVIEW_OFFSET_Y = UI_HEIGHT + 30
PREVIEW_BLOCK_SIZE = 20

# Game timing
FPS = 60
INITIAL_FALL_SPEED = 800  # ms per row
MIN_FALL_SPEED = 100
SPEED_INCREASE_INTERVAL = 10  # lines cleared per speed increase
SPEED_DECREASE = 50  # ms reduction per level

# Scoring
SCORE_1_LINE = 100
SCORE_2_LINES = 300
SCORE_3_LINES = 500
SCORE_4_LINES = 800
SOFT_DROP_SCORE = 1
HARD_DROP_SCORE = 2

# Colors (RGB)
COLOR_BG = (18, 18, 22)
COLOR_UI_BG = (25, 25, 32)
COLOR_GRID_BG = (12, 12, 16)
COLOR_GRID_BORDER = (50, 50, 60)
COLOR_GRID_LINES = (30, 30, 35)
COLOR_TEXT = (220, 220, 225)
COLOR_TEXT_DIM = (140, 140, 150)
COLOR_GHOST = (60, 60, 70)

# Tetromino colors (I, O, T, S, Z, J, L)
COLORS = [
    (0, 200, 200),    # I - Cyan
    (240, 200, 40),   # O - Yellow
    (170, 70, 200),   # T - Purple
    (80, 200, 80),    # S - Green
    (220, 60, 60),    # Z - Red
    (70, 120, 220),   # J - Blue
    (220, 140, 40),   # L - Orange
]

# Tetromino shapes
# Each shape is a list of (row, col) offsets
SHAPES = {
    'I': [(0, 0), (0, -1), (0, 1), (0, 2)],
    'O': [(0, 0), (0, 1), (1, 0), (1, 1)],
    'T': [(0, 0), (-1, 0), (0, -1), (0, 1)],
    'S': [(0, 0), (0, 1), (1, 0), (1, -1)],
    'Z': [(0, 0), (0, -1), (1, 0), (1, 1)],
    'J': [(0, 0), (-1, 0), (1, 0), (1, -1)],
    'L': [(0, 0), (-1, 0), (1, 0), (1, 1)],
}

# Wall kick data for rotation
# Format: (rotation, index) -> (dx, dy) offsets to try
WALL_KICKS = {
    'normal': [
        [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],  # 0->R
        [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],      # R->2
        [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],     # 2->L
        [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],   # L->0
    ],
    'I': [
        [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
        [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
    ],
}

# Shape order for randomizer
SHAPE_ORDER = list(SHAPES.keys())
