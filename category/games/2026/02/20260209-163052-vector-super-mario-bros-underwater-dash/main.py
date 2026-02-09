"""Vector Super Mario Bros Underwater Dash - Main entry point."""

import pygame
import sys

from game import GameState
from renderer import Renderer


def main():
    pygame.init()

    state = GameState()
    renderer = Renderer(state)
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        keys = pygame.key.get_pressed()
        inputs = {
            'left': keys[pygame.K_LEFT],
            'right': keys[pygame.K_RIGHT],
            'swim': keys[pygame.K_SPACE] or keys[pygame.K_UP],
        }

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and state.game_over:
                    state.reset()

        state.update(dt, inputs)
        renderer.render()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
