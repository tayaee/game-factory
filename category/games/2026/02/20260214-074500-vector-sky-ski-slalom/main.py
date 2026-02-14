"""Vector Sky Ski Slalom - Main entry point."""

import pygame
import sys

from game import Game
from renderer import Renderer


def main():
    pygame.init()

    game = Game()
    renderer = Renderer(game)
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        keys = pygame.key.get_pressed()
        inputs = {
            'left': keys[pygame.K_LEFT],
            'right': keys[pygame.K_RIGHT],
        }

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game.game_over:
                    game.reset()

        game.update(dt, inputs)
        renderer.render()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
