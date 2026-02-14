"""Game entities for Vector Snake Rattle Coin Dash."""

import pygame
import random
import math
from config import *


class Snake:
    """Represents snake entity on isometric grid."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset snake to initial state."""
        # Start in middle of the grid
        start_x = GRID_SIZE // 2
        start_y = GRID_SIZE // 2

        # Snake body as list of (grid_x, grid_y) positions
        self.body = [
            (start_x, start_y),
            (start_x, start_y + 1),
            (start_x, start_y + 2)
        ]
        self.direction = DIR_UP
        self.next_direction = DIR_UP
        self.grow_pending = 0

    def set_direction(self, direction):
        """Set snake's direction (prevents 180-degree turns)."""
        # Prevent reversing direction
        if (direction[0] * -1, direction[1] * -1) == self.direction:
            return False

        self.next_direction = direction
        return True

    def update(self):
        """Update snake position."""
        self.direction = self.next_direction

        # Calculate new head position
        head_x, head_y = self.body[0]
        new_x = head_x + self.direction[0]
        new_y = head_y + self.direction[1]

        # Check wall collision
        if new_x < 0 or new_x >= GRID_SIZE or new_y < 0 or new_y >= GRID_SIZE:
            return False

        # Check self collision (skip the tail as it will move unless growing)
        body_to_check = self.body[:-1] if self.grow_pending == 0 else self.body
        if (new_x, new_y) in body_to_check:
            return False

        # Add new head
        self.body.insert(0, (new_x, new_y))

        # Remove tail if not growing
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

        return True

    def grow(self, amount=1):
        """Schedule snake to grow."""
        self.grow_pending += amount

    def get_head_position(self):
        """Get current head position."""
        return self.body[0]

    def get_length(self):
        """Get current snake length."""
        return len(self.body)

    def check_coin_collision(self, coin_pos):
        """Check if snake head collides with coin."""
        return self.body[0] == coin_pos

    def draw(self, surface):
        """Draw snake on isometric grid."""
        for i, (grid_x, grid_y) in enumerate(self.body):
            screen_x, screen_y = grid_to_screen(grid_x, grid_y)

            # Draw isometric diamond for each segment
            self._draw_isometric_diamond(surface, screen_x, screen_y, i == 0)

    def _draw_isometric_diamond(self, surface, screen_x, screen_y, is_head):
        """Draw an isometric diamond shape."""
        half_size = CELL_SIZE // 2
        quarter_size = CELL_SIZE // 4

        # Diamond vertices
        points = [
            (screen_x, screen_y - half_size),  # Top
            (screen_x + half_size, screen_y),  # Right
            (screen_x, screen_y + half_size),  # Bottom
            (screen_x - half_size, screen_y),  # Left
        ]

        if is_head:
            # Head: bright white with glow
            color = COLOR_SNAKE_HEAD
            pygame.draw.polygon(surface, COLOR_SNAKE_GLOW, points)
            pygame.draw.polygon(surface, color, points, 2)

            # Draw inner diamond for head
            inner_points = [
                (screen_x, screen_y - quarter_size),
                (screen_x + quarter_size, screen_y),
                (screen_x, screen_y + quarter_size),
                (screen_x - quarter_size, screen_y),
            ]
            pygame.draw.polygon(surface, color, inner_points)

            # Draw direction indicator (small circle)
            pygame.draw.circle(surface, (200, 200, 200), (screen_x, screen_y), 3)
        else:
            # Body: lighter gray
            pygame.draw.polygon(surface, COLOR_SNAKE_BODY, points)
            pygame.draw.polygon(surface, COLOR_GRID_LINES, points, 1)


class Coin:
    """Represents coin entity on isometric grid."""

    def __init__(self):
        self.position = (0, 0)
        self.pulse_phase = 0
        self.spawn_coins = 0  # Coins collected counter

    def spawn(self, snake_body):
        """Spawn coin at a random empty position."""
        empty_positions = []

        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if (x, y) not in snake_body:
                    empty_positions.append((x, y))

        if empty_positions:
            self.position = random.choice(empty_positions)

    def update(self):
        """Update coin animation."""
        self.pulse_phase = (self.pulse_phase + 0.15) % (2 * 3.14159)

    def draw(self, surface):
        """Draw coin on isometric grid."""
        grid_x, grid_y = self.position
        screen_x, screen_y = grid_to_screen(grid_x, grid_y)

        # Pulsing effect
        pulse = (math.cos(self.pulse_phase) + 1) / 2  # 0 to 1
        scale = 0.8 + pulse * 0.4  # Scale from 0.8 to 1.2

        half_size = int((CELL_SIZE // 2) * scale)
        quarter_size = int(half_size // 2)

        # Draw outer glow ring
        glow_points = [
            (screen_x, screen_y - half_size - 2),
            (screen_x + half_size + 2, screen_y),
            (screen_x, screen_y + half_size + 2),
            (screen_x - half_size - 2, screen_y),
        ]
        pygame.draw.polygon(surface, (100, 100, 100), glow_points, 1)

        # Draw main coin diamond
        coin_points = [
            (screen_x, screen_y - half_size),
            (screen_x + half_size, screen_y),
            (screen_x, screen_y + half_size),
            (screen_x - half_size, screen_y),
        ]
        pygame.draw.polygon(surface, COLOR_COIN, coin_points)
        pygame.draw.polygon(surface, COLOR_COIN_OUTLINE, coin_points, 2)

        # Draw inner highlight
        inner_points = [
            (screen_x, screen_y - quarter_size),
            (screen_x + quarter_size, screen_y),
            (screen_x, screen_y + quarter_size),
            (screen_x - quarter_size, screen_y),
        ]
        pygame.draw.polygon(surface, (255, 230, 150), inner_points)
