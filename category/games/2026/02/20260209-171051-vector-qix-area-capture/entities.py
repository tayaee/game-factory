"""Game entities and logic."""

import math
import random
from typing import List, Tuple, Optional, Set
import pygame
import config


class Player:
    """The player marker that moves along the field edges and draws trails."""

    def __init__(self, field_rect: pygame.Rect):
        self.field_rect = field_rect
        self.reset_position()
        self.speed = config.PLAYER_SPEED
        self.is_drawing = False
        self.trail: List[Tuple[int, int]] = []

    def reset_position(self):
        """Reset player to starting position at top-left corner."""
        self.x = self.field_rect.left
        self.y = self.field_rect.top
        self.on_border = True
        self.direction = (0, 0)  # (dx, dy)
        self.trail = []

    def set_direction(self, dx: int, dy: int):
        """Set movement direction."""
        if dx != 0 and dy != 0:
            return  # No diagonal movement
        self.direction = (dx, dy)

    def start_drawing(self):
        """Start drawing a trail (only if on border)."""
        if self.on_border and self.direction != (0, 0):
            self.is_drawing = True
            self.trail = [(int(self.x), int(self.y))]

    def stop_drawing(self):
        """Stop drawing and return to border."""
        self.is_drawing = False
        self.on_border = True

    def update(self) -> bool:
        """
        Update player position.
        Returns True if player completed a trail (returned to border).
        """
        if self.direction == (0, 0):
            return False

        dx, dy = self.direction
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        # Constrain to field bounds
        new_x = max(self.field_rect.left, min(self.field_rect.right, new_x))
        new_y = max(self.field_rect.top, min(self.field_rect.bottom, new_y))

        self.x = new_x
        self.y = new_y

        # Check if on border
        on_left = self.x <= self.field_rect.left + 1
        on_right = self.x >= self.field_rect.right - 1
        on_top = self.y <= self.field_rect.top + 1
        on_bottom = self.y >= self.field_rect.bottom - 1

        was_on_border = self.on_border
        self.on_border = on_left or on_right or on_top or on_bottom

        # Add to trail if drawing
        if self.is_drawing:
            # Only add points that are different enough
            if not self.trail or (abs(self.x - self.trail[-1][0]) > 2 or abs(self.y - self.trail[-1][1]) > 2):
                self.trail.append((int(self.x), int(self.y)))

        # Check if returned to border while drawing
        trail_completed = False
        if self.is_drawing and self.on_border and not was_on_border:
            trail_completed = True
            self.is_drawing = False

        return trail_completed

    def get_rect(self) -> pygame.Rect:
        """Get player collision rectangle."""
        return pygame.Rect(
            self.x - config.PLAYER_SIZE // 2,
            self.y - config.PLAYER_SIZE // 2,
            config.PLAYER_SIZE,
            config.PLAYER_SIZE
        )

    def draw(self, surface: pygame.Surface):
        """Draw the player."""
        rect = self.get_rect()
        pygame.draw.rect(surface, config.PLAYER_COLOR, rect)

        # Draw trail
        if len(self.trail) > 1:
            pygame.draw.lines(surface, config.TRAIL_COLOR, False, self.trail, config.TRAIL_WIDTH)


class Qix:
    """The wandering enemy that moves unpredictably in the unclaimed area."""

    def __init__(self, field_rect: pygame.Rect, claimed_regions: List[pygame.Rect]):
        self.field_rect = field_rect
        self.claimed_regions = claimed_regions
        self.reset_position()

    def reset_position(self):
        """Reset Qix to a random position in unclaimed area."""
        self.x = self.field_rect.centerx
        self.y = self.field_rect.centery
        self.vx = random.choice([-1, 1]) * config.QIX_SPEED
        self.vy = random.choice([-1, 1]) * config.QIX_SPEED
        self.lines = []
        self.phase = 0

    def update(self, claimed_regions: List[pygame.Rect]):
        """Update Qix position and animation."""
        self.claimed_regions = claimed_regions

        # Random direction changes
        if random.random() < 0.02:
            self.vx = random.choice([-1, 1]) * config.QIX_SPEED
        if random.random() < 0.02:
            self.vy = random.choice([-1, 1]) * config.QIX_SPEED

        # Move
        new_x = self.x + self.vx
        new_y = self.y + self.vy

        # Bounce off field edges
        if new_x < self.field_rect.left + config.QIX_SIZE:
            new_x = self.field_rect.left + config.QIX_SIZE
            self.vx *= -1
        elif new_x > self.field_rect.right - config.QIX_SIZE:
            new_x = self.field_rect.right - config.QIX_SIZE
            self.vx *= -1

        if new_y < self.field_rect.top + config.QIX_SIZE:
            new_y = self.field_rect.top + config.QIX_SIZE
            self.vy *= -1
        elif new_y > self.field_rect.bottom - config.QIX_SIZE:
            new_y = self.field_rect.bottom - config.QIX_SIZE
            self.vy *= -1

        # Check collision with claimed areas
        test_rect = pygame.Rect(new_x - config.QIX_SIZE // 2, new_y - config.QIX_SIZE // 2,
                               config.QIX_SIZE, config.QIX_SIZE)
        for region in claimed_regions:
            if region.colliderect(test_rect):
                self.vx *= -1
                self.vy *= -1
                break
        else:
            self.x = new_x
            self.y = new_y

        # Update animation
        self.phase = (self.phase + 0.2) % (2 * math.pi)

    def get_center(self) -> Tuple[float, float]:
        """Get Qix center position."""
        return (self.x, self.y)

    def get_radius(self) -> float:
        """Get Qix collision radius."""
        return config.QIX_SIZE

    def check_collision_with_trail(self, trail: List[Tuple[int, int]]) -> bool:
        """Check if Qix collides with player's trail."""
        if len(trail) < 2:
            return False

        cx, cy = self.get_center()
        radius = self.get_radius()

        for point in trail:
            px, py = point
            distance = math.sqrt((cx - px) ** 2 + (cy - py) ** 2)
            if distance < radius + config.TRAIL_WIDTH:
                return True

        return False

    def get_distance_from(self, x: float, y: float) -> float:
        """Get distance from a point."""
        return math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)

    def draw(self, surface: pygame.Surface):
        """Draw the Qix as flickering lines."""
        self.lines = []
        for i in range(config.QIX_LINE_COUNT):
            angle = (2 * math.pi * i / config.QIX_LINE_COUNT) + self.phase
            end_x = self.x + math.cos(angle) * config.QIX_LINE_LENGTH
            end_y = self.y + math.sin(angle) * config.QIX_LINE_LENGTH
            self.lines.append((self.x, self.y, end_x, end_y))

        for line in self.lines:
            pygame.draw.line(surface, config.QIX_COLOR, (line[0], line[1]), (line[2], line[3]), 2)


class Spark:
    """Enemy that travels along the claimed borders."""

    def __init__(self, field_rect: pygame.Rect, direction: int = 1):
        self.field_rect = field_rect
        self.direction = direction  # 1 for clockwise, -1 for counter-clockwise
        self.speed = config.SPARK_SPEED
        self.reset_position()
        self.edge = 0  # 0: top, 1: right, 2: bottom, 3: left
        self.progress = 0.0  # Progress along current edge (0-1)

    def reset_position(self):
        """Reset spark position."""
        self.edge = random.randint(0, 3)
        self.progress = random.random()

    def update(self):
        """Move spark along border."""
        edge_length = self.field_rect.width if self.edge % 2 == 0 else self.field_rect.height
        step = self.speed / edge_length

        if self.direction > 0:
            self.progress += step
            if self.progress >= 1.0:
                self.progress = 0.0
                self.edge = (self.edge + 1) % 4
        else:
            self.progress -= step
            if self.progress < 0.0:
                self.progress = 1.0
                self.edge = (self.edge - 1) % 4

    def get_position(self) -> Tuple[float, float]:
        """Get current position."""
        if self.edge == 0:  # Top edge
            return (self.field_rect.left + self.progress * self.field_rect.width, self.field_rect.top)
        elif self.edge == 1:  # Right edge
            return (self.field_rect.right, self.field_rect.top + self.progress * self.field_rect.height)
        elif self.edge == 2:  # Bottom edge
            return (self.field_rect.right - self.progress * self.field_rect.width, self.field_rect.bottom)
        else:  # Left edge
            return (self.field_rect.left, self.field_rect.bottom - self.progress * self.field_rect.height)

    def check_collision_with_player(self, player: Player) -> bool:
        """Check if spark collides with player."""
        sx, sy = self.get_position()
        distance = math.sqrt((sx - player.x) ** 2 + (sy - player.y) ** 2)
        return distance < config.SPARK_SIZE + config.PLAYER_SIZE

    def draw(self, surface: pygame.Surface):
        """Draw the spark."""
        x, y = self.get_position()
        pygame.draw.circle(surface, config.SPARK_COLOR, (int(x), int(y)), config.SPARK_SIZE)


class GameState:
    """Main game state management."""

    def __init__(self):
        self.field_rect = pygame.Rect(
            config.FIELD_MARGIN,
            config.FIELD_MARGIN + 30,
            config.FIELD_WIDTH,
            config.FIELD_HEIGHT
        )

        self.player = Player(self.field_rect)
        self.qix = Qix(self.field_rect, [])
        self.sparks = [
            Spark(self.field_rect, 1),
            Spark(self.field_rect, -1)
        ]

        self.lives = config.LIVES_START
        self.score = 0
        self.level = 1
        self.game_over = False
        self.level_complete = False

        # Claimed regions (filled areas)
        self.claimed_regions: List[pygame.Rect] = []

        # Total area
        self.total_area = self.field_rect.width * self.field_rect.height

        # Animation timers
        self.death_timer = 0
        self.level_complete_timer = 0

    def get_claimed_percentage(self) -> float:
        """Get percentage of area claimed."""
        claimed_area = sum(r.width * r.height for r in self.claimed_regions)
        return (claimed_area / self.total_area) * 100

    def fill_area_from_trail(self, trail: List[Tuple[int, int]]) -> pygame.Rect:
        """
        Create a filled region from a completed trail.
        This is a simplified version that creates a bounding box fill.
        """
        if len(trail) < 2:
            return None

        # Find bounding box of trail
        min_x = min(p[0] for p in trail)
        max_x = max(p[0] for p in trail)
        min_y = min(p[1] for p in trail)
        max_y = max(p[1] for p in trail)

        # Determine which side to fill (the smaller area)
        # For simplicity, we fill the area enclosed by the trail and border
        width = max_x - min_x
        height = max_y - min_y

        # Create rect for the filled area
        fill_rect = pygame.Rect(min_x, min_y, width + 1, height + 1)

        # Make sure it's within field bounds
        fill_rect.clip_ip(self.field_rect)

        return fill_rect

    def complete_trail(self, trail: List[Tuple[int, int]]) -> int:
        """
        Process a completed trail and return score earned.
        """
        fill_rect = self.fill_area_from_trail(trail)
        if fill_rect and fill_rect.width > 0 and fill_rect.height > 0:
            # Check for overlaps with existing regions
            merged = False
            for i, region in enumerate(self.claimed_regions):
                if region.colliderect(fill_rect):
                    # Merge regions
                    self.claimed_regions[i] = region.union(fill_rect)
                    merged = True
                    break

            if not merged:
                self.claimed_regions.append(fill_rect)

            # Calculate score
            claimed_pct = self.get_claimed_percentage()
            area_pct = (fill_rect.width * fill_rect.height / self.total_area) * 100

            # Risk multiplier based on distance from Qix
            trail_center = (fill_rect.centerx, fill_rect.centery)
            distance = self.qix.get_distance_from(*trail_center)
            risk_multiplier = min(1 + distance / 500, config.RISK_MULTIPLIER_MAX)

            points = int(area_pct * config.POINTS_PER_PERCENT * risk_multiplier)
            return points

        return 0

    def lose_life(self):
        """Handle player death."""
        self.lives -= 1
        self.death_timer = 60  # Frames to show death animation
        self.player.trail = []
        self.player.is_drawing = False

        if self.lives <= 0:
            self.game_over = True
        else:
            self.player.reset_position()
            self.qix.reset_position()
            for spark in self.sparks:
                spark.reset_position()

    def next_level(self):
        """Advance to next level."""
        self.level += 1
        self.level_complete_timer = 60
        self.claimed_regions = []
        self.player.reset_position()
        self.qix.reset_position()
        self.qix.speed *= config.LEVEL_MULTIPLIER
        for spark in self.sparks:
            spark.reset_position()
            spark.speed *= config.LEVEL_MULTIPLIER

    def update(self) -> bool:
        """
        Update game state.
        Returns True if trail was completed.
        """
        if self.game_over or self.level_complete:
            return False

        if self.death_timer > 0:
            self.death_timer -= 1
            return False

        if self.level_complete_timer > 0:
            self.level_complete_timer -= 1
            if self.level_complete_timer == 0:
                self.level_complete = False
            return False

        # Update player
        trail_completed = self.player.update()

        if trail_completed:
            score = self.complete_trail(self.player.trail)
            self.score += score
            self.player.trail = []

            # Check win condition
            if self.get_claimed_percentage() >= config.WIN_PERCENTAGE:
                self.level_complete = True
                self.score += config.LEVEL_COMPLETE_BONUS
                self.next_level()

        # Update Qix
        self.qix.update(self.claimed_regions)

        # Check Qix collision with trail
        if self.player.is_drawing and self.qix.check_collision_with_trail(self.player.trail):
            self.score += config.DEATH_PENALTY
            self.lose_life()
            return False

        # Update sparks
        for spark in self.sparks:
            spark.update()
            if spark.check_collision_with_player(self.player):
                self.score += config.DEATH_PENALTY
                self.lose_life()
                return False

        return trail_complete

    def reset(self):
        """Reset the game."""
        self.__init__()
