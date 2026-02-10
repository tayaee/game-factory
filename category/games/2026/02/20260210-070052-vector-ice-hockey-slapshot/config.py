"""Configuration constants for Vector Ice Hockey Slapshot."""

# Window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 400
FPS = 60

# Colors
COLOR_BG = (200, 220, 255)           # Light ice blue
COLOR_RINK_BORDER = (50, 50, 80)     # Dark blue border
COLOR_CENTER_LINE = (200, 100, 100)  # Red center line
COLOR_GOAL_LINE = (50, 50, 50)       # Dark goal line
COLOR_P1 = (50, 100, 200)            # Blue for Player 1
COLOR_P2 = (200, 50, 50)             # Red for Player 2
COLOR_PUCK = (20, 20, 20)            # Black puck
COLOR_TEXT = (0, 0, 0)               # Black text

# Rink dimensions
RINK_MARGIN = 20
GOAL_WIDTH = 100
GOAL_DEPTH = 20

# Player settings
PLAYER_RADIUS = 20
PLAYER_SPEED = 4.0
PLAYER_FRICTION = 0.98
SLAPSHOT_FORCE = 12.0
SLAPSHOT_COOLDOWN = 30  # frames
SLAPSHOT_RANGE = 50

# Puck settings
PUCK_RADIUS = 10
PUCK_FRICTION = 0.995  # Very low friction for ice
PUCK_MAX_SPEED = 15.0

# Game settings
WINNING_SCORE = 5
GOAL_RESET_DELAY = 60  # frames

# AI Integration
STATE_SPACE = {
    "player1_pos": 2,      # (x, y)
    "player1_vel": 2,      # (vx, vy)
    "player2_pos": 2,      # (x, y)
    "player2_vel": 2,      # (vx, vy)
    "puck_pos": 2,         # (x, y)
    "puck_vel": 2,         # (vx, vy)
    "scores": 2,           # (p1_score, p2_score)
}

ACTION_SPACE = {
    "type": "continuous",
    "description": "2D force vector + slapshot trigger"
}

REWARD_STRUCTURE = {
    "goal_scored": 1.0,
    "goal_conceded": -1.0,
    "puck_contact": 0.1,
    "per_step_penalty": -0.01,
}
