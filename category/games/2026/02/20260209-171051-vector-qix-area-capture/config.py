"""Game configuration constants."""

# Window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Game field settings
FIELD_MARGIN = 50
FIELD_WIDTH = WINDOW_WIDTH - 2 * FIELD_MARGIN
FIELD_HEIGHT = WINDOW_HEIGHT - 2 * FIELD_MARGIN - 60
GRID_SIZE = 4

# Player settings
PLAYER_SIZE = 8
PLAYER_SPEED = 3
PLAYER_COLOR = (0, 255, 0)  # Green
TRAIL_WIDTH = 2
TRAIL_COLOR = (255, 255, 0)  # Yellow

# Qix (enemy) settings
QIX_COLOR = (255, 0, 255)  # Magenta
QIX_SPEED = 2
QIX_SIZE = 20
QIX_LINE_COUNT = 5
QIX_LINE_LENGTH = 15

# Spark (border enemy) settings
SPARK_COLOR = (255, 100, 0)  # Orange
SPARK_SIZE = 6
SPARK_SPEED = 2

# Fill settings
FILL_COLOR = (100, 100, 255)  # Light blue
BORDER_COLOR = (200, 200, 255)  # Light border
CLAIMED_COLOR = (50, 50, 150)  # Dark blue for claimed area

# UI settings
BG_COLOR = (20, 20, 30)  # Dark background
FIELD_BG_COLOR = (10, 10, 20)  # Even darker field background
TEXT_COLOR = (255, 255, 255)
FONT_SIZE_LARGE = 36
FONT_SIZE_MEDIUM = 24
FONT_SIZE_SMALL = 18

# Game settings
LIVES_START = 3
WIN_PERCENTAGE = 75
LEVEL_MULTIPLIER = 1.2

# Score settings
POINTS_PER_PERCENT = 10
RISK_MULTIPLIER_MAX = 2.0
DEATH_PENALTY = -500
LEVEL_COMPLETE_BONUS = 2000
