"""Main game logic for Vector Heian-Kyo Alien Trap."""

import pygame
from config import *
from entities import GameState, Direction


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Heian-Kyo Alien Trap")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.large_font = pygame.font.Font(None, 48)

        self.game_state = GameState()

    def handle_input(self) -> bool:
        """Handle keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.game_state.game_over:
                    if event.key == pygame.K_r:
                        self.game_state = GameState()
                    continue

                if self.game_state.level_complete:
                    if event.key == pygame.K_n:
                        self.game_state.next_level()
                    continue

                # Movement and actions
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.game_state.step(ACTION_UP)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.game_state.step(ACTION_DOWN)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.game_state.step(ACTION_LEFT)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.game_state.step(ACTION_RIGHT)
                elif event.key == pygame.K_z:
                    self.game_state.step(ACTION_DIG)
                elif event.key == pygame.K_x:
                    self.game_state.step(ACTION_FILL)
                elif event.key == pygame.K_r:
                    self.game_state.reset()

        return True

    def update(self) -> None:
        """Update game state."""
        pass

    def draw(self) -> None:
        """Render the game."""
        self.screen.fill(COLOR_BG)

        self._draw_ui()
        self._draw_grid()
        self._draw_game_elements()

        if self.game_state.game_over:
            self._draw_game_over()
        elif self.game_state.level_complete:
            self._draw_level_complete()

        pygame.display.flip()

    def _draw_ui(self) -> None:
        """Draw user interface."""
        # UI background
        ui_rect = pygame.Rect(0, 0, SCREEN_WIDTH, UI_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_UI_BG, ui_rect)
        pygame.draw.line(self.screen, COLOR_BORDER, (0, UI_HEIGHT), (SCREEN_WIDTH, UI_HEIGHT), 2)

        # Level info
        level_text = self.font.render(f"Level: {self.game_state.level}", True, COLOR_TEXT)
        self.screen.blit(level_text, (20, 15))

        # Lives
        lives_text = self.font.render(f"Lives: {self.game_state.lives}", True, COLOR_TEXT)
        self.screen.blit(lives_text, (20, 45))

        # Score
        score_text = self.font.render(f"Score: {self.game_state.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (150, 15))

        # Reward
        reward_text = self.small_font.render(f"Reward: {self.game_state.total_reward:.1f}", True, COLOR_TEXT_DIM)
        self.screen.blit(reward_text, (150, 50))

        # Aliens remaining
        aliens_remaining = sum(1 for a in self.game_state.aliens if not a.is_buried)
        aliens_text = self.font.render(f"Aliens: {aliens_remaining}", True, COLOR_TEXT)
        self.screen.blit(aliens_text, (300, 15))

        # Controls
        controls_text = self.small_font.render("Arrows/WASD: Move | Z: Dig | X: Fill", True, COLOR_TEXT_DIM)
        self.screen.blit(controls_text, (SCREEN_WIDTH - controls_text.get_width() - 20, 15))

        restart_text = self.small_font.render("R: Restart | ESC: Quit", True, COLOR_TEXT_DIM)
        self.screen.blit(restart_text, (SCREEN_WIDTH - restart_text.get_width() - 20, 45))

    def _draw_grid(self) -> None:
        """Draw the game grid."""
        for row in range(self.game_state.grid_rows):
            for col in range(self.game_state.grid_cols):
                x = GRID_OFFSET_X + col * TILE_SIZE
                y = GRID_OFFSET_Y + row * TILE_SIZE
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

                # Draw floor
                pygame.draw.rect(self.screen, COLOR_FLOOR, rect)

                # Draw wall
                if (row, col) in self.game_state.walls:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                    pygame.draw.rect(self.screen, COLOR_WALL_OUTLINE, rect, 2)

                # Draw hole
                elif (row, col) in self.game_state.holes:
                    pygame.draw.rect(self.screen, COLOR_HOLE, rect)
                    pygame.draw.rect(self.screen, COLOR_HOLE_OUTLINE, rect, 2)

                # Draw grid border
                pygame.draw.rect(self.screen, (40, 40, 45), rect, 1)

    def _draw_game_elements(self) -> None:
        """Draw player and aliens."""
        state = self.game_state.get_state()

        for row in range(self.game_state.grid_rows):
            for col in range(self.game_state.grid_cols):
                x = GRID_OFFSET_X + col * TILE_SIZE
                y = GRID_OFFSET_Y + row * TILE_SIZE

                # Draw action progress indicator
                if self.game_state.action_progress > 0:
                    ar, ac = self.game_state.action_pos
                    if row == ar and col == ac:
                        progress = self.game_state.action_progress / DIG_TIME
                        color = COLOR_DIGGING if self.game_state.current_action == 'dig' else (100, 180, 100)
                        indicator_width = int(TILE_SIZE * progress)
                        if indicator_width > 0:
                            indicator_rect = pygame.Rect(x, y + TILE_SIZE - 6, indicator_width, 4)
                            pygame.draw.rect(self.screen, color, indicator_rect)

        # Draw aliens
        for alien in self.game_state.aliens:
            if alien.is_buried:
                continue

            ax = GRID_OFFSET_X + alien.col * TILE_SIZE
            ay = GRID_OFFSET_Y + alien.row * TILE_SIZE

            if alien.in_hole:
                self._draw_trapped_alien(ax, ay, alien.hole_time / ALIEN_ESCAPE_TIME)
            else:
                self._draw_alien(ax, ay)

        # Draw player
        px = GRID_OFFSET_X + self.game_state.player_col * TILE_SIZE
        py = GRID_OFFSET_Y + self.game_state.player_row * TILE_SIZE
        self._draw_player(px, py)

    def _draw_player(self, x: int, y: int) -> None:
        """Draw the player at the given position."""
        center_x = x + TILE_SIZE // 2
        center_y = y + TILE_SIZE // 2
        radius = TILE_SIZE // 3

        # Player body
        pygame.draw.circle(self.screen, COLOR_PLAYER, (center_x, center_y), radius)
        pygame.draw.circle(self.screen, COLOR_PLAYER_OUTLINE, (center_x, center_y), radius, 2)

        # Inner detail
        pygame.draw.circle(self.screen, (40, 100, 130), (center_x, center_y), radius // 2)

    def _draw_alien(self, x: int, y: int) -> None:
        """Draw an alien at the given position."""
        center_x = x + TILE_SIZE // 2
        center_y = y + TILE_SIZE // 2
        size = TILE_SIZE // 2.5

        # Alien body (diamond shape)
        points = [
            (center_x, center_y - size),
            (center_x + size, center_y),
            (center_x, center_y + size),
            (center_x - size, center_y)
        ]
        pygame.draw.polygon(self.screen, COLOR_ALIEN, points)
        pygame.draw.polygon(self.screen, COLOR_ALIEN_OUTLINE, points, 2)

        # Eyes
        eye_offset = size // 3
        eye_size = 3
        pygame.draw.circle(self.screen, (255, 255, 255), (center_x - eye_offset, center_y - 2), eye_size)
        pygame.draw.circle(self.screen, (255, 255, 255), (center_x + eye_offset, center_y - 2), eye_size)

    def _draw_trapped_alien(self, x: int, y: int, escape_progress: float) -> None:
        """Draw an alien trapped in a hole."""
        center_x = x + TILE_SIZE // 2
        center_y = y + TILE_SIZE // 2
        size = TILE_SIZE // 3

        # Struggling animation
        offset = int(3 * (1 - escape_progress * 2) if escape_progress < 0.5 else 0)

        # Alien body (smaller, trapped)
        points = [
            (center_x, center_y - size + offset),
            (center_x + size - offset, center_y),
            (center_x, center_y + size - offset),
            (center_x - size + offset, center_y)
        ]
        pygame.draw.polygon(self.screen, COLOR_ALIEN_TRAPPED, points)
        pygame.draw.polygon(self.screen, (160, 120, 80), points, 2)

        # Escape timer bar
        bar_width = TILE_SIZE - 10
        bar_height = 4
        bar_x = x + 5
        bar_y = y + TILE_SIZE - 8
        pygame.draw.rect(self.screen, (40, 30, 25), (bar_x, bar_y, bar_width, bar_height))
        fill_width = int(bar_width * escape_progress)
        if fill_width > 0:
            color = (100, 100, 80) if escape_progress < 0.7 else (180, 100, 80)
            pygame.draw.rect(self.screen, color, (bar_x, bar_y, fill_width, bar_height))

    def _draw_level_complete(self) -> None:
        """Draw level complete overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title_text = self.large_font.render("LEVEL COMPLETE!", True, (100, 200, 120))
        score_text = self.font.render(f"Score: {self.game_state.score}", True, COLOR_TEXT)
        reward_text = self.font.render(f"Total Reward: {self.game_state.total_reward:.1f}", True, COLOR_TEXT)
        next_text = self.small_font.render("Press N for next level", True, COLOR_TEXT_DIM)

        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        self.screen.blit(title_text, (center_x - title_text.get_width() // 2, center_y - 60))
        self.screen.blit(score_text, (center_x - score_text.get_width() // 2, center_y))
        self.screen.blit(reward_text, (center_x - reward_text.get_width() // 2, center_y + 35))
        self.screen.blit(next_text, (center_x - next_text.get_width() // 2, center_y + 80))

    def _draw_game_over(self) -> None:
        """Draw game over overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title_text = self.large_font.render("GAME OVER", True, (200, 80, 80))
        score_text = self.font.render(f"Final Score: {self.game_state.score}", True, COLOR_TEXT)
        level_text = self.font.render(f"Level Reached: {self.game_state.level}", True, COLOR_TEXT)
        restart_text = self.small_font.render("Press R to play again", True, COLOR_TEXT_DIM)
        quit_text = self.small_font.render("Press ESC to quit", True, COLOR_TEXT_DIM)

        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        self.screen.blit(title_text, (center_x - title_text.get_width() // 2, center_y - 70))
        self.screen.blit(score_text, (center_x - score_text.get_width() // 2, center_y - 10))
        self.screen.blit(level_text, (center_x - level_text.get_width() // 2, center_y + 25))
        self.screen.blit(restart_text, (center_x - restart_text.get_width() // 2, center_y + 70))
        self.screen.blit(quit_text, (center_x - quit_text.get_width() // 2, center_y + 100))

    def run(self) -> None:
        """Main game loop."""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
