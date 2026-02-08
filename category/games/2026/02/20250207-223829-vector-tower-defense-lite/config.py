# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Grid settings
GRID_SIZE = 40
TOWER_SIZE = 30

# Colors
BACKGROUND_COLOR = (30, 30, 35)
PATH_COLOR = (60, 60, 70)
GRASS_COLOR = (40, 50, 40)
UI_BG_COLOR = (20, 20, 25)
TEXT_COLOR = (220, 220, 220)
ACCENT_COLOR = (70, 130, 180)

# Enemy settings
ENEMY_SIZE = 15
ENEMY_BASE_SPEED = 1.5
ENEMY_SPAWN_INTERVAL = 1500  # ms

# Tower types
TOWER_TYPES = {
    1: {"name": "Basic", "color": (100, 149, 237), "cost": 50, "damage": 10, "range": 100, "fire_rate": 60},
    2: {"name": "Sniper", "color": (220, 20, 60), "cost": 100, "damage": 30, "range": 200, "fire_rate": 90},
}

# Projectile settings
PROJECTILE_SPEED = 8
PROJECTILE_SIZE = 5

# Game settings
STARTING_LIVES = 20
STARTING_GOLD = 150
WAVE_LENGTH = 10
WAVE_BONUS = 50

# Path waypoints (x, y) - creates a winding path
PATH_POINTS = [
    (0, 80),
    (200, 80),
    (200, 400),
    (500, 400),
    (500, 200),
    (700, 200),
    (700, 520),
    (SCREEN_WIDTH, 520),
]

# UI settings
UI_HEIGHT = 80
BUTTON_SIZE = 50
