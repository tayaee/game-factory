"""Game entities for Frogger."""

import pygame
from config import *


class Frog:
    """The player character."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset frog to starting position."""
        self.grid_x = COLS // 2
        self.grid_y = START_ROW
        self.x = self.grid_x * GRID_SIZE + GRID_SIZE // 2
        self.y = self.grid_y * GRID_SIZE + GRID_SIZE // 2
        self.alive = True
        self.on_log = False
        self.move_cooldown = 0

    def move(self, dx, dy):
        """Move the frog by grid units."""
        if self.move_cooldown > 0 or not self.alive:
            return

        new_x = self.grid_x + dx
        new_y = self.grid_y + dy

        if 0 <= new_x < COLS and 0 <= new_y < ROWS:
            self.grid_x = new_x
            self.grid_y = new_y
            self.x = self.grid_x * GRID_SIZE + GRID_SIZE // 2
            self.y = self.grid_y * GRID_SIZE + GRID_SIZE // 2
            self.move_cooldown = FROG_MOVE_COOLDOWN
            return True
        return False

    def update(self):
        """Update frog state."""
        if self.move_cooldown > 0:
            self.move_cooldown -= 1

    def draw(self, surface):
        """Draw the frog."""
        if not self.alive:
            return

        # Draw frog body
        rect = pygame.Rect(
            self.x - FROG_SIZE // 2,
            self.y - FROG_SIZE // 2,
            FROG_SIZE,
            FROG_SIZE
        )
        pygame.draw.rect(surface, COLOR_FROG, rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_FROG_OUTLINE, rect, 2, border_radius=6)

        # Draw eyes
        eye_size = 6
        eye_offset = FROG_SIZE // 4
        pygame.draw.circle(surface, (255, 255, 255),
                          (int(self.x - eye_offset), int(self.y - eye_offset)), eye_size)
        pygame.draw.circle(surface, (255, 255, 255),
                          (int(self.x + eye_offset), int(self.y - eye_offset)), eye_size)
        pygame.draw.circle(surface, (0, 0, 0),
                          (int(self.x - eye_offset), int(self.y - eye_offset)), eye_size // 2)
        pygame.draw.circle(surface, (0, 0, 0),
                          (int(self.x + eye_offset), int(self.y - eye_offset)), eye_size // 2)

    def get_rect(self):
        """Get collision rect."""
        return pygame.Rect(
            self.x - FROG_SIZE // 2 + 4,
            self.y - FROG_SIZE // 2 + 4,
            FROG_SIZE - 8,
            FROG_SIZE - 8
        )


class Obstacle:
    """Moving obstacle (vehicle or log)."""

    def __init__(self, row, x, obstacle_type, speed):
        self.row = row
        self.x = x
        self.y = row * GRID_SIZE + GRID_SIZE // 2
        self.type = obstacle_type
        self.speed = speed

        if obstacle_type == 'car':
            self.width = VEHICLE_WIDTHS['car']
            self.height = VEHICLE_HEIGHTS['car']
            self.color = COLOR_CAR
        elif obstacle_type == 'truck':
            self.width = VEHICLE_WIDTHS['truck']
            self.height = VEHICLE_HEIGHTS['truck']
            self.color = COLOR_TRUCK
        else:  # log
            if obstacle_type == 'short':
                self.width = LOG_WIDTHS[0]
            elif obstacle_type == 'medium':
                self.width = LOG_WIDTHS[1]
            else:  # long
                self.width = LOG_WIDTHS[2]
            self.height = LOG_HEIGHT
            self.color = COLOR_LOG

    def update(self, speed_multiplier=1.0):
        """Update obstacle position."""
        self.x += self.speed * speed_multiplier

        # Wrap around screen
        if self.speed > 0 and self.x > SCREEN_WIDTH + self.width:
            self.x = -self.width
        elif self.speed < 0 and self.x < -self.width:
            self.x = SCREEN_WIDTH + self.width

    def draw(self, surface):
        """Draw the obstacle."""
        rect = pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )

        if self.type in ['car', 'truck']:
            # Draw vehicle
            pygame.draw.rect(surface, self.color, rect, border_radius=4)
            # Draw windows
            window_color = (150, 200, 220)
            if self.type == 'car':
                window_width = self.width // 3
                window_rect = pygame.Rect(
                    self.x - window_width // 2,
                    self.y - self.height // 3,
                    window_width,
                    self.height // 2
                )
                pygame.draw.rect(surface, window_color, window_rect, border_radius=2)
            else:  # truck
                window_width = self.width // 4
                window_rect = pygame.Rect(
                    self.x - self.width // 2 + window_width,
                    self.y - self.height // 3,
                    window_width,
                    self.height // 2
                )
                pygame.draw.rect(surface, window_color, window_rect, border_radius=2)
        else:  # log
            pygame.draw.rect(surface, self.color, rect, border_radius=8)
            # Draw wood grain
            pygame.draw.line(surface, (100, 60, 30),
                            (self.x - self.width // 4, self.y),
                            (self.x - self.width // 4, self.y), 2)
            pygame.draw.line(surface, (100, 60, 30),
                            (self.x + self.width // 4, self.y),
                            (self.x + self.width // 4, self.y), 2)

    def get_rect(self):
        """Get collision rect."""
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )


class Lane:
    """A horizontal lane containing obstacles."""

    def __init__(self, row, lane_type, speed, size_type, spacing):
        self.row = row
        self.type = lane_type
        self.base_speed = speed
        self.obstacles = []

        # Create obstacles
        num_obstacles = 3
        for i in range(num_obstacles):
            x = (i * spacing * GRID_SIZE) % SCREEN_WIDTH
            self.obstacles.append(Obstacle(row, x, lane_type, speed))

    def update(self, speed_multiplier=1.0):
        """Update all obstacles in lane."""
        for obs in self.obstacles:
            obs.update(speed_multiplier)

    def draw(self, surface):
        """Draw all obstacles in lane."""
        for obs in self.obstacles:
            obs.draw(surface)

    def check_collision(self, frog_rect):
        """Check if frog collides with any obstacle."""
        for obs in self.obstacles:
            if obs.get_rect().colliderect(frog_rect):
                return obs
        return None


class Lilypad:
    """A goal lilypad at the top of the screen."""

    def __init__(self, grid_x):
        self.grid_x = grid_x
        self.x = grid_x * GRID_SIZE + GRID_SIZE // 2
        self.y = GOAL_ROW * GRID_SIZE + GRID_SIZE // 2
        self.filled = False

    def draw(self, surface):
        """Draw the lilypad."""
        color = COLOR_LILYPAD_FILLED if self.filled else COLOR_LILYPAD
        radius = GRID_SIZE // 2 - 4
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), radius)
        if not self.filled:
            pygame.draw.circle(surface, (30, 150, 60), (int(self.x), int(self.y)), radius - 4)

    def get_rect(self):
        """Get collision rect."""
        return pygame.Rect(
            self.x - GRID_SIZE // 3,
            self.y - GRID_SIZE // 3,
            GRID_SIZE // 1.5,
            GRID_SIZE // 1.5
        )
