"""
Vector Galaxian Swarm Attack
Defend the starship against tactical alien swarms in this high-intensity vector shooter.
"""

import pygame
import random
import math
from typing import List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60

# Colors - Vector style
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 50, 50)
COLOR_GREEN = (50, 255, 50)
COLOR_CYAN = (50, 200, 255)
COLOR_YELLOW = (255, 255, 50)
COLOR_ORANGE = (255, 165, 0)
COLOR_PURPLE = (200, 50, 255)

# Game settings
PLAYER_SPEED = 5
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 20
PLAYER_Y = SCREEN_HEIGHT - 50

BULLET_SPEED = 10
BULLET_WIDTH = 4
BULLET_HEIGHT = 12
MAX_PLAYER_BULLETS = 2

ENEMY_BULLET_SPEED = 4
ENEMY_BULLET_WIDTH = 3
ENEMY_BULLET_HEIGHT = 8

# Scoring
SCORE_DRONE_FORMATION = 30
SCORE_DRONE_DIVING = 60
SCORE_EMISSARY_FORMATION = 50
SCORE_EMISSARY_DIVING = 100
SCORE_FLAGSHIP = 150
FLAGSHIP_ESCORT_BONUS = 300

# Wave settings
ROWS_PER_ENEMY_TYPE = 2
COLUMNS = 10
ENEMY_SPACING_X = 50
ENEMY_SPACING_Y = 45
FORMATION_START_X = (SCREEN_WIDTH - COLUMNS * ENEMY_SPACING_X) // 2 + 25
FORMATION_START_Y = 80


class EnemyType(Enum):
    DRONE = 0      # Bottom tier, basic
    EMISSARY = 1   # Middle tier, shoots while diving
    FLAGSHIP = 2   # Top tier, leads escort dives


class DiveState(Enum):
    IN_FORMATION = 0
    DIVING = 1
    RETURNING = 2


@dataclass
class BezierPoint:
    x: float
    y: float


class Enemy:
    """Base enemy class with state machine for diving behavior."""

    def __init__(self, enemy_type: EnemyType, grid_x: int, grid_y: int):
        self.type = enemy_type
        self.grid_x = grid_x
        self.grid_y = grid_y

        # Formation position
        self.formation_x = FORMATION_START_X + grid_x * ENEMY_SPACING_X
        self.formation_y = FORMATION_START_Y + grid_y * ENEMY_SPACING_Y

        # Current position
        self.x = self.formation_x
        self.y = self.formation_y

        # Dive state
        self.dive_state = DiveState.IN_FORMATION
        self.dive_timer = random.uniform(2, 8)  # Time before considering dive
        self.dive_progress = 0.0

        # Movement
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        # Bezier curve for diving
        self.control_points: List[BezierPoint] = []
        self.dive_speed = 0.01

        # Shooting
        self.can_shoot = enemy_type in [EnemyType.EMISSARY, EnemyType.FLAGSHIP]
        self.shoot_cooldown = random.uniform(0.5, 2.0)
        self.shoot_timer = 0.0

        # Visual
        self.width = self._get_width()
        self.height = self._get_height()
        self.color = self._get_color()

        # Escort tracking (for flagship)
        self.escort_leader: Optional['Enemy'] = None
        self.escort_offset: Tuple[float, float] = (0, 0)

    def _get_width(self) -> int:
        if self.type == EnemyType.FLAGSHIP:
            return 35
        elif self.type == EnemyType.EMISSARY:
            return 30
        return 25

    def _get_height(self) -> int:
        if self.type == EnemyType.FLAGSHIP:
            return 30
        elif self.type == EnemyType.EMISSARY:
            return 25
        return 20

    def _get_color(self) -> Tuple[int, int, int]:
        if self.type == EnemyType.FLAGSHIP:
            return COLOR_RED
        elif self.type == EnemyType.EMISSARY:
            return COLOR_PURPLE
        return COLOR_YELLOW

    def start_dive(self, target_x: float, target_y: float) -> None:
        """Initiate a dive attack using bezier curve."""
        self.dive_state = DiveState.DIVING
        self.dive_progress = 0.0

        # Setup bezier curve points
        # Start at current position
        start = BezierPoint(self.x, self.y)

        # Control point for curve (creates diving arc)
        control_x = self.x + (target_x - self.x) * 0.3
        control_y = self.y + (SCREEN_HEIGHT - self.y) * 0.5
        control = BezierPoint(control_x, control_y)

        # End point (below player)
        end = BezierPoint(target_x, target_y)

        self.control_points = [start, control, end]

        # Dive speed based on enemy type
        base_speed = 0.015
        if self.type == EnemyType.DRONE:
            self.dive_speed = base_speed * 1.2
        elif self.type == EnemyType.EMISSARY:
            self.dive_speed = base_speed * 1.0
        else:  # FLAGSHIP
            self.dive_speed = base_speed * 0.8

    def start_escort_dive(self, leader: 'Enemy', offset_x: float, offset_y: float) -> None:
        """Start dive as an escort to a flagship."""
        self.escort_leader = leader
        self.escort_offset = (offset_x, offset_y)
        self.dive_state = DiveState.DIVING
        self.dive_progress = leader.dive_progress
        self.control_points = leader.control_points
        self.dive_speed = leader.dive_speed

    def update(self, dt: float, player_x: float, player_y: float) -> Optional['EnemyBullet']:
        """Update enemy state and return bullet if fired."""
        bullet = None

        # Update shoot timer
        if self.can_shoot:
            self.shoot_timer -= dt
            if self.shoot_timer <= 0 and self.dive_state == DiveState.DIVING:
                # Fire while diving
                bullet = self._shoot_at_player(player_x, player_y)
                self.shoot_timer = self.shoot_cooldown

        if self.dive_state == DiveState.IN_FORMATION:
            # Sway in formation
            sway_offset = math.sin(pygame.time.get_ticks() * 0.001) * 5
            self.x = self.formation_x + sway_offset
            self.y = self.formation_y

            # Update dive timer
            self.dive_timer -= dt
            if self.dive_timer <= 0:
                # 30% chance to dive when timer expires
                if random.random() < 0.3:
                    self.start_dive(player_x + random.uniform(-50, 50), SCREEN_HEIGHT + 50)
                else:
                    self.dive_timer = random.uniform(3, 10)

        elif self.dive_state == DiveState.DIVING:
            # Follow escort leader if applicable
            if self.escort_leader and self.escort_leader.dive_state == DiveState.DIVING:
                self.dive_progress = self.escort_leader.dive_progress
            else:
                self.dive_progress += self.dive_speed
                self.escort_leader = None

            # Calculate bezier curve position
            if self.dive_progress >= 1.0:
                # Dive complete, return to formation
                self.dive_state = DiveState.RETURNING
            else:
                pos = self._bezier_point(self.dive_progress)
                self.x = pos.x
                self.y = pos.y

                # Add escort offset
                if self.escort_leader:
                    self.x += self.escort_offset[0]
                    self.y += self.escort_offset[1]

        elif self.dive_state == DiveState.RETURNING:
            # Move back to formation
            dx = self.formation_x - self.x
            dy = self.formation_y - self.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < 5:
                self.x = self.formation_x
                self.y = self.formation_y
                self.dive_state = DiveState.IN_FORMATION
                self.dive_timer = random.uniform(2, 8)
                self.escort_leader = None
            else:
                return_speed = 8
                self.x += (dx / dist) * return_speed
                self.y += (dy / dist) * return_speed

        return bullet

    def _bezier_point(self, t: float) -> BezierPoint:
        """Calculate point on quadratic bezier curve."""
        if len(self.control_points) != 3:
            return BezierPoint(self.x, self.y)

        p0, p1, p2 = self.control_points

        # Quadratic bezier formula
        x = (1 - t) ** 2 * p0.x + 2 * (1 - t) * t * p1.x + t ** 2 * p2.x
        y = (1 - t) ** 2 * p0.y + 2 * (1 - t) * t * p1.y + t ** 2 * p2.y

        return BezierPoint(x, y)

    def _shoot_at_player(self, player_x: float, player_y: float) -> 'EnemyBullet':
        """Calculate bullet trajectory toward player."""
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 0:
            vel_x = (dx / dist) * ENEMY_BULLET_SPEED
            vel_y = (dy / dist) * ENEMY_BULLET_SPEED
        else:
            vel_x, vel_y = 0, ENEMY_BULLET_SPEED

        return EnemyBullet(self.x + self.width / 2, self.y + self.height, vel_x, vel_y)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.width / 2), int(self.y - self.height / 2),
                          self.width, self.height)

    def get_score_value(self) -> int:
        """Get point value based on type and state."""
        if self.type == EnemyType.FLAGSHIP:
            return SCORE_FLAGSHIP
        elif self.type == EnemyType.EMISSARY:
            return SCORE_EMISSARY_DIVING if self.dive_state == DiveState.DIVING else SCORE_EMISSARY_FORMATION
        else:
            return SCORE_DRONE_DIVING if self.dive_state == DiveState.DIVING else SCORE_DRONE_FORMATION

    def draw(self, surface: pygame.Surface) -> None:
        rect = self.get_rect()

        if self.type == EnemyType.FLAGSHIP:
            # Draw flagship (larger, more detailed)
            # Main body
            pygame.draw.polygon(surface, self.color, [
                (rect.centerx, rect.top),
                (rect.left, rect.centery),
                (rect.left + 5, rect.bottom),
                (rect.right - 5, rect.bottom),
                (rect.right, rect.centery)
            ])

            # Wings
            pygame.draw.polygon(surface, COLOR_ORANGE, [
                (rect.left + 5, rect.centery),
                (rect.left - 5, rect.bottom - 5),
                (rect.left + 10, rect.bottom)
            ])
            pygame.draw.polygon(surface, COLOR_ORANGE, [
                (rect.right - 5, rect.centery),
                (rect.right + 5, rect.bottom - 5),
                (rect.right - 10, rect.bottom)
            ])

            # Core
            pygame.draw.circle(surface, COLOR_WHITE, rect.center, 5)

        elif self.type == EnemyType.EMISSARY:
            # Draw emissary (medium, shoots while diving)
            pygame.draw.polygon(surface, self.color, [
                (rect.centerx, rect.top),
                (rect.left, rect.centery + 3),
                (rect.left + 3, rect.bottom),
                (rect.right - 3, rect.bottom),
                (rect.right, rect.centery + 3)
            ])

            # Detail line
            pygame.draw.line(surface, COLOR_WHITE,
                           (rect.left + 5, rect.centery),
                           (rect.right - 5, rect.centery), 2)

        else:  # DRONE
            # Draw drone (simplest)
            pygame.draw.polygon(surface, self.color, [
                (rect.centerx, rect.top),
                (rect.left + 3, rect.bottom),
                (rect.right - 3, rect.bottom)
            ])

        # Draw diving indicator
        if self.dive_state == DiveState.DIVING:
            pygame.draw.circle(surface, COLOR_WHITE, rect.center, 3)


class EnemyBullet:
    """Projectile fired by enemies."""

    def __init__(self, x: float, y: float, vel_x: float, vel_y: float):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.active = True

    def update(self) -> None:
        self.x += self.vel_x
        self.y += self.vel_y

        if (self.y > SCREEN_HEIGHT or self.x < 0 or
            self.x > SCREEN_WIDTH or self.y < 0):
            self.active = False

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - ENEMY_BULLET_WIDTH / 2),
                          int(self.y - ENEMY_BULLET_HEIGHT / 2),
                          ENEMY_BULLET_WIDTH, ENEMY_BULLET_HEIGHT)

    def draw(self, surface: pygame.Surface) -> None:
        rect = self.get_rect()
        pygame.draw.ellipse(surface, COLOR_RED, rect)
        pygame.draw.ellipse(surface, COLOR_ORANGE, rect, 1)


class PlayerBullet:
    """Projectile fired by the player."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.active = True

    def update(self) -> None:
        self.y -= BULLET_SPEED
        if self.y < 0:
            self.active = False

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - BULLET_WIDTH / 2),
                          int(self.y - BULLET_HEIGHT / 2),
                          BULLET_WIDTH, BULLET_HEIGHT)

    def draw(self, surface: pygame.Surface) -> None:
        rect = self.get_rect()
        pygame.draw.rect(surface, COLOR_CYAN, rect)
        pygame.draw.rect(surface, COLOR_WHITE, rect, 1)


class Player:
    """Player-controlled ship."""

    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = PLAYER_Y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.speed = PLAYER_SPEED
        self.alive = True
        self.invulnerable_timer = 0.0

    def update(self, dt: float, keys) -> None:
        if not self.alive:
            return

        # Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed

        # Clamp to screen
        self.x = max(self.width // 2, min(SCREEN_WIDTH - self.width // 2, self.x))

        # Update invulnerability
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.width // 2),
                          int(self.y - self.height // 2),
                          self.width, self.height)

    def hit(self) -> bool:
        """Return True if player actually takes damage (not invulnerable)."""
        if self.invulnerable_timer > 0:
            return False
        self.invulnerable_timer = 2.0  # 2 seconds invulnerability
        return True

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return

        # Blink when invulnerable
        if self.invulnerable_timer > 0 and int(pygame.time.get_ticks() * 10) % 2 == 0:
            return

        rect = self.get_rect()

        # Draw ship body
        pygame.draw.polygon(surface, COLOR_GREEN, [
            (rect.centerx, rect.top),
            (rect.left, rect.bottom),
            (rect.left + 8, rect.bottom - 5),
            (rect.centerx, rect.bottom - 3),
            (rect.right - 8, rect.bottom - 5),
            (rect.right, rect.bottom)
        ])

        # Cockpit
        pygame.draw.circle(surface, COLOR_CYAN,
                         (rect.centerx, rect.centery), 4)

        # Engine glow
        engine_y = rect.bottom + 3
        pygame.draw.polygon(surface, COLOR_ORANGE, [
            (rect.left + 8, rect.bottom),
            (rect.centerx, engine_y + random.randint(3, 8)),
            (rect.right - 8, rect.bottom)
        ])


class Explosion:
    """Visual explosion effect."""

    def __init__(self, x: float, y: float, large: bool = False):
        self.x = x
        self.y = y
        self.max_radius = 30 if large else 20
        self.radius = 5
        self.duration = 20 if large else 15
        self.timer = self.duration
        self.active = True

    def update(self) -> None:
        self.timer -= 1
        self.radius = int(self.max_radius * (1 - self.timer / self.duration))
        if self.timer <= 0:
            self.active = False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.active:
            return

        alpha = int(255 * (self.timer / self.duration))

        # Outer glow
        if self.radius > 5:
            glow_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*COLOR_ORANGE, alpha // 2),
                             (self.radius, self.radius), self.radius)
            surface.blit(glow_surface, (int(self.x - self.radius), int(self.y - self.radius)))

        # Main explosion
        pygame.draw.circle(surface, COLOR_YELLOW, (int(self.x), int(self.y)), self.radius)

        # Inner core
        core_radius = max(2, self.radius // 2)
        pygame.draw.circle(surface, COLOR_WHITE, (int(self.x), int(self.y)), core_radius)


class Star:
    """Background star for parallax effect."""

    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.5, 2.0)
        self.brightness = random.randint(100, 255)

    def update(self) -> None:
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface: pygame.Surface) -> None:
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 1)


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Galaxian Swarm Attack")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.won = False

        # Fonts
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self) -> None:
        """Reset game to initial state."""
        self.player = Player()
        self.enemies: List[Enemy] = []
        self.player_bullets: List[PlayerBullet] = []
        self.enemy_bullets: List[EnemyBullet] = []
        self.explosions: List[Explosion] = []
        self.stars = [Star() for _ in range(50)]

        self.score = 0
        self.lives = 3
        self.wave = 1
        self.game_over = False
        self.won = False
        self.wave_clear_timer = 0

        self._init_enemies()

    def _init_enemies(self) -> None:
        """Initialize enemy formation."""
        self.enemies.clear()

        # Create 2 rows of each type (6 rows total)
        row_offset = 0

        # Top rows - Flagships
        for row in range(2):
            for col in range(COLUMNS):
                enemy = Enemy(EnemyType.FLAGSHIP, col, row + row_offset)
                self.enemies.append(enemy)
        row_offset += 2

        # Middle rows - Emissaries
        for row in range(2):
            for col in range(COLUMNS):
                enemy = Enemy(EnemyType.EMISSARY, col, row + row_offset)
                self.enemies.append(enemy)
        row_offset += 2

        # Bottom rows - Drones
        for row in range(2):
            for col in range(COLUMNS):
                enemy = Enemy(EnemyType.DRONE, col, row + row_offset)
                self.enemies.append(enemy)

    def handle_input(self) -> None:
        """Handle keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                if self.game_over or self.won:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                    elif event.key == pygame.K_r:
                        self.reset_game()
                else:
                    # Shoot
                    if event.key == pygame.K_SPACE:
                        self._fire_player_bullet()

    def _fire_player_bullet(self) -> None:
        """Fire a bullet from the player."""
        active_bullets = [b for b in self.player_bullets if b.active]

        if len(active_bullets) < MAX_PLAYER_BULLETS and self.player.alive:
            bullet = PlayerBullet(self.player.x, self.player.y - self.player.height // 2)
            self.player_bullets.append(bullet)

    def _trigger_flagship_dive(self) -> None:
        """Trigger a flagship-led escort dive attack."""
        flagships = [e for e in self.enemies if e.type == EnemyType.FLAGSHIP
                     and e.dive_state == DiveState.IN_FORMATION]

        if not flagships:
            return

        flagship = random.choice(flagships)
        target_x = self.player.x + random.uniform(-30, 30)
        flagship.start_dive(target_x, SCREEN_HEIGHT + 50)

        # Select 1-2 escorts
        emissaries = [e for e in self.enemies if e.type == EnemyType.EMISSARY
                      and e.dive_state == DiveState.IN_FORMATION]

        if emissaries:
            escorts = random.sample(emissaries, min(2, len(emissaries)))
            for i, escort in enumerate(escorts):
                offset_x = 40 if i == 0 else -40
                offset_y = 20
                escort.start_escort_dive(flagship, offset_x, offset_y)

    def update(self, dt: float) -> None:
        """Update game state."""
        # Update stars
        for star in self.stars:
            star.update()

        if self.game_over or self.won:
            return

        keys = pygame.key.get_pressed()
        self.player.update(dt, keys)

        # Update player bullets
        for bullet in self.player_bullets[:]:
            bullet.update()
            if not bullet.active:
                self.player_bullets.remove(bullet)

        # Update enemy bullets
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if not bullet.active:
                self.enemy_bullets.remove(bullet)

        # Update explosions
        for explosion in self.explosions[:]:
            explosion.update()
            if not explosion.active:
                self.explosions.remove(explosion)

        # Random flagship dive (every 5-10 seconds)
        if random.random() < 0.003:  # Approximately twice per 10 seconds at 60 FPS
            self._trigger_flagship_dive()

        # Update enemies
        player_rect = self.player.get_rect()

        for enemy in self.enemies[:]:
            bullet = enemy.update(dt, self.player.x, self.player.y)

            if bullet:
                self.enemy_bullets.append(bullet)

            enemy_rect = enemy.get_rect()

            # Check collision with player bullets
            for player_bullet in self.player_bullets[:]:
                if player_bullet.active and enemy_rect.colliderect(player_bullet.get_rect()):
                    # Check for flagship escort bonus
                    score_add = enemy.get_score_value()
                    is_escort = enemy.escort_leader is not None
                    leader_destroyed = False

                    if is_escort and enemy.escort_leader in self.enemies:
                        # Escort destroyed, check if leader still alive
                        pass
                    elif enemy.type == EnemyType.FLAGSHIP:
                        # Check if any escorts are active
                        active_escorts = [e for e in self.enemies
                                        if e.escort_leader == enemy]
                        if len(active_escorts) >= 2:
                            # Flagship with escorts destroyed = bonus
                            score_add += FLAGSHIP_ESCORT_BONUS
                            leader_destroyed = True

                    self.score += score_add
                    self.explosions.append(Explosion(enemy.x, enemy.y,
                                                    enemy.type == EnemyType.FLAGSHIP))
                    self.enemies.remove(enemy)
                    player_bullet.active = False
                    break

            # Check collision with player
            if enemy not in self.enemies:
                continue

            if enemy_rect.colliderect(player_rect):
                if self.player.hit():
                    self.lives -= 1
                    self.explosions.append(Explosion(self.player.x, self.player.y, True))
                    if self.lives <= 0:
                        self.game_over = True
                        self.player.alive = False
                    else:
                        # Brief pause after death
                        pass

        # Check enemy bullet collisions with player
        for bullet in self.enemy_bullets[:]:
            if bullet.active and player_rect.colliderect(bullet.get_rect()):
                if self.player.hit():
                    self.lives -= 1
                    bullet.active = False
                    self.explosions.append(Explosion(self.player.x, self.player.y, True))
                    if self.lives <= 0:
                        self.game_over = True
                        self.player.alive = False

        # Check for wave clear
        if not self.enemies:
            self.wave_clear_timer += 1
            if self.wave_clear_timer >= 120:  # 2 seconds
                self.wave += 1
                if self.wave > 3:
                    self.won = True
                else:
                    self._init_enemies()
                    self.wave_clear_timer = 0

    def draw(self) -> None:
        """Draw all game elements."""
        self.screen.fill(COLOR_BLACK)

        # Draw stars
        for star in self.stars:
            star.draw(self.screen)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw player bullets
        for bullet in self.player_bullets:
            bullet.draw(self.screen)

        # Draw enemy bullets
        for bullet in self.enemy_bullets:
            bullet.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw explosions
        for explosion in self.explosions:
            explosion.draw(self.screen)

        # Draw UI
        self._draw_ui()

        # Draw overlays
        if self.game_over:
            self._draw_overlay("GAME OVER", f"Final Score: {self.score}", "Press SPACE to Restart")
        elif self.won:
            self._draw_overlay("VICTORY!", f"Final Score: {self.score}", "Press SPACE to Play Again")
        elif self.wave_clear_timer > 0:
            wave_text = self.font_medium.render(f"WAVE {self.wave} COMPLETE!", True, COLOR_GREEN)
            rect = wave_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(wave_text, rect)

        pygame.display.flip()

    def _draw_ui(self) -> None:
        """Draw user interface elements."""
        # Score
        score_text = self.font_small.render(f"SCORE: {self.score}", True, COLOR_WHITE)
        self.screen.blit(score_text, (10, 10))

        # Wave
        wave_text = self.font_small.render(f"WAVE: {self.wave}/3", True, COLOR_CYAN)
        self.screen.blit(wave_text, (10, 40))

        # Lives
        lives_text = self.font_small.render(f"LIVES: {self.lives}", True, COLOR_GREEN)
        self.screen.blit(lives_text, (SCREEN_WIDTH - 100, 10))

        # Draw lives as ships
        for i in range(self.lives - 1):
            x = SCREEN_WIDTH - 30 - i * 25
            y = 40
            pygame.draw.polygon(self.screen, COLOR_GREEN, [
                (x, y),
                (x - 8, y + 10),
                (x + 8, y + 10)
            ])

    def _draw_overlay(self, title: str, subtitle: str, instruction: str) -> None:
        """Draw game over/victory overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        title_color = COLOR_GREEN if self.won else COLOR_RED
        title_text = self.font_large.render(title, True, title_color)
        subtitle_text = self.font_medium.render(subtitle, True, COLOR_WHITE)
        instr_text = self.font_small.render(instruction, True, COLOR_YELLOW)

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
