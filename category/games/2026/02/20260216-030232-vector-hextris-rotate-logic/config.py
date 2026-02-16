"""Game configuration and constants for Vector Hextris."""

import pygame

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
CAPTION = "Vector Hextris - Rotate Logic"

# Colors
COLOR_BG = (20, 20, 30)
COLOR_HEXAGON = (80, 80, 100)
COLOR_HEXAGON_BORDER = (120, 120, 140)
COLOR_LIMIT_LINE = (200, 50, 50)
COLOR_TEXT = (255, 255, 255)
COLOR_GAME_OVER = (255, 50, 50)

BLOCK_COLORS = [
    (255, 65, 54),   # Red
    (0, 116, 217),   # Blue
    (46, 204, 64),   # Green
    (255, 220, 0),   # Yellow
]

# Hexagon settings
HEXAGON_RADIUS = 80
HEXAGON_SIDES = 6
ROTATION_STEP = 60

# Block settings
BLOCK_WIDTH = 20
BLOCK_HEIGHT = 12
BLOCKS_PER_ROW = 6  # Number of blocks in a falling bar
MATCH_MIN = 3       # Minimum blocks to match

# Spawn settings
SPAWN_INTERVAL_INITIAL = 120  # Frames between spawns at start
SPAWN_INTERVAL_MIN = 30       # Minimum frames between spawns
SPAWN_DISTANCE = 350          # Distance from center to spawn

# Speed settings
FALL_SPEED_INITIAL = 1.5      # Initial fall speed
FALL_SPEED_MAX = 4.0          # Maximum fall speed
SPEED_INCREASE_RATE = 0.0005  # Speed increase per frame

# Game limits
MAX_STACK_HEIGHT = 10         # Maximum blocks per side before game over
CLEAR_DELAY = 10              # Frames to wait before clearing matched blocks

# Scoring
SCORE_PER_BLOCK = 10
SCORE_COMBO_MULTIPLIER = 1.5

# Text sizes
FONT_SIZE_LARGE = 48
FONT_SIZE_MEDIUM = 24
FONT_SIZE_SMALL = 16
