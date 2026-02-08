"""Bird entity with physics."""

import pygame
from config import *


class Bird:
    """Player-controlled bird with gravity physics."""

    def __init__(self):
        self.x = BIRD_X
        self.y = BIRD_START_Y
        self.velocity = 0
        self.size = BIRD_SIZE

    def jump(self):
        """Apply upward velocity for a jump."""
        self.velocity = JUMP_VELOCITY

    def update(self):
        """Update bird physics."""
        self.velocity += GRAVITY
        if self.velocity > MAX_FALL_SPEED:
            self.velocity = MAX_FALL_SPEED
        self.y += self.velocity

    def get_rect(self):
        """Get collision rectangle."""
        return pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size,
            self.size
        )

    def draw(self, screen):
        """Draw the bird as a simple vector shape."""
        # Body
        pygame.draw.circle(
            screen,
            BIRD_YELLOW,
            (int(self.x), int(self.y)),
            self.size // 2
        )

        # Wing
        wing_offset = 5 if self.velocity < 0 else -5
        pygame.draw.ellipse(
            screen,
            BIRD_ORANGE,
            (
                self.x - 10,
                self.y + wing_offset,
                15,
                10
            )
        )

        # Eye
        pygame.draw.circle(
            screen,
            WHITE,
            (int(self.x + 5), int(self.y - 5)),
            5
        )
        pygame.draw.circle(
            screen,
            BLACK,
            (int(self.x + 7), int(self.y - 5)),
            2
        )

        # Beak
        pygame.draw.polygon(
            screen,
            BIRD_ORANGE,
            [
                (self.x + 10, self.y),
                (self.x + 20, self.y + 3),
                (self.x + 10, self.y + 6)
            ]
        )

    def get_observation(self):
        """Return bird state for AI observation."""
        return {
            "y": self.y,
            "velocity": self.velocity
        }
