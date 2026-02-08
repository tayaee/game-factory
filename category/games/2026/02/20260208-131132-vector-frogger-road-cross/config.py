"""Game configuration constants."""

# Screen settings
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 30

# Grid settings
GRID_SIZE = 40
COLS = SCREEN_WIDTH // GRID_SIZE
ROWS = SCREEN_HEIGHT // GRID_SIZE

# Colors
COLOR_BG = (20, 20, 30)
COLOR_ROAD = (40, 40, 50)
COLOR_WATER = (30, 60, 100)
COLOR_SAFE_ZONE = (30, 80, 40)
COLOR_GRASS = (40, 90, 50)
COLOR_FROG = (50, 200, 50)
COLOR_FROG_OUTLINE = (30, 150, 30)
COLOR_CAR = (200, 60, 60)
COLOR_TRUCK = (200, 150, 50)
COLOR_LOG = (120, 80, 40)
COLOR_LILYPAD = (40, 180, 80)
COLOR_LILYPAD_FILLED = (80, 220, 120)
COLOR_TEXT = (255, 255, 255)
COLOR_GAME_OVER = (200, 50, 50)

# Game zones
START_ROW = ROWS - 1
GOAL_ROW = 0
ROAD_START = ROWS - 6
ROAD_END = ROWS - 2
WATER_START = 1
WATER_END = 5

# Scoring
SCORE_FORWARD = 10
SCORE_GOAL = 100
SCORE_LEVEL_BONUS = 500
PENALTY_DEATH = -100
STEP_PENALTY = -0.1

# Speed settings (pixels per frame)
BASE_SPEED = 2
SPEED_INCREMENT = 0.5

# Frog settings
FROG_SIZE = GRID_SIZE - 4
FROG_MOVE_COOLDOWN = 10  # Frames between moves

# Lilypad settings
NUM_LILYPADS = 5
LILYPAD_GAP = COLS // (NUM_LILYPADS + 1)

# Vehicle settings
VEHICLE_WIDTHS = {
    'car': GRID_SIZE,
    'truck': GRID_SIZE * 2,
}
VEHICLE_HEIGHTS = {
    'car': GRID_SIZE - 8,
    'truck': GRID_SIZE - 8,
}

# Log settings
LOG_WIDTHS = [GRID_SIZE * 2, GRID_SIZE * 3, GRID_SIZE * 4]
LOG_HEIGHT = GRID_SIZE - 8

# Lane configuration: (row, type, speed, width_range, spacing)
LANES = [
    # Road lanes (bottom to top)
    (ROWS - 2, 'car', 2, 'car', 4),
    (ROWS - 3, 'truck', -1.5, 'truck', 5),
    (ROWS - 4, 'car', 2.5, 'car', 3),
    (ROWS - 5, 'truck', -2, 'truck', 4),
    # Water lanes (bottom to top)
    (5, 'log', 1.5, 'long', 4),
    (4, 'log', -2, 'medium', 3),
    (3, 'log', 2.5, 'short', 3),
    (2, 'log', -1.8, 'long', 4),
    (1, 'log', 2.2, 'medium', 3),
]
