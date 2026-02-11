"""
Vector Lode Runner Gold Collect
Navigate platforms and dig traps to collect all gold pieces while avoiding guards.
"""

import pygame
import random
from typing import List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


# Constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 60

# Grid settings
GRID_WIDTH = 20
GRID_HEIGHT = 15
TILE_SIZE = 32

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_BRICK = (139, 69, 19)
COLOR_BRICK_DARK = (100, 50, 15)
COLOR_LADDER = (160, 82, 45)
COLOR_LADDER_LIGHT = (200, 120, 80)
COLOR_ROPE = (180, 140, 100)
COLOR_GOLD = (255, 215, 0)
COLOR_GOLD_SHINE = (255, 235, 100)
COLOR_PLAYER = (50, 150, 255)
COLOR_GUARD = (255, 80, 80)
COLOR_EXIT = (50, 255, 50)
COLOR_EXIT_HIDDEN = (100, 100, 100)
COLOR_HOLE = (80, 40, 10)
COLOR_HOLE_EDGE = (60, 30, 5)

# Physics
GRAVITY = 0.5
MAX_FALL_SPEED = 8
CLIMB_SPEED = 3
MOVE_SPEED = 3
GUARD_SPEED = 2

# Game mechanics
DIG_DURATION = 5000  # 5 seconds in milliseconds
TRAP_DURATION = 4000  # 4 seconds in milliseconds
DIG_COOLDOWN = 1000  # 1 second cooldown

# Scoring
SCORE_GOLD = 50
SCORE_TRAP_ENEMY = 20
SCORE_LEVEL_COMPLETE = 500
SCORE_GAME_OVER = -100


class TileType(Enum):
    EMPTY = 0
    BRICK = 1
    LADDER = 2
    ROPE = 3
    HOLE = 4


@dataclass
class Hole:
    grid_x: int
    grid_y: int
    create_time: int
    regenerating: bool = False


@dataclass
class TrappedGuard:
    guard: 'Guard'
    trap_time: int
    hole_x: int
    hole_y: int


class Entity:
    """Base class for all game entities."""

    def __init__(self, grid_x: int, grid_y: int):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * TILE_SIZE + TILE_SIZE // 2
        self.y = grid_y * TILE_SIZE
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.width = 24
        self.height = 28
        self.on_ground = False
        self.on_ladder = False
        self.on_rope = False
        self.facing_right = True

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - self.width // 2),
            int(self.y - self.height + 4),
            self.width,
            self.height
        )

    def get_center(self) -> Tuple[int, int]:
        return (int(self.x), int(self.y - self.height // 2))

    def update_grid_pos(self):
        self.grid_x = int(self.x // TILE_SIZE)
        self.grid_y = int((self.y + self.height // 2) // TILE_SIZE)


class Player(Entity):
    """Player-controlled character."""

    def __init__(self, grid_x: int, grid_y: int):
        super().__init__(grid_x, grid_y)
        self.dig_cooldown = 0
        self.alive = True

    def update(self, dt: float, keys, level: 'Level') -> None:
        if not self.alive:
            return

        self.vel_x = 0
        self.vel_y = 0

        # Update cooldown
        if self.dig_cooldown > 0:
            self.dig_cooldown -= int(dt * 1000)

        # Get current tile info
        gx, gy = self.grid_x, self.grid_y
        tile_below = level.get_tile(gx, gy + 1) if gy + 1 < GRID_HEIGHT else TileType.EMPTY
        tile_current = level.get_tile(gx, gy)
        tile_above = level.get_tile(gx, gy - 1) if gy > 0 else TileType.EMPTY

        self.on_ladder = tile_current == TileType.LADDER
        self.on_rope = tile_current == TileType.ROPE
        self.on_ground = (tile_below == TileType.BRICK or
                         tile_below == TileType.LADDER or
                         self.y >= (gy + 1) * TILE_SIZE - 5)

        # Horizontal movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -MOVE_SPEED
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = MOVE_SPEED
            self.facing_right = True

        # Vertical movement
        if self.on_ladder:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.vel_y = -CLIMB_SPEED
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.vel_y = CLIMB_SPEED
        elif self.on_rope:
            # Can only go down from rope
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.vel_y = CLIMB_SPEED
        else:
            # Apply gravity when not on ladder/rope/ground
            if not self.on_ground:
                self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)

        # Apply velocity with collision
        self._apply_movement(level)

    def dig(self, direction: int, level: 'Level') -> Optional[int]:
        """Dig a hole in the given direction (-1 left, 1 right). Returns hole grid_x if dug."""
        if self.dig_cooldown > 0:
            return None

        target_x = self.grid_x + direction
        target_y = self.grid_y + 1

        if (0 <= target_x < GRID_WIDTH and 0 <= target_y < GRID_HEIGHT):
            if level.get_tile(target_x, target_y) == TileType.BRICK:
                # Check if there's something below the brick (need support)
                if target_y + 1 < GRID_HEIGHT:
                    below = level.get_tile(target_x, target_y + 1)
                    if below in [TileType.BRICK, TileType.LADDER]:
                        level.dig_hole(target_x, target_y)
                        self.dig_cooldown = DIG_COOLDOWN
                        return target_x

        return None

    def _apply_movement(self, level: 'Level') -> None:
        # Horizontal movement with wall collision
        new_x = self.x + self.vel_x
        test_grid_x = int(new_x // TILE_SIZE)

        # Check horizontal collision
        if self.vel_x > 0:  # Moving right
            right_edge = int((new_x + self.width // 2) // TILE_SIZE)
            if right_edge < GRID_WIDTH:
                tile_right = level.get_tile(right_edge, self.grid_y)
                if tile_right != TileType.BRICK and tile_right != TileType.HOLE:
                    self.x = new_x
        elif self.vel_x < 0:  # Moving left
            left_edge = int((new_x - self.width // 2) // TILE_SIZE)
            if left_edge >= 0:
                tile_left = level.get_tile(left_edge, self.grid_y)
                if tile_left != TileType.BRICK and tile_left != TileType.HOLE:
                    self.x = new_x

        # Vertical movement
        new_y = self.y + self.vel_y
        test_grid_y = int((new_y + self.height // 2) // TILE_SIZE)

        # Check vertical collision
        if self.vel_y > 0:  # Falling down
            if test_grid_y < GRID_HEIGHT:
                tile_below = level.get_tile(self.grid_x, test_grid_y)
                if tile_below == TileType.BRICK:
                    self.y = test_grid_y * TILE_SIZE
                    self.vel_y = 0
                elif tile_below == TileType.LADDER or tile_below == TileType.EMPTY:
                    self.y = min(new_y, test_grid_y * TILE_SIZE + TILE_SIZE // 2)
            else:
                self.y = new_y
        elif self.vel_y < 0:  # Climbing up
            tile_above = level.get_tile(self.grid_x, test_grid_y)
            if tile_above != TileType.BRICK:
                self.y = new_y

        # Clamp to screen
        self.x = max(TILE_SIZE // 2, min(SCREEN_WIDTH - TILE_SIZE // 2, self.x))
        self.y = max(0, min(SCREEN_HEIGHT, self.y))

        self.update_grid_pos()

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return

        rect = self.get_rect()

        # Body
        pygame.draw.rect(surface, COLOR_PLAYER,
                        (rect.x + 4, rect.y + 8, rect.width - 8, rect.height - 12))

        # Head
        head_center = (rect.centerx, rect.y + 8)
        pygame.draw.circle(surface, COLOR_PLAYER, head_center, 7)

        # Eyes (show direction)
        eye_offset = 3 if self.facing_right else -3
        pygame.draw.circle(surface, COLOR_WHITE,
                          (head_center[0] + eye_offset, head_center[1] - 1), 2)
        pygame.draw.circle(surface, COLOR_BLACK,
                          (head_center[0] + eye_offset, head_center[1] - 1), 1)

        # Arms/Legs indication
        if self.on_ladder:
            # Climbing pose
            pygame.draw.line(surface, COLOR_PLAYER,
                           (rect.left + 6, rect.centery),
                           (rect.right - 6, rect.y + 12), 3)
        elif self.vel_y > 1:
            # Falling pose
            pygame.draw.line(surface, COLOR_PLAYER,
                           (rect.left + 4, rect.bottom - 4),
                           (rect.left + 8, rect.bottom), 3)
            pygame.draw.line(surface, COLOR_PLAYER,
                           (rect.right - 4, rect.bottom - 4),
                           (rect.right - 8, rect.bottom), 3)


class Guard(Entity):
    """AI-controlled enemy that chases the player."""

    def __init__(self, grid_x: int, grid_y: int):
        super().__init__(grid_x, grid_y)
        self.patrol_dir = 1
        self.state = 'chase'  # chase, trapped, respawn
        self.respawn_timer = 0
        self.alive = True

    def update(self, dt: float, level: 'Level', player: Player) -> None:
        if self.state == 'respawn':
            self.respawn_timer -= int(dt * 1000)
            if self.respawn_timer <= 0:
                self.state = 'chase'
                self.alive = True
            return

        if not self.alive:
            return

        # Get current tile info
        gx, gy = self.grid_x, self.grid_y
        tile_below = level.get_tile(gx, gy + 1) if gy + 1 < GRID_HEIGHT else TileType.EMPTY
        tile_current = level.get_tile(gx, gy)

        self.on_ladder = tile_current == TileType.LADDER
        self.on_ground = (tile_below == TileType.BRICK or
                         tile_below == TileType.LADDER or
                         self.y >= (gy + 1) * TILE_SIZE - 5)

        # Simple AI: chase player
        dx = player.x - self.x
        dy = player.y - self.y

        # Horizontal movement
        if abs(dx) > 5:
            move_x = GUARD_SPEED if dx > 0 else -GUARD_SPEED
            self.vel_x = move_x
            self.facing_right = dx > 0
        else:
            self.vel_x = 0

        # Vertical movement on ladders
        if self.on_ladder:
            if dy < -10:
                self.vel_y = -CLIMB_SPEED * 0.7
            elif dy > 10:
                self.vel_y = CLIMB_SPEED * 0.7
            else:
                self.vel_y = 0
        else:
            # Apply gravity when not on ladder
            if not self.on_ground:
                self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)

        # Apply movement
        self._apply_movement(level)

    def _apply_movement(self, level: 'Level') -> None:
        # Similar to player but simpler
        new_x = self.x + self.vel_x

        # Check horizontal bounds
        if TILE_SIZE // 2 <= new_x <= SCREEN_WIDTH - TILE_SIZE // 2:
            test_x = int(new_x // TILE_SIZE)
            if self.vel_x > 0:
                right_edge = int((new_x + self.width // 2) // TILE_SIZE)
                tile_right = level.get_tile(right_edge, self.grid_y)
                if tile_right not in [TileType.BRICK, TileType.HOLE]:
                    self.x = new_x
            elif self.vel_x < 0:
                left_edge = int((new_x - self.width // 2) // TILE_SIZE)
                tile_left = level.get_tile(left_edge, self.grid_y)
                if tile_left not in [TileType.BRICK, TileType.HOLE]:
                    self.x = new_x

        # Vertical movement
        new_y = self.y + self.vel_y
        test_grid_y = int((new_y + self.height // 2) // TILE_SIZE)

        if self.vel_y > 0:
            if test_grid_y < GRID_HEIGHT:
                tile_below = level.get_tile(self.grid_x, test_grid_y)
                if tile_below == TileType.BRICK:
                    self.y = test_grid_y * TILE_SIZE
                elif tile_below != TileType.HOLE:
                    self.y = min(new_y, test_grid_y * TILE_SIZE + TILE_SIZE // 2)
            else:
                self.y = new_y
        elif self.vel_y < 0:
            tile_above = level.get_tile(self.grid_x, test_grid_y)
            if tile_above != TileType.BRICK:
                self.y = new_y

        self.y = max(0, min(SCREEN_HEIGHT, self.y))
        self.update_grid_pos()

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive or self.state == 'respawn':
            return

        rect = self.get_rect()

        # Body (red)
        pygame.draw.rect(surface, COLOR_GUARD,
                        (rect.x + 4, rect.y + 8, rect.width - 8, rect.height - 12))

        # Head
        head_center = (rect.centerx, rect.y + 8)
        pygame.draw.circle(surface, COLOR_GUARD, head_center, 7)

        # Angry eyes
        eye_offset = 3 if self.facing_right else -3
        pygame.draw.circle(surface, COLOR_WHITE,
                          (head_center[0] + eye_offset, head_center[1]), 2)
        pygame.draw.circle(surface, COLOR_BLACK,
                          (head_center[0] + eye_offset, head_center[1]), 1)

        # Antenna
        pygame.draw.line(surface, COLOR_GUARD,
                        (rect.centerx, rect.y + 2),
                        (rect.centerx, rect.y - 4), 2)
        pygame.draw.circle(surface, COLOR_GUARD, (rect.centerx, rect.y - 5), 2)


class Gold:
    """Collectible gold piece."""

    def __init__(self, grid_x: int, grid_y: int):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * TILE_SIZE + TILE_SIZE // 2
        self.y = grid_y * TILE_SIZE + TILE_SIZE // 2
        self.collected = False
        self.anim_offset = random.random() * 6.28

    def get_rect(self) -> pygame.Rect:
        size = 16
        return pygame.Rect(int(self.x - size // 2), int(self.y - size // 2), size, size)

    def update(self, time_ms: int) -> None:
        # Gentle bobbing animation
        self.y = (self.grid_y * TILE_SIZE + TILE_SIZE // 2 +
                 3 * (1 + int((time_ms / 200 + self.anim_offset) * 3.14) % 2))

    def draw(self, surface: pygame.Surface) -> None:
        if self.collected:
            return

        rect = self.get_rect()

        # Gold coin shape
        pygame.draw.circle(surface, COLOR_GOLD, rect.center, 7)
        pygame.draw.circle(surface, COLOR_GOLD_SHINE, rect.center, 5)

        # Shine spot
        shine_x = rect.centerx - 2
        shine_y = rect.centery - 2
        pygame.draw.circle(surface, COLOR_WHITE, (shine_x, shine_y), 2)


class Level:
    """Game level with tiles, gold, and entities."""

    def __init__(self, level_num: int = 1):
        self.level_num = level_num
        self.tiles: List[List[TileType]] = []
        self.gold_pieces: List[Gold] = []
        self.guards: List[Guard] = []
        self.holes: List[Hole] = []
        self.trapped_guards: List[TrappedGuard] = []
        self.exit_pos: Tuple[int, int] = (GRID_WIDTH // 2, 0)
        self.exit_visible = False
        self.total_gold = 0
        self.collected_gold = 0

        self._generate_level()

    def get_tile(self, grid_x: int, grid_y: int) -> TileType:
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            return self.tiles[grid_y][grid_x]
        return TileType.EMPTY

    def set_tile(self, grid_x: int, grid_y: int, tile_type: TileType) -> None:
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            self.tiles[grid_y][grid_x] = tile_type

    def dig_hole(self, grid_x: int, grid_y: int) -> None:
        self.set_tile(grid_x, grid_y, TileType.HOLE)
        self.holes.append(Hole(grid_x, grid_y, pygame.time.get_ticks()))

    def _generate_level(self) -> None:
        """Generate a level with platforms, ladders, gold, and guards."""
        # Initialize empty level
        self.tiles = [[TileType.EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

        # Border walls
        for y in range(GRID_HEIGHT):
            self.tiles[y][0] = TileType.BRICK
            self.tiles[y][GRID_WIDTH - 1] = TileType.BRICK

        # Floor
        for x in range(GRID_WIDTH):
            self.tiles[GRID_HEIGHT - 1][x] = TileType.BRICK

        # Platform layouts based on level
        platforms = [
            (2, 5, 10),    # y, x_start, x_end
            (5, 2, 8),
            (5, 12, 18),
            (8, 1, 9),
            (8, 11, 19),
            (11, 3, 7),
            (11, 13, 17),
        ]

        for py, px_start, px_end in platforms:
            for x in range(px_start, px_end + 1):
                self.tiles[py][x] = TileType.BRICK

        # Ladders
        ladder_positions = [
            (5, 3), (15, 3),
            (3, 6), (17, 6),
            (9, 9),
            (5, 12), (15, 12),
        ]

        for lx, ly in ladder_positions:
            for y in range(ly, GRID_HEIGHT - 1):
                if self.tiles[y][lx] == TileType.BRICK:
                    # Carve through brick
                    self.tiles[y][lx] = TileType.LADDER
                elif self.tiles[y][lx] == TileType.EMPTY:
                    self.tiles[y][lx] = TileType.LADDER

        # Add some ropes
        for x in range(2, GRID_WIDTH - 5, 5):
            if self.tiles[3][x] != TileType.BRICK and self.tiles[3][x] != TileType.LADDER:
                for i in range(4):
                    if x + i < GRID_WIDTH:
                        self.tiles[3][x + i] = TileType.ROPE

        # Place gold
        gold_positions = [
            (3, 2), (17, 2),
            (7, 4), (13, 4),
            (4, 7), (16, 7),
            (8, 10), (12, 10),
            (5, 5), (15, 5),
            (10, 7),
            (6, 9), (14, 9),
        ]

        for gx, gy in gold_positions:
            if self.tiles[gy][gx] != TileType.BRICK:
                self.gold_pieces.append(Gold(gx, gy))
                self.total_gold += 1

        # Place guards
        guard_positions = [(4, 1), (16, 1), (10, 4)]
        for gx, gy in guard_positions:
            self.guards.append(Guard(gx, gy))

        # Exit position (top center)
        self.exit_pos = (GRID_WIDTH // 2, 0)

    def update(self, dt: float, time_ms: int) -> None:
        """Update holes and trapped guards."""
        # Update holes
        for hole in self.holes[:]:
            age = time_ms - hole.create_time
            if age >= DIG_DURATION:
                # Check if guard is trapped
                trapped = [tg for tg in self.trapped_guards
                          if tg.hole_x == hole.grid_x and tg.hole_y == hole.grid_y]
                if not trapped:
                    # Regenerate the brick
                    self.set_tile(hole.grid_x, hole.grid_y, TileType.BRICK)
                    self.holes.remove(hole)

        # Update trapped guards
        for tg in self.trapped_guards[:]:
            if time_ms - tg.trap_time >= TRAP_DURATION:
                # Guard escapes - respawn at top
                tg.guard.state = 'respawn'
                tg.guard.respawn_timer = 3000
                tg.guard.grid_x = random.randint(2, GRID_WIDTH - 3)
                tg.guard.grid_y = 1
                tg.guard.x = tg.guard.grid_x * TILE_SIZE + TILE_SIZE // 2
                tg.guard.y = tg.guard.grid_y * TILE_SIZE
                self.trapped_guards.remove(tg)

        # Update gold
        for gold in self.gold_pieces:
            gold.update(time_ms)

        # Check if all gold collected
        if self.collected_gold >= self.total_gold and not self.exit_visible:
            self.exit_visible = True

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all level elements."""
        # Draw tiles
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                tile = self.tiles[y][x]
                px = x * TILE_SIZE
                py = y * TILE_SIZE

                if tile == TileType.BRICK:
                    self._draw_brick(surface, px, py)
                elif tile == TileType.LADDER:
                    self._draw_ladder(surface, px, py)
                elif tile == TileType.ROPE:
                    self._draw_rope(surface, px, py)
                elif tile == TileType.HOLE:
                    self._draw_hole(surface, px, py)

        # Draw exit
        exit_x = self.exit_pos[0] * TILE_SIZE
        exit_y = self.exit_pos[1] * TILE_SIZE
        if self.exit_visible:
            pygame.draw.rect(surface, COLOR_EXIT,
                           (exit_x + 4, exit_y, TILE_SIZE - 8, TILE_SIZE // 2))
            # Ladder rungs
            for i in range(3):
                y = exit_y + 4 + i * 8
                pygame.draw.line(surface, COLOR_BLACK,
                               (exit_x + 6, y), (exit_x + TILE_SIZE - 6, y), 2)
        else:
            pygame.draw.rect(surface, COLOR_EXIT_HIDDEN,
                           (exit_x + 8, exit_y + 4, TILE_SIZE - 16, 8))

        # Draw gold
        for gold in self.gold_pieces:
            gold.draw(surface)

    def _draw_brick(self, surface: pygame.Surface, x: int, y: int) -> None:
        pygame.draw.rect(surface, COLOR_BRICK, (x, y, TILE_SIZE, TILE_SIZE))
        # Brick pattern
        pygame.draw.rect(surface, COLOR_BRICK_DARK, (x, y, TILE_SIZE, TILE_SIZE), 1)
        pygame.draw.line(surface, COLOR_BRICK_DARK, (x, y + TILE_SIZE // 2),
                        (x + TILE_SIZE, y + TILE_SIZE // 2), 1)
        pygame.draw.line(surface, COLOR_BRICK_DARK, (x + TILE_SIZE // 2, y),
                        (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 1)

    def _draw_ladder(self, surface: pygame.Surface, x: int, y: int) -> None:
        # Side rails
        pygame.draw.line(surface, COLOR_LADDER, (x + 6, y), (x + 6, y + TILE_SIZE), 3)
        pygame.draw.line(surface, COLOR_LADDER, (x + TILE_SIZE - 6, y),
                        (x + TILE_SIZE - 6, y + TILE_SIZE), 3)
        # Rungs
        for i in range(4):
            ry = y + 6 + i * 7
            pygame.draw.line(surface, COLOR_LADDER_LIGHT, (x + 6, ry),
                           (x + TILE_SIZE - 6, ry), 2)

    def _draw_rope(self, surface: pygame.Surface, x: int, y: int) -> None:
        # Draw rope
        mid_y = y + TILE_SIZE // 2
        pygame.draw.line(surface, COLOR_ROPE, (x, mid_y), (x + TILE_SIZE, mid_y), 2)

    def _draw_hole(self, surface: pygame.Surface, x: int, y: int) -> None:
        pygame.draw.rect(surface, COLOR_HOLE, (x, y, TILE_SIZE, TILE_SIZE))
        # Edges showing where brick was
        for i in range(4):
            ey = y + i * 8
            pygame.draw.line(surface, COLOR_HOLE_EDGE, (x, ey), (x + 4, ey), 2)
            pygame.draw.line(surface, COLOR_HOLE_EDGE, (x + TILE_SIZE - 4, ey),
                           (x + TILE_SIZE, ey), 2)


class Game:
    """Main game controller."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Lode Runner Gold Collect")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.won = False
        self.level_complete = False

        # Fonts
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        # Game state
        self.score = 0
        self.lives = 3
        self.current_level = 1

        self.reset_game()

    def reset_game(self) -> None:
        """Reset to initial game state."""
        self.score = 0
        self.lives = 3
        self.current_level = 1
        self.game_over = False
        self.won = False
        self.level_complete = False
        self._load_level()

    def _load_level(self) -> None:
        """Load a new level."""
        self.level = Level(self.current_level)
        self.player = Player(2, GRID_HEIGHT - 2)
        self.level_complete = False

    def handle_input(self) -> None:
        """Handle keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                elif self.level_complete:
                    if event.key == pygame.K_SPACE:
                        self.current_level += 1
                        if self.current_level > 3:
                            self.won = True
                        else:
                            self._load_level()
                else:
                    # Dig controls
                    if event.key == pygame.K_z:
                        hole_x = self.player.dig(-1, self.level)
                        if hole_x is not None:
                            self.score += 0
                    elif event.key == pygame.K_x:
                        hole_x = self.player.dig(1, self.level)
                        if hole_x is not None:
                            self.score += 0

    def update(self, dt: float) -> None:
        """Update game state."""
        time_ms = pygame.time.get_ticks()

        if self.game_over or self.won or self.level_complete:
            return

        # Update level
        self.level.update(dt, time_ms)

        # Update player
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys, self.level)

        # Update guards
        for guard in self.level.guards:
            guard.update(dt, self.level, self.player)

        # Check gold collection
        player_rect = self.player.get_rect()
        for gold in self.level.gold_pieces:
            if not gold.collected and player_rect.colliderect(gold.get_rect()):
                gold.collected = True
                self.level.collected_gold += 1
                self.score += SCORE_GOLD

        # Check guard collisions
        for guard in self.level.guards:
            if guard.state == 'chase' and player_rect.colliderect(guard.get_rect()):
                self._player_death()

        # Check if guard falls in hole
        for guard in self.level.guards:
            if guard.state == 'chase':
                guard_tile = self.level.get_tile(guard.grid_x, guard.grid_y)
                if guard_tile == TileType.HOLE:
                    # Check if guard just fell in
                    already_trapped = any(tg.guard == guard for tg in self.level.trapped_guards)
                    if not already_trapped:
                        self.level.trapped_guards.append(
                            TrappedGuard(guard, time_ms, guard.grid_x, guard.grid_y))
                        self.score += SCORE_TRAP_ENEMY

        # Check exit reach
        if self.level.exit_visible:
            exit_rect = pygame.Rect(
                self.level.exit_pos[0] * TILE_SIZE,
                self.level.exit_pos[1] * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE // 2
            )
            if player_rect.colliderect(exit_rect):
                self.score += SCORE_LEVEL_COMPLETE
                self.level_complete = True

    def _player_death(self) -> None:
        """Handle player death."""
        self.lives -= 1
        self.score += SCORE_GAME_OVER

        if self.lives <= 0:
            self.game_over = True
            self.player.alive = False
        else:
            # Respawn player
            self.player = Player(2, GRID_HEIGHT - 2)

    def draw(self) -> None:
        """Draw all game elements."""
        self.screen.fill(COLOR_BLACK)

        # Draw level
        self.level.draw(self.screen)

        # Draw guards
        for guard in self.level.guards:
            guard.draw(self.screen)

        # Draw trapped guards (in holes)
        for tg in self.level.trapped_guards:
            gx = tg.hole_x * TILE_SIZE + TILE_SIZE // 2
            gy = tg.hole_y * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(self.screen, COLOR_GUARD, (gx, gy), 8)

        # Draw player
        self.player.draw(self.screen)

        # Draw UI
        self._draw_ui()

        # Draw overlays
        if self.game_over:
            self._draw_overlay("GAME OVER", f"Final Score: {self.score}", "Press R to Restart")
        elif self.won:
            self._draw_overlay("VICTORY!", f"Final Score: {self.score}", "Press R to Play Again")
        elif self.level_complete:
            level_text = f"Level {self.current_level} Complete!"
            self._draw_overlay(level_text, f"Score: {self.score}", "Press SPACE for Next Level")

        pygame.display.flip()

    def _draw_ui(self) -> None:
        """Draw user interface elements."""
        # Score
        score_text = self.font_small.render(f"SCORE: {self.score}", True, COLOR_WHITE)
        self.screen.blit(score_text, (10, 10))

        # Lives
        lives_text = self.font_small.render(f"LIVES: {self.lives}", True, COLOR_PLAYER)
        self.screen.blit(lives_text, (10, 40))

        # Level
        level_text = self.font_small.render(f"LEVEL: {self.current_level}", True, COLOR_GOLD)
        self.screen.blit(level_text, (10, 70))

        # Gold remaining
        gold_left = self.level.total_gold - self.level.collected_gold
        gold_text = self.font_small.render(f"GOLD: {gold_left}/{self.level.total_gold}",
                                          True, COLOR_GOLD)
        self.screen.blit(gold_text, (SCREEN_WIDTH - 120, 10))

        # Controls hint
        if self.level.collected_gold < self.level.total_gold:
            hint_text = self.font_small.render("Z: Dig Left | X: Dig Right", True, COLOR_WHITE)
            self.screen.blit(hint_text, (SCREEN_WIDTH - 220, 40))

    def _draw_overlay(self, title: str, subtitle: str, instruction: str) -> None:
        """Draw game overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title_color = COLOR_EXIT if self.won or self.level_complete else COLOR_GUARD
        title_text = self.font_large.render(title, True, title_color)
        subtitle_text = self.font_medium.render(subtitle, True, COLOR_WHITE)
        instr_text = self.font_small.render(instruction, True, COLOR_GOLD)

        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        instr_rect = instr_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
        self.screen.blit(instr_text, instr_rect)

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            self.handle_input()
            self.update(dt)
            self.draw()

        pygame.quit()


def main():
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
