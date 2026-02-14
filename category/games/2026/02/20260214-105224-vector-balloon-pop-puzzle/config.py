"""Game configuration constants."""

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
FPS = 60

# Grid configuration
GRID_COLS = 10
GRID_ROWS = 10
CELL_SIZE = 50
GRID_START_X = (SCREEN_WIDTH - GRID_COLS * CELL_SIZE) // 2
GRID_START_Y = 50

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (100, 100, 100)

# Balloon colors
BALLOON_COLORS = [
    (231, 76, 60),    # Red
    (52, 152, 219),   # Blue
    (46, 204, 113),   # Green
    (241, 196, 15),   # Yellow
]

COLOR_NAMES = ["Red", "Blue", "Green", "Yellow"]

# Game mechanics
DART_LIMIT = 15
DART_SPEED = 12
LAUNCHER_WIDTH = 60
LAUNCHER_HEIGHT = 40
LAUNCHER_Y = SCREEN_HEIGHT - 80
LAUNCHER_SPEED = 5

# Physics
GRAVITY = 0.3
BALLOON_FLOAT_SPEED = 2
