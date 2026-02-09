"""Game state and river log physics logic for Vector Frog River Log Jump."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Vec2:
    x: float
    y: float


class Frog:
    def __init__(self, x: float, y: float):
        self.pos = Vec2(x, y)
        self.width = 32
        self.height = 32
        self.alive = True
        self.finished = False
        self.on_log = False
        self.current_log: Optional['Log'] = None
        self.move_cooldown = 0.0
        self.hop_offset = 0.0
        self.hop_direction = 1

    def update(self, dt: float):
        if self.move_cooldown > 0:
            self.move_cooldown -= dt

        # Hopping animation
        self.hop_offset += dt * 10 * self.hop_direction
        if self.hop_offset > 3:
            self.hop_direction = -1
        elif self.hop_offset < 0:
            self.hop_offset = 0
            self.hop_direction = 1

        # Move with log if on one
        if self.on_log and self.current_log:
            self.pos.x += self.current_log.speed * dt

    def jump(self, direction: str):
        if self.move_cooldown > 0 or not self.alive or self.finished:
            return

        grid_size = 40
        if direction == 'up':
            self.pos.y -= grid_size
        elif direction == 'down':
            self.pos.y += grid_size
        elif direction == 'left':
            self.pos.x -= grid_size
        elif direction == 'right':
            self.pos.x += grid_size

        self.move_cooldown = 0.15
        self.on_log = False
        self.current_log = None


class Log:
    def __init__(self, x: float, y: float, width: int, speed: float):
        self.pos = Vec2(x, y)
        self.width = width
        self.height = 40
        self.speed = speed

    def update(self, dt: float):
        self.pos.x += self.speed * dt

    def get_rect(self):
        return (self.pos.x, self.pos.y, self.width, self.height)


class GameState:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.grid_size = 40
        self.reset()

    def reset(self):
        # Frog starts at bottom center
        start_x = (self.width // self.grid_size // 2) * self.grid_size
        start_y = (self.height // self.grid_size - 1) * self.grid_size
        self.frog = Frog(start_x, start_y)

        self.score = 0
        self.game_over = False
        self.win = False
        self.lives = 3

        # Game areas
        self.grass_rows = [14, 13]  # Bottom and top safe zones
        self.river_rows = list(range(1, 13))  # Middle 12 rows are river

        # Create logs for each river row
        self.logs: List[Log] = []
        self._init_logs()

    def _init_logs(self):
        # Each row has logs moving in alternating directions
        log_configs = [
            # (row, width, speed, count, spacing)
            (1, 80, 80, 3, 280),
            (2, 120, -100, 2, 350),
            (3, 60, 60, 4, 220),
            (4, 100, -80, 3, 300),
            (5, 80, 100, 3, 280),
            (6, 140, -60, 2, 400),
            (7, 60, 70, 4, 220),
            (8, 100, -90, 3, 300),
            (9, 80, 80, 3, 280),
            (10, 120, -70, 2, 350),
            (11, 60, 90, 4, 220),
            (12, 100, -80, 3, 300),
        ]

        for row, width, speed, count, spacing in log_configs:
            y = row * self.grid_size
            for i in range(count):
                x = i * spacing + (row * 37) % 100
                self.logs.append(Log(x, y, width, speed))

    def update(self, dt: float):
        if self.game_over:
            return

        # Update logs
        for log in self.logs:
            log.update(dt)
            # Wrap logs around screen
            if log.speed > 0 and log.pos.x > self.width:
                log.pos.x = -log.width
            elif log.speed < 0 and log.pos.x + log.width < 0:
                log.pos.x = self.width

        # Update frog
        self.frog.update(dt)

        # Check frog position
        frog_row = int(self.frog.pos.y // self.grid_size)
        frog_center = self.frog.pos.x + self.frog.width / 2

        # Check win condition (reached top grass)
        if frog_row >= 14:
            self.frog.finished = True
            self.score += 500
            self.win = True
            self.game_over = True
            return

        # Check bounds
        if self.frog.pos.x < 0 or self.frog.pos.x + self.frog.width > self.width:
            self._lose_life()
            return

        # Check if in river area
        if 1 <= frog_row <= 12:
            # Must be on a log
            on_any_log = False
            frog_rect = (
                self.frog.pos.x,
                self.frog.pos.y,
                self.frog.width,
                self.frog.height
            )

            for log in self.logs:
                log_rect = log.get_rect()
                if self._rects_collide(frog_rect, log_rect):
                    on_any_log = True
                    self.frog.on_log = True
                    self.frog.current_log = log
                    break

            if not on_any_log:
                self._lose_life()
                return

    def _lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.frog.alive = False
            self.score = 0
            self.game_over = True
        else:
            # Reset frog position
            start_x = (self.width // self.grid_size // 2) * self.grid_size
            start_y = (self.height // self.grid_size - 1) * self.grid_size
            self.frog.pos.x = start_x
            self.frog.pos.y = start_y
            self.frog.on_log = False
            self.frog.current_log = None

    def jump(self, direction: str):
        if not self.game_over:
            self.frog.jump(direction)
            # Award points for forward movement
            if direction == 'up':
                self.score += 10

    def _rects_collide(self, r1, r2) -> bool:
        return (r1[0] < r2[0] + r2[2] and
                r1[0] + r1[2] > r2[0] and
                r1[1] < r2[1] + r2[3] and
                r1[1] + r1[3] > r2[1])
