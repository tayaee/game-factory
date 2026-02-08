"""Game entities for Vector Snake Grid Survival."""

import pygame
import random
from config import *


class Snake:
    """Represents the snake entity."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset snake to initial state."""
        # Start in the middle of the grid
        start_x = GRID_COLS // 2
        start_y = GRID_ROWS // 2

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
        """Set the snake's direction (prevents 180-degree turns)."""
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
        if new_x < 0 or new_x >= GRID_COLS or new_y < 0 or new_y >= GRID_ROWS:
            return False

        # Check self collision (skip the tail as it will move)
        if (new_x, new_y) in self.body[:-1]:
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

    def check_food_collision(self, food_pos):
        """Check if snake head collides with food."""
        return self.body[0] == food_pos

    def draw(self, surface):
        """Draw the snake."""
        for i, (grid_x, grid_y) in enumerate(self.body):
            x = grid_x * GRID_SIZE
            y = grid_y * GRID_SIZE + UI_HEIGHT

            # Head is slightly larger and brighter
            if i == 0:
                # Glow effect for head
                glow_rect = pygame.Rect(x - 2, y - 2, GRID_SIZE + 4, GRID_SIZE + 4)
                pygame.draw.rect(surface, COLOR_SNAKE_GLOW, glow_rect, border_radius=4)

                body_rect = pygame.Rect(x + 1, y + 1, GRID_SIZE - 2, GRID_SIZE - 2)
                pygame.draw.rect(surface, COLOR_SNAKE_HEAD, body_rect, border_radius=4)

                # Draw eyes
                eye_size = 4
                eye_offset = 8
                if self.direction == DIR_UP:
                    pygame.draw.circle(surface, (255, 255, 255), (x + eye_offset, y + eye_offset), eye_size)
                    pygame.draw.circle(surface, (255, 255, 255), (x + GRID_SIZE - eye_offset, y + eye_offset), eye_size)
                elif self.direction == DIR_DOWN:
                    pygame.draw.circle(surface, (255, 255, 255), (x + eye_offset, y + GRID_SIZE - eye_offset), eye_size)
                    pygame.draw.circle(surface, (255, 255, 255), (x + GRID_SIZE - eye_offset, y + GRID_SIZE - eye_offset), eye_size)
                elif self.direction == DIR_LEFT:
                    pygame.draw.circle(surface, (255, 255, 255), (x + eye_offset, y + eye_offset), eye_size)
                    pygame.draw.circle(surface, (255, 255, 255), (x + eye_offset, y + GRID_SIZE - eye_offset), eye_size)
                else:
                    pygame.draw.circle(surface, (255, 255, 255), (x + GRID_SIZE - eye_offset, y + eye_offset), eye_size)
                    pygame.draw.circle(surface, (255, 255, 255), (x + GRID_SIZE - eye_offset, y + GRID_SIZE - eye_offset), eye_size)
            else:
                # Body segments fade slightly
                fade_factor = 1 - (i / max(len(self.body), 20)) * 0.3
                color = (
                    int(COLOR_SNAKE_BODY[0] * fade_factor),
                    int(COLOR_SNAKE_BODY[1] * fade_factor),
                    int(COLOR_SNAKE_BODY[2] * fade_factor)
                )
                body_rect = pygame.Rect(x + 2, y + 2, GRID_SIZE - 4, GRID_SIZE - 4)
                pygame.draw.rect(surface, color, body_rect, border_radius=3)


class Food:
    """Represents the food entity."""

    def __init__(self):
        self.position = (0, 0)
        self.spawn_timer = 0
        self.pulse_phase = 0

    def spawn(self, snake_body):
        """Spawn food at a random empty position."""
        empty_positions = []

        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                if (x, y) not in snake_body:
                    empty_positions.append((x, y))

        if empty_positions:
            self.position = random.choice(empty_positions)

    def update(self):
        """Update food animation."""
        self.pulse_phase = (self.pulse_phase + 0.1) % (2 * 3.14159)

    def draw(self, surface):
        """Draw the food."""
        grid_x, grid_y = self.position
        x = grid_x * GRID_SIZE + GRID_SIZE // 2
        y = grid_y * GRID_SIZE + UI_HEIGHT + GRID_SIZE // 2

        # Pulsing glow effect
        pulse = (math.sin(self.pulse_phase) + 1) / 2  # 0 to 1
        glow_radius = int(GRID_SIZE // 2 + 4 + pulse * 4)

        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surface,
            (*COLOR_FOOD_GLOW, 50 + int(pulse * 50)),
            (glow_radius, glow_radius),
            glow_radius
        )
        surface.blit(glow_surface, (x - glow_radius, y - glow_radius))

        # Main food circle
        food_radius = int(GRID_SIZE // 2 - 4 + pulse * 2)
        pygame.draw.circle(surface, COLOR_FOOD, (x, y), food_radius)

        # Highlight
        highlight_radius = food_radius // 3
        highlight_offset = food_radius // 3
        pygame.draw.circle(
            surface,
            (255, 200, 200),
            (x - highlight_offset, y - highlight_offset),
            highlight_radius
        )


import math
