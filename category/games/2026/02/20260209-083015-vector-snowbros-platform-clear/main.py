"""Vector Snow Bros - Platform Clear Game

A classic arcade platformer where you freeze enemies into snowballs
and roll them to defeat other enemies.
"""

import pygame
import sys
import math
from enum import Enum
from typing import List, Optional, Tuple


class Direction(Enum):
    LEFT = -1
    RIGHT = 1
    NONE = 0


class GameState(Enum):
    PLAYING = 0
    LEVEL_CLEARED = 1
    GAME_OVER = 2


class EntityType(Enum):
    PLAYER = 0
    ENEMY_PATROL = 1
    ENEMY_CHASE = 2
    SNOWBALL = 3
    SNOW_PARTICLE = 4


# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
JUMP_FORCE = -12
MOVE_SPEED = 5
SNOW_SPEED = 8

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 100)
ORANGE = (255, 165, 0)
PURPLE = (200, 100, 255)
GRAY = (100, 100, 100)
DARK_BLUE = (30, 80, 150)

# Level layout (0 = empty, 1 = platform)
LEVEL_LAYOUT = [
    "00000000000000000000",
    "00000000000000000000",
    "00000000000000000000",
    "00000000000000000000",
    "00000000000000000000",
    "00000000000000000000",
    "00000111100000000000",
    "00000000000000000000",
    "00000001100000000000",
    "00000000000000000000",
    "00000000011000000000",
    "00000000000000000000",
    "00000000000000000000",
    "00111100001111000000",
    "00000000000000000000",
    "00000000000000000000",
    "00000110000000110000",
    "00000000000000000000",
    "00000000000000000000",
    "00000000000000000000",
    "00110011000011000000",
    "00000000000000000000",
    "00000000000000000000",
    "01100000000000001100",
    "00000000000000000000",
    "00000000000000000000",
    "00000000000000000000",
    "00000000000000000000",
    "11111111111111111111",
    "11111111111111111111",
]

TILE_SIZE = SCREEN_WIDTH // len(LEVEL_LAYOUT[0])


class Vector2:
    """Simple 2D vector class for physics calculations."""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        l = self.length()
        if l == 0:
            return Vector2(0, 0)
        return Vector2(self.x / l, self.y / l)

    def to_tuple(self):
        return (int(self.x), int(self.y))


class SnowParticle:
    """Snow particles for the snow breath effect."""
    def __init__(self, x: float, y: float, vx: float, vy: float, lifetime: int = 30):
        self.pos = Vector2(x, y)
        self.vel = Vector2(vx, vy)
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.radius = 3

    def update(self):
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y
        self.vel.y += 0.1  # Light gravity
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color = (*WHITE[:3], alpha)
        pygame.draw.circle(surface, WHITE, self.pos.to_tuple(), self.radius)


class Projectile:
    """Snow projectile from player's attack."""
    def __init__(self, x: float, y: float, direction: Direction):
        self.pos = Vector2(x, y)
        self.vel = Vector2(SNOW_SPEED * direction.value, 0)
        self.radius = 8
        self.active = True

    def update(self, platforms):
        self.pos.x += self.vel.x

        # Check platform collision
        tile_x = int(self.pos.x // TILE_SIZE)
        tile_y = int(self.pos.y // TILE_SIZE)

        if (tile_x >= 0 and tile_x < len(LEVEL_LAYOUT[0]) and
            tile_y >= 0 and tile_y < len(LEVEL_LAYOUT)):
            if LEVEL_LAYOUT[tile_y][tile_x] == '1':
                self.active = False

        # Out of bounds
        if self.pos.x < 0 or self.pos.x > SCREEN_WIDTH:
            self.active = False

        return self.active

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, self.pos.to_tuple(), self.radius)
        pygame.draw.circle(surface, BLUE, self.pos.to_tuple(), self.radius - 2)


class Snowball:
    """Frozen enemy that can be rolled."""
    def __init__(self, x: float, y: float, radius: int = 30):
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.radius = radius
        self.active = True
        self.on_ground = False
        self.push_cooldown = 0

    def update(self, platforms):
        # Apply gravity
        self.vel.y += GRAVITY

        # Move and check collisions
        new_pos = self.pos + self.vel

        # Horizontal collision
        tile_x_left = int((new_pos.x - self.radius) // TILE_SIZE)
        tile_x_right = int((new_pos.x + self.radius) // TILE_SIZE)
        tile_y = int(self.pos.y // TILE_SIZE)

        hit_wall = False
        for tx in [tile_x_left, tile_x_right]:
            if (tx >= 0 and tx < len(LEVEL_LAYOUT[0]) and
                tile_y >= 0 and tile_y < len(LEVEL_LAYOUT)):
                if LEVEL_LAYOUT[tile_y][tx] == '1':
                    hit_wall = True
                    self.vel.x *= -0.8  # Bounce
                    break

        if not hit_wall:
            self.pos.x = new_pos.x

        # Vertical collision
        tile_y_bottom = int((new_pos.y + self.radius) // TILE_SIZE)
        tile_x = int(self.pos.x // TILE_SIZE)

        self.on_ground = False
        if (tile_x >= 0 and tile_x < len(LEVEL_LAYOUT[0]) and
            tile_y_bottom >= 0 and tile_y_bottom < len(LEVEL_LAYOUT)):
            if LEVEL_LAYOUT[tile_y_bottom][tile_x] == '1':
                if self.vel.y > 0:
                    self.pos.y = tile_y_bottom * TILE_SIZE - self.radius
                    self.vel.y = 0
                    self.on_ground = True

        if not self.on_ground:
            self.pos.y = new_pos.y

        # Friction
        if self.on_ground:
            self.vel.x *= 0.98
        else:
            self.vel.x *= 0.999

        if abs(self.vel.x) < 0.1:
            self.vel.x = 0

        # Off screen
        if self.pos.y > SCREEN_HEIGHT + 100:
            self.active = False

        if self.push_cooldown > 0:
            self.push_cooldown -= 1

        return self.active

    def draw(self, surface):
        # Main snowball body
        pygame.draw.circle(surface, WHITE, self.pos.to_tuple(), self.radius)
        pygame.draw.circle(surface, (200, 220, 255), self.pos.to_tuple(), self.radius - 5)

        # Shading
        offset = int(self.radius * 0.3)
        pygame.draw.circle(surface, (255, 255, 255),
                          (int(self.pos.x - offset), int(self.pos.y - offset)),
                          int(self.radius * 0.3))

        # Outline
        pygame.draw.circle(surface, BLUE, self.pos.to_tuple(), self.radius, 2)


class Enemy:
    """Enemy base class with freezing mechanic."""
    def __init__(self, x: float, y: float, enemy_type: EntityType):
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.enemy_type = enemy_type
        self.width = 32
        self.height = 32
        self.active = True
        self.frozen_level = 0  # 0-100, when 100 becomes snowball
        self.direction = Direction.RIGHT
        self.on_ground = False
        self.patrol_start = x
        self.patrol_range = 150
        self.color = RED if enemy_type == EntityType.ENEMY_PATROL else ORANGE

    def update(self, platforms, player_pos):
        if not self.active:
            return False

        # Decrease frozen level (thaw)
        if self.frozen_level > 0:
            self.frozen_level -= 0.3
            if self.frozen_level < 0:
                self.frozen_level = 0
            return True  # Can't move while frozen

        # Apply gravity
        self.vel.y += GRAVITY

        # AI behavior based on type
        if self.enemy_type == EntityType.ENEMY_PATROL:
            self._patrol()
        else:
            self._chase(player_pos)

        # Move and check collisions
        new_pos_x = self.pos.x + self.vel.x
        new_pos_y = self.pos.y + self.vel.y

        # Horizontal collision
        tile_x_left = int((new_pos_x) // TILE_SIZE)
        tile_x_right = int((new_pos_x + self.width) // TILE_SIZE)
        tile_y = int(self.pos.y // TILE_SIZE)

        can_move_x = True
        for tx in [tile_x_left, tile_x_right]:
            for ty in [tile_y, tile_y + 1]:
                if (tx >= 0 and tx < len(LEVEL_LAYOUT[0]) and
                    ty >= 0 and ty < len(LEVEL_LAYOUT)):
                    if LEVEL_LAYOUT[ty][tx] == '1':
                        can_move_x = False
                        self.direction = Direction.LEFT if self.direction == Direction.RIGHT else Direction.RIGHT
                        break

        if can_move_x:
            self.pos.x = new_pos_x

        # Vertical collision
        tile_y_bottom = int((new_pos_y + self.height) // TILE_SIZE)
        tile_x = int((self.pos.x + self.width // 2) // TILE_SIZE)

        self.on_ground = False
        if (tile_x >= 0 and tile_x < len(LEVEL_LAYOUT[0]) and
            tile_y_bottom >= 0 and tile_y_bottom < len(LEVEL_LAYOUT)):
            if LEVEL_LAYOUT[tile_y_bottom][tile_x] == '1':
                if self.vel.y > 0:
                    self.pos.y = tile_y_bottom * TILE_SIZE - self.height
                    self.vel.y = 0
                    self.on_ground = True

        if not self.on_ground:
            self.pos.y = new_pos_y

        return True

    def _patrol(self):
        speed = 2
        self.vel.x = speed * self.direction.value

        # Check patrol bounds
        if self.pos.x > self.patrol_start + self.patrol_range:
            self.direction = Direction.LEFT
        elif self.pos.x < self.patrol_start - self.patrol_range:
            self.direction = Direction.RIGHT

    def _chase(self, player_pos):
        speed = 1.5

        if player_pos.x > self.pos.x:
            self.direction = Direction.RIGHT
        else:
            self.direction = Direction.LEFT

        self.vel.x = speed * self.direction.value

    def hit_by_snow(self):
        """Increase frozen level when hit by snow."""
        self.frozen_level += 25
        return self.frozen_level >= 100

    def get_rect(self):
        return pygame.Rect(int(self.pos.x), int(self.pos.y), self.width, self.height)

    def draw(self, surface):
        # Draw frozen ice overlay
        if self.frozen_level > 0:
            ice_alpha = int(255 * (self.frozen_level / 100))
            ice_color = (200, 240, 255)

            # Ice block
            ice_rect = pygame.Rect(
                int(self.pos.x - 5),
                int(self.pos.y - 5),
                self.width + 10,
                self.height + 10
            )
            ice_surface = pygame.Surface((ice_rect.width, ice_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(ice_surface, (*ice_color, ice_alpha // 2), ice_surface.get_rect())
            pygame.draw.rect(ice_surface, (*WHITE, ice_alpha), ice_surface.get_rect(), 2)
            surface.blit(ice_surface, ice_rect.topleft)

        # Draw enemy body
        rect = self.get_rect()
        pygame.draw.rect(surface, self.color, rect, border_radius=8)

        # Eyes
        eye_offset = -4 if self.direction == Direction.LEFT else 4
        pygame.draw.circle(surface, WHITE, (int(rect.centerx + eye_offset), int(rect.centery - 4)), 5)
        pygame.draw.circle(surface, BLACK, (int(rect.centerx + eye_offset), int(rect.centery - 4)), 2)

        # Angry eyebrows
        pygame.draw.line(surface, BLACK,
                        (int(rect.centerx - 8 + eye_offset), int(rect.centery - 10)),
                        (int(rect.centerx + eye_offset), int(rect.centery - 8)), 2)
        pygame.draw.line(surface, BLACK,
                        (int(rect.centerx + eye_offset), int(rect.centery - 8)),
                        (int(rect.centerx + 8 + eye_offset), int(rect.centery - 10)), 2)


class Player:
    """Player character with movement, jumping, and snow shooting."""
    def __init__(self, x: float, y: float):
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.width = 32
        self.height = 40
        self.direction = Direction.RIGHT
        self.on_ground = False
        self.shoot_cooldown = 0
        self.lives = 3
        self.score = 0
        self.invincible = 0

    def update(self, keys, platforms):
        # Horizontal movement
        self.vel.x = 0
        if keys[pygame.K_LEFT]:
            self.vel.x = -MOVE_SPEED
            self.direction = Direction.LEFT
        if keys[pygame.K_RIGHT]:
            self.vel.x = MOVE_SPEED
            self.direction = Direction.RIGHT

        # Jumping
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel.y = JUMP_FORCE
            self.on_ground = False

        # Apply gravity
        self.vel.y += GRAVITY

        # Move and check collisions
        new_pos_x = self.pos.x + self.vel.x
        new_pos_y = self.pos.y + self.vel.y

        # Horizontal collision
        tile_x_left = int((new_pos_x) // TILE_SIZE)
        tile_x_right = int((new_pos_x + self.width) // TILE_SIZE)
        tile_y = int(self.pos.y // TILE_SIZE)

        can_move_x = True
        for tx in [tile_x_left, tile_x_right]:
            for ty in [tile_y, tile_y + 1]:
                if (tx >= 0 and tx < len(LEVEL_LAYOUT[0]) and
                    ty >= 0 and ty < len(LEVEL_LAYOUT)):
                    if LEVEL_LAYOUT[ty][tx] == '1':
                        can_move_x = False
                        break

        if can_move_x:
            self.pos.x = new_pos_x

        # Vertical collision
        tile_y_bottom = int((new_pos_y + self.height) // TILE_SIZE)
        tile_x = int((self.pos.x + self.width // 2) // TILE_SIZE)

        self.on_ground = False
        if (tile_x >= 0 and tile_x < len(LEVEL_LAYOUT[0]) and
            tile_y_bottom >= 0 and tile_y_bottom < len(LEVEL_LAYOUT)):
            if LEVEL_LAYOUT[tile_y_bottom][tile_x] == '1':
                if self.vel.y > 0:
                    self.pos.y = tile_y_bottom * TILE_SIZE - self.height
                    self.vel.y = 0
                    self.on_ground = True

        if not self.on_ground:
            self.pos.y = new_pos_y

        # Screen bounds
        self.pos.x = max(0, min(self.pos.x, SCREEN_WIDTH - self.width))

        # Cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.invincible > 0:
            self.invincible -= 1

    def can_shoot(self):
        return self.shoot_cooldown == 0

    def shoot(self):
        self.shoot_cooldown = 20
        spawn_x = self.pos.x + (self.width if self.direction == Direction.RIGHT else -10)
        return Projectile(spawn_x, self.pos.y + self.height // 2, self.direction)

    def get_rect(self):
        return pygame.Rect(int(self.pos.x), int(self.pos.y), self.width, self.height)

    def take_damage(self):
        if self.invincible == 0:
            self.lives -= 1
            self.invincible = 120
            return True
        return False

    def draw(self, surface):
        # Blink when invincible
        if self.invincible > 0 and (self.invincible // 4) % 2 == 0:
            return

        rect = self.get_rect()

        # Body
        pygame.draw.rect(surface, BLUE, rect, border_radius=8)

        # Hat
        hat_rect = pygame.Rect(int(rect.x + 4), int(rect.y), rect.width - 8, 12)
        pygame.draw.rect(surface, DARK_BLUE, hat_rect, border_radius=4)

        # Face
        face_color = (255, 220, 180)
        face_rect = pygame.Rect(int(rect.x + 6), int(rect.y + 14), rect.width - 12, 16)
        pygame.draw.rect(surface, face_color, face_rect, border_radius=4)

        # Eyes
        eye_offset = -2 if self.direction == Direction.LEFT else 2
        pygame.draw.circle(surface, BLACK,
                          (int(rect.centerx + eye_offset), int(rect.y + 20)), 3)

        # Scarf
        scarf_rect = pygame.Rect(int(rect.x + 4), int(rect.y + 28), rect.width - 8, 6)
        pygame.draw.rect(surface, RED, scarf_rect, border_radius=2)


class Game:
    """Main game class."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Snow Bros - Platform Clear")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.reset_game()

    def reset_game(self):
        self.player = Player(SCREEN_WIDTH // 2, 100)
        self.enemies: List[Enemy] = []
        self.snowballs: List[Snowball] = []
        self.projectiles: List[Projectile] = []
        self.particles: List[SnowParticle] = []
        self.snow_particles: List[SnowParticle] = []
        self.state = GameState.PLAYING
        self.level_cleared_timer = 0

        # Spawn enemies
        self._spawn_enemies()

    def _spawn_enemies(self):
        # Patrol enemies on platforms
        positions = [
            (150, 200, EntityType.ENEMY_PATROL),
            (400, 300, EntityType.ENEMY_PATROL),
            (600, 200, EntityType.ENEMY_CHASE),
            (250, 450, EntityType.ENEMY_CHASE),
            (500, 450, EntityType.ENEMY_PATROL),
        ]

        for x, y, etype in positions:
            self.enemies.append(Enemy(x, y, etype))

    def handle_input(self):
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if event.key == pygame.K_z and self.state == GameState.PLAYING:
                    if self.player.can_shoot():
                        self.projectiles.append(self.player.shoot())

                # Restart
                if event.key == pygame.K_r and self.state != GameState.PLAYING:
                    self.reset_game()

        if self.state == GameState.PLAYING:
            self.player.update(keys, LEVEL_LAYOUT)

        return True

    def update(self):
        if self.state != GameState.PLAYING:
            return

        # Update projectiles
        self.projectiles = [p for p in self.projectiles if p.update(LEVEL_LAYOUT)]

        # Update enemies
        for enemy in self.enemies[:]:
            if not enemy.update(LEVEL_LAYOUT, self.player.pos):
                self.enemies.remove(enemy)
                continue

            # Check projectile collision
            enemy_rect = enemy.get_rect()
            for proj in self.projectiles[:]:
                proj_pos = proj.pos.to_tuple()
                if enemy_rect.collidepoint(proj_pos):
                    self.projectiles.remove(proj)
                    if enemy.hit_by_snow():
                        # Convert to snowball
                        snowball = Snowball(enemy.pos.x, enemy.pos.y)
                        self.snowballs.append(snowball)
                        self.enemies.remove(enemy)
                        self.player.score += 100
                    self._create_snow_particles(proj.pos.x, proj.pos.y)
                    break

            # Check player collision
            if self.player.invincible == 0:
                player_rect = self.player.get_rect()
                if player_rect.colliderect(enemy_rect):
                    if self.player.take_damage():
                        if self.player.lives <= 0:
                            self.state = GameState.GAME_OVER

        # Update snowballs
        for snowball in self.snowballs[:]:
            if not snowball.update(LEVEL_LAYOUT):
                self.snowballs.remove(snowball)
                continue

            # Check snowball collision with enemies
            ball_rect = pygame.Rect(
                int(snowball.pos.x - snowball.radius),
                int(snowball.pos.y - snowball.radius),
                snowball.radius * 2,
                snowball.radius * 2
            )

            for enemy in self.enemies[:]:
                if ball_rect.colliderect(enemy.get_rect()):
                    self.enemies.remove(enemy)
                    self.player.score += 500
                    self._create_snow_particles(enemy.pos.x, enemy.pos.y, count=15)

            # Player can push snowballs
            if snowball.push_cooldown == 0:
                player_rect = self.player.get_rect()
                if player_rect.colliderect(ball_rect):
                    # Determine push direction
                    if self.player.pos.x < snowball.pos.x:
                        snowball.vel.x = max(snowball.vel.x, 5)
                    else:
                        snowball.vel.x = min(snowball.vel.x, -5)
                    snowball.push_cooldown = 10

        # Update snow particles
        self.snow_particles = [p for p in self.snow_particles if p.update()]

        # Check level cleared
        if not self.enemies:
            self.state = GameState.LEVEL_CLEARED
            self.level_cleared_timer = 180
            self.player.score += 1000

    def _create_snow_particles(self, x: float, y: float, count: int = 8):
        import random
        for _ in range(count):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-5, -1)
            self.snow_particles.append(SnowParticle(x, y, vx, vy))

    def draw(self):
        self.screen.fill(BLACK)

        # Draw platforms
        for y, row in enumerate(LEVEL_LAYOUT):
            for x, cell in enumerate(row):
                if cell == '1':
                    rect = pygame.Rect(
                        x * TILE_SIZE,
                        y * TILE_SIZE,
                        TILE_SIZE,
                        TILE_SIZE
                    )
                    pygame.draw.rect(self.screen, GRAY, rect)
                    pygame.draw.rect(self.screen, (150, 150, 150), rect, 2)
                    # Add brick pattern
                    pygame.draw.line(self.screen, (80, 80, 80),
                                    (rect.x, rect.centery), (rect.right, rect.centery), 1)

        # Draw snowballs
        for snowball in self.snowballs:
            snowball.draw(self.screen)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw projectiles
        for proj in self.projectiles:
            proj.draw(self.screen)

        # Draw snow particles
        for particle in self.snow_particles:
            particle.draw(self.screen)

        # Draw HUD
        score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, RED)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))

        # Draw game state overlays
        if self.state == GameState.LEVEL_CLEARED:
            self._draw_centered_text("LEVEL CLEARED!", GREEN, -50)
            self._draw_centered_text(f"Bonus: +1000", YELLOW, 10)
            self._draw_centered_text("Press R to continue", WHITE, 60)

        elif self.state == GameState.GAME_OVER:
            self._draw_centered_text("GAME OVER", RED, -50)
            self._draw_centered_text(f"Final Score: {self.player.score}", YELLOW, 10)
            self._draw_centered_text("Press R to restart", WHITE, 60)

        pygame.display.flip()

    def _draw_centered_text(self, text: str, color, y_offset: int):
        surface = self.large_font.render(text, True, color)
        rect = surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
        self.screen.blit(surface, rect)

    def run(self):
        while True:
            if not self.handle_input():
                break

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
