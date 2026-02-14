"""Game configuration and constants for Vector Snake Rattle Coin Dash."""

import math

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 15

# Isometric grid settings
GRID_SIZE = 20  # 20x20 grid
CELL_SIZE = 24  # Size of each isometric cell

# Isometric conversion constants
# Convert grid (x, y) to screen (screen_x, screen_y)
# For isometric: screen_x = (x - y) * (cell_width / 2), screen_y = (x + y) * (cell_height / 2)
ISO_ANGLE = math.radians(30)
ISO_COS = math.cos(ISO_ANGLE)
ISO_SIN = math.sin(ISO_ANGLE)

# Screen offset to center the isometric grid
OFFSET_X = SCREEN_WIDTH // 2
OFFSET_Y = 100

# UI settings
UI_HEIGHT = 60

# Colors (minimalist monochromatic vector style with gold accents)
COLOR_BG = (0, 0, 0)  # Pure black
COLOR_GRID = (40, 40, 40)  # Dark gray
COLOR_GRID_LINES = (80, 80, 80)  # Medium gray
COLOR_SNAKE_HEAD = (255, 255, 255)  # Pure white
COLOR_SNAKE_BODY = (200, 200, 200)  # Light gray
COLOR_SNAKE_GLOW = (180, 180, 180)  # Gray glow
COLOR_COIN = (255, 215, 0)  # Gold
COLOR_COIN_OUTLINE = (255, 255, 255)  # White outline
COLOR_TEXT = (255, 255, 255)  # White
COLOR_TEXT_DIM = (150, 150, 150)  # Dim gray
COLOR_GAME_OVER = (255, 255, 255)  # White

# Game settings
INITIAL_SNAKE_LENGTH = 3
INITIAL_SPEED = 8  # FPS
MAX_SPEED = 20  # FPS
SPEED_INCREMENT = 1  # FPS increase per 5 coins

# Scoring (as specified: 100 points per coin)
SCORE_COIN = 100
SCORE_STEP = 0  # No points for just surviving
PENALTY_DEATH = -100

# Directions
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)


def grid_to_screen(grid_x, grid_y):
    """Convert grid coordinates to isometric screen coordinates."""
    # Isometric projection
    screen_x = OFFSET_X + (grid_x - grid_y) * CELL_SIZE
    screen_y = OFFSET_Y + (grid_x + grid_y) * (CELL_SIZE // 2)
    return screen_x, screen_y


def screen_to_grid(screen_x, screen_y):
    """Convert screen coordinates to grid coordinates (approximate)."""
    # Reverse isometric projection
    rel_x = screen_x - OFFSET_X
    rel_y = screen_y - OFFSET_Y

    grid_x = (rel_x / CELL_SIZE + rel_y / (CELL_SIZE // 2)) // 2
    grid_y = (rel_y / (CELL_SIZE // 2) - rel_x / CELL_SIZE) // 2

    return int(grid_x), int(grid_y)
