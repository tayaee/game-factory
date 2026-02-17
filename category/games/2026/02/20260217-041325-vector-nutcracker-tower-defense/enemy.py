"""Enemy class for tower defense game."""

import pygame
from config import *


class Enemy:
    """Enemy that follows the path toward the toy box."""

    def __init__(self, enemy_type, path):
        """Initialize enemy."""
        self.type = enemy_type
        self.config = ENEMY_TYPES[enemy_type]
        self.max_health = self.config["health"]
        self.health = self.max_health
        self.speed = self.config["speed"]
        self.reward = self.config["reward"]
        self.color = self.config["color"]

        self.path = path
        self.path_index = 0
        self.x = path[0][0] * CELL_SIZE + CELL_SIZE // 2 + GRID_OFFSET_X
        self.y = path[0][1] * CELL_SIZE + CELL_SIZE // 2 + GRID_OFFSET_Y

        self.slow_timer = 0
        self.original_speed = self.speed
        self.alive = True
        self.reached_end = False

    def update(self, dt):
        """Update enemy position and status."""
        # Handle slow effect
        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.speed = self.original_speed

        if self.path_index >= len(self.path) - 1:
            self.reached_end = True
            return

        # Get current and target positions
        current_pos = self.path[self.path_index]
        target_pos = self.path[self.path_index + 1]

        target_x = target_pos[0] * CELL_SIZE + CELL_SIZE // 2 + GRID_OFFSET_X
        target_y = target_pos[1] * CELL_SIZE + CELL_SIZE // 2 + GRID_OFFSET_Y

        # Calculate direction
        dx = target_x - self.x
        dy = target_y - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5

        # Move toward target
        move_dist = self.speed * CELL_SIZE * dt
        if dist <= move_dist:
            self.x = target_x
            self.y = target_y
            self.path_index += 1
        else:
            self.x += (dx / dist) * move_dist
            self.y += (dy / dist) * move_dist

    def apply_slow(self, factor, duration):
        """Apply slow effect to enemy."""
        self.speed = self.original_speed * factor
        self.slow_timer = duration

    def take_damage(self, damage):
        """Apply damage to enemy."""
        self.health -= damage
        if self.health <= 0:
            self.alive = False

    def draw(self, surface):
        """Draw enemy as a wind-up mouse shape."""
        # Calculate grid position for display
        grid_x = int((self.x - GRID_OFFSET_X) // CELL_SIZE)
        grid_y = int((self.y - GRID_OFFSET_Y) // CELL_SIZE)

        center_x = self.x
        center_y = self.y

        # Draw body (ellipse)
        body_width = CELL_SIZE * 0.7
        body_height = CELL_SIZE * 0.5
        pygame.draw.ellipse(surface, self.color,
                           (center_x - body_width // 2, center_y - body_height // 2,
                            body_width, body_height))

        # Draw head (circle)
        head_radius = CELL_SIZE * 0.25
        pygame.draw.circle(surface, self.color, (int(center_x + body_width // 3), int(center_y)), int(head_radius))

        # Draw ears (triangles)
        ear_size = CELL_SIZE * 0.15
        pygame.draw.polygon(surface, self.color, [
            (center_x + body_width // 3 - ear_size, center_y - head_radius),
            (center_x + body_width // 3 + ear_size, center_y - head_radius),
            (center_x + body_width // 3, center_y - head_radius - ear_size * 1.5)
        ])
        pygame.draw.polygon(surface, self.color, [
            (center_x + body_width // 3 - ear_size * 0.5, center_y - head_radius + 2),
            (center_x + body_width // 3 + ear_size * 1.5, center_y - head_radius + 2),
            (center_x + body_width // 3 + ear_size * 0.5, center_y - head_radius - ear_size * 1.5)
        ])

        # Draw slow effect
        if self.slow_timer > 0:
            pygame.draw.circle(surface, COLOR_FROST_PROJECTILE, (int(center_x), int(center_y)),
                            int(body_width * 0.8), 2)

        # Draw health bar
        if self.health < self.max_health:
            bar_width = CELL_SIZE * 0.8
            bar_height = 4
            bar_x = center_x - bar_width // 2
            bar_y = center_y + body_height // 2 + 5

            health_percent = self.health / self.max_health
            pygame.draw.rect(surface, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, bar_width * health_percent, bar_height))

    def get_position(self):
        """Get current position."""
        return (self.x, self.y)

    def get_grid_position(self):
        """Get current grid position."""
        grid_x = int((self.x - GRID_OFFSET_X) // CELL_SIZE)
        grid_y = int((self.y - GRID_OFFSET_Y) // CELL_SIZE)
        return (grid_x, grid_y)

    def is_alive(self):
        """Check if enemy is still alive."""
        return self.alive
