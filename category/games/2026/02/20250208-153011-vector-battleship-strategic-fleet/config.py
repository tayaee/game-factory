# Screen settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Board settings
GRID_SIZE = 10
CELL_SIZE = 40
BOARD_OFFSET_X = 80
BOARD_OFFSET_Y = 150
PLAYER_BOARD_OFFSET_X = 550
ENEMY_BOARD_OFFSET_X = 80

# Ship configurations
SHIPS = {
    "Carrier": {"size": 5, "count": 1},
    "Battleship": {"size": 4, "count": 1},
    "Destroyer": {"size": 3, "count": 1},
    "Submarine": {"size": 3, "count": 1},
    "Patrol Boat": {"size": 2, "count": 1}
}

# Cell states
EMPTY = 0
SHIP = 1
MISS = 2
HIT = 3
SUNK = 4

# Colors
BACKGROUND_COLOR = (245, 245, 250)
BOARD_COLOR = (220, 225, 235)
GRID_COLOR = (180, 185, 195)
SHIP_COLOR = (60, 80, 100)
MISS_COLOR = (150, 160, 170)
HIT_COLOR = (200, 60, 60)
SUNK_COLOR = (80, 80, 80)
HIGHLIGHT_COLOR = (70, 130, 180)
HOVER_COLOR = (100, 180, 220)
VALID_PLACEMENT_COLOR = (80, 180, 100)
INVALID_PLACEMENT_COLOR = (200, 80, 80)

# Text colors
TITLE_COLOR = (30, 40, 50)
TEXT_COLOR = (50, 60, 70)
SUBTEXT_COLOR = (100, 110, 120)

# UI settings
PANEL_WIDTH = 300
BUTTON_HEIGHT = 40

# Rewards
REWARD_HIT = 10
REWARD_MISS = -1
REWARD_SINK = 50
REWARD_WIN = 200
REWARD_LOSS = -100

# AI delay (milliseconds)
AI_THINK_DELAY = 500
