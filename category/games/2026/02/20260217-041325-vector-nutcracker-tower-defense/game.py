"""Main game class for tower defense game."""

import pygame
import sys
from config import *
from enemy import Enemy
from tower import Tower, Projectile


class Game:
    """Main game controller."""

    def __init__(self):
        """Initialize game."""
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Vector Nutcracker Tower Defense")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 18)

        # Game state
        self.currency = INITIAL_CURRENCY
        self.health = INITIAL_HEALTH
        self.wave = 0
        self.score = 0
        self.time_survived = 0
        self.game_over = False
        self.victory = False
        self.show_range = False

        # Towers and enemies
        self.towers = []
        self.enemies = []
        self.projectiles = []

        # Wave management
        self.current_wave_enemies = []
        self.spawn_timer = 0
        self.wave_in_progress = False
        self.wave_delay = 3.0
        self.wave_delay_timer = 0

        # Tower selection
        self.selected_tower = "Scout"

        # Path for validity checking
        self.path_set = set(ENEMY_PATH)

        # Initialize first wave
        self.prepare_wave()

    def prepare_wave(self):
        """Prepare next wave of enemies."""
        if self.wave >= len(WAVES):
            self.victory = True
            self.game_over = True
            return

        wave_config = WAVES[self.wave]
        self.current_wave_enemies = []
        for enemy_data in wave_config:
            for _ in range(enemy_data["count"]):
                self.current_wave_enemies.append(enemy_data["type"])

        self.wave_in_progress = False
        self.wave_delay_timer = self.wave_delay
        self.spawn_timer = 0

    def spawn_enemy(self):
        """Spawn next enemy from current wave."""
        if not self.current_wave_enemies:
            return False

        enemy_type = self.current_wave_enemies.pop(0)
        enemy = Enemy(enemy_type, ENEMY_PATH)
        self.enemies.append(enemy)
        return True

    def is_valid_position(self, grid_x, grid_y):
        """Check if position is valid for tower placement."""
        # Check bounds
        if not (0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE):
            return False

        # Check if on path
        if (grid_x, grid_y) in self.path_set:
            return False

        # Check if tower already exists
        for tower in self.towers:
            if tower.grid_x == grid_x and tower.grid_y == grid_y:
                return False

        return True

    def get_tower_at(self, grid_x, grid_y):
        """Get tower at grid position."""
        for tower in self.towers:
            if tower.grid_x == grid_x and tower.grid_y == grid_y:
                return tower
        return None

    def handle_events(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_1:
                    self.selected_tower = "Scout"
                elif event.key == pygame.K_2:
                    self.selected_tower = "Heavy"
                elif event.key == pygame.K_3:
                    self.selected_tower = "Frost"
                elif event.key == pygame.K_r:
                    self.show_range = not self.show_range
                elif event.key == pygame.K_SPACE and self.game_over:
                    self.restart_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    grid_x = (mouse_x - GRID_OFFSET_X) // CELL_SIZE
                    grid_y = (mouse_y - GRID_OFFSET_Y) // CELL_SIZE

                    if self.is_valid_position(grid_x, grid_y):
                        tower_config = TOWER_TYPES[self.selected_tower]
                        if self.currency >= tower_config["cost"]:
                            self.towers.append(Tower(grid_x, grid_y, self.selected_tower))
                            self.currency -= tower_config["cost"]

    def restart_game(self):
        """Restart the game."""
        self.currency = INITIAL_CURRENCY
        self.health = INITIAL_HEALTH
        self.wave = 0
        self.score = 0
        self.time_survived = 0
        self.game_over = False
        self.victory = False
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.prepare_wave()

    def update(self, dt):
        """Update game state."""
        if self.game_over:
            return

        self.time_survived += dt

        # Wave delay
        if self.wave_delay_timer > 0:
            self.wave_delay_timer -= dt
            return

        # Start wave
        if not self.wave_in_progress:
            self.wave_in_progress = True

        # Spawn enemies
        if self.spawn_timer <= 0 and self.current_wave_enemies:
            self.spawn_timer = WAVES[self.wave][0]["interval"]
            self.spawn_enemy()
        elif self.spawn_timer > 0:
            self.spawn_timer -= dt

        # Check if wave is complete
        if self.wave_in_progress and not self.current_wave_enemies and not self.enemies:
            self.wave += 1
            self.score += 100 * self.wave  # Wave completion bonus
            self.prepare_wave()
            return

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(dt)

            if enemy.reached_end:
                self.health -= 1
                self.enemies.remove(enemy)
                if self.health <= 0:
                    self.game_over = True

            elif not enemy.alive:
                self.score += enemy.reward
                self.currency += enemy.reward
                self.enemies.remove(enemy)

        # Update towers
        for tower in self.towers:
            tower.update(dt)

            # Find target
            if tower.can_fire():
                target = self.find_target(tower)
                if target:
                    tower.set_target(target.get_position())
                    projectile = tower.fire(target.get_position())
                    self.projectiles.append(projectile)
                else:
                    # Reset angle slowly if no target
                    tower.target_angle = 0

        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update(dt)

            if not projectile.active:
                self.projectiles.remove(projectile)
                continue

            # Check collision with enemies
            for enemy in self.enemies:
                if not enemy.alive:
                    continue
                ex, ey = enemy.get_position()
                dist = ((projectile.x - ex) ** 2 + (projectile.y - ey) ** 2) ** 0.5
                if dist < CELL_SIZE * 0.4:
                    enemy.take_damage(projectile.damage)
                    if projectile.is_frost:
                        enemy.apply_slow(projectile.slow_factor, projectile.slow_duration)
                    projectile.active = False
                    break

    def find_target(self, tower):
        """Find target enemy for tower."""
        tower_pos = tower.get_position()
        tower_range = tower.get_range_pixels()

        # Find closest enemy in range
        closest = None
        closest_dist = float('inf')

        for enemy in self.enemies:
            if not enemy.alive:
                continue
            enemy_pos = enemy.get_position()
            dist = ((tower_pos[0] - enemy_pos[0]) ** 2 + (tower_pos[1] - enemy_pos[1]) ** 2) ** 0.5

            if dist <= tower_range and dist < closest_dist:
                closest = enemy
                closest_dist = dist

        return closest

    def draw_grid(self):
        """Draw the game grid."""
        # Draw background
        pygame.draw.rect(self.screen, COLOR_BG,
                        (GRID_OFFSET_X - 10, GRID_OFFSET_Y - 10,
                         GRID_SIZE * CELL_SIZE + 20, GRID_SIZE * CELL_SIZE + 20))

        # Draw grid cells
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = (GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y + y * CELL_SIZE,
                       CELL_SIZE, CELL_SIZE)

                if (x, y) in self.path_set:
                    pygame.draw.rect(self.screen, COLOR_PATH, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_GRID, rect, 1)

        # Draw toy box at end of path
        end_pos = ENEMY_PATH[-1]
        toy_box_rect = (GRID_OFFSET_X + end_pos[0] * CELL_SIZE,
                        GRID_OFFSET_Y + end_pos[1] * CELL_SIZE,
                        CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, COLOR_TOY_BOX, toy_box_rect)

        # Draw toy box decoration
        center_x = GRID_OFFSET_X + end_pos[0] * CELL_SIZE + CELL_SIZE // 2
        center_y = GRID_OFFSET_Y + end_pos[1] * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.rect(self.screen, (200, 150, 200),
                        (center_x - 10, center_y - 8, 20, 16))
        pygame.draw.circle(self.screen, (255, 200, 255), (int(center_x), int(center_y - 5)), 5)
        pygame.draw.circle(self.screen, (255, 200, 255), (int(center_x), int(center_y + 5)), 5)

        # Draw start indicator
        start_pos = ENEMY_PATH[0]
        start_rect = (GRID_OFFSET_X + start_pos[0] * CELL_SIZE,
                     GRID_OFFSET_Y + start_pos[1] * CELL_SIZE,
                     CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, (150, 150, 150), start_rect, 3)

        # Draw placement preview
        if not self.game_over:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x = (mouse_x - GRID_OFFSET_X) // CELL_SIZE
            grid_y = (mouse_y - GRID_OFFSET_Y) // CELL_SIZE

            if (0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE):
                rect = (GRID_OFFSET_X + grid_x * CELL_SIZE, GRID_OFFSET_Y + grid_y * CELL_SIZE,
                       CELL_SIZE, CELL_SIZE)

                tower_config = TOWER_TYPES[self.selected_tower]
                color = COLOR_VALID if (self.is_valid_position(grid_x, grid_y) and
                                      self.currency >= tower_config["cost"]) else COLOR_INVALID
                pygame.draw.rect(self.screen, color, rect, 2)

                # Show range preview
                center_x = GRID_OFFSET_X + grid_x * CELL_SIZE + CELL_SIZE // 2
                center_y = GRID_OFFSET_Y + grid_y * CELL_SIZE + CELL_SIZE // 2
                range_pixels = tower_config["range"] * CELL_SIZE
                pygame.draw.circle(self.screen, (*color, 80), (int(center_x), int(center_y)),
                                int(range_pixels), 1)

    def draw_ui(self):
        """Draw user interface."""
        # Top bar background
        pygame.draw.rect(self.screen, COLOR_UI_BG, (0, 0, WINDOW_WIDTH, 35))

        # Health
        health_text = self.font.render(f"Health: {self.health}", True, (255, 100, 100))
        self.screen.blit(health_text, (10, 8))

        # Currency
        currency_text = self.font.render(f"Gold: {self.currency}", True, (255, 215, 0))
        self.screen.blit(currency_text, (120, 8))

        # Wave
        wave_text = self.font.render(f"Wave: {self.wave + 1}/{len(WAVES)}", True, (150, 200, 255))
        self.screen.blit(wave_text, (240, 8))

        # Score
        score_text = self.font.render(f"Score: {self.score}", True, (200, 200, 200))
        self.screen.blit(score_text, (WINDOW_WIDTH - 100, 8))

        # Tower selection panel
        panel_y = WINDOW_HEIGHT - 70
        panel_width = 250
        pygame.draw.rect(self.screen, COLOR_UI_BG, (10, panel_y, panel_width, 60))

        # Tower options
        tower_keys = ["1", "2", "3"]
        tower_names = ["Scout", "Heavy", "Frost"]

        for i, (key, name) in enumerate(zip(tower_keys, tower_names)):
            config = TOWER_TYPES[name]
            x_offset = 10 + i * 80
            is_selected = self.selected_tower == name
            can_afford = self.currency >= config["cost"]

            # Tower button background
            bg_color = config["color"] if can_afford else (80, 80, 80)
            if is_selected:
                pygame.draw.rect(self.screen, (255, 255, 255), (x_offset, panel_y + 5, 70, 50), 2)

            # Tower preview
            center_x = x_offset + 35
            center_y = panel_y + 25
            size = 20
            pygame.draw.rect(self.screen, bg_color,
                           (center_x - size // 2, center_y - size // 2 - 5, size, size))
            pygame.draw.polygon(self.screen, bg_color, [
                (center_x - size // 3, center_y + 2),
                (center_x + size // 3, center_y + 2),
                (center_x, center_y - size // 2 - 2)
            ])

            # Tower info
            name_text = self.small_font.render(name, True, (255, 255, 255) if can_afford else (150, 150, 150))
            self.screen.blit(name_text, (x_offset + 10, panel_y + 40))

            cost_text = self.small_font.render(f"${config['cost']}", True,
                                             (100, 255, 100) if can_afford else (255, 100, 100))
            self.screen.blit(cost_text, (x_offset + 10, panel_y + 55))

            # Key hint
            key_text = self.font.render(key, True, (255, 255, 0))
            self.screen.blit(key_text, (x_offset + 50, panel_y + 10))

        # Controls hint
        hint_text = self.small_font.render("R: Toggle Range | ESC: Exit", True, (150, 150, 150))
        self.screen.blit(hint_text, (270, panel_y + 25))

        # Wave status
        if self.wave_delay_timer > 0:
            wave_text = self.title_font.render(f"Wave {self.wave + 1} in {self.wave_delay_timer:.1f}s",
                                             True, (255, 255, 255))
            text_rect = wave_text.get_rect(center=(WINDOW_WIDTH // 2, 15))
            pygame.draw.rect(self.screen, COLOR_UI_BG, text_rect.inflate(20, 10))
            self.screen.blit(wave_text, text_rect)

        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            if self.victory:
                title = self.title_font.render("Victory!", True, (100, 255, 100))
            else:
                title = self.title_font.render("Game Over", True, (255, 100, 100))

            title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
            self.screen.blit(title, title_rect)

            final_score = self.title_font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            score_rect = final_score.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(final_score, score_rect)

            waves_survived = self.font.render(f"Waves Survived: {self.wave}", True, (200, 200, 200))
            waves_rect = waves_survived.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
            self.screen.blit(waves_survived, waves_rect)

            restart_text = self.font.render("Press SPACE to restart", True, (255, 255, 0))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80))
            self.screen.blit(restart_text, restart_rect)

    def draw(self):
        """Draw everything."""
        self.screen.fill(COLOR_BG)

        self.draw_grid()

        # Draw towers
        for tower in self.towers:
            tower.draw(self.screen, self.show_range)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)

        self.draw_ui()

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while True:
            dt = self.clock.tick(FPS) / 1000.0

            self.handle_events()
            self.update(dt)
            self.draw()
