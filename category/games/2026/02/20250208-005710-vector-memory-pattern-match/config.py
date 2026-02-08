"""Game configuration constants."""

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)

# Tile colors - 4 distinct colors for the Simon game
TILE_COLORS = [
    (0, 200, 0),      # Green - top left
    (0, 0, 200),      # Blue - top right
    (200, 0, 0),      # Red - bottom left
    (200, 200, 0)     # Yellow - bottom right
]

# Flash colors (brighter version)
FLASH_COLORS = [
    (0, 255, 0),
    (0, 0, 255),
    (255, 0, 0),
    (255, 255, 0)
]

# Sound frequencies (Hz)
TONE_FREQUENCIES = [
    262,  # C4
    330,  # E4
    392,  # G4
    523   # C5
]

# Game board settings
BOARD_SIZE = 400
TILE_GAP = 10
BOARD_X = (SCREEN_WIDTH - BOARD_SIZE) // 2
BOARD_Y = (SCREEN_HEIGHT - BOARD_SIZE) // 2
TILE_SIZE = (BOARD_SIZE - TILE_GAP * 3) // 2

# Timing (milliseconds)
FLASH_DURATION = 300
PAUSE_BETWEEN_FLASHES = 100
PAUSE_BEFORE_USER_TURN = 500
GAME_OVER_DELAY = 1500

# Reward structure for AI training
REWARD_CORRECT_STEP = 0.1
REWARD_ROUND_COMPLETE = 1.0
REWARD_GAME_OVER = -1.0

# Fonts
SCORE_FONT_SIZE = 36
MESSAGE_FONT_SIZE = 48
