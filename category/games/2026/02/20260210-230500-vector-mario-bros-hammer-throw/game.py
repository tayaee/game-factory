"""Main game logic for Vector Mario Bros Hammer Throw."""

import pygame
import math
import random
from config import *
from entities import Player, Hammer, Enemy, Platform


class Game:
    """Main game class."""

    def __init__(self):
        """Initialize the game."""
        pygame.init()
        pygame.display.set_caption("Vector Mario Bros Hammer Throw")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)

        self.reset_game()

    def reset_game(self):
        """Reset game state."""
        self.player = Player(PLAYER_X, PLAYER_Y)
        self.platform = Platform(PLATFORM_Y)
        self.hammers = []
        self.enemies = []
        self.score = 0
        self.state = STATE_PLAYING
        self.spawn_timer = 0
        self.enemies_defeated = 0
        self.wave = 1
        self.multi_kill_timer = 0
        self.multi_kill_count = 0

        # Spawn initial enemies
        self.spawn_wave()

    def spawn_wave(self):
        """Spawn a wave of enemies."""
        self.enemies = []
        for i in range(min(5 + self.wave, MAX_ENEMIES)):
            platform_y = random.choice(PLATFORM_LEVELS)
            x = random.choice([150, SCREEN_WIDTH - 150])
            enemy_type = "koopa" if random.random() > 0.5 else "goomba"
            self.enemies.append(Enemy(x, platform_y, platform_y, enemy_type))

    def spawn_enemy(self):
        """Spawn a single enemy."""
        if len(self.enemies) < MAX_ENEMIES:
            platform_y = random.choice(PLATFORM_LEVELS)
            x = random.choice([150, SCREEN_WIDTH - 150])
            enemy_type = "koopa" if random.random() > 0.4 else "goomba"
            self.enemies.append(Enemy(x, platform_y, platform_y, enemy_type))

    def check_collision(self, hammer, enemy):
        """Check collision between hammer and enemy."""
        hammer_hitbox = hammer.get_hitbox()
        enemy_hitbox = enemy.get_hitbox()

        if hammer_hitbox["type"] == "circle" and enemy_hitbox["type"] == "rect":
            # Circle-rectangle collision
            closest_x = max(enemy_hitbox["x"],
                          min(hammer_hitbox["x"],
                              enemy_hitbox["x"] + enemy_hitbox["width"]))
            closest_y = max(enemy_hitbox["y"],
                          min(hammer_hitbox["y"],
                              enemy_hitbox["y"] + enemy_hitbox["height"]))

            distance_x = hammer_hitbox["x"] - closest_x
            distance_y = hammer_hitbox["y"] - closest_y
            distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

            return distance < hammer_hitbox["radius"]
        return False

    def check_player_collision(self):
        """Check collision between player and enemies."""
        player_hitbox = self.player.get_hitbox()

        for enemy in self.enemies:
            enemy_hitbox = enemy.get_hitbox()
            if (player_hitbox["x"] < enemy_hitbox["x"] + enemy_hitbox["width"] and
                player_hitbox["x"] + player_hitbox["width"] > enemy_hitbox["x"] and
                player_hitbox["y"] < enemy_hitbox["y"] + enemy_hitbox["height"] and
                player_hitbox["y"] + player_hitbox["height"] > enemy_hitbox["y"]):
                return True
        return False

    def update(self, dt):
        """Update game state."""
        if self.state != STATE_PLAYING:
            return

        # Update player
        self.player.update(dt)

        # Update charging
        if self.player.charging:
            self.player.update_charge(dt)

        # Update hammers
        for hammer in self.hammers[:]:
            result = hammer.update(dt)
            if result == "miss":
                self.hammers.remove(hammer)
                self.score += REWARD_MISS
                self.multi_kill_count = 0

        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt)

        # Check collisions
        hit_count = 0
        for hammer in self.hammers[:]:
            for enemy in self.enemies[:]:
                if enemy.alive and self.check_collision(hammer, enemy):
                    enemy.alive = False
                    hammer.active = False
                    if hammer in self.hammers:
                        self.hammers.remove(hammer)
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                    hit_count += 1
                    self.enemies_defeated += 1
                    break

        if hit_count > 0:
            self.multi_kill_count += hit_count
            if self.multi_kill_count >= 2:
                self.score += REWARD_MULTI_KILL * hit_count
            else:
                self.score += REWARD_HIT * hit_count
            self.multi_kill_timer = 1.0

        # Multi-kill timeout
        if self.multi_kill_timer > 0:
            self.multi_kill_timer -= dt
            if self.multi_kill_timer <= 0:
                self.multi_kill_count = 0

        # Spawn enemies
        self.spawn_timer += dt * 1000
        if self.spawn_timer >= SPAWN_INTERVAL:
            self.spawn_timer = 0
            self.spawn_enemy()

        # Check player collision
        if self.check_player_collision():
            self.game_over()

        # Check wave complete
        if self.enemies_defeated >= ENEMIES_PER_WAVE * self.wave:
            self.wave += 1
            self.spawn_wave()

        # Check game over (no hammers left and no active hammers)
        if self.player.hammers_left <= 0 and len(self.hammers) == 0:
            self.game_over()

    def game_over(self):
        """End the game."""
        self.state = STATE_GAME_OVER
        self.score += REWARD_GAME_OVER

    def handle_input(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif self.state == STATE_PLAYING:
                    if event.key == pygame.K_SPACE:
                        self.player.start_charge()

                elif self.state in [STATE_GAME_OVER, STATE_VICTORY]:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and self.state == STATE_PLAYING:
                    hammer = self.player.release_throw()
                    if hammer:
                        self.hammers.append(hammer)

        # Continuous key handling
        if self.state == STATE_PLAYING:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.player.adjust_angle(60)
            if keys[pygame.K_DOWN]:
                self.player.adjust_angle(-60)

    def draw(self):
        """Draw the game."""
        self.screen.fill(COLOR_BG)

        # Draw platforms
        self.platform.draw(self.screen)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw hammers
        for hammer in self.hammers:
            hammer.draw(self.screen)

        # Draw angle indicator
        self.draw_angle_indicator()

        # Draw power bar
        if self.player.charging:
            self.draw_power_bar()

        # Draw UI
        self.draw_ui()

        # Draw game over screen
        if self.state == STATE_GAME_OVER:
            self.draw_game_over()

        pygame.display.flip()

    def draw_angle_indicator(self):
        """Draw the angle indicator."""
        center_x = self.player.x + self.player.width // 2
        center_y = self.player.y - 20
        length = 40

        angle_rad = math.radians(self.player.angle)
        end_x = center_x + math.cos(angle_rad) * length
        end_y = center_y - math.sin(angle_rad) * length

        pygame.draw.line(self.screen, COLOR_ANGLE_INDICATOR,
                        (center_x, center_y), (end_x, end_y), 2)

        # Draw arc
        rect = pygame.Rect(center_x - length, center_y - length, length * 2, length * 2)
        start_angle = math.radians(0)
        end_angle = math.radians(self.player.angle)
        pygame.draw.arc(self.screen, COLOR_ANGLE_INDICATOR, rect,
                       -end_angle, -start_angle, 1)

    def draw_power_bar(self):
        """Draw the power charging bar."""
        bar_width = 100
        bar_height = 10
        bar_x = self.player.x + self.player.width + 10
        bar_y = self.player.y - 50

        # Background
        pygame.draw.rect(self.screen, COLOR_POWER_BAR_BG,
                        (bar_x, bar_y, bar_width, bar_height))

        # Fill
        fill_width = int((self.player.power / MAX_POWER) * bar_width)
        pygame.draw.rect(self.screen, COLOR_POWER_BAR,
                        (bar_x, bar_y, fill_width, bar_height))

        # Border
        pygame.draw.rect(self.screen, (255, 255, 255),
                        (bar_x, bar_y, bar_width, bar_height), 1)

    def draw_ui(self):
        """Draw the UI elements."""
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_UI_TEXT)
        self.screen.blit(score_text, (10, 10))

        # Hammers
        hammer_text = self.font.render(f"Hammers: {self.player.hammers_left}", True, COLOR_UI_TEXT)
        self.screen.blit(hammer_text, (10, 35))

        # Angle
        angle_text = self.font.render(f"Angle: {int(self.player.angle)}", True, COLOR_UI_TEXT)
        self.screen.blit(angle_text, (10, 60))

        # Wave
        wave_text = self.font.render(f"Wave: {self.wave}", True, COLOR_UI_TEXT)
        self.screen.blit(wave_text, (10, 85))

        # Multi-kill
        if self.multi_kill_timer > 0:
            multi_text = self.font.render(f"Multi-Kill x{self.multi_kill_count}!",
                                        True, (255, 255, 0))
            self.screen.blit(multi_text, (SCREEN_WIDTH // 2 - 50, 100))

    def draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        go_text = self.large_font.render("GAME OVER", True, (255, 50, 50))
        self.screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, 200))

        # Score
        score_text = self.font.render(f"Final Score: {self.score}", True, COLOR_UI_TEXT)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 260))

        # Defeated
        defeated_text = self.font.render(f"Enemies Defeated: {self.enemies_defeated}",
                                       True, COLOR_UI_TEXT)
        self.screen.blit(defeated_text, (SCREEN_WIDTH // 2 - defeated_text.get_width() // 2, 290))

        # Restart
        restart_text = self.font.render("Press R to Restart or ESC to Exit",
                                      True, (200, 200, 200))
        self.screen.blit(restart_text,
                        (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 350))

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            self.handle_input()
            self.update(dt)
            self.draw()

        pygame.quit()


def get_state():
    """Return current state for AI agents."""
    pass


def get_action_space():
    """Return action space description for AI agents."""
    pass
