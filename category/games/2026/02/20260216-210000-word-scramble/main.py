"""
Word Scramble
Unscramble letters to form words in this vocabulary puzzle game.
"""

import pygame
import sys
from game import Game


def main():
    pygame.init()
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
