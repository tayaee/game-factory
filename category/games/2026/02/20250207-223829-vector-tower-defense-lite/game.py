import pygame
import sys
from config import *
from path import Path
from enemy import Enemy
from tower import Tower, Projectile


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Tower Defense Lite")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.title_font = pygame.font.Font(None, 36)
        self.reset_game()

    def reset_game(self):
        self.path = Path()
        self.enemies = []
        self.towers = []
        self.projectiles = []
        self.lives = STARTING_LIVES
        self.gold = STARTING_GOLD
        self.score = 0
        self.wave = 1
        self.enemies_spawned = 0
        self.enemies_to_spawn = WAVE_LENGTH
        self.last_spawn_time = 0
        self.selected_tower_type = 1
        self.game_over = False
        self.show_ranges = False
        self.mouse_pos = (0, 0)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.selected_tower_type = 1
                elif event.key == pygame.K_2:
                    self.selected_tower_type = 2
                elif event.key == pygame.K_r:
                    self.show_ranges = not self.show_ranges
                elif event.key == pygame.K_SPACE and self.game_over:
                    self.reset_game()

            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                if event.button == 1:  # Left click
                    game_area_height = SCREEN_HEIGHT - UI_HEIGHT
                    if event.pos[1] < game_area_height:
                        self.try_place_tower(event.pos[0], event.pos[1])

        return True

    def try_place_tower(self, x, y):
        # Check if on path
        if self.path.is_on_path(x, y):
            return

        # Check if overlapping existing tower
        for tower in self.towers:
            tower_rect = tower.get_rect()
            if tower_rect.collidepoint(x, y):
                return

        # Check if can afford
        cost = TOWER_TYPES[self.selected_tower_type]["cost"]
        if self.gold >= cost:
            self.gold -= cost
            self.towers.append(Tower(x, y, self.selected_tower_type))

    def spawn_enemy(self, current_time):
        if self.enemies_spawned >= self.enemies_to_spawn:
            return

        if current_time - self.last_spawn_time >= ENEMY_SPAWN_INTERVAL:
            wave_multiplier = 1.0 + (self.wave - 1) * 0.2
            self.enemies.append(Enemy(self.path, wave_multiplier))
            self.enemies_spawned += 1
            self.last_spawn_time = current_time

    def update(self):
        if self.game_over:
            return

        current_time = pygame.time.get_ticks()

        # Spawn enemies
        self.spawn_enemy(current_time)

        # Check wave complete
        if (self.enemies_spawned >= self.enemies_to_spawn and
            len(self.enemies) == 0):
            self.wave += 1
            self.enemies_spawned = 0
            self.enemies_to_spawn = WAVE_LENGTH + self.wave * 2
            self.gold += WAVE_BONUS

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.reached_end:
                self.lives -= 1
                self.enemies.remove(enemy)
                if self.lives <= 0:
                    self.game_over = True
            elif not enemy.alive:
                self.score += 10
                self.gold += enemy.value
                self.enemies.remove(enemy)

        # Update towers
        for tower in self.towers:
            projectile = tower.update(self.enemies)
            if projectile:
                self.projectiles.append(projectile)

        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update()
            if not projectile.active:
                self.projectiles.remove(projectile)

    def draw(self):
        # Background
        self.screen.fill(BACKGROUND_COLOR)

        # Draw grass areas
        self.screen.fill(GRASS_COLOR, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - UI_HEIGHT))

        # Draw path
        self.path.draw(self.screen)

        # Draw tower ranges
        if self.show_ranges:
            for tower in self.towers:
                tower.draw_range(self.screen)

        # Draw towers
        for tower in self.towers:
            tower.draw(self.screen)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)

        # Draw placement preview
        if not self.game_over:
            self.draw_placement_preview()

        # Draw UI
        self.draw_ui()

        # Draw game over
        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_placement_preview(self):
        x, y = self.mouse_pos
        if y >= SCREEN_HEIGHT - UI_HEIGHT:
            return

        # Check valid placement
        can_place = True
        if self.path.is_on_path(x, y):
            can_place = False
        else:
            for tower in self.towers:
                if tower.get_rect().collidepoint(x, y):
                    can_place = False
                    break

        tower_info = TOWER_TYPES[self.selected_tower_type]
        color = (*tower_info["color"], 100) if can_place else (200, 50, 50, 100)

        # Create transparent surface
        preview_surf = pygame.Surface((TOWER_SIZE + 10, TOWER_SIZE + 10), pygame.SRCALPHA)
        pygame.draw.circle(preview_surf, color, (TOWER_SIZE // 2 + 5, TOWER_SIZE // 2 + 5), TOWER_SIZE // 2)
        self.screen.blit(preview_surf, (x - TOWER_SIZE // 2 - 5, y - TOWER_SIZE // 2 - 5))

        # Draw range preview
        range_surf = pygame.Surface((tower_info["range"] * 2, tower_info["range"] * 2), pygame.SRCALPHA)
        pygame.draw.circle(range_surf, (200, 200, 200, 30), (tower_info["range"], tower_info["range"]), tower_info["range"], 1)
        self.screen.blit(range_surf, (x - tower_info["range"], y - tower_info["range"]))

    def draw_ui(self):
        ui_rect = pygame.Rect(0, SCREEN_HEIGHT - UI_HEIGHT, SCREEN_WIDTH, UI_HEIGHT)
        pygame.draw.rect(self.screen, UI_BG_COLOR, ui_rect)
        pygame.draw.line(self.screen, ACCENT_COLOR, (0, SCREEN_HEIGHT - UI_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT - UI_HEIGHT), 2)

        # Stats
        stats_y = SCREEN_HEIGHT - UI_HEIGHT + 10
        lives_text = self.font.render(f"Lives: {self.lives}", True, (220, 80, 80))
        gold_text = self.font.render(f"Gold: {self.gold}", True, (220, 200, 80))
        score_text = self.font.render(f"Score: {self.score}", True, (80, 200, 80))
        wave_text = self.font.render(f"Wave: {self.wave}", True, TEXT_COLOR)

        self.screen.blit(lives_text, (20, stats_y))
        self.screen.blit(gold_text, (20, stats_y + 25))
        self.screen.blit(score_text, (200, stats_y))
        self.screen.blit(wave_text, (200, stats_y + 25))

        # Tower selection buttons
        button_x = 400
        for tower_id, info in TOWER_TYPES.items():
            is_selected = self.selected_tower_type == tower_id
            can_afford = self.gold >= info["cost"]

            button_rect = pygame.Rect(button_x, SCREEN_HEIGHT - UI_HEIGHT + 15, BUTTON_SIZE, BUTTON_SIZE)

            # Button background
            bg_color = info["color"] if is_selected else (60, 60, 70)
            if not can_afford:
                bg_color = (80, 50, 50)
            pygame.draw.rect(self.screen, bg_color, button_rect, border_radius=5)

            # Border
            border_color = ACCENT_COLOR if is_selected else (100, 100, 100)
            if not can_afford:
                border_color = (150, 80, 80)
            pygame.draw.rect(self.screen, border_color, button_rect, 2 if is_selected else 1, border_radius=5)

            # Tower icon
            center_x = button_rect.centerx
            center_y = button_rect.centery
            pygame.draw.circle(self.screen, (30, 30, 30), (center_x, center_y), 12)

            # Label
            key_text = self.font.render(str(tower_id), True, TEXT_COLOR)
            self.screen.blit(key_text, (button_rect.x + 5, button_rect.bottom - 20))

            # Cost
            cost_text = self.font.render(f"${info['cost']}", True, (180, 180, 180) if can_afford else (150, 100, 100))
            self.screen.blit(cost_text, (button_rect.x, button_rect.top - 2))

            # Name below
            name_text = self.font.render(info["name"], True, TEXT_COLOR)
            self.screen.blit(name_text, (button_rect.x + 5, button_rect.bottom + 2))

            button_x += BUTTON_SIZE + 10

        # Help text
        help_text = self.font.render("[R] Toggle Ranges  [SPACE] Restart", True, (150, 150, 150))
        self.screen.blit(help_text, (SCREEN_WIDTH - 280, stats_y + 15))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.title_font.render("GAME OVER", True, (220, 80, 80))
        score_text = self.title_font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
        wave_text = self.font.render(f"Waves Survived: {self.wave - 1}", True, (180, 180, 180))
        restart_text = self.font.render("Press SPACE to restart", True, ACCENT_COLOR)

        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
        self.screen.blit(wave_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 80))

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
