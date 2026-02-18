"""Configuration settings for Color Flow Puzzle."""

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
CELL_SIZE = 100
GRID_SIZE = 5
MARGIN = 150

# Colors
BACKGROUND_COLOR = (40, 40, 40)
GRID_COLOR = (60, 60, 60)
TEXT_COLOR = (255, 255, 255)

# Pipe colors - high contrast solid colors
COLORS = [
    (255, 0, 0),      # Red
    (0, 255, 0),      # Green
    (0, 150, 255),    # Blue
    (255, 255, 0),    # Yellow
    (255, 0, 255),    # Magenta
    (0, 255, 255),    # Cyan
]

# Game settings
FPS = 60
POINTS_PER_CONNECTION = 100
TIME_BONUS_MULTIPLIER = 10
LEVEL_TIME_LIMIT = 300  # 5 minutes
