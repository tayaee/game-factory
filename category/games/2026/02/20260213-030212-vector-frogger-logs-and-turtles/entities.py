"""Game entities for Vector Frogger: Logs and Turtles."""

import pygame
from config import *


class Frog:
    """The player character frog."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset frog to starting position."""
        self.grid_x = COLS // 2
        self.grid_y = START_ROW
        self.x = self.grid_x * GRID_SIZE + GRID_SIZE // 2
        self.y = self.grid_y * GRID_SIZE + GRID_SIZE // 2
        self.alive = True
        self.on_platform = False
        self.platform_speed = 0
        self.move_cooldown = 0
        self.previous_row = START_ROW

    def move(self, dx, dy):
        """Move frog by grid units."""
        if self.move_cooldown > 0 or not self.alive:
            return False

        new_x = self.grid_x + dx
        new_y = self.grid_y + dy

        if 0 <= new_x < COLS and 0 <= new_y < ROWS:
            self.previous_row = self.grid_y
            self.grid_x = new_x
            self.grid_y = new_y
            self.x = self.grid_x * GRID_SIZE + GRID_SIZE // 2
            self.y = self.grid_y * GRID_SIZE + GRID_SIZE // 2
            self.move_cooldown = FROG_MOVE_COOLDOWN
            return True
        return False

    def moved_forward(self):
        """Check if frog moved forward (upward) on last move."""
        return self.grid_y < self.previous_row

    def update(self):
        """Update frog state."""
        if self.move_cooldown > 0:
            self.move_cooldown -= 1

        # Move with platform if on one
        if self.on_platform and self.alive:
            self.x += self.platform_speed
            self.grid_x = int(self.x // GRID_SIZE)

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
        pygame.draw.rect(surface, COLOR_FROG, rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_FROG_OUTLINE, rect, 2, border_radius=8)

        # Draw eyes
        eye_size = 7
        eye_offset = FROG_SIZE // 4
        eye_y_offset = FROG_SIZE // 5

        # Left eye
        pygame.draw.circle(
            surface, (255, 255, 255),
            (int(self.x - eye_offset), int(self.y - eye_y_offset)), eye_size
        )
        pygame.draw.circle(
            surface, (0, 0, 0),
            (int(self.x - eye_offset), int(self.y - eye_y_offset)), eye_size // 2
        )

        # Right eye
        pygame.draw.circle(
            surface, (255, 255, 255),
            (int(self.x + eye_offset), int(self.y - eye_y_offset)), eye_size
        )
        pygame.draw.circle(
            surface, (0, 0, 0),
            (int(self.x + eye_offset), int(self.y - eye_y_offset)), eye_size // 2
        )

    def get_rect(self):
        """Get collision rect for frog."""
        return pygame.Rect(
            self.x - FROG_SIZE // 2 + 4,
            self.y - FROG_SIZE // 2 + 4,
            FROG_SIZE - 8,
            FROG_SIZE - 8
        )


class Log:
    """A floating log in the river."""

    def __init__(self, row, x, size, speed):
        self.row = row
        self.x = x
        self.y = row * GRID_SIZE + GRID_SIZE // 2
        self.width = PLATFORM_WIDTHS[size]
        self.height = PLATFORM_HEIGHT
        self.speed = speed
        self.is_submerged = False

    def update(self, speed_multiplier=1.0):
        """Update log position."""
        self.x += self.speed * speed_multiplier

        # Wrap around screen
        if self.speed > 0 and self.x > SCREEN_WIDTH + self.width:
            self.x = -self.width
        elif self.speed < 0 and self.x < -self.width:
            self.x = SCREEN_WIDTH + self.width

    def draw(self, surface):
        """Draw the log."""
        rect = pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
        pygame.draw.rect(surface, COLOR_LOG, rect, border_radius=10)

        # Draw wood grain details
        grain_spacing = self.width // 4
        for i in range(1, 4):
            gx = self.x - self.width // 2 + i * grain_spacing
            if gx < self.x + self.width // 2:
                pygame.draw.line(
                    surface, COLOR_LOG_GRAIN,
                    (gx, self.y - self.height // 4),
                    (gx, self.y + self.height // 4), 2
                )

    def get_rect(self):
        """Get collision rect."""
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )


class Turtle:
    """A floating turtle that periodically submerges."""

    def __init__(self, row, x, size, speed, cycle_offset=0):
        self.row = row
        self.x = x
        self.y = row * GRID_SIZE + GRID_SIZE // 2
        self.width = PLATFORM_WIDTHS[size]
        self.height = PLATFORM_HEIGHT
        self.speed = speed
        self.cycle_offset = cycle_offset
        self.is_submerged = False
        self.submerge_timer = 0

    def update(self, speed_multiplier=1.0, current_time=0):
        """Update turtle position and submersion state."""
        self.x += self.speed * speed_multiplier

        # Wrap around screen
        if self.speed > 0 and self.x > SCREEN_WIDTH + self.width:
            self.x = -self.width
        elif self.speed < 0 and self.x < -self.width:
            self.x = SCREEN_WIDTH + self.width

        # Update submersion cycle
        cycle_time = (current_time + self.cycle_offset) % (TURTLE_SUBMERGE_CYCLE + TURTLE_SUBMERGE_DURATION)
        self.is_submerged = cycle_time >= TURTLE_SUBMERGE_CYCLE

    def draw(self, surface):
        """Draw the turtle."""
        rect = pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )

        if self.is_submerged:
            # Draw submerged turtle (darker, barely visible)
            pygame.draw.rect(surface, COLOR_TURTLE_SUBMERGED, rect, border_radius=8)
            pygame.draw.rect(surface, COLOR_WATER_DEEP, rect, 2, border_radius=8)
        else:
            # Draw visible turtle
            pygame.draw.rect(surface, COLOR_TURTLE, rect, border_radius=8)
            pygame.draw.rect(surface, COLOR_TURTLE_SHELL, rect, 3, border_radius=8)

            # Draw shell pattern
            shell_rect = pygame.Rect(
                self.x - self.width // 2 + 6,
                self.y - self.height // 2 + 6,
                self.width - 12,
                self.height - 12
            )
            pygame.draw.rect(surface, COLOR_TURTLE_SHELL, shell_rect, border_radius=4)

            # Draw turtle eyes (when visible)
            eye_size = 4
            eye_y = self.y - self.height // 4
            for eye_x in [self.x - self.width // 4, self.x + self.width // 4]:
                pygame.draw.circle(surface, (255, 255, 255), (int(eye_x), int(eye_y)), eye_size)

    def get_rect(self):
        """Get collision rect."""
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )


class Platform:
    """Wrapper for log or turtle platforms."""

    def __init__(self, platform_type, row, x, size, speed, cycle_offset=0):
        self.platform_type = platform_type
        if platform_type == 'log':
            self.entity = Log(row, x, size, speed)
        else:
            self.entity = Turtle(row, x, size, speed, cycle_offset)

    def update(self, speed_multiplier=1.0, current_time=0):
        """Update platform."""
        if self.platform_type == 'turtle':
            self.entity.update(speed_multiplier, current_time)
        else:
            self.entity.update(speed_multiplier)

    def draw(self, surface):
        """Draw platform."""
        self.entity.draw(surface)

    def get_rect(self):
        """Get collision rect."""
        return self.entity.get_rect()

    @property
    def speed(self):
        return self.entity.speed

    @property
    def is_submerged(self):
        return getattr(self.entity, 'is_submerged', False)


class Lane:
    """A horizontal lane containing platforms."""

    def __init__(self, row, speed, platform_type, size, spacing):
        self.row = row
        self.base_speed = speed
        self.platform_type = platform_type
        self.platforms = []

        # Create platforms evenly spaced
        num_platforms = 3
        for i in range(num_platforms):
            x = (i * spacing * GRID_SIZE) % SCREEN_WIDTH
            # Add cycle offset for turtles so they don't all submerge at once
            cycle_offset = i * 500 if platform_type == 'turtle' else 0
            self.platforms.append(Platform(platform_type, row, x, size, speed, cycle_offset))

    def update(self, speed_multiplier=1.0, current_time=0):
        """Update all platforms in lane."""
        for platform in self.platforms:
            platform.update(speed_multiplier, current_time)

    def draw(self, surface):
        """Draw all platforms in lane."""
        for platform in self.platforms:
            platform.draw(surface)

    def check_collision(self, frog_rect):
        """Check if frog collides with any surface platform."""
        for platform in self.platforms:
            if platform.get_rect().colliderect(frog_rect):
                if not platform.is_submerged:
                    return platform
        return None
