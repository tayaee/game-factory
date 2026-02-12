"""Game entities for Battle City Base Defense."""

import pygame
import random
import math
from typing import List, Optional, Tuple
from config import *


class Direction:
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class Bullet:
    def __init__(self, x: float, y: float, direction: Tuple[int, int], speed: float, owner: str):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.owner = owner  # "player" or "enemy"
        self.alive = True

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - BULLET_SIZE // 2),
            int(self.y - BULLET_SIZE // 2),
            BULLET_SIZE,
            BULLET_SIZE
        )

    def update(self):
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed

    def is_on_screen(self) -> bool:
        return (GRID_OFFSET_X <= self.x <= GRID_OFFSET_X + GRID_COLS * CELL_SIZE and
                GRID_OFFSET_Y <= self.y <= GRID_OFFSET_Y + GRID_ROWS * CELL_SIZE)


class Tank:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.direction = Direction.UP
        self.cooldown = 0
        self.alive = True

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - PLAYER_SIZE // 2),
            int(self.y - PLAYER_SIZE // 2),
            PLAYER_SIZE,
            PLAYER_SIZE
        )

    def get_center(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def can_shoot(self) -> bool:
        return self.cooldown == 0

    def shoot(self) -> Optional[Bullet]:
        if not self.can_shoot():
            return None
        self.cooldown = PLAYER_COOLDOWN
        return Bullet(self.x, self.y, self.direction, PLAYER_BULLET_SPEED, "player")

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1


class Player(Tank):
    def __init__(self):
        super().__init__(
            GRID_OFFSET_X + 6 * CELL_SIZE + CELL_SIZE // 2,
            GRID_OFFSET_Y + 12 * CELL_SIZE + CELL_SIZE // 2
        )
        self.lives = PLAYER_MAX_LIVES
        self.invincible = 0
        self.bullets: List[Bullet] = []

    def move(self, dx: int, dy: int, grid):
        if not self.alive:
            return

        new_x = self.x + dx * PLAYER_SPEED
        new_y = self.y + dy * PLAYER_SPEED

        if self._can_move_to(new_x, new_y, grid):
            self.x = new_x
            self.y = new_y

        if dx != 0 or dy != 0:
            if dx > 0:
                self.direction = Direction.RIGHT
            elif dx < 0:
                self.direction = Direction.LEFT
            elif dy > 0:
                self.direction = Direction.DOWN
            elif dy < 0:
                self.direction = Direction.UP

    def _can_move_to(self, x: float, y: float, grid) -> bool:
        # Check boundaries
        half_size = PLAYER_SIZE // 2
        left = int((x - half_size) // CELL_SIZE)
        right = int((x + half_size - 1) // CELL_SIZE)
        top = int((y - half_size) // CELL_SIZE)
        bottom = int((y + half_size - 1) // CELL_SIZE)

        if not (0 <= left < GRID_COLS and 0 <= right < GRID_COLS and
                0 <= top < GRID_ROWS and 0 <= bottom < GRID_ROWS):
            return False

        # Check each corner
        corners = [(left, top), (right, top), (left, bottom), (right, bottom)]
        for cx, cy in corners:
            if not grid.is_passable(cx, cy):
                return False

        return True

    def update(self, grid):
        if self.invincible > 0:
            self.invincible -= 1
        super().update()

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.is_on_screen():
                self.bullets.remove(bullet)

    def respawn(self):
        self.x = GRID_OFFSET_X + 6 * CELL_SIZE + CELL_SIZE // 2
        self.y = GRID_OFFSET_Y + 12 * CELL_SIZE + CELL_SIZE // 2
        self.direction = Direction.UP
        self.invincible = 120


class Enemy(Tank):
    def __init__(self, enemy_type: int = ENEMY_NORMAL):
        spawn_x = random.choice([0, 6, 12])
        super().__init__(
            GRID_OFFSET_X + spawn_x * CELL_SIZE + CELL_SIZE // 2,
            GRID_OFFSET_Y + CELL_SIZE // 2
        )
        self.enemy_type = enemy_type
        self.speed = ENEMY_SPEED
        self.move_timer = 0
        self.bullets: List[Bullet] = []

        if enemy_type == ENEMY_FAST:
            self.speed = ENEMY_SPEED * 1.5
        elif enemy_type == ENEMY_POWER:
            self.bullet_speed = PLAYER_BULLET_SPEED * 1.5
        else:
            self.bullet_speed = ENEMY_BULLET_SPEED

    def shoot(self) -> Optional[Bullet]:
        if not self.can_shoot():
            return None
        self.cooldown = ENEMY_COOLDOWN
        return Bullet(self.x, self.y, self.direction, self.bullet_speed, "enemy")

    def get_score_value(self) -> int:
        scores = {
            ENEMY_NORMAL: SCORE_ENEMY_NORMAL,
            ENEMY_FAST: SCORE_ENEMY_FAST,
            ENEMY_POWER: SCORE_ENEMY_POWER,
            ENEMY_ARMOR: SCORE_ENEMY_ARMOR
        }
        return scores.get(self.enemy_type, SCORE_ENEMY_NORMAL)

    def get_color(self):
        colors = {
            ENEMY_NORMAL: COLOR_ENEMY,
            ENEMY_FAST: COLOR_ENEMY_FAST,
            ENEMY_POWER: COLOR_ENEMY_POWER,
            ENEMY_ARMOR: COLOR_ENEMY_ARMOR
        }
        return colors.get(self.enemy_type, COLOR_ENEMY)

    def update_ai(self, grid, player_pos: Tuple[float, float]):
        self.move_timer += 1

        if self.move_timer >= ENEMY_MOVE_CHANGE_INTERVAL:
            self.move_timer = 0
            # Random direction change
            directions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
            self.direction = random.choice(directions)
        else:
            # Continue in current direction
            pass

        # Try to move
        new_x = self.x + self.direction[0] * self.speed
        new_y = self.y + self.direction[1] * self.speed

        if not self._can_move_to(new_x, new_y, grid):
            # Change direction if blocked
            directions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
            random.shuffle(directions)
            for d in directions:
                test_x = self.x + d[0] * self.speed
                test_y = self.y + d[1] * self.speed
                if self._can_move_to(test_x, test_y, grid):
                    self.direction = d
                    self.x = test_x
                    self.y = test_y
                    break
        else:
            self.x = new_x
            self.y = new_y

        super().update()

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.is_on_screen():
                self.bullets.remove(bullet)

    def _can_move_to(self, x: float, y: float, grid) -> bool:
        half_size = PLAYER_SIZE // 2
        left = int((x - half_size) // CELL_SIZE)
        right = int((x + half_size - 1) // CELL_SIZE)
        top = int((y - half_size) // CELL_SIZE)
        bottom = int((y + half_size - 1) // CELL_SIZE)

        if not (0 <= left < GRID_COLS and 0 <= right < GRID_COLS and
                0 <= top < GRID_ROWS and 0 <= bottom < GRID_ROWS):
            return False

        corners = [(left, top), (right, top), (left, bottom), (right, bottom)]
        for cx, cy in corners:
            if not grid.is_passable(cx, cy):
                return False

        return True


class Base:
    def __init__(self):
        self.grid_x = 6
        self.grid_y = 12
        self.alive = True
        self.hp = 1

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            GRID_OFFSET_X + self.grid_x * CELL_SIZE + 2,
            GRID_OFFSET_Y + self.grid_y * CELL_SIZE + 2,
            CELL_SIZE - 4,
            CELL_SIZE - 4
        )

    def damage(self):
        self.hp -= 1
        if self.hp <= 0:
            self.alive = False


class Grid:
    # Tile types
    EMPTY = 0
    BRICK = 1
    STEEL = 2
    WATER = 3

    def __init__(self):
        self.tiles = [[self.EMPTY for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]
        self._setup_level()

    def _setup_level(self):
        # Brick wall clusters
        brick_clusters = [
            # Top area walls
            (1, 1, 2, 2), (10, 1, 2, 2),
            # Middle barriers
            (2, 4, 3, 2), (8, 4, 3, 2),
            # Side defenses
            (0, 6, 1, 3), (12, 6, 1, 3),
            # Center area
            (4, 7, 2, 2), (7, 7, 2, 2),
            # Base protection (partial - leave gap for player)
            (5, 11, 3, 1),
        ]

        for x, y, w, h in brick_clusters:
            for i in range(w):
                for j in range(h):
                    if 0 <= x + i < GRID_COLS and 0 <= y + j < GRID_ROWS:
                        self.tiles[x + i][y + j] = self.BRICK

        # Steel walls (indestructible)
        steel_positions = [
            (2, 2), (10, 2),
            (5, 5), (7, 5),
            (2, 8), (10, 8),
        ]

        for x, y in steel_positions:
            if 0 <= x < GRID_COLS and 0 <= y < GRID_ROWS:
                self.tiles[x][y] = self.STEEL

        # Water (impassable for tanks, bullets fly over)
        water_clusters = [
            (4, 3, 2, 3),
            (7, 3, 2, 3),
        ]

        for x, y, w, h in water_clusters:
            for i in range(w):
                for j in range(h):
                    if 0 <= x + i < GRID_COLS and 0 <= y + j < GRID_ROWS:
                        self.tiles[x + i][y + j] = self.WATER

    def is_passable(self, grid_x: int, grid_y: int) -> bool:
        if not (0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS):
            return False
        tile = self.tiles[grid_x][grid_y]
        return tile == self.EMPTY

    def is_bullet_passable(self, grid_x: int, grid_y: int) -> bool:
        if not (0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS):
            return False
        tile = self.tiles[grid_x][grid_y]
        return tile == self.EMPTY or tile == self.WATER

    def is_destructible(self, grid_x: int, grid_y: int) -> bool:
        if not (0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS):
            return False
        return self.tiles[grid_x][grid_y] == self.BRICK

    def destroy_tile(self, grid_x: int, grid_y: int):
        if 0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS:
            if self.tiles[grid_x][grid_y] == self.BRICK:
                self.tiles[grid_x][grid_y] = self.EMPTY

    def get_tile_rect(self, grid_x: int, grid_y: int) -> pygame.Rect:
        return pygame.Rect(
            GRID_OFFSET_X + grid_x * CELL_SIZE,
            GRID_OFFSET_Y + grid_y * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
