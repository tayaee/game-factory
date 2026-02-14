"""Main game logic for Vector Super Mario Bros Fire Flower Sniping."""

import math
import random
import pygame
from config import *


class Fireball:
    """Represents a fireball projectile with bouncing physics."""

    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * FIREBALL_SPEED
        self.vy = -math.sin(angle) * FIREBALL_SPEED
        self.radius = 8
        self.active = True
        self.bounces = 0
        self.lifetime = FIREBALL_LIFETIME

    def update(self, platforms):
        """Update fireball position and handle bounces."""
        if not self.active:
            return

        # Apply gravity
        self.vy += GRAVITY

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Decrease lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False
            return

        # Floor bounce
        if self.y >= SCREEN_HEIGHT - 20 - self.radius:
            self.y = SCREEN_HEIGHT - 20 - self.radius
            self.vy = -self.vy * BOUNCE_VELOCITY_MULTIPLIER
            self.bounces += 1

        # Ceiling bounce
        if self.y <= self.radius:
            self.y = self.radius
            self.vy = -self.vy * BOUNCE_VELOCITY_MULTIPLIER
            self.bounces += 1

        # Wall bounce
        if self.x >= SCREEN_WIDTH - self.radius:
            self.x = SCREEN_WIDTH - self.radius
            self.vx = -self.vx * BOUNCE_VELOCITY_MULTIPLIER
            self.bounces += 1
        elif self.x <= self.radius:
            self.x = self.radius
            self.vx = -self.vx * BOUNCE_VELOCITY_MULTIPLIER
            self.bounces += 1

        # Platform bounces
        for platform in platforms:
            if self.check_platform_collision(platform):
                self.handle_platform_bounce(platform)
                self.bounces += 1

        # Check if should deactivate
        if self.bounces >= FIREBALL_MAX_BOUNCES:
            self.active = False

    def check_platform_collision(self, platform):
        """Check collision with a platform."""
        if self.x + self.radius > platform.x and self.x - self.radius < platform.x + platform.width:
            if self.y + self.radius > platform.y and self.y - self.radius < platform.y + platform.height:
                return True
        return False

    def handle_platform_bounce(self, platform):
        """Handle bounce off a platform."""
        # Determine which side was hit
        overlap_left = (self.x + self.radius) - platform.x
        overlap_right = (platform.x + platform.width) - (self.x - self.radius)
        overlap_top = (self.y + self.radius) - platform.y
        overlap_bottom = (platform.y + platform.height) - (self.y - self.radius)

        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

        if min_overlap == overlap_top:
            self.y = platform.y - self.radius
            self.vy = -abs(self.vy) * BOUNCE_VELOCITY_MULTIPLIER
        elif min_overlap == overlap_bottom:
            self.y = platform.y + platform.height + self.radius
            self.vy = abs(self.vy) * BOUNCE_VELOCITY_MULTIPLIER
        elif min_overlap == overlap_left:
            self.x = platform.x - self.radius
            self.vx = -abs(self.vx) * BOUNCE_VELOCITY_MULTIPLIER
        else:
            self.x = platform.x + platform.width + self.radius
            self.vx = abs(self.vx) * BOUNCE_VELOCITY_MULTIPLIER

    def draw(self, surface):
        """Draw the fireball."""
        if not self.active:
            return

        # Draw main fireball
        pygame.draw.circle(surface, COLOR_ORANGE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, COLOR_YELLOW, (int(self.x - 2), int(self.y - 2)), self.radius // 2)

        # Draw glow effect
        for i in range(3):
            alpha = 100 - i * 30
            glow_radius = self.radius + (i + 1) * 2
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*COLOR_ORANGE, alpha), (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surface, (int(self.x) - glow_radius, int(self.y) - glow_radius))

    def get_rect(self):
        """Get collision rectangle."""
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)


class Enemy:
    """Base class for enemies."""

    def __init__(self, x, y, width, height, color, enemy_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.enemy_type = enemy_type
        self.alive = True
        self.vx = random.choice([-1, 1]) * 0.5
        self.vy = 0

    def update(self):
        """Update enemy position."""
        self.x += self.vx

        # Bounce off screen edges
        if self.x <= 200 or self.x >= SCREEN_WIDTH - self.width:
            self.vx = -self.vx

    def draw(self, surface):
        """Draw the enemy."""
        if not self.alive:
            return

        pygame.draw.rect(surface, self.color, (int(self.x), int(self.y), self.width, self.height))

        # Draw face based on type
        if self.enemy_type == "goomba":
            # Eyes
            pygame.draw.circle(surface, COLOR_WHITE, (int(self.x + 8), int(self.y + 10)), 4)
            pygame.draw.circle(surface, COLOR_WHITE, (int(self.x + self.width - 8), int(self.y + 10)), 4)
            pygame.draw.circle(surface, COLOR_BLACK, (int(self.x + 8), int(self.y + 10)), 2)
            pygame.draw.circle(surface, COLOR_BLACK, (int(self.x + self.width - 8), int(self.y + 10)), 2)
            # Eyebrows
            pygame.draw.line(surface, COLOR_BLACK, (self.x + 4, self.y + 5), (self.x + 12, self.y + 8), 2)
            pygame.draw.line(surface, COLOR_BLACK, (self.x + self.width - 12, self.y + 8), (self.x + self.width - 4, self.y + 5), 2)

    def get_rect(self):
        """Get collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class PiranhaPlant(Enemy):
    """Piranha Plant enemy that stays in position."""

    def __init__(self, x, y):
        super().__init__(x, y, 25, PIRANHA_HEIGHT, COLOR_RED, "piranha")
        self.anim_offset = random.random() * math.pi * 2
        self.base_y = y

    def update(self):
        """Animate piranha plant."""
        import time
        offset = math.sin(time.time() * 3 + self.anim_offset) * 5
        self.y = self.base_y + offset

    def draw(self, surface):
        """Draw piranha plant."""
        if not self.alive:
            return

        # Stem
        stem_width = 6
        pygame.draw.rect(surface, COLOR_GREEN, (int(self.x + self.width // 2 - stem_width // 2), int(self.y), stem_width, 20))

        # Head (mouth)
        head_y = self.y - 10
        pygame.draw.circle(surface, self.color, (int(self.x + self.width // 2), int(head_y)), self.width // 2)

        # Teeth
        for i in range(4):
            tooth_x = self.x + 5 + i * 6
            pygame.draw.polygon(surface, COLOR_WHITE, [
                (tooth_x, head_y + 5),
                (tooth_x + 3, head_y + 12),
                (tooth_x + 6, head_y + 5)
            ])

        # Eyes
        pygame.draw.circle(surface, COLOR_WHITE, (int(self.x + 8), int(head_y - 3)), 4)
        pygame.draw.circle(surface, COLOR_WHITE, (int(self.x + self.width - 8), int(head_y - 3)), 4)
        pygame.draw.circle(surface, COLOR_BLACK, (int(self.x + 8), int(head_y - 3)), 2)
        pygame.draw.circle(surface, COLOR_BLACK, (int(self.x + self.width - 8), int(head_y - 3)), 2)


class Player:
    """Represents Mario (the player)."""

    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT - 60
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.arm_angle = math.pi / 4  # 45 degrees up
        self.min_arm_angle = math.pi / 6
        self.max_arm_angle = math.pi * 2 / 3

    def move_left(self):
        """Move player left."""
        self.x = max(50, self.x - PLAYER_SPEED)

    def move_right(self):
        """Move player right."""
        self.x = min(200, self.x + PLAYER_SPEED)

    def adjust_aim(self, delta):
        """Adjust aim angle."""
        self.arm_angle = max(self.min_arm_angle, min(self.max_arm_angle, self.arm_angle + delta))

    def get_fireball_spawn_position(self):
        """Get position to spawn fireball."""
        spawn_x = self.x + math.cos(self.arm_angle) * 25
        spawn_y = self.y - math.sin(self.arm_angle) * 25
        return spawn_x, spawn_y

    def draw(self, surface):
        """Draw Mario."""
        # Body
        pygame.draw.rect(surface, COLOR_RED, (int(self.x), int(self.y), self.width, self.height))

        # Face
        face_x = self.x + self.width // 2
        face_y = self.y - 5
        pygame.draw.circle(surface, COLOR_ORANGE, (int(face_x), int(face_y)), 12)

        # Hat
        pygame.draw.rect(surface, COLOR_RED, (int(face_x - 12), int(face_y - 15), 24, 8))

        # Eyes
        pygame.draw.circle(surface, COLOR_BLACK, (int(face_x - 4), int(face_y - 2)), 2)
        pygame.draw.circle(surface, COLOR_BLACK, (int(face_x + 4), int(face_y - 2)), 2)

        # Mustache
        pygame.draw.line(surface, COLOR_BLACK, (face_x - 6, face_y + 4), (face_x + 6, face_y + 4), 2)

        # Arm (aiming indicator)
        arm_end_x = self.x + self.width // 2 + math.cos(self.arm_angle) * 25
        arm_end_y = self.y - math.sin(self.arm_angle) * 25
        pygame.draw.line(surface, COLOR_ORANGE, (self.x + self.width // 2, self.y), (arm_end_x, arm_end_y), 6)

        # Hand
        pygame.draw.circle(surface, COLOR_WHITE, (int(arm_end_x), int(arm_end_y)), 5)

    def get_rect(self):
        """Get collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Platform:
    """Represents a platform that fireballs can bounce off."""

    def __init__(self, x, y, width):
        self.x = x
        self.y = y
        self.width = width
        self.height = PLATFORM_HEIGHT

    def draw(self, surface):
        """Draw the platform."""
        pygame.draw.rect(surface, COLOR_BROWN, (int(self.x), int(self.y), self.width, self.height))
        pygame.draw.rect(surface, COLOR_DARK_GREEN, (int(self.x), int(self.y), self.width, 3))

    def get_rect(self):
        """Get collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Game:
    """Main game class managing all game state."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Super Mario Bros Fire Flower Sniping")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        """Reset game to initial state."""
        self.player = Player()
        self.fireballs = []
        self.enemies = []
        self.platforms = []
        self.score = 0
        self.fireballs_remaining = FIREBALL_LIMIT_PER_STAGE
        self.lives = STARTING_LIVES
        self.stage = 1
        self.game_over = False
        self.won = False
        self.stage_cleared = False

        self.generate_stage()

    def generate_stage(self):
        """Generate a new stage with enemies and platforms."""
        self.enemies = []
        self.platforms = []
        self.fireballs = []
        self.fireballs_remaining = FIREBALL_LIMIT_PER_STAGE
        self.stage_cleared = False

        # Generate platforms
        num_platforms = 2 + self.stage // 2
        for i in range(num_platforms):
            plat_x = random.randint(250, SCREEN_WIDTH - 150)
            plat_y = random.randint(150, SCREEN_HEIGHT - 200)
            plat_width = random.randint(80, 150)
            self.platforms.append(Platform(plat_x, plat_y, plat_width))

        # Generate enemies
        num_enemies = 3 + self.stage * 2
        for i in range(num_enemies):
            if random.random() < 0.3:
                # Piranha plant (stationary)
                enemy_x = random.randint(250, SCREEN_WIDTH - 50)
                enemy_y = random.randint(100, SCREEN_HEIGHT - 150)
                self.enemies.append(PiranhaPlant(enemy_x, enemy_y))
            else:
                # Goomba (moving)
                enemy_x = random.randint(250, SCREEN_WIDTH - 50)
                enemy_y = random.randint(100, SCREEN_HEIGHT - 100)
                self.enemies.append(Enemy(enemy_x, enemy_y, ENEMY_WIDTH, ENEMY_HEIGHT, COLOR_BROWN, "goomba"))

    def handle_input(self):
        """Handle keyboard input."""
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.player.move_left()
        if keys[pygame.K_RIGHT]:
            self.player.move_right()
        if keys[pygame.K_UP]:
            self.player.adjust_aim(0.05)
        if keys[pygame.K_DOWN]:
            self.player.adjust_aim(-0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over and not self.stage_cleared:
                    if self.fireballs_remaining > 0:
                        spawn_x, spawn_y = self.player.get_fireball_spawn_position()
                        self.fireballs.append(Fireball(spawn_x, spawn_y, self.player.arm_angle))
                        self.fireballs_remaining -= 1
                elif event.key == pygame.K_r:
                    if self.game_over:
                        self.score = 0
                        self.stage = 1
                        self.lives = STARTING_LIVES
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    return False

        return True

    def update(self):
        """Update game state."""
        if self.game_over:
            return

        if self.stage_cleared:
            self.stage += 1
            self.generate_stage()
            return

        # Update enemies
        for enemy in self.enemies:
            enemy.update()

            # Check if enemy reached player
            if enemy.x <= self.player.x + self.player.width:
                self.lives -= 1
                self.enemies.remove(enemy)
                if self.lives <= 0:
                    self.game_over = True

        # Update fireballs
        for fireball in self.fireballs[:]:
            fireball.update(self.platforms)

            if not fireball.active:
                if fireball in self.fireballs:
                    self.fireballs.remove(fireball)
                continue

            # Check collision with enemies
            fireball_rect = fireball.get_rect()
            for enemy in self.enemies[:]:
                enemy_rect = enemy.get_rect()
                if fireball_rect.colliderect(enemy_rect):
                    # Calculate score based on bounces
                    bounce_bonus = 1 + (fireball.bounces * 0.5)
                    points = int(ENEMY_COLLISION_SCORE * bounce_bonus)
                    self.score += points

                    self.enemies.remove(enemy)
                    self.fireballs.remove(fireball)
                    break

        # Check stage clear
        if not self.enemies:
            self.score += STAGE_CLEAR_BONUS
            self.stage_cleared = True

        # Check game over (out of fireballs and enemies remain)
        if not self.enemies:
            pass  # Stage cleared
        elif self.fireballs_remaining == 0 and not self.fireballs:
            self.game_over = True
            self.won = False

    def draw(self):
        """Draw everything."""
        self.screen.fill(COLOR_BLACK)

        # Draw floor
        pygame.draw.rect(self.screen, COLOR_GRAY, (0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))

        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw fireballs
        for fireball in self.fireballs:
            fireball.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw trajectory guide
        spawn_x, spawn_y = self.player.get_fireball_spawn_position()
        guide_length = 40
        guide_x = spawn_x + math.cos(self.player.arm_angle) * guide_length
        guide_y = spawn_y - math.sin(self.player.arm_angle) * guide_length
        pygame.draw.line(self.screen, COLOR_GRAY, (spawn_x, spawn_y), (guide_x, guide_y), 2)

        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_WHITE)
        stage_text = self.font.render(f"Stage: {self.stage}", True, COLOR_WHITE)
        fireballs_text = self.font.render(f"Fireballs: {self.fireballs_remaining}", True, COLOR_ORANGE)
        lives_text = self.font.render(f"Lives: {self.lives}", True, COLOR_RED)

        self.screen.blit(score_text, (20, 10))
        self.screen.blit(stage_text, (20, 50))
        self.screen.blit(fireballs_text, (SCREEN_WIDTH - 180, 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 180, 50))

        # Draw stage cleared message
        if self.stage_cleared:
            msg = f"STAGE {self.stage - 1} CLEARED!"
            text = self.font.render(msg, True, COLOR_GREEN)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            pygame.draw.rect(self.screen, COLOR_BLACK, rect.inflate(20, 10))
            self.screen.blit(text, rect)

        # Draw game over message
        if self.game_over and not self.stage_cleared:
            msg = "GAME OVER! Press R to restart"
            text = self.font.render(msg, True, COLOR_RED)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            pygame.draw.rect(self.screen, COLOR_BLACK, rect.inflate(20, 10))
            self.screen.blit(text, rect)

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
