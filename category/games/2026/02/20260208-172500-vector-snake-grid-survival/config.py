"""Game configuration and constants for Vector Snake Grid Survival."""

# Screen settings
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 680
FPS = 15

# Grid settings
GRID_SIZE = 32
GRID_COLS = SCREEN_WIDTH // GRID_SIZE  # 20
GRID_ROWS = (SCREEN_HEIGHT - 80) // GRID_SIZE  # 20 (80px for UI)
UI_HEIGHT = 80

# Colors (minimalist vector style)
COLOR_BG = (20, 20, 25)
COLOR_GRID = (35, 35, 45)
COLOR_SNAKE_HEAD = (0, 220, 130)
COLOR_SNAKE_BODY = (0, 180, 100)
COLOR_SNAKE_GLOW = (0, 255, 150)
COLOR_FOOD = (255, 60, 80)
COLOR_FOOD_GLOW = (255, 100, 120)
COLOR_TEXT = (220, 220, 220)
COLOR_TEXT_DIM = (120, 120, 120)
COLOR_GAME_OVER = (255, 80, 80)
COLOR_BORDER = (50, 50, 60)

# Game settings
INITIAL_SNAKE_LENGTH = 3
INITIAL_SPEED = 8  # FPS
MAX_SPEED = 20  # FPS
SPEED_INCREMENT = 0.5  # FPS increase per food

# Scoring
SCORE_FOOD = 10
SCORE_STEP = 0  # No points for just surviving
PENALTY_DEATH = -100

# Directions
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)
