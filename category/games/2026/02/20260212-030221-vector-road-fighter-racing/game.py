"""Main game logic for Road Fighter Racing."""

import pygame
import random
import sys
from typing import List, Dict, Any

from config import *
from entities import Player, Enemy, FuelTank


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Road Fighter Racing")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)

        self.reset()
        self.game_state = STATE_MENU

    def reset(self):
        """Reset the game to initial state."""
        self.player = Player()
        self.enemies: List[Enemy] = []
        self.fuel_tanks: List[FuelTank] = []
        self.score = 0
        self.spawn_timer = 0
        self.fuel_spawn_timer = 0
        self.road_offset = 0.0
        self.difficulty = 1.0

    def get_observation(self) -> Dict[str, Any]:
        """Get current game state for AI agents."""
        visible_enemies = []
        for enemy in self.enemies:
            if enemy.is_visible(self.player.distance):
                rel_y = enemy.get_screen_y(self.player.distance)
                visible_enemies.append({
                    "lane": enemy.lane,
                    "relative_y": (WINDOW_HEIGHT - rel_y) / WINDOW_HEIGHT,
                    "erratic": enemy.erratic
                })

        visible_fuel = []
        for fuel in self.fuel_tanks:
            if fuel.is_visible(self.player.distance) and not fuel.collected:
                rel_y = fuel.get_screen_y(self.player.distance)
                visible_fuel.append({
                    "lane": fuel.lane,
                    "relative_y": (WINDOW_HEIGHT - rel_y) / WINDOW_HEIGHT
                })

        return {
            "player": {
                "lane": self.player.lane,
                "speed": self.player.velocity / PLAYER_MAX_SPEED,
                "fuel": self.player.fuel / MAX_FUEL,
                "distance": self.player.distance / TARGET_DISTANCE
            },
            "enemies": visible_enemies,
            "fuel": visible_fuel,
            "score": self.score,
            "game_state": self.game_state
        }

    def step_ai(self, action: int) -> tuple:
        """Execute AI action and return (observation, reward, done)."""
        prev_distance = self.player.distance
        prev_fuel = self.player.fuel
        prev_crashing = self.player.crashing

        # Actions: 0=left, 1=right, 2=accelerate, 3=brake, 4=nothing
        if action == 0:
            self.player.change_lane(-1)
        elif action == 1:
            self.player.change_lane(1)
        elif action == 2:
            self.player.accelerate()
        elif action == 3:
            self.player.brake()

        self.update()

        reward = (self.player.distance - prev_distance) * SCORE_PER_DISTANCE
        reward += (prev_fuel - self.player.fuel) * 0.1

        if self.player.crashing and not prev_crashing:
            reward -= CRASH_PENALTY

        done = self.game_state in [STATE_GAME_OVER, STATE_WIN]

        return self.get_observation(), reward, done

    def _spawn_enemy(self):
        """Spawn a new enemy ahead of the player."""
        spawn_distance = self.player.distance + WINDOW_HEIGHT + random.randint(50, 200)

        # Check if spawn position is clear
        for enemy in self.enemies:
            if abs(enemy.distance - spawn_distance) < 100:
                return  # Too close to existing enemy

        # Difficulty increases over time
        erratic_chance = 0.1 + (self.player.distance / TARGET_DISTANCE) * 0.3
        erratic = random.random() < erratic_chance

        self.enemies.append(Enemy(spawn_distance, erratic))

    def _spawn_fuel(self):
        """Spawn a fuel tank ahead of the player."""
        spawn_distance = self.player.distance + WINDOW_HEIGHT + random.randint(100, 300)
        self.fuel_tanks.append(FuelTank(spawn_distance))

    def _check_collisions(self):
        """Check for collisions between entities."""
        player_rect = self.player.get_rect()

        # Check enemy collisions
        for enemy in self.enemies[:]:
            enemy_rect = enemy.get_rect(self.player.distance)
            if player_rect.colliderect(enemy_rect):
                if self.player.crash():
                    self.enemies.remove(enemy)

        # Check fuel collection
        for fuel in self.fuel_tanks:
            if not fuel.collected:
                fuel_rect = fuel.get_rect(self.player.distance)
                if player_rect.colliderect(fuel_rect):
                    fuel.collected = True
                    self.player.fuel = min(MAX_FUEL, self.player.fuel + FUEL_AMOUNT)
                    self.score += FUEL_BONUS_MULTIPLIER * FUEL_AMOUNT

    def update(self):
        """Main game update loop."""
        if self.game_state != STATE_PLAYING:
            return

        self.player.update()

        # Update road offset for scrolling effect
        self.road_offset = (self.road_offset + self.player.velocity) % 40

        # Spawn enemies
        spawn_rate = max(60, int(120 - self.player.distance / 200))
        self.spawn_timer += 1
        if self.spawn_timer >= spawn_rate:
            self.spawn_timer = 0
            if len(self.enemies) < 10:
                self._spawn_enemy()

        # Spawn fuel
        self.fuel_spawn_timer += 1
        if self.fuel_spawn_timer >= FUEL_SPAWN_INTERVAL:
            self.fuel_spawn_timer = 0
            if len(self.fuel_tanks) < 3:
                self._spawn_fuel()

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.distance < self.player.distance - 100:
                self.enemies.remove(enemy)

        # Clean up collected fuel
        self.fuel_tanks = [f for f in self.fuel_tanks
                          if not f.collected and f.distance > self.player.distance - 100]

        # Update score based on distance
        self.score = int(self.player.distance)

        # Check collisions
        self._check_collisions()

        # Check win/lose conditions
        if self.player.distance >= TARGET_DISTANCE:
            self.game_state = STATE_WIN
        elif self.player.fuel <= 0:
            self.game_state = STATE_GAME_OVER

    def draw_road(self):
        """Draw the scrolling road."""
        # Draw grass background
        self.screen.fill(COLOR_BG)

        # Draw road
        road_rect = pygame.Rect(ROAD_LEFT, 0, ROAD_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_ROAD, road_rect)

        # Draw road borders
        pygame.draw.line(self.screen, COLOR_ROAD_LINE, (ROAD_LEFT, 0), (ROAD_LEFT, WINDOW_HEIGHT), 3)
        pygame.draw.line(self.screen, COLOR_ROAD_LINE, (ROAD_RIGHT, 0), (ROAD_RIGHT, WINDOW_HEIGHT), 3)

        # Draw lane markings
        for i in range(1, NUM_LANES):
            x = ROAD_LEFT + i * LANE_WIDTH
            for y in range(int(-self.road_offset), WINDOW_HEIGHT, 40):
                pygame.draw.line(self.screen, COLOR_ROAD_LINE, (x, y), (x, y + 20), 2)

    def draw_entities(self):
        """Draw all game entities."""
        # Draw fuel tanks
        for fuel in self.fuel_tanks:
            if fuel.is_visible(self.player.distance) and not fuel.collected:
                rect = fuel.get_rect(self.player.distance)
                pygame.draw.rect(self.screen, COLOR_FUEL, rect)
                pygame.draw.rect(self.screen, (200, 150, 0), rect, 2)
                # Draw 'F' on fuel
                f_text = self.tiny_font.render("F", True, (0, 0, 0))
                self.screen.blit(f_text, (rect.centerx - f_text.get_width() // 2,
                                         rect.centery - f_text.get_height() // 2))

        # Draw enemies
        for enemy in self.enemies:
            if enemy.is_visible(self.player.distance):
                rect = enemy.get_rect(self.player.distance)
                color = COLOR_ERRATIC if enemy.erratic else COLOR_ENEMY
                pygame.draw.rect(self.screen, color, rect)

                # Car details
                pygame.draw.rect(self.screen, (50, 50, 50),
                               (rect.x + 5, rect.y + 5, rect.width - 10, 10))  # Windshield
                pygame.draw.rect(self.screen, (200, 50, 50),
                               (rect.x + 3, rect.y + rect.height - 8, 8, 5))  # Left taillight
                pygame.draw.rect(self.screen, (200, 50, 50),
                               (rect.x + rect.width - 11, rect.y + rect.height - 8, 8, 5))  # Right taillight

        # Draw player
        player_rect = self.player.get_rect()

        # Flashing when invincible
        if self.player.invincible > 0 and (self.player.invincible // 4) % 2 == 0:
            pass  # Skip drawing to flash
        else:
            # Car body
            pygame.draw.rect(self.screen, COLOR_PLAYER, player_rect)

            # Windshield
            pygame.draw.rect(self.screen, (100, 150, 200),
                           (player_rect.x + 5, player_rect.y + player_rect.height - 20,
                            player_rect.width - 10, 12))

            # Wheels
            pygame.draw.rect(self.screen, (20, 20, 20),
                           (player_rect.x - 3, player_rect.y + 5, 6, 12))
            pygame.draw.rect(self.screen, (20, 20, 20),
                           (player_rect.x + player_rect.width - 3, player_rect.y + 5, 6, 12))
            pygame.draw.rect(self.screen, (20, 20, 20),
                           (player_rect.x - 3, player_rect.y + player_rect.height - 17, 6, 12))
            pygame.draw.rect(self.screen, (20, 20, 20),
                           (player_rect.x + player_rect.width - 3, player_rect.y + player_rect.height - 17, 6, 12))

    def draw_hud(self):
        """Draw the HUD."""
        # HUD background
        hud_height = 60
        pygame.draw.rect(self.screen, COLOR_HUD,
                        (0, WINDOW_HEIGHT - hud_height, WINDOW_WIDTH, hud_height))

        # Distance/Score
        distance_text = self.small_font.render(f"DISTANCE: {int(self.player.distance)}/{TARGET_DISTANCE}",
                                              True, COLOR_TEXT)
        self.screen.blit(distance_text, (10, WINDOW_HEIGHT - 50))

        # Speed
        speed_pct = int((self.player.velocity / PLAYER_MAX_SPEED) * 100)
        speed_text = self.small_font.render(f"SPEED: {speed_pct}%", True, COLOR_TEXT)
        self.screen.blit(speed_text, (10, WINDOW_HEIGHT - 25))

        # Fuel bar
        fuel_pct = self.player.fuel / MAX_FUEL
        fuel_color = COLOR_FUEL_BAR if fuel_pct > 0.3 else COLOR_FUEL_BAR_LOW
        fuel_bar_width = 150
        fuel_rect = pygame.Rect(WINDOW_WIDTH - fuel_bar_width - 10, WINDOW_HEIGHT - 45,
                               fuel_bar_width * fuel_pct, 20)
        pygame.draw.rect(self.screen, (50, 50, 50),
                        (WINDOW_WIDTH - fuel_bar_width - 10, WINDOW_HEIGHT - 45,
                         fuel_bar_width, 20))
        pygame.draw.rect(self.screen, fuel_color, fuel_rect)
        pygame.draw.rect(self.screen, COLOR_TEXT,
                        (WINDOW_WIDTH - fuel_bar_width - 10, WINDOW_HEIGHT - 45,
                         fuel_bar_width, 20), 2)

        fuel_text = self.small_font.render("FUEL", True, COLOR_TEXT)
        self.screen.blit(fuel_text, (WINDOW_WIDTH - fuel_bar_width - 50, WINDOW_HEIGHT - 42))

    def draw_menu(self):
        """Draw the menu screen."""
        self.screen.fill(COLOR_BG)
        self.draw_road()

        title_text = self.font.render("ROAD FIGHTER", True, COLOR_FUEL)
        self.screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 150))

        subtitle_text = self.small_font.render("RACING", True, COLOR_TEXT)
        self.screen.blit(subtitle_text, (WINDOW_WIDTH // 2 - subtitle_text.get_width() // 2, 190))

        instr_lines = [
            "Arrow LEFT/RIGHT: Change lanes",
            "Arrow UP: Accelerate",
            "Arrow DOWN: Brake",
            "Collect 'F' for fuel",
            "Avoid other cars!",
            "",
            "Press SPACE to start"
        ]

        y = 280
        for line in instr_lines:
            text = self.small_font.render(line, True, COLOR_TEXT)
            self.screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, y))
            y += 25

    def draw_game_over(self):
        """Draw the game over screen."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        go_text = self.font.render("OUT OF FUEL!", True, COLOR_FUEL_BAR_LOW)
        self.screen.blit(go_text, (WINDOW_WIDTH // 2 - go_text.get_width() // 2, 200))

        score_text = self.small_font.render(f"Distance: {int(self.player.distance)}", True, COLOR_TEXT)
        self.screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 250))

        restart_text = self.small_font.render("Press R to restart or ESC to quit", True, COLOR_TEXT)
        self.screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, 320))

    def draw_win(self):
        """Draw the win screen."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        win_text = self.font.render("YOU WIN!", True, COLOR_FUEL_BAR)
        self.screen.blit(win_text, (WINDOW_WIDTH // 2 - win_text.get_width() // 2, 200))

        score_text = self.small_font.render(f"Final Distance: {int(self.player.distance)}", True, COLOR_TEXT)
        self.screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 250))

        fuel_text = self.small_font.render(f"Fuel Remaining: {int(self.player.fuel)}", True, COLOR_TEXT)
        self.screen.blit(fuel_text, (WINDOW_WIDTH // 2 - fuel_text.get_width() // 2, 280))

        restart_text = self.small_font.render("Press R to restart or ESC to quit", True, COLOR_TEXT)
        self.screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, 350))

    def draw(self):
        """Render the game."""
        if self.game_state == STATE_MENU:
            self.draw_menu()
        else:
            self.draw_road()
            self.draw_entities()
            self.draw_hud()

            if self.game_state == STATE_GAME_OVER:
                self.draw_game_over()
            elif self.game_state == STATE_WIN:
                self.draw_win()

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True

        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif self.game_state == STATE_MENU:
                        if event.key == pygame.K_SPACE:
                            self.reset()
                            self.game_state = STATE_PLAYING

                    elif self.game_state == STATE_PLAYING:
                        if event.key == pygame.K_LEFT:
                            self.player.change_lane(-1)
                        elif event.key == pygame.K_RIGHT:
                            self.player.change_lane(1)

                    elif self.game_state in [STATE_GAME_OVER, STATE_WIN]:
                        if event.key == pygame.K_r:
                            self.reset()
                            self.game_state = STATE_PLAYING

            # Continuous input for acceleration/braking
            if self.game_state == STATE_PLAYING:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_UP]:
                    self.player.accelerate()
                elif keys[pygame.K_DOWN]:
                    self.player.brake()

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
