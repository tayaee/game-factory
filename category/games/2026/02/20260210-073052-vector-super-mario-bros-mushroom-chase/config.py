"""Configuration constants for Vector Super Mario Bros Mushroom Chase."""

# Window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors (monochrome high-contrast palette)
COLOR_BG = (20, 20, 25)
COLOR_PLATFORM = (200, 200, 200)
COLOR_PLAYER = (50, 150, 255)
COLOR_PLAYER_OUTLINE = (100, 200, 255)
COLOR_MUSHROOM = (255, 100, 100)
COLOR_MUSHROOM_CAP = (255, 50, 50)
COLOR_MUSHROOM_DOTS = (255, 255, 255)
COLOR_TEXT = (220, 220, 220)
COLOR_SCORE = (255, 255, 100)
COLOR_WARNING = (255, 50, 50)

# Player settings
PLAYER_WIDTH = 24
PLAYER_HEIGHT = 32
PLAYER_SPEED = 4
PLAYER_JUMP_SPEED = -10
PLAYER_ACCEL = 0.5
PLAYER_FRICTION = 0.85
GRAVITY = 0.4
MAX_FALL_SPEED = 12

# Mushroom settings
MUSHROOM_WIDTH = 20
MUSHROOM_HEIGHT = 20
MUSHROOM_SPEED = 2
MUSHROOM_BOUNCE_SPEED = 5

# Game rules
SCORE_CATCH = 100
SCORE_PENALTY = -50
WIN_SCORE = 1000
MAX_MUSHROOMS_LOST = 5

# Reward structure for AI
REWARD_STRUCTURE = {
    "catch": 1.0,
    "mushroom_lost": -0.5,
    "per_step": -0.001,
    "close_to_mushroom": 0.01
}
