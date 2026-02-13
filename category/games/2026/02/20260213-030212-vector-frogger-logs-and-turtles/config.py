"""Game configuration constants for Vector Frogger: Logs and Turtles."""

# Screen settings
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
FPS = 60

# Grid settings
GRID_SIZE = 60
COLS = SCREEN_WIDTH // GRID_SIZE  # 10
ROWS = SCREEN_HEIGHT // GRID_SIZE  # 10

# Colors
COLOR_BG = (20, 25, 35)
COLOR_WATER = (35, 70, 120)
COLOR_WATER_DEEP = (25, 50, 90)
COLOR_GRASS = (45, 100, 55)
COLOR_SAFE_ZONE = (50, 120, 60)
COLOR_FROG = (60, 220, 60)
COLOR_FROG_OUTLINE = (35, 170, 35)
COLOR_LOG = (130, 90, 50)
COLOR_LOG_GRAIN = (100, 65, 35)
COLOR_TURTLE = (200, 70, 60)
COLOR_TURTLE_SUBMERGED = (80, 100, 140)
COLOR_TURTLE_SHELL = (160, 50, 45)
COLOR_TEXT = (255, 255, 255)
COLOR_GAME_OVER = (220, 60, 60)
COLOR_GOAL = (100, 200, 255)
COLOR_WARNING = (255, 180, 50)

# Game zones
START_ROW = ROWS - 1  # Row 9
GOAL_ROW = 0          # Row 0
RIVER_START = 1       # Row 1
RIVER_END = 8         # Row 8

# Scoring
SCORE_FORWARD = 10
SCORE_GOAL = 100
DEATH_PENALTY = -50
TIME_PENALTY = -1

# Speed settings (pixels per frame)
BASE_SPEED = 2
SPEED_INCREMENT = 0.3

# Frog settings
FROG_SIZE = GRID_SIZE - 8
FROG_MOVE_COOLDOWN = 8  # Frames between moves

# Platform settings
PLATFORM_WIDTHS = {
    'short': GRID_SIZE * 2,
    'medium': GRID_SIZE * 3,
    'long': GRID_SIZE * 4,
}
PLATFORM_HEIGHT = GRID_SIZE - 10

# Turtle settings
TURTLE_SUBMERGE_CYCLE = 3000  # ms (3 seconds)
TURTLE_SUBMERGE_DURATION = 1000  # ms (1 second submerged)
TURTLE_SIZE = GRID_SIZE - 14

# Lane configuration: (row, speed, platform_type, size, spacing)
# Speed > 0 moves right, Speed < 0 moves left
# Platform types: 'log' or 'turtle'
LANES = [
    (8, 1.5, 'log', 'short', 4.5),
    (7, -2.0, 'turtle', 'medium', 4),
    (6, 2.5, 'log', 'long', 5),
    (5, -1.8, 'turtle', 'medium', 3.5),
    (4, 2.2, 'log', 'short', 3),
    (3, -2.5, 'turtle', 'long', 4),
    (2, 1.8, 'log', 'medium', 3.5),
    (1, -2.0, 'turtle', 'short', 3),
]
