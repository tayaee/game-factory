"""Game configuration and constants."""

# Window settings
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
FPS = 60
CAPTION = "Vector Tumble Tower Collapse"

# Colors
COLOR_BG = (40, 44, 52)
COLOR_GROUND = (60, 64, 72)
COLOR_BLOCK_EVEN = (205, 133, 63)
COLOR_BLOCK_ODD = (139, 90, 43)
COLOR_BLOCK_HOVER = (255, 180, 100)
COLOR_BLOCK_SELECTED = (100, 200, 255)
COLOR_DROP_ZONE = (100, 255, 100, 50)
COLOR_TEXT = (220, 220, 220)
COLOR_TEXT_WARNING = (255, 100, 100)
COLOR_UI_BG = (30, 32, 38)

# Tower settings
TOWER_LAYERS = 18
BLOCKS_PER_LAYER = 3
BLOCK_WIDTH = 80
BLOCK_HEIGHT = 25
BLOCK_DEPTH = 24  # For 3D effect
LAYER_HEIGHT = BLOCK_HEIGHT

# Physics settings
GRAVITY = 500.0
FRICTION = 0.95
RESTITUTION = 0.1  # Bounciness (low for wood)
GROUND_Y = SCREEN_HEIGHT - 80
TOWER_CENTER_X = SCREEN_WIDTH // 2
TOWER_BASE_Y = GROUND_Y - 10

# Game mechanics
MAX_PULL_DISTANCE = 150
DROP_ZONE_HEIGHT = 80
STABILITY_THRESHOLD = 0.15  # Max tilt angle before warning
COLLAPSE_THRESHOLD = 0.4  # Max tilt before collapse
BLOCK_MASS = 1.0

# Scoring
SCORE_PER_BLOCK = 10
PENALTY_COLLAPSE = -100

# UI settings
UI_HEIGHT = 80
FONT_SIZE = 24
TITLE_FONT_SIZE = 32

# AI/Agent settings
OBSERVATION_SPACE = {
    "block_positions": "list of (x, y, rotation) for all blocks",
    "tower_height": "current number of layers",
    "center_of_mass": "(x, y) of tower center of mass",
    "stability_score": "0.0 to 1.0, 1.0 being perfectly stable"
}

ACTION_SPACE = {
    "select_block": "block index to select",
    "target_position": "(x, y) target position for placement"
}

REWARD_STRUCTURE = {
    "block_placed": f"+{SCORE_PER_BLOCK}",
    "tower_stable": "+1 per stable frame",
    "tower_unstable": "-0.1 per unstable frame",
    "collapse": f"{PENALTY_COLLAPSE}"
}
