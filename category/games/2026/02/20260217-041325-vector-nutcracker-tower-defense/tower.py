"""Tower and projectile classes for tower defense game."""

import pygame
import math
from config import *


class Projectile:
    """Projectile fired by towers."""

    def __init__(self, x, y, target_x, target_y, damage, speed, is_frost=False, slow_factor=0.5, slow_duration=2.0):
        """Initialize projectile."""
        self.x = x
        self.y = y
        self.damage = damage
        self.speed = speed
        self.is_frost = is_frost
        self.slow_factor = slow_factor
        self.slow_duration = slow_duration
        self.active = True

        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist > 0:
            self.dx = (dx / dist) * speed
            self.dy = (dy / dist) * speed
        else:
            self.dx = speed
            self.dy = 0

    def update(self, dt):
        """Update projectile position."""
        self.x += self.dx
        self.y += self.dy

        # Check if out of bounds
        if (self.x < 0 or self.x > WINDOW_WIDTH or
            self.y < 0 or self.y > WINDOW_HEIGHT):
            self.active = False

    def draw(self, surface):
        """Draw projectile."""
        color = COLOR_FROST_PROJECTILE if self.is_frost else COLOR_PROJECTILE
        radius = 4 if self.is_frost else 3
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), radius)
        if self.is_frost:
            pygame.draw.circle(surface, (200, 220, 255), (int(self.x), int(self.y)), radius + 2, 1)

    def get_position(self):
        """Get projectile position."""
        return (self.x, self.y)


class Tower:
    """Nutcracker tower that fires projectiles."""

    def __init__(self, grid_x, grid_y, tower_type):
        """Initialize tower."""
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.type = tower_type
        self.config = TOWER_TYPES[tower_type]
        self.cost = self.config["cost"]
        self.range = self.config["range"]
        self.damage = self.config["damage"]
        self.cooldown = self.config["cooldown"]
        self.color = self.config["color"]
        self.projectile_speed = self.config["projectile_speed"]

        self.x = grid_x * CELL_SIZE + CELL_SIZE // 2 + GRID_OFFSET_X
        self.y = grid_y * CELL_SIZE + CELL_SIZE // 2 + GRID_OFFSET_Y

        self.cooldown_timer = 0
        self.angle = 0
        self.target_angle = 0

        # Frost tower special properties
        self.slow_factor = self.config.get("slow_factor", 1.0)
        self.slow_duration = self.config.get("slow_duration", 0)

    def update(self, dt):
        """Update tower state."""
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

        # Smoothly rotate toward target
        angle_diff = self.target_angle - self.angle
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        self.angle += angle_diff * 10 * dt

    def can_fire(self):
        """Check if tower can fire."""
        return self.cooldown_timer <= 0

    def fire(self, target_pos):
        """Fire at target position."""
        self.cooldown_timer = self.cooldown
        is_frost = self.type == "Frost"

        return Projectile(
            self.x, self.y,
            target_pos[0], target_pos[1],
            self.damage,
            self.projectile_speed,
            is_frost,
            self.slow_factor,
            self.slow_duration
        )

    def set_target(self, target_pos):
        """Set target for turret rotation."""
        dx = target_pos[0] - self.x
        dy = target_pos[1] - self.y
        self.target_angle = math.atan2(dy, dx)

    def get_range_pixels(self):
        """Get range in pixels."""
        return self.range * CELL_SIZE

    def get_position(self):
        """Get tower position."""
        return (self.x, self.y)

    def draw(self, surface, show_range=False):
        """Draw tower as a nutcracker."""
        center_x = self.x
        center_y = self.y
        size = CELL_SIZE * 0.8

        # Draw range indicator
        if show_range:
            pygame.draw.circle(surface, (*self.color, 50), (int(center_x), int(center_y)),
                            int(self.get_range_pixels()), 1)

        # Draw base (rectangle)
        base_height = size * 0.3
        base_width = size * 0.6
        pygame.draw.rect(surface, self.color,
                        (center_x - base_width // 2, center_y + size // 4,
                         base_width, base_height))

        # Draw body (rectangle)
        body_width = size * 0.4
        body_height = size * 0.5
        pygame.draw.rect(surface, self.color,
                        (center_x - body_width // 2, center_y - body_height // 3,
                         body_width, body_height))

        # Draw turret (rotated)
        turret_length = size * 0.4
        turret_width = size * 0.15
        end_x = center_x + math.cos(self.angle) * turret_length
        end_y = center_y + math.sin(self.angle) * turret_length

        # Calculate perpendicular for turret width
        perp_x = math.cos(self.angle + math.pi / 2) * turret_width / 2
        perp_y = math.sin(self.angle + math.pi / 2) * turret_width / 2

        turret_points = [
            (center_x - perp_x, center_y - perp_y),
            (end_x - perp_x, end_y - perp_y),
            (end_x + perp_x, end_y + perp_y),
            (center_x + perp_x, center_y + perp_y)
        ]
        pygame.draw.polygon(surface, self.color, turret_points)

        # Draw hat (triangle)
        hat_width = size * 0.5
        hat_height = size * 0.3
        pygame.draw.polygon(surface, self.color, [
            (center_x - hat_width // 2, center_y - body_height // 3),
            (center_x + hat_width // 2, center_y - body_height // 3),
            (center_x, center_y - body_height // 3 - hat_height)
        ])

        # Draw eyes
        eye_size = size * 0.05
        eye_offset_x = size * 0.1
        eye_offset_y = -body_height // 6
        pygame.draw.circle(surface, (255, 255, 255),
                         (int(center_x - eye_offset_x), int(center_y + eye_offset_y)),
                         int(eye_size))
        pygame.draw.circle(surface, (255, 255, 255),
                         (int(center_x + eye_offset_x), int(center_y + eye_offset_y)),
                         int(eye_size))
