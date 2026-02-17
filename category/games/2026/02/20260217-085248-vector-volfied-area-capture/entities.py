"""Game entities: Player, Boss, Sparks."""

import pygame
import random
import config
from pygame import Rect
from typing import List, Tuple


class Player:
    """The player's Shield craft."""

    def __init__(self, field_rect: Rect):
        self.field_rect = field_rect
        self.reset()

    def reset(self) -> None:
        """Reset player to starting position."""
        # Start at the middle of the top edge
        self.x = self.field_rect.centerx
        self.y = self.field_rect.top
        self.dx = 0
        self.dy = 0
        self.is_drawing = False
        self.trail: List[Tuple[int, int]] = []

    def set_direction(self, dx: int, dy: int) -> None:
        """Set movement direction."""
        self.dx = dx
        self.dy = dy

    def start_drawing(self) -> None:
        """Start drawing a trail."""
        if not self.is_drawing:
            self.is_drawing = True
            self.trail = [(self.x, self.y)]

    def stop_drawing(self) -> None:
        """Stop drawing a trail."""
        self.is_drawing = False

    def clear_trail(self) -> None:
        """Clear the current trail."""
        self.trail = []
        self.is_drawing = False

    def is_on_border(self, x: int, y: int) -> bool:
        """Check if position is on the field border."""
        return (x == self.field_rect.left or x == self.field_rect.right or
                y == self.field_rect.top or y == self.field_rect.bottom)

    def is_on_perimeter(self) -> bool:
        """Check if current position is on the field perimeter."""
        return self.is_on_border(self.x, self.y)

    def move(self, claimed_grid: List[List[bool]]) -> Tuple[bool, Rect]:
        """Move player and return (claimed_area, area_rect) if area claimed."""
        new_x = self.x + self.dx * config.PLAYER_SPEED
        new_y = self.y + self.dy * config.PLAYER_SPEED

        # Clamp to field bounds
        new_x = max(self.field_rect.left, min(self.field_rect.right, new_x))
        new_y = max(self.field_rect.top, min(self.field_rect.bottom, new_y))

        # If not moving, return
        if new_x == self.x and new_y == self.y:
            return False, None

        # Check if trying to enter claimed area
        grid_x = int((new_x - self.field_rect.x) // 2)
        grid_y = int((new_y - self.field_rect.y) // 2)

        if self.is_drawing:
            # When drawing, can only enter unclaimed space
            if claimed_grid and 0 <= grid_y < len(claimed_grid) and 0 <= grid_x < len(claimed_grid[0]):
                if claimed_grid[grid_y][grid_x]:
                    # Hit claimed area, stop drawing
                    self.clear_trail()
                    return False, None
        else:
            # When not drawing, can move on border or unclaimed
            if claimed_grid and 0 <= grid_y < len(claimed_grid) and 0 <= grid_x < len(claimed_grid[0]):
                if claimed_grid[grid_y][grid_x] and not self.is_on_border(new_x, new_y):
                    return False, None

        self.x = new_x
        self.y = new_y

        # Add to trail if drawing
        if self.is_drawing:
            self.trail.append((self.x, self.y))

        # Check if we returned to border while drawing
        claimed_area = None
        if self.is_drawing and self.is_on_border(self.x, self.y) and len(self.trail) > 2:
            claimed_area = self._calculate_claimed_area()
            self.clear_trail()

        return claimed_area is not None, claimed_area

    def _calculate_claimed_area(self) -> Rect:
        """Calculate the area claimed by the current trail."""
        if len(self.trail) < 3:
            return None

        # Simple area calculation using bounding box
        xs = [p[0] for p in self.trail]
        ys = [p[1] for p in self.trail]

        return Rect(
            min(xs),
            min(ys),
            max(xs) - min(xs),
            max(ys) - min(ys)
        )

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the player and trail."""
        # Draw trail
        if len(self.trail) > 1:
            pygame.draw.lines(surface, config.TRAIL_COLOR, False, self.trail, config.TRAIL_WIDTH)

        # Draw player as a diamond shape
        half_size = config.PLAYER_SIZE // 2
        points = [
            (self.x, self.y - half_size),
            (self.x + half_size, self.y),
            (self.x, self.y + half_size),
            (self.x - half_size, self.y)
        ]
        pygame.draw.polygon(surface, config.PLAYER_COLOR, points)

        # Draw center dot
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), 2)


class Boss:
    """The main boss entity that moves within unclaimed space."""

    def __init__(self, field_rect: Rect, claimed_regions: List[Rect]):
        self.field_rect = field_rect
        self.claimed_regions = claimed_regions
        self.reset()

    def reset(self) -> None:
        """Reset boss to center of unclaimed area."""
        self.x = self.field_rect.centerx
        self.y = self.field_rect.centery
        self.vx = random.choice([-1, 1]) * config.BOSS_BASE_SPEED
        self.vy = random.choice([-1, 1]) * config.BOSS_BASE_SPEED
        self.phase = 0

    def update(self, level: int, claimed_regions: List[Rect]) -> None:
        """Update boss position and behavior."""
        self.claimed_regions = claimed_regions
        speed = config.BOSS_BASE_SPEED + (level - 1) * 0.3

        # Change direction periodically
        self.phase += 0.02
        if random.random() < 0.01:
            self.vx = random.choice([-1, 1]) * speed
            self.vy = random.choice([-1, 1]) * speed

        # Wavy movement
        wobble = pygame.math.Vector2(
            random.uniform(-0.5, 0.5),
            random.uniform(-0.5, 0.5)
        )

        new_x = self.x + self.vx + wobble.x
        new_y = self.y + self.vy + wobble.y

        # Check if in claimed region
        in_claimed = False
        for region in self.claimed_regions:
            if region.collidepoint(new_x, new_y):
                in_claimed = True
                break

        # Bounce off walls and claimed areas
        if in_claimed or new_x <= self.field_rect.left or new_x >= self.field_rect.right:
            self.vx *= -1
        else:
            self.x = new_x

        if in_claimed or new_y <= self.field_rect.top or new_y >= self.field_rect.bottom:
            self.vy *= -1
        else:
            self.y = new_y

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the boss as a rotating cross."""
        size = config.BOSS_SIZE

        # Pulsing effect
        pulse = 1 + 0.2 * pygame.math.Vector2(self.phase).length()

        # Draw cross shape
        pygame.draw.line(
            surface,
            config.BOSS_COLOR,
            (self.x - size * pulse, self.y),
            (self.x + size * pulse, self.y),
            3
        )
        pygame.draw.line(
            surface,
            config.BOSS_COLOR,
            (self.x, self.y - size * pulse),
            (self.x, self.y + size * pulse),
            3
        )

        # Draw center
        pygame.draw.circle(surface, config.BOSS_COLOR, (int(self.x), int(self.y)), 4)

        # Draw glow
        glow_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surface,
            (*config.BOSS_COLOR, 50),
            (size * 2, size * 2),
            int(size * 1.5)
        )
        surface.blit(glow_surface, (self.x - size * 2, self.y - size * 2))

    def collides_with_trail(self, trail: List[Tuple[int, int]]) -> bool:
        """Check if boss collides with the player's trail."""
        if not trail:
            return False

        for point in trail:
            dist = ((self.x - point[0]) ** 2 + (self.y - point[1]) ** 2) ** 0.5
            if dist < config.BOSS_SIZE + config.TRAIL_WIDTH:
                return True
        return False

    def collides_with_player(self, player: Player) -> bool:
        """Check if boss collides with the player."""
        dist = ((self.x - player.x) ** 2 + (self.y - player.y) ** 2) ** 0.5
        return dist < config.BOSS_SIZE + config.PLAYER_SIZE


class Spark:
    """Small fast enemies that hunt the player."""

    def __init__(self, field_rect: Rect, start_side: str = None):
        self.field_rect = field_rect
        self.reset(start_side)

    def reset(self, start_side: str = None) -> None:
        """Reset spark to a random border position."""
        sides = ['top', 'bottom', 'left', 'right']
        if start_side:
            self.side = start_side
        else:
            self.side = random.choice(sides)

        self.speed = config.SPARK_BASE_SPEED

        if self.side == 'top':
            self.x = self.field_rect.left + 50
            self.y = self.field_rect.top
            self.direction = 1  # Moving right
        elif self.side == 'bottom':
            self.x = self.field_rect.right - 50
            self.y = self.field_rect.bottom
            self.direction = -1  # Moving left
        elif self.side == 'left':
            self.x = self.field_rect.left
            self.y = self.field_rect.top + 50
            self.direction = 1  # Moving down
        else:  # right
            self.x = self.field_rect.right
            self.y = self.field_rect.bottom - 50
            self.direction = -1  # Moving up

    def update(self, level: int, player_x: int, player_y: int) -> None:
        """Update spark position."""
        speed = self.speed + (level - 1) * 0.2

        if self.side in ['top', 'bottom']:
            self.x += self.direction * speed

            # Bounce at corners
            if self.x >= self.field_rect.right - 20:
                self.direction = -1
            elif self.x <= self.field_rect.left + 20:
                self.direction = 1

            # Chase player if on same horizontal line and close
            if abs(self.y - player_y) < 50:
                if player_x > self.x:
                    self.direction = 1
                else:
                    self.direction = -1
        else:
            self.y += self.direction * speed

            # Bounce at corners
            if self.y >= self.field_rect.bottom - 20:
                self.direction = -1
            elif self.y <= self.field_rect.top + 20:
                self.direction = 1

            # Chase player if on same vertical line and close
            if abs(self.x - player_x) < 50:
                if player_y > self.y:
                    self.direction = 1
                else:
                    self.direction = -1

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the spark."""
        size = config.SPARK_SIZE
        pygame.draw.circle(surface, config.SPARK_COLOR, (int(self.x), int(self.y)), size)
        pygame.draw.circle(surface, (255, 200, 100), (int(self.x), int(self.y)), size - 2)

    def collides_with_trail(self, trail: List[Tuple[int, int]]) -> bool:
        """Check if spark collides with the player's trail."""
        if not trail:
            return False

        for point in trail:
            dist = ((self.x - point[0]) ** 2 + (self.y - point[1]) ** 2) ** 0.5
            if dist < config.SPARK_SIZE + config.TRAIL_WIDTH:
                return True
        return False

    def collides_with_player(self, player: Player) -> bool:
        """Check if spark collides with the player."""
        dist = ((self.x - player.x) ** 2 + (self.y - player.y) ** 2) ** 0.5
        return dist < config.SPARK_SIZE + config.PLAYER_SIZE


class GameState:
    """Complete game state management."""

    def __init__(self):
        self.field_rect = Rect(config.FIELD_X, config.FIELD_Y, config.FIELD_WIDTH, config.FIELD_HEIGHT)

        # Create a grid for claimed/unclaimed tracking
        grid_w = config.FIELD_WIDTH // 2
        grid_h = config.FIELD_HEIGHT // 2
        self.claimed_grid = [[False for _ in range(grid_w)] for _ in range(grid_h)]

        # Mark borders as claimed
        for x in range(grid_w):
            self.claimed_grid[0][x] = True
            self.claimed_grid[grid_h - 1][x] = True
        for y in range(grid_h):
            self.claimed_grid[y][0] = True
            self.claimed_grid[y][grid_w - 1] = True

        self.claimed_regions: List[Rect] = [self.field_rect]

        self.player = Player(self.field_rect)
        self.boss = Boss(self.field_rect, self.claimed_regions)
        self.sparks = [
            Spark(self.field_rect, 'top'),
            Spark(self.field_rect, 'bottom'),
            Spark(self.field_rect, 'left')
        ]

        self.score = 0
        self.lives = config.STARTING_LIVES
        self.level = 1
        self.game_over = False
        self.level_complete = False
        self.claimed_area = 0

    def reset(self) -> None:
        """Reset the game to initial state."""
        grid_w = config.FIELD_WIDTH // 2
        grid_h = config.FIELD_HEIGHT // 2
        self.claimed_grid = [[False for _ in range(grid_w)] for _ in range(grid_h)]

        for x in range(grid_w):
            self.claimed_grid[0][x] = True
            self.claimed_grid[grid_h - 1][x] = True
        for y in range(grid_h):
            self.claimed_grid[y][0] = True
            self.claimed_grid[y][grid_w - 1] = True

        self.claimed_regions = [self.field_rect]
        self.claimed_area = 0

        self.player.reset()
        self.boss.reset()
        for spark in self.sparks:
            spark.reset()

        self.score = 0
        self.lives = config.STARTING_LIVES
        self.level = 1
        self.game_over = False
        self.level_complete = False

    def next_level(self) -> None:
        """Advance to the next level."""
        self.level += 1
        self.player.reset()
        self.boss.reset()
        for spark in self.sparks:
            spark.reset()
        self.level_complete = False

    def lose_life(self) -> None:
        """Handle losing a life."""
        self.lives -= 1
        self.score = max(0, self.score - config.DEATH_PENALTY)
        self.player.clear_trail()
        self.player.reset()

        if self.lives <= 0:
            self.game_over = True

    def claim_area(self, area_rect: Rect) -> None:
        """Mark an area as claimed."""
        if not area_rect:
            return

        self.claimed_regions.append(area_rect)

        # Mark grid cells as claimed
        grid_w = config.FIELD_WIDTH // 2
        start_x = max(0, int((area_rect.x - self.field_rect.x) // 2))
        start_y = max(0, int((area_rect.y - self.field_rect.y) // 2))
        end_x = min(grid_w, int((area_rect.right - self.field_rect.x) // 2) + 1)
        end_y = min(grid_h, int((area_rect.bottom - self.field_rect.y) // 2) + 1)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                self.claimed_grid[y][x] = True

        # Calculate score
        area_size = area_rect.width * area_rect.height
        multiplier = 1.0
        if area_size > config.SIZE_MULTIPLIER_THRESHOLD:
            multiplier = 1.5
        if area_size > config.SIZE_MULTIPLIER_THRESHOLD * 2:
            multiplier = 2.0

        points = int(area_size / config.BASE_SCORE_PER_AREA * multiplier)
        self.score += points

    def update(self) -> None:
        """Update all game entities."""
        if self.game_over or self.level_complete:
            return

        # Move player and check for area claim
        claimed, area_rect = self.player.move(self.claimed_grid)
        if claimed:
            self.claim_area(area_rect)

        # Update enemies
        self.boss.update(self.level, self.claimed_regions)
        for spark in self.sparks:
            spark.update(self.level, self.player.x, self.player.y)

        # Check collisions
        if self.boss.collides_with_trail(self.player.trail):
            self.lose_life()
        elif self.boss.collides_with_player(self.player):
            self.lose_life()

        for spark in self.sparks:
            if spark.collides_with_trail(self.player.trail):
                self.lose_life()
                break
            if spark.collides_with_player(self.player):
                self.lose_life()
                break

        # Check win condition
        if not self.game_over and self.get_claimed_percentage() >= config.WIN_PERCENTAGE:
            self.level_complete = True
            self.score += config.LEVEL_COMPLETE_BONUS * self.level

    def get_claimed_percentage(self) -> float:
        """Calculate the percentage of claimed area."""
        total_cells = 0
        claimed_cells = 0

        for row in self.claimed_grid:
            for cell in row:
                total_cells += 1
                if cell:
                    claimed_cells += 1

        return (claimed_cells / total_cells) * 100 if total_cells > 0 else 0
