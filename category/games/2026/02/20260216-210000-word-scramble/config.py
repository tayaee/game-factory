"""
Configuration for Word Scramble game.
"""

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
COLOR_BG = (20, 20, 30)
COLOR_TEXT = (255, 255, 255)
COLOR_ACCENT = (70, 130, 180)
COLOR_LETTER = (255, 200, 100)
COLOR_LETTER_SELECTED = (255, 100, 100)
COLOR_HINT = (100, 100, 150)
COLOR_CORRECT = (100, 200, 100)
COLOR_WRONG = (200, 100, 100)

# Game settings
MAX_HINTS = 3
POINTS_PER_LETTER = 10
BONUS_POINTS = 50
TIME_PENALTY_PER_HINT = 20
TIME_PENALTY_PER_WRONG = 10

# Word list (scrambled words with their solutions)
WORDS = [
    ("ELPPA", "APPLE"),
    ("ELBANAC", "BANANA"),
    ("ERP", "PEAR"),
    ("GRAPE", "GRAPE"),
    ("EERLG", "LEMON"),
    ("HCRYE", "CHERRY"),
    ("ORGEAN", "ORANGE"),
    ("RUBMY", "BERRY"),
    ("EPACH", "PEACH"),
    ("EPLU", "PLUM"),
    ("OTAMOT", "TOMATO"),
    ("POTOAT", "POTATO"),
    ("TONAR", "CARROT"),
    ("EELLC", "CELERY"),
    ("OCLOC", "COCONUT"),
    ("EPRPIE", "PINEAPPLE"),
    ("EABERRTSTR", "STRAWBERRY"),
    ("EAWTREMLON", "WATERMELON"),
    ("EGARVNA", "AVENGERS"),
    ("ETRAS", "STARE"),
    ("ETAES", ("TEAS", "EAST", "SEAT", "EATS")),
    ("PEKA", "PEAK"),
    ("ELANP", "PLANE"),
    ("KEBA", "BAKE"),
    ("KEAM", "MAKE"),
    ("KEWT", "WEAK"),
    ("RAET", "TEAR"),
    ("ERAT", "RATE"),
    ("RTAE", ("RATE", "TEAR")),
    ("ART", "RAT"),
    ("RAT", ("RAT", "ART", "TAR")),
    ("TAR", "TAR"),
    ("TEB", "BET"),
    ("EBT", "BET"),
    ("BET", "BET"),
    ("ETN", "NET"),
    ("TNE", "NET"),
    ("NET", "NET"),
    ("TEG", "GET"),
    ("EGT", "GET"),
    ("GET", "GET"),
    ("ETP", "PET"),
    ("TPE", "PET"),
    ("PET", "PET"),
    ("EMT", "MET"),
    ("TME", "MET"),
    ("MET", "MET"),
    ("ETY", "YET"),
    ("TEY", "YET"),
    ("YET", "YET"),
]

# Font sizes
FONT_SIZE_LARGE = 48
FONT_SIZE_MEDIUM = 32
FONT_SIZE_SMALL = 24
