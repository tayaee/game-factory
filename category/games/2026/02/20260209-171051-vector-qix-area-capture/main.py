"""Vector Qix - Area Capture

A classic arcade reimagining where you claim territory while dodging
the deadly geometric flicker of the Qix.
"""

from game import QixGame


def main():
    """Entry point for the Qix game."""
    game = QixGame()
    game.run()


if __name__ == "__main__":
    main()
