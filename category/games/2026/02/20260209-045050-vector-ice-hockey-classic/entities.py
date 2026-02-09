"""Game entities for Vector Ice Hockey Classic."""

import pygame
import random
from config import *


class Vector:
    """Simple 2D vector class for physics calculations."""

    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def magnitude(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            return Vector(self.x / mag, self.y / mag)
        return Vector(0, 0)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def to_tuple(self):
        return (self.x, self.y)


class Puck:
    """Hockey puck with physics-based movement."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.pos = Vector(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.vel = Vector(0, 0)
        self.radius = PUCK_RADIUS

    def update(self):
        # Apply velocity
        self.pos = self.pos + self.vel

        # Apply friction
        self.vel = self.vel * PUCK_FRICTION

        # Stop if very slow
        if self.vel.magnitude() < 0.1:
            self.vel = Vector(0, 0)

        # Cap max speed
        if self.vel.magnitude() > PUCK_MAX_SPEED:
            self.vel = self.vel.normalize() * PUCK_MAX_SPEED

        # Boundary collision
        self._handle_boundaries()

    def _handle_boundaries(self):
        # Left and right walls (bounce)
        if self.pos.x - self.radius < RINK_MARGIN:
            self.pos.x = RINK_MARGIN + self.radius
            self.vel.x *= -BOUNCE_DAMPING
        elif self.pos.x + self.radius > SCREEN_WIDTH - RINK_MARGIN:
            self.pos.x = SCREEN_WIDTH - RINK_MARGIN - self.radius
            self.vel.x *= -BOUNCE_DAMPING

        # Top and bottom walls (bounce, except in goal area)
        in_goal_range = (SCREEN_WIDTH / 2 - GOAL_WIDTH / 2 <
                         self.pos.x < SCREEN_WIDTH / 2 + GOAL_WIDTH / 2)

        if not in_goal_range:
            if self.pos.y - self.radius < RINK_MARGIN:
                self.pos.y = RINK_MARGIN + self.radius
                self.vel.y *= -BOUNCE_DAMPING
            elif self.pos.y + self.radius > SCREEN_HEIGHT - RINK_MARGIN:
                self.pos.y = SCREEN_HEIGHT - RINK_MARGIN - self.radius
                self.vel.y *= -BOUNCE_DAMPING

    def draw(self, surface):
        # Draw puck shadow
        pygame.draw.circle(
            surface, (100, 100, 100),
            (int(self.pos.x + 3), int(self.pos.y + 3)),
            self.radius
        )
        # Draw puck
        pygame.draw.circle(
            surface, COLOR_PUCK,
            (int(self.pos.x), int(self.pos.y)),
            self.radius
        )
        # Draw highlight
        pygame.draw.circle(
            surface, (80, 80, 80),
            (int(self.pos.x - 3), int(self.pos.y - 3)),
            self.radius // 3
        )

    def get_rect(self):
        return pygame.Rect(
            self.pos.x - self.radius,
            self.pos.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )


class Player:
    """Base class for hockey players."""

    def __init__(self, x, y, color):
        self.start_pos = Vector(x, y)
        self.pos = Vector(x, y)
        self.vel = Vector(0, 0)
        self.color = color
        self.radius = PLAYER_RADIUS

    def reset(self):
        self.pos = Vector(self.start_pos.x, self.start_pos.y)
        self.vel = Vector(0, 0)

    def move(self, dx, dy):
        self.vel = Vector(dx * PLAYER_SPEED, dy * PLAYER_SPEED)

    def update(self):
        self.pos = self.pos + self.vel

        # Boundary constraint
        self.pos.x = max(RINK_MARGIN + self.radius,
                         min(SCREEN_WIDTH - RINK_MARGIN - self.radius, self.pos.x))
        self.pos.y = max(RINK_MARGIN + self.radius,
                         min(SCREEN_HEIGHT - RINK_MARGIN - self.radius, self.pos.y))

    def draw(self, surface):
        # Draw shadow
        pygame.draw.circle(
            surface, (100, 100, 100),
            (int(self.pos.x + 4), int(self.pos.y + 4)),
            self.radius
        )
        # Draw player
        pygame.draw.circle(
            surface, self.color,
            (int(self.pos.x), int(self.pos.y)),
            self.radius
        )
        # Draw inner circle
        pygame.draw.circle(
            surface, (255, 255, 255),
            (int(self.pos.x), int(self.pos.y)),
            self.radius // 2
        )
        # Draw outline
        pygame.draw.circle(
            surface, (30, 30, 30),
            (int(self.pos.x), int(self.pos.y)),
            self.radius,
            3
        )


class AIOpponent(Player):
    """AI opponent for single-player mode."""

    def __init__(self, x, y):
        super().__init__(x, y, COLOR_OPPONENT)
        self.reaction_timer = 0
        self.target_x = x

    def reset(self):
        super().reset()
        self.target_x = self.start_pos.x

    def update_ai(self, puck):
        self.reaction_timer += 1

        if self.reaction_timer < AI_REACTION_DELAY:
            return

        self.reaction_timer = 0

        # Simple AI logic
        if puck.pos.y < SCREEN_HEIGHT / 2:
            # Puck is in player's half - move toward center
            target_x = SCREEN_WIDTH / 2
        else:
            # Puck is in AI's half - chase it
            if random.random() < AI_ERROR_CHANCE:
                # Add some randomness
                target_x = puck.pos.x + random.uniform(-50, 50)
            else:
                target_x = puck.pos.x

        # Smooth movement toward target
        dx = target_x - self.pos.x
        if abs(dx) > 5:
            self.vel.x = AI_SPEED if dx > 0 else -AI_SPEED
        else:
            self.vel.x = 0

        # Defensive positioning
        target_y = SCREEN_HEIGHT * 0.75
        if puck.pos.y > SCREEN_HEIGHT * 0.6:
            target_y = puck.pos.y - 30

        dy = target_y - self.pos.y
        if abs(dy) > 5:
            self.vel.y = AI_SPEED * 0.7 if dy > 0 else -AI_SPEED * 0.7
        else:
            self.vel.y = 0

        # Keep in AI's half
        if self.pos.y < SCREEN_HEIGHT / 2:
            self.pos.y = SCREEN_HEIGHT / 2 + self.radius


RINK_MARGIN = 30
