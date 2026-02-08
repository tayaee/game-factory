"""Pipe obstacle entities."""

import pygame
import random
from config import *


class Pipe:
    """A pair of pipes with a gap in between."""

    def __init__(self, x):
        self.x = x
        self.width = PIPE_WIDTH
        self.gap_y = random.randint(
            GROUND_HEIGHT + 50,
            SCREEN_HEIGHT - GROUND_HEIGHT - PIPE_GAP - 50
        )
        self.passed = False

    def update(self):
        """Move pipe left."""
        self.x -= PIPE_SPEED

    def get_top_rect(self):
        """Get top pipe collision rectangle."""
        return pygame.Rect(
            self.x,
            0,
            self.width,
            self.gap_y
        )

    def get_bottom_rect(self):
        """Get bottom pipe collision rectangle."""
        return pygame.Rect(
            self.x,
            self.gap_y + PIPE_GAP,
            self.width,
            SCREEN_HEIGHT - self.gap_y - PIPE_GAP
        )

    def draw(self, screen):
        """Draw both pipes."""
        # Top pipe
        top_rect = self.get_top_rect()
        pygame.draw.rect(screen, PIPE_GREEN, top_rect)
        pygame.draw.rect(screen, PIPE_RIM, top_rect, 3)

        # Top pipe cap
        cap_height = 30
        pygame.draw.rect(
            screen,
            PIPE_GREEN,
            (self.x - 5, self.gap_y - cap_height, self.width + 10, cap_height)
        )
        pygame.draw.rect(
            screen,
            PIPE_RIM,
            (self.x - 5, self.gap_y - cap_height, self.width + 10, cap_height),
            3
        )

        # Bottom pipe
        bottom_rect = self.get_bottom_rect()
        pygame.draw.rect(screen, PIPE_GREEN, bottom_rect)
        pygame.draw.rect(screen, PIPE_RIM, bottom_rect, 3)

        # Bottom pipe cap
        pygame.draw.rect(
            screen,
            PIPE_GREEN,
            (self.x - 5, self.gap_y + PIPE_GAP, self.width + 10, cap_height)
        )
        pygame.draw.rect(
            screen,
            PIPE_RIM,
            (self.x - 5, self.gap_y + PIPE_GAP, self.width + 10, cap_height),
            3
        )

    def is_off_screen(self):
        """Check if pipe has moved off screen."""
        return self.x + self.width < 0

    def get_observation(self):
        """Return pipe state for AI observation."""
        return {
            "x": self.x,
            "gap_y": self.gap_y
        }


class PipeManager:
    """Manages pipe spawning and cleanup."""

    def __init__(self):
        self.pipes = []
        self.last_spawn_time = 0

    def update(self, current_time, dt):
        """Update all pipes and spawn new ones."""
        # Spawn new pipe
        if current_time - self.last_spawn_time > PIPE_SPAWN_INTERVAL:
            self.pipes.append(Pipe(SCREEN_WIDTH))
            self.last_spawn_time = current_time

        # Update existing pipes
        for pipe in self.pipes:
            pipe.update()

        # Remove off-screen pipes
        self.pipes = [p for p in self.pipes if not p.is_off_screen()]

    def draw(self, screen):
        """Draw all pipes."""
        for pipe in self.pipes:
            pipe.draw(screen)

    def check_collision(self, bird_rect):
        """Check if bird collides with any pipe."""
        for pipe in self.pipes:
            if bird_rect.colliderect(pipe.get_top_rect()):
                return True
            if bird_rect.colliderect(pipe.get_bottom_rect()):
                return True
        return False

    def get_next_pipe(self, bird_x):
        """Get the next pipe the bird will encounter."""
        for pipe in self.pipes:
            if pipe.x + pipe.width > bird_x:
                return pipe
        return None

    def update_score(self, bird_x):
        """Update score when bird passes a pipe."""
        score_increment = 0
        for pipe in self.pipes:
            if not pipe.passed and pipe.x + pipe.width < bird_x:
                pipe.passed = True
                score_increment += 1
        return score_increment
