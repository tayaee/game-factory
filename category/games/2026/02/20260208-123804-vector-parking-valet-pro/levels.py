"""Level definitions for the parking game."""

from obstacle import Obstacle, ParkingSpot
from config import *


LEVELS = [
    {
        "name": "Easy Start",
        "car_start": (100, 350, 0),
        "parking_spot": (800, 350, 0),
        "obstacles": [],
        "time_limit": 60,
        "description": "Simple straight-line parking"
    },
    {
        "name": "Reverse In",
        "car_start": (850, 350, 180),
        "parking_spot": (150, 350, 180),
        "obstacles": [],
        "time_limit": 60,
        "description": "Reverse into the spot"
    },
    {
        "name": "The Barrier",
        "car_start": (100, 350, 0),
        "parking_spot": (850, 350, 0),
        "obstacles": [
            Obstacle(450, 100, 50, 200, "barrier"),
            Obstacle(450, 400, 50, 200, "barrier"),
        ],
        "time_limit": 75,
        "description": "Navigate around the central barrier"
    },
    {
        "name": "Tight Squeeze",
        "car_start": (100, 200, 0),
        "parking_spot": (850, 500, 90),
        "obstacles": [
            Obstacle(300, 0, 30, 400, "barrier"),
            Obstacle(600, 300, 30, 400, "barrier"),
        ],
        "time_limit": 90,
        "description": "Wind through narrow gaps"
    },
    {
        "name": "The Maze",
        "car_start": (80, 80, 45),
        "parking_spot": (900, 600, 180),
        "obstacles": [
            Obstacle(200, 0, 30, 350, "barrier"),
            Obstacle(400, 200, 30, 500, "barrier"),
            Obstacle(600, 0, 30, 400, "barrier"),
            Obstacle(750, 350, 30, 350, "barrier"),
        ],
        "time_limit": 120,
        "description": "Navigate the maze"
    },
    {
        "name": "Parallel Parking",
        "car_start": (100, 400, 0),
        "parking_spot": (500, 400, 0),
        "obstacles": [
            Obstacle(420, 320, 60, 160, "car"),
            Obstacle(620, 320, 60, 160, "car"),
        ],
        "time_limit": 90,
        "description": "Parallel park between cars"
    },
    {
        "name": "Championship Course",
        "car_start": (80, 600, -45),
        "parking_spot": (900, 100, 90),
        "obstacles": [
            Obstacle(150, 0, 40, 450, "barrier"),
            Obstacle(300, 250, 40, 450, "barrier"),
            Obstacle(450, 0, 40, 350, "barrier"),
            Obstacle(600, 200, 40, 500, "barrier"),
            Obstacle(750, 0, 40, 300, "barrier"),
        ],
        "time_limit": 150,
        "description": "The ultimate parking challenge"
    },
]


def load_level(level_index):
    """Load a level by index.

    Args:
        level_index: Index of the level to load

    Returns:
        dict with level data or None if index is invalid
    """
    if 0 <= level_index < len(LEVELS):
        return LEVELS[level_index]
    return None


def get_level_count():
    """Return total number of levels."""
    return len(LEVELS)
