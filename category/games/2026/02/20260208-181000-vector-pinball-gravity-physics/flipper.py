"""Flipper mechanics and collision detection."""

import math
import pygame
from config import *


class Flipper:
    """Rotating flipper for hitting the ball."""

    def __init__(self, pivot_x, pivot_y, is_left=True):
        self.pivot_x = pivot_x
        self.pivot_y = pivot_y
        self.is_left = is_left

        if is_left:
            self.base_angle = FLIPPER_REST_ANGLE
            self.active_angle = FLIPPER_ACTIVE_ANGLE
        else:
            self.base_angle = 180 - FLIPPER_REST_ANGLE
            self.active_angle = 180 - FLIPPER_ACTIVE_ANGLE

        self.current_angle = self.base_angle
        self.target_angle = self.base_angle
        self.is_active = False

        self.length = FLIPPER_LENGTH
        self.width = FLIPPER_WIDTH

    def activate(self):
        """Activate the flipper (rotate up)."""
        self.is_active = True
        self.target_angle = self.active_angle

    def deactivate(self):
        """Deactivate the flipper (return to rest)."""
        self.is_active = False
        self.target_angle = self.base_angle

    def update(self):
        """Update flipper rotation."""
        diff = self.target_angle - self.current_angle

        if abs(diff) < FLIPPER_SPEED:
            self.current_angle = self.target_angle
        else:
            self.current_angle += FLIPPER_SPEED if diff > 0 else -FLIPPER_SPEED

    def get_end_point(self):
        """Get the current end point of the flipper."""
        rad = math.radians(self.current_angle)
        end_x = self.pivot_x + self.length * math.cos(rad)
        end_y = self.pivot_y + self.length * math.sin(rad)
        return end_x, end_y

    def get_normal(self):
        """Get the normal vector of the flipper surface."""
        rad = math.radians(self.current_angle)
        # Normal is perpendicular to the flipper
        nx = -math.sin(rad)
        ny = math.cos(rad)
        return nx, ny

    def draw(self, screen):
        """Render the flipper."""
        end_x, end_y = self.get_end_point()

        # Draw flipper as a line with thickness
        color = RED if self.is_active else ORANGE
        pygame.draw.line(
            screen,
            color,
            (self.pivot_x, self.pivot_y),
            (end_x, end_y),
            self.width
        )

        # Draw pivot point
        pygame.draw.circle(screen, SILVER, (self.pivot_x, self.pivot_y), 6)

    def check_collision(self, ball):
        """Check and handle collision with ball."""
        end_x, end_y = self.get_end_point()

        # Vector from pivot to ball
        dx = ball.x - self.pivot_x
        dy = ball.y - self.pivot_y

        # Project onto flipper direction
        rad = math.radians(self.current_angle)
        flipper_dx = math.cos(rad)
        flipper_dy = math.sin(rad)

        # Calculate projection
        projection = dx * flipper_dx + dy * flipper_dy

        # Check if ball is within flipper length
        if 0 <= projection <= self.length:
            # Calculate perpendicular distance
            perp_dist = abs(dx * (-flipper_dy) + dy * flipper_dx)

            if perp_dist < ball.radius + self.width / 2:
                # Collision detected
                nx, ny = self.get_normal()

                # Push ball out of flipper
                overlap = ball.radius + self.width / 2 - perp_dist
                ball.x += nx * overlap
                ball.y += ny * overlap

                # Add flipper velocity if flipper is moving
                if self.is_active:
                    speed_boost = 8 if self.is_left else -8
                    ball.vy -= 12
                    ball.vx += speed_boost

                # Bounce
                ball.bounce_normal(nx, ny)

                return True

        # Check collision with pivot point
        pivot_dist = math.sqrt(dx * dx + dy * dy)
        if pivot_dist < ball.radius + 6:
            # Normalize direction from pivot to ball
            if pivot_dist > 0:
                nx = dx / pivot_dist
                ny = dy / pivot_dist
                ball.bounce_normal(nx, ny)

                # Push ball out
                overlap = ball.radius + 6 - pivot_dist
                ball.x += nx * overlap
                ball.y += ny * overlap

                return True

        return False

    def get_angle_for_observation(self):
        """Return normalized angle for AI observation."""
        return (self.current_angle - self.base_angle) / (self.active_angle - self.base_angle)
