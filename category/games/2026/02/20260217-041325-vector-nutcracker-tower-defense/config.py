"""Game configuration constants."""

# Window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Grid settings
GRID_SIZE = 16
CELL_SIZE = 40
GRID_OFFSET_X = 80
GRID_OFFSET_Y = 40

# Game settings
INITIAL_CURRENCY = 100
INITIAL_HEALTH = 10

# Enemy path (16x16 grid, 0-indexed)
ENEMY_PATH = [
    (0, 7), (1, 7), (2, 7), (3, 7),
    (3, 6), (3, 5), (3, 4),
    (4, 4), (5, 4), (6, 4), (7, 4),
    (7, 5), (7, 6), (7, 7), (7, 8), (7, 9), (7, 10),
    (8, 10), (9, 10), (10, 10), (11, 10),
    (11, 9), (11, 8), (11, 7), (11, 6), (11, 5),
    (12, 5), (13, 5), (14, 5), (15, 5)
]

# Enemy types
ENEMY_TYPES = {
    "Standard": {"health": 50, "speed": 1.0, "reward": 15, "color": (200, 100, 100)},
    "Fast": {"health": 30, "speed": 2.0, "reward": 20, "color": (100, 200, 100)},
    "Tank": {"health": 150, "speed": 0.5, "reward": 40, "color": (100, 100, 200)}
}

# Tower types
TOWER_TYPES = {
    "Scout": {
        "cost": 20,
        "range": 3.0,
        "damage": 10,
        "cooldown": 0.5,
        "color": (100, 200, 200),
        "projectile_speed": 8.0
    },
    "Heavy": {
        "cost": 50,
        "range": 4.0,
        "damage": 40,
        "cooldown": 2.0,
        "color": (200, 150, 50),
        "projectile_speed": 5.0
    },
    "Frost": {
        "cost": 40,
        "range": 2.5,
        "damage": 5,
        "cooldown": 1.5,
        "color": (150, 150, 255),
        "projectile_speed": 6.0,
        "slow_factor": 0.5,
        "slow_duration": 2.0
    }
}

# Wave configuration
WAVES = [
    [{"type": "Standard", "count": 3, "interval": 2.0}],
    [{"type": "Standard", "count": 5, "interval": 1.5}],
    [{"type": "Standard", "count": 3, "interval": 1.0}, {"type": "Fast", "count": 2, "interval": 1.0}],
    [{"type": "Fast", "count": 5, "interval": 1.0}],
    [{"type": "Standard", "count": 5, "interval": 1.0}, {"type": "Tank", "count": 1, "interval": 3.0}],
    [{"type": "Tank", "count": 2, "interval": 2.0}, {"type": "Fast", "count": 3, "interval": 1.0}],
    [{"type": "Standard", "count": 5, "interval": 0.8}, {"type": "Fast", "count": 5, "interval": 0.8}, {"type": "Tank", "count": 2, "interval": 2.0}],
    [{"type": "Tank", "count": 3, "interval": 1.5}, {"type": "Fast", "count": 5, "interval": 0.8}],
    [{"type": "Standard", "count": 10, "interval": 0.6}, {"type": "Tank", "count": 3, "interval": 1.5}],
    [{"type": "Standard", "count": 5, "interval": 0.5}, {"type": "Fast", "count": 8, "interval": 0.5}, {"type": "Tank", "count": 4, "interval": 1.2}]
]

# Colors
COLOR_BG = (20, 20, 30)
COLOR_GRID = (50, 50, 70)
COLOR_PATH = (80, 70, 60)
COLOR_VALID = (50, 80, 50)
COLOR_INVALID = (80, 50, 50)
COLOR_TEXT = (220, 220, 220)
COLOR_UI_BG = (40, 40, 60)
COLOR_TOY_BOX = (180, 100, 180)
COLOR_PROJECTILE = (255, 255, 100)
COLOR_FROST_PROJECTILE = (150, 200, 255)
