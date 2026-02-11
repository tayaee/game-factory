"""Game entities: Player, Paratroopa."""

import pygame
import random
import math
from config import (
    PLAYER_WIDTH, PLAYER_HEIGHT, GROUND_Y,
    PARATROOPA_WIDTH, PARATROOPA_HEIGHT,
    GRAVITY, MAX_FALL_SPEED, JUMP_IMPULSE, BOUNCE_IMPULSE,
    MOVE_SPEED, FRICTION, MIN_ENEMY_SPEED, MAX_ENEMY_SPEED,
    COLOR_PLAYER, COLOR_PLAYER_FACE,
    COLOR_PARATROOPA_BODY, COLOR_PARATROOPA_SHELL, COLOR_PARATROOPA_WING,
    SCREEN_WIDTH, SCREEN_HEIGHT
)


class Player:
    """Player character with gravity-based physics."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.on_ground = True
        self.alive = True
        self.start_x = x
        self.start_y = y
        self.has_jumped_once = False

    def reset(self):
        """Reset player to starting position."""
        self.x = self.start_x
        self.y = self.start_y
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = True
        self.alive = True
        self.has_jumped_once = False

    def update(self, keys):
        """Update player physics and input."""
        if not self.alive:
            return

        # Horizontal input
        if keys[pygame.K_LEFT]:
            self.vel_x = -MOVE_SPEED
        elif keys[pygame.K_RIGHT]:
            self.vel_x = MOVE_SPEED
        else:
            self.vel_x *= FRICTION
            if abs(self.vel_x) < 0.1:
                self.vel_x = 0

        # Apply horizontal velocity
        self.x += self.vel_x

        # Screen bounds
        if self.x < 0:
            self.x = 0
            self.vel_x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            self.vel_x = 0

        # Jump input (only from ground initially)
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = JUMP_IMPULSE
            self.on_ground = False
            self.has_jumped_once = True

        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        self.y += self.vel_y

        # Ground collision
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.on_ground = True

        # Check if fallen off screen (game over)
        if self.y > SCREEN_HEIGHT:
            self.alive = False

    def bounce(self):
        """Apply bounce impulse from stomping an enemy."""
        self.vel_y = BOUNCE_IMPULSE
        self.on_ground = False

    def get_hitbox(self):
        """Return player collision rectangle."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def get_stomp_zone(self):
        """Return the stomp zone (bottom of player)."""
        return pygame.Rect(
            int(self.x + 4),
            int(self.y + self.height - 8),
            self.width - 8,
            8
        )

    def draw(self, surface):
        """Draw player."""
        # Body
        pygame.draw.rect(surface, COLOR_PLAYER, (int(self.x), int(self.y), self.width, self.height))

        # Face
        face_x = int(self.x + 4)
        face_y = int(self.y + 4)
        pygame.draw.rect(surface, COLOR_PLAYER_FACE, (face_x, face_y, 16, 12))

        # Eyes
        pygame.draw.circle(surface, (0, 0, 0), (face_x + 5, face_y + 5), 2)
        pygame.draw.circle(surface, (0, 0, 0), (face_x + 11, face_y + 5), 2)

        # Hat brim
        pygame.draw.rect(surface, (200, 30, 30), (int(self.x), int(self.y - 2), self.width, 4))


class Paratroopa:
    """Flying Koopa Paratroopa with sinusoidal movement pattern."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PARATROOPA_WIDTH
        self.height = PARATROOPA_HEIGHT
        self.speed = random.uniform(MIN_ENEMY_SPEED, MAX_ENEMY_SPEED)
        self.amplitude = random.uniform(30, 80)
        self.frequency = random.uniform(0.02, 0.05)
        self.phase = random.uniform(0, math.pi * 2)
        self.time_offset = 0
        self.direction = 1 if random.choice([True, False]) else -1
        self.alive = True
        self.spawn_y = y

    def update(self):
        """Update paratroopa position with sinusoidal movement."""
        self.time_offset += 1

        # Vertical sinusoidal movement
        self.y = self.spawn_y + math.sin(self.time_offset * self.frequency + self.phase) * self.amplitude

        # Horizontal movement
        self.x += self.speed * self.direction

        # Bounce off walls
        if self.x <= 0:
            self.x = 0
            self.direction = 1
        elif self.x >= SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            self.direction = -1

        # Move down gradually
        self.spawn_y += 0.3

    def get_hitbox(self):
        """Return paratroopa collision rectangle."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def get_stomp_hitbox(self):
        """Return hitbox for stomping (top portion)."""
        return pygame.Rect(
            int(self.x + 2),
            int(self.y),
            self.width - 4,
            10
        )

    def draw(self, surface):
        """Draw paratroopa."""
        # Wings
        wing_offset = math.sin(self.time_offset * 0.3) * 3
        pygame.draw.ellipse(
            surface,
            COLOR_PARATROOPA_WING,
            (int(self.x - 8), int(self.y + 8 + wing_offset), 12, 20)
        )
        pygame.draw.ellipse(
            surface,
            COLOR_PARATROOPA_WING,
            (int(self.x + self.width - 4), int(self.y + 8 - wing_offset), 12, 20)
        )

        # Shell/body
        pygame.draw.ellipse(
            surface,
            COLOR_PARATROOPA_SHELL,
            (int(self.x), int(self.y + 8), self.width, self.height - 8)
        )

        # Shell pattern
        pygame.draw.ellipse(
            surface,
            (150, 100, 30),
            (int(self.x + 4), int(self.y + 12), self.width - 8, self.height - 16)
        )

        # Head
        pygame.draw.circle(
            surface,
            COLOR_PARATROOPA_BODY,
            (int(self.x + self.width // 2), int(self.y + 6)),
            8
        )

        # Eyes
        eye_offset_x = 4 if self.direction > 0 else -4
        pygame.draw.circle(
            surface,
            (255, 255, 255),
            (int(self.x + self.width // 2 + eye_offset_x), int(self.y + 4)),
            3
        )
        pygame.draw.circle(
            surface,
            (0, 0, 0),
            (int(self.x + self.width // 2 + eye_offset_x + self.direction), int(self.y + 4)),
            1
        )
