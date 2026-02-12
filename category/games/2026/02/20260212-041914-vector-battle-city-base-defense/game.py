"""Main game logic for Battle City Base Defense."""

import pygame
import sys
import random
from typing import List, Dict, Any, Optional

from config import *
from entities import *


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Battle City Base Defense")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)

        self.reset()
        self.game_state = STATE_MENU

    def reset(self):
        """Reset the game to initial state."""
        self.grid = Grid()
        self.player = Player()
        self.enemies: List[Enemy] = []
        self.base = Base()
        self.score = 0
        self.spawn_timer = 0
        self.enemies_spawned = 0
        self.enemies_destroyed = 0
        self.wave = 1

    def get_observation(self) -> Dict[str, Any]:
        """Get current game state for AI agents."""
        grid_obs = []
        for x in range(GRID_COLS):
            row = []
            for y in range(GRID_ROWS):
                tile = self.grid.tiles[x][y]
                row.append(int(tile))
            grid_obs.append(row)

        enemies_obs = []
        for enemy in self.enemies:
            rel_x = (enemy.x - GRID_OFFSET_X) / (GRID_COLS * CELL_SIZE)
            rel_y = (enemy.y - GRID_OFFSET_Y) / (GRID_ROWS * CELL_SIZE)
            enemies_obs.append({
                "x": rel_x,
                "y": rel_y,
                "type": enemy.enemy_type,
                "direction": enemy.direction
            })

        player_obs = {
            "x": (self.player.x - GRID_OFFSET_X) / (GRID_COLS * CELL_SIZE),
            "y": (self.player.y - GRID_OFFSET_Y) / (GRID_ROWS * CELL_SIZE),
            "direction": self.player.direction,
            "lives": self.player.lives,
            "invincible": self.player.invincible > 0
        }

        base_obs = {
            "alive": self.base.alive,
            "x": self.base.grid_x / GRID_COLS,
            "y": self.base.grid_y / GRID_ROWS
        }

        return {
            "grid": grid_obs,
            "player": player_obs,
            "enemies": enemies_obs,
            "base": base_obs,
            "score": self.score,
            "enemies_remaining": ENEMY_TOTAL_COUNT - self.enemies_destroyed,
            "game_state": self.game_state
        }

    def step_ai(self, action: int) -> tuple:
        """Execute AI action and return (observation, reward, done)."""
        prev_score = self.score
        prev_lives = self.player.lives
        prev_base_alive = self.base.alive

        # Actions: 0=up, 1=down, 2=left, 3=right, 4=shoot, 5=nothing
        if action == 0:
            self.player.move(0, -1, self.grid)
        elif action == 1:
            self.player.move(0, 1, self.grid)
        elif action == 2:
            self.player.move(-1, 0, self.grid)
        elif action == 3:
            self.player.move(1, 0, self.grid)
        elif action == 4:
            if len(self.player.bullets) < PLAYER_MAX_BULLETS:
                bullet = self.player.shoot()
                if bullet:
                    self.player.bullets.append(bullet)

        self.update()

        reward = self.score - prev_score
        reward += (prev_lives - self.player.lives) * REWARD_LOSE_LIFE

        if prev_base_alive and not self.base.alive:
            reward += REWARD_BASE_DESTROYED

        done = self.game_state in [STATE_GAME_OVER, STATE_WIN]

        return self.get_observation(), reward, done

    def _check_bullet_collisions(self):
        """Check bullet collisions with grid, tanks, and base."""
        all_bullets = []

        # Collect player bullets
        for bullet in self.player.bullets:
            all_bullets.append((bullet, "player"))

        # Collect enemy bullets
        for enemy in self.enemies:
            for bullet in enemy.bullets:
                all_bullets.append((bullet, "enemy"))

        bullets_to_remove = []

        for bullet, owner in all_bullets:
            grid_x = int((bullet.x - GRID_OFFSET_X) // CELL_SIZE)
            grid_y = int((bullet.y - GRID_OFFSET_Y) // CELL_SIZE)

            # Check grid collision
            if not self.grid.is_bullet_passable(grid_x, grid_y):
                bullets_to_remove.append(bullet)
                if self.grid.is_destructible(grid_x, grid_y):
                    self.grid.destroy_tile(grid_x, grid_y)
                    self.score += REWARD_HIT_BRICK
                continue

            # Check base collision
            if grid_x == self.base.grid_x and grid_y == self.base.grid_y:
                bullets_to_remove.append(bullet)
                if self.base.alive:
                    self.base.damage()
                continue

            # Check tank collisions
            if owner == "player":
                # Check enemy tanks
                for enemy in self.enemies:
                    if enemy.alive:
                        enemy_rect = enemy.get_rect()
                        if enemy_rect.collidepoint(bullet.x, bullet.y):
                            bullets_to_remove.append(bullet)
                            self.enemies.remove(enemy)
                            self.enemies_destroyed += 1
                            self.score += enemy.get_score_value()
                            break
            else:
                # Check player tank
                if self.player.alive and self.player.invincible == 0:
                    player_rect = self.player.get_rect()
                    if player_rect.collidepoint(bullet.x, bullet.y):
                        bullets_to_remove.append(bullet)
                        self.player.lives -= 1
                        if self.player.lives > 0:
                            self.player.respawn()
                        else:
                            self.player.alive = False
                        break

        # Remove collided bullets
        for bullet in bullets_to_remove:
            if bullet in self.player.bullets:
                self.player.bullets.remove(bullet)
            for enemy in self.enemies:
                if bullet in enemy.bullets:
                    enemy.bullets.remove(bullet)

    def _check_tank_collisions(self):
        """Check for collisions between tanks."""
        if not self.player.alive:
            return

        player_rect = self.player.get_rect()

        for enemy in self.enemies:
            if enemy.alive:
                enemy_rect = enemy.get_rect()
                if player_rect.colliderect(enemy_rect):
                    # Push player back slightly
                    dx = self.player.x - enemy.x
                    dy = self.player.y - enemy.y
                    if abs(dx) > abs(dy):
                        self.player.x += 5 if dx > 0 else -5
                    else:
                        self.player.y += 5 if dy > 0 else -5

    def _spawn_enemy(self):
        """Spawn a new enemy at the top."""
        if self.enemies_spawned >= ENEMY_TOTAL_COUNT:
            return

        if len(self.enemies) >= 4:
            return

        # Check if spawn position is clear
        spawn_positions = [0, 6, 12]
        for spawn_x in spawn_positions:
            world_x = GRID_OFFSET_X + spawn_x * CELL_SIZE + CELL_SIZE // 2
            world_y = GRID_OFFSET_Y + CELL_SIZE // 2

            spawn_clear = True
            spawn_rect = pygame.Rect(world_x - 20, world_y - 20, 40, 40)

            player_rect = self.player.get_rect()
            if spawn_rect.colliderect(player_rect):
                spawn_clear = False

            for enemy in self.enemies:
                if spawn_rect.colliderect(enemy.get_rect()):
                    spawn_clear = False

            if spawn_clear:
                # Determine enemy type based on wave
                if self.enemies_spawned % 4 == 3:
                    enemy_type = ENEMY_ARMOR
                elif self.enemies_spawned % 4 == 2:
                    enemy_type = ENEMY_POWER
                elif self.enemies_spawned % 4 == 1:
                    enemy_type = ENEMY_FAST
                else:
                    enemy_type = ENEMY_NORMAL

                new_enemy = Enemy(enemy_type)
                new_enemy.x = world_x
                new_enemy.y = world_y
                self.enemies.append(new_enemy)
                self.enemies_spawned += 1
                break

    def update(self):
        """Main game update loop."""
        if self.game_state != STATE_PLAYING:
            return

        # Update player
        self.player.update(self.grid)

        # Spawn enemies
        self.spawn_timer += 1
        if self.spawn_timer >= ENEMY_SPAWN_INTERVAL:
            self.spawn_timer = 0
            self._spawn_enemy()

        # Update enemies
        for enemy in self.enemies:
            if enemy.alive:
                enemy.update_ai(self.grid, self.player.get_center())

                # Enemy shooting (random chance)
                if random.random() < 0.02 and len(enemy.bullets) < ENEMY_MAX_BULLETS:
                    bullet = enemy.shoot()
                    if bullet:
                        enemy.bullets.append(bullet)

        # Check collisions
        self._check_bullet_collisions()
        self._check_tank_collisions()

        # Check win/lose conditions
        if not self.base.alive:
            self.game_state = STATE_GAME_OVER
        elif not self.player.alive:
            self.game_state = STATE_GAME_OVER
        elif self.enemies_destroyed >= ENEMY_TOTAL_COUNT:
            self.game_state = STATE_WIN

    def draw_grid(self):
        """Draw the game grid."""
        # Draw background
        self.screen.fill(COLOR_BG)

        # Draw grid tiles
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                tile = self.grid.tiles[x][y]
                rect = self.grid.get_tile_rect(x, y)

                if tile == Grid.BRICK:
                    pygame.draw.rect(self.screen, COLOR_BRICK, rect)
                    # Brick pattern
                    pygame.draw.rect(self.screen, (150, 60, 30),
                                   (rect.x + 2, rect.y + 2, rect.width - 4, rect.height - 4), 2)
                    pygame.draw.line(self.screen, (150, 60, 30),
                                    (rect.x, rect.centery), (rect.right, rect.centery), 2)
                elif tile == Grid.STEEL:
                    pygame.draw.rect(self.screen, COLOR_STEEL, rect)
                    # Steel pattern
                    pygame.draw.rect(self.screen, (100, 100, 110),
                                   (rect.x + 4, rect.y + 4, rect.width - 8, rect.height - 8), 2)
                elif tile == Grid.WATER:
                    pygame.draw.rect(self.screen, COLOR_WATER, rect)
                    # Water waves
                    for i in range(3):
                        offset = (y + i) % 3
                        pygame.draw.line(self.screen, (80, 130, 220),
                                        (rect.x + 5, rect.y + 8 + offset * 10),
                                        (rect.right - 5, rect.y + 8 + offset * 10), 2)
                else:
                    # Grid lines for empty space
                    pygame.draw.rect(self.screen, COLOR_GRID, rect, 1)

    def draw_base(self):
        """Draw the base."""
        rect = self.base.get_rect()

        if self.base.alive:
            # Eagle base
            color = COLOR_BASE
            # Draw eagle shape (simplified)
            points = [
                (rect.centerx, rect.top + 5),
                (rect.right - 8, rect.centery - 3),
                (rect.right - 5, rect.bottom - 5),
                (rect.centerx, rect.bottom - 10),
                (rect.left + 5, rect.bottom - 5),
                (rect.left + 8, rect.centery - 3)
            ]
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.polygon(self.screen, (150, 150, 30), points, 2)
        else:
            # Destroyed base
            pygame.draw.rect(self.screen, (80, 60, 40), rect)
            # Rubble
            for _ in range(5):
                rx = rect.left + random.randint(5, rect.width - 10)
                ry = rect.top + random.randint(5, rect.height - 10)
                pygame.draw.circle(self.screen, (100, 80, 60), (rx, ry), random.randint(3, 6))

    def draw_tank(self, tank: Tank, color):
        """Draw a tank."""
        if not tank.alive:
            return

        # For player invincibility flashing
        if isinstance(tank, Player) and tank.invincible > 0:
            if (tank.invincible // 4) % 2 == 0:
                return

        rect = tank.get_rect()
        half_w = rect.width // 2
        half_h = rect.height // 2

        # Tank body
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (50, 40, 30), rect, 2)

        # Turret
        turret_color = (color[0] - 30, color[1] - 30, color[2] - 30)
        pygame.draw.rect(self.screen, turret_color,
                        (rect.centerx - 6, rect.centery - 6, 12, 12))

        # Barrel
        barrel_length = 12
        if tank.direction == Direction.UP:
            barrel = (rect.centerx - 2, rect.top - barrel_length, 4, barrel_length)
        elif tank.direction == Direction.DOWN:
            barrel = (rect.centerx - 2, rect.bottom, 4, barrel_length)
        elif tank.direction == Direction.LEFT:
            barrel = (rect.left - barrel_length, rect.centery - 2, barrel_length, 4)
        else:
            barrel = (rect.right, rect.centery - 2, barrel_length, 4)

        pygame.draw.rect(self.screen, (80, 70, 50), barrel)

        # Tracks
        track_color = (40, 30, 20)
        if tank.direction in [Direction.UP, Direction.DOWN]:
            pygame.draw.rect(self.screen, track_color,
                           (rect.left - 3, rect.top + 2, 4, rect.height - 4))
            pygame.draw.rect(self.screen, track_color,
                           (rect.right - 1, rect.top + 2, 4, rect.height - 4))
        else:
            pygame.draw.rect(self.screen, track_color,
                           (rect.left + 2, rect.top - 3, rect.width - 4, 4))
            pygame.draw.rect(self.screen, track_color,
                           (rect.left + 2, rect.bottom - 1, rect.width - 4, 4))

    def draw_bullets(self):
        """Draw all bullets."""
        all_bullets = self.player.bullets[:]
        for enemy in self.enemies:
            all_bullets.extend(enemy.bullets)

        for bullet in all_bullets:
            rect = bullet.get_rect()
            color = COLOR_BULLET if bullet.owner == "player" else (255, 150, 150)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)

    def draw_hud(self):
        """Draw the HUD."""
        # HUD background
        pygame.draw.rect(self.screen, COLOR_HUD, (0, 0, WINDOW_WIDTH, GRID_OFFSET_Y))

        # Score
        score_text = self.small_font.render(f"SCORE: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 18))

        # Lives
        lives_text = self.small_font.render(f"LIVES: {self.player.lives}", True, COLOR_TEXT)
        self.screen.blit(lives_text, (200, 18))

        # Enemies remaining
        remaining = ENEMY_TOTAL_COUNT - self.enemies_destroyed
        enemies_text = self.small_font.render(f"ENEMIES: {remaining}", True, COLOR_TEXT)
        self.screen.blit(enemies_text, (350, 18))

    def draw_menu(self):
        """Draw the menu screen."""
        self.draw_grid()
        self.draw_base()

        # Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLOR_OVERLAY)
        self.screen.blit(overlay, (0, 0))

        # Title
        title_text = self.font.render("BATTLE CITY", True, COLOR_PLAYER)
        self.screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 150))

        subtitle_text = self.small_font.render("BASE DEFENSE", True, COLOR_TEXT)
        self.screen.blit(subtitle_text, (WINDOW_WIDTH // 2 - subtitle_text.get_width() // 2, 190))

        # Instructions
        instr_lines = [
            "Arrow Keys: Move tank",
            "Spacebar: Fire bullet",
            "",
            "Destroy all 10 enemy tanks",
            "Protect your base at all costs!",
            "Brick walls can be destroyed",
            "Steel walls are indestructible",
            "",
            "Press SPACE to start"
        ]

        y = 250
        for line in instr_lines:
            text = self.small_font.render(line, True, COLOR_TEXT)
            self.screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, y))
            y += 22

    def draw_game_over(self):
        """Draw the game over screen."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLOR_OVERLAY)
        self.screen.blit(overlay, (0, 0))

        go_text = self.font.render("GAME OVER", True, COLOR_ENEMY)
        self.screen.blit(go_text, (WINDOW_WIDTH // 2 - go_text.get_width() // 2, 200))

        score_text = self.small_font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 250))

        destroyed_text = self.small_font.render(
            f"Enemies Destroyed: {self.enemies_destroyed}/{ENEMY_TOTAL_COUNT}",
            True, COLOR_TEXT
        )
        self.screen.blit(destroyed_text, (WINDOW_WIDTH // 2 - destroyed_text.get_width() // 2, 280))

        restart_text = self.small_font.render("Press R to restart or ESC to quit", True, COLOR_TEXT)
        self.screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, 340))

    def draw_win(self):
        """Draw the win screen."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLOR_OVERLAY)
        self.screen.blit(overlay, (0, 0))

        win_text = self.font.render("VICTORY!", True, COLOR_PLAYER)
        self.screen.blit(win_text, (WINDOW_WIDTH // 2 - win_text.get_width() // 2, 200))

        score_text = self.small_font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 250))

        bonus_text = self.small_font.render("Base Defended Successfully!", True, COLOR_BASE)
        self.screen.blit(bonus_text, (WINDOW_WIDTH // 2 - bonus_text.get_width() // 2, 280))

        restart_text = self.small_font.render("Press R to restart or ESC to quit", True, COLOR_TEXT)
        self.screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, 340))

    def draw(self):
        """Render the game."""
        if self.game_state == STATE_MENU:
            self.draw_menu()
        else:
            self.draw_grid()
            self.draw_base()

            # Draw bullets
            self.draw_bullets()

            # Draw enemies
            for enemy in self.enemies:
                self.draw_tank(enemy, enemy.get_color())

            # Draw player
            self.draw_tank(self.player, COLOR_PLAYER)

            # Draw HUD
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

                    elif self.game_state in [STATE_GAME_OVER, STATE_WIN]:
                        if event.key == pygame.K_r:
                            self.reset()
                            self.game_state = STATE_PLAYING

                    elif self.game_state == STATE_PLAYING:
                        if event.key == pygame.K_SPACE:
                            if len(self.player.bullets) < PLAYER_MAX_BULLETS:
                                bullet = self.player.shoot()
                                if bullet:
                                    self.player.bullets.append(bullet)

            # Continuous input for movement
            if self.game_state == STATE_PLAYING:
                keys = pygame.key.get_pressed()
                dx, dy = 0, 0
                if keys[pygame.K_UP]:
                    dy = -1
                elif keys[pygame.K_DOWN]:
                    dy = 1
                elif keys[pygame.K_LEFT]:
                    dx = -1
                elif keys[pygame.K_RIGHT]:
                    dx = 1

                if dx != 0 or dy != 0:
                    self.player.move(dx, dy, self.grid)

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
