"""Ball physics and collision handling."""

import math
import random
import pygame
from config import *


class Ball:
    """Physics-based pinball."""

    def __init__(self, x=None, y=None):
        self.x = x if x is not None else BALL_START_X
        self.y = y if y is not None else BALL_START_Y
        self.vx = 0
        self.vy = 0
        self.radius = BALL_RADIUS

    def update(self):
        """Apply physics and update position."""
        # Apply gravity
        self.vy += GRAVITY

        # Apply friction
        self.vx *= FRICTION
        self.vy *= FRICTION

        # Clamp velocity
        speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if speed > MAX_SPEED:
            scale = MAX_SPEED / speed
            self.vx *= scale
            self.vy *= scale

        # Update position
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen):
        """Render the ball."""
        pygame.draw.circle(screen, SILVER, (int(self.x), int(self.y)), self.radius)
        # Add shine effect
        pygame.draw.circle(screen, WHITE, (int(self.x - 2), int(self.y - 2)), 2)

    def get_rect(self):
        """Get bounding rectangle."""
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def launch(self, speed=15):
        """Launch the ball upward."""
        self.vx = (random.random() * 2 - 1) * 2
        self.vy = -speed

    def bounce_horizontal(self):
        """Bounce off vertical surface."""
        self.vx = -self.vx * RESTITUTION

    def bounce_vertical(self):
        """Bounce off horizontal surface."""
        self.vy = -self.vy * RESTITUTION

    def bounce_normal(self, nx, ny):
        """Bounce off surface with given normal vector."""
        # Calculate dot product of velocity and normal
        dot = self.vx * nx + self.vy * ny

        # Calculate reflected velocity
        self.vx = (self.vx - 2 * dot * nx) * RESTITUTION
        self.vy = (self.vy - 2 * dot * ny) * RESTITUTION

    def is_lost(self):
        """Check if ball has fallen below the screen."""
        return self.y > SCREEN_HEIGHT + self.radius * 2
