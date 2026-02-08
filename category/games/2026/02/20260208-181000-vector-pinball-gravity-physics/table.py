"""Pinball table elements: bumpers, slingshots, and walls."""

import math
import pygame
from config import *


class Bumper:
    """Circular bumper that bounces the ball."""

    def __init__(self, x, y, radius=BUMPER_RADIUS, color=RED, points=BUMPER_POINTS):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.base_color = color
        self.points = points
        self.hit_timer = 0

    def update(self):
        """Update animation state."""
        if self.hit_timer > 0:
            self.hit_timer -= 1
            if self.hit_timer == 0:
                self.color = self.base_color

    def draw(self, screen):
        """Render the bumper."""
        # Outer ring
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        # Inner circle
        inner_radius = self.radius - 4
        pygame.draw.circle(screen, DARK_GRAY, (self.x, self.y), inner_radius)
        # Center dot
        pygame.draw.circle(screen, self.color, (self.x, self.y), 5)

    def check_collision(self, ball):
        """Check and handle collision with ball."""
        dx = ball.x - self.x
        dy = ball.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < self.radius + ball.radius:
            # Normalize collision vector
            if dist > 0:
                nx = dx / dist
                ny = dy / dist

                # Push ball out
                overlap = self.radius + ball.radius - dist
                ball.x += nx * overlap
                ball.y += ny * overlap

                # Bounce with extra energy
                ball.bounce_normal(nx, ny)
                ball.vx *= 1.2
                ball.vy *= 1.2

                # Flash effect
                self.color = WHITE
                self.hit_timer = 5

                return True

        return False


class Slingshot:
    """Triangular slingshot that bounces the ball."""

    def __init__(self, x, y, width=40, height=50, color=GREEN, points=SLINGSHOT_POINTS):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.base_color = color
        self.points = points
        self.hit_timer = 0

    def get_vertices(self):
        """Get triangle vertices."""
        return [
            (self.x, self.y + self.height),
            (self.x - self.width // 2, self.y),
            (self.x + self.width // 2, self.y)
        ]

    def update(self):
        """Update animation state."""
        if self.hit_timer > 0:
            self.hit_timer -= 1
            if self.hit_timer == 0:
                self.color = self.base_color

    def draw(self, screen):
        """Render the slingshot."""
        vertices = self.get_vertices()
        pygame.draw.polygon(screen, self.color, vertices)
        pygame.draw.polygon(screen, WHITE, vertices, 2)

    def check_collision(self, ball):
        """Check and handle collision with ball."""
        # Simple bounding circle check
        dx = ball.x - self.x
        dy = ball.y - (self.y + self.height / 2)
        dist = math.sqrt(dx * dx + dy * dy)

        collision_radius = self.width / 2 + ball.radius

        if dist < collision_radius:
            # Normalize collision vector
            if dist > 0:
                nx = dx / dist
                ny = dy / dist

                # Push ball out
                overlap = collision_radius - dist
                ball.x += nx * overlap
                ball.y += ny * overlap

                # Bounce with extra energy
                ball.bounce_normal(nx, ny)
                ball.vx *= 1.3
                ball.vy *= 1.3

                # Flash effect
                self.color = WHITE
                self.hit_timer = 5

                return True

        return False


class Wall:
    """Static wall boundary."""

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def draw(self, screen):
        """Render the wall."""
        pygame.draw.line(screen, GRAY, (self.x1, self.y1), (self.x2, self.y2), WALL_THICKNESS)

    def check_collision(self, ball):
        """Check and handle collision with ball."""
        # Line segment vector
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        length = math.sqrt(dx * dx + dy * dy)

        if length == 0:
            return False

        # Normalize line direction
        nx = dx / length
        ny = dy / length

        # Vector from line start to ball
        bx = ball.x - self.x1
        by = ball.y - self.y1

        # Project ball onto line
        projection = bx * nx + by * ny

        # Find closest point on line segment
        if projection < 0:
            closest_x = self.x1
            closest_y = self.y1
        elif projection > length:
            closest_x = self.x2
            closest_y = self.y2
        else:
            closest_x = self.x1 + projection * nx
            closest_y = self.y1 + projection * ny

        # Calculate distance to closest point
        dist_x = ball.x - closest_x
        dist_y = ball.y - closest_y
        dist = math.sqrt(dist_x * dist_x + dist_y * dist_y)

        if dist < ball.radius + WALL_THICKNESS / 2:
            # Calculate normal at collision point
            if dist > 0:
                normal_x = dist_x / dist
                normal_y = dist_y / dist
            else:
                # Ball center is on the line, use perpendicular
                normal_x = -ny
                normal_y = nx

            # Push ball out
            overlap = ball.radius + WALL_THICKNESS / 2 - dist
            ball.x += normal_x * overlap
            ball.y += normal_y * overlap

            # Bounce
            ball.bounce_normal(normal_x, normal_y)

            return True

        return False
