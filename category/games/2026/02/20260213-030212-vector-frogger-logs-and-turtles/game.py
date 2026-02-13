"""Main game logic for Vector Frogger: Logs and Turtles."""

import pygame
from config import *
from entities import Frog, Lane


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Frogger: Logs and Turtles")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)

        self.reset_game()

    def reset_game(self):
        """Reset the entire game state."""
        self.frog = Frog()
        self.lanes = []
        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_over = False
        self.high_score = 0
        self.successful_crossings = 0
        self.forward_scored = False

        self._init_lanes()

    def _init_lanes(self):
        """Initialize river lanes with platforms."""
        self.lanes = []
        for row, speed, platform_type, size, spacing in LANES:
            self.lanes.append(Lane(row, speed, platform_type, size, spacing))

    def handle_input(self):
        """Handle keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.game_over:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_r:
                        self.reset_game()
                else:
                    moved = False
                    if event.key == pygame.K_UP:
                        moved = self.frog.move(0, -1)
                    elif event.key == pygame.K_DOWN:
                        moved = self.frog.move(0, 1)
                    elif event.key == pygame.K_LEFT:
                        moved = self.frog.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        moved = self.frog.move(1, 0)

                    if moved:
                        self.forward_scored = False
                        # Award points for moving forward
                        if self.frog.moved_forward():
                            self.score += SCORE_FORWARD
                            self.forward_scored = True

        return True

    def update(self):
        """Update game state."""
        if self.game_over:
            return

        current_time = pygame.time.get_ticks()
        self.frog.update()

        # Update lanes with speed multiplier based on level
        speed_multiplier = 1.0 + (self.level - 1) * SPEED_INCREMENT / BASE_SPEED
        for lane in self.lanes:
            lane.update(speed_multiplier, current_time)

        # Check collisions and game logic
        self._check_river_collision(current_time)

        # Check if frog reached goal
        if self.frog.grid_y == GOAL_ROW:
            self._reach_goal()

        # Check if frog went out of bounds while on platform
        if self.frog.x < 0 or self.frog.x > SCREEN_WIDTH:
            self._death()

        # Time penalty
        self.score += TIME_PENALTY // FPS

    def _check_river_collision(self, current_time):
        """Check frog collisions with platforms in river."""
        frog_rect = self.frog.get_rect()
        frog_row = self.frog.grid_y

        # Check if in river zone
        if RIVER_START <= frog_row <= RIVER_END:
            on_platform = False
            for lane in self.lanes:
                if lane.row == frog_row:
                    platform = lane.check_collision(frog_rect)
                    if platform:
                        on_platform = True
                        self.frog.on_platform = True
                        # Move frog with platform (speed adjusted by level)
                        speed_multiplier = 1.0 + (self.level - 1) * SPEED_INCREMENT / BASE_SPEED
                        self.frog.platform_speed = platform.speed * speed_multiplier
                        break

            if not on_platform:
                # Frog fell in water
                self.frog.on_platform = False
                self._death()
        else:
            self.frog.on_platform = False

    def _reach_goal(self):
        """Handle frog reaching the goal."""
        self.score += SCORE_GOAL
        self.successful_crossings += 1

        # Increase level every 3 successful crossings
        if self.successful_crossings % 3 == 0:
            self.level += 1

        # Reset frog position
        self.frog.reset()
        self.forward_scored = False

    def _death(self):
        """Handle frog death."""
        self.lives -= 1
        self.score += DEATH_PENALTY

        if self.lives <= 0:
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
        else:
            self.frog.reset()
            self.forward_scored = False

    def draw(self):
        """Render the game."""
        self.screen.fill(COLOR_BG)

        # Draw zones
        self._draw_zones()

        # Draw lanes
        for lane in self.lanes:
            lane.draw(self.screen)

        # Draw frog
        self.frog.draw(self.screen)

        # Draw UI
        self._draw_ui()

        # Draw game over screen
        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_zones(self):
        """Draw background zones."""
        # Goal zone (top)
        goal_rect = pygame.Rect(0, 0, SCREEN_WIDTH, GRID_SIZE)
        pygame.draw.rect(self.screen, COLOR_SAFE_ZONE, goal_rect)

        # Goal indicator text
        goal_text = self.small_font.render("GOAL", True, (255, 255, 255))
        for i in range(COLS):
            x = i * GRID_SIZE + GRID_SIZE // 2 - goal_text.get_width() // 2
            y = GRID_SIZE // 2 - goal_text.get_height() // 2
            self.screen.blit(goal_text, (x, y))

        # River zone
        river_rect = pygame.Rect(
            0, RIVER_START * GRID_SIZE,
            SCREEN_WIDTH, (RIVER_END - RIVER_START + 1) * GRID_SIZE
        )
        pygame.draw.rect(self.screen, COLOR_WATER, river_rect)

        # Draw water ripples (decorative)
        for row in range(RIVER_START, RIVER_END + 1):
            for i in range(0, SCREEN_WIDTH, 120):
                ripple_x = i + (row * 30) % SCREEN_WIDTH
                ripple_y = row * GRID_SIZE + GRID_SIZE // 2
                pygame.draw.ellipse(
                    self.screen, (50, 85, 140),
                    (ripple_x, ripple_y - 5, 40, 10), 1
                )

        # Start zone (bottom)
        start_y = (RIVER_END + 1) * GRID_SIZE
        start_rect = pygame.Rect(0, start_y, SCREEN_WIDTH, (ROWS - RIVER_END - 1) * GRID_SIZE)
        pygame.draw.rect(self.screen, COLOR_GRASS, start_rect)

        # Start indicator text
        start_text = self.small_font.render("START", True, (255, 255, 255))
        start_x = SCREEN_WIDTH // 2 - start_text.get_width() // 2
        start_y_pos = START_ROW * GRID_SIZE + GRID_SIZE // 2 - start_text.get_height() // 2
        self.screen.blit(start_text, (start_x, start_y_pos))

    def _draw_ui(self):
        """Draw user interface."""
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        # Level
        level_text = self.font.render(f"Level: {self.level}", True, COLOR_TEXT)
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 10))

        # Lives
        lives_text = self.font.render(f"Lives: {self.lives}", True, COLOR_TEXT)
        self.screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 10, 10))

        # High score
        if self.high_score > 0:
            high_text = self.small_font.render(f"High: {self.high_score}", True, (180, 180, 180))
            self.screen.blit(high_text, (10, 50))

        # Crossings
        crossings_text = self.small_font.render(f"Crossings: {self.successful_crossings}", True, (150, 200, 150))
        self.screen.blit(crossings_text, (SCREEN_WIDTH - crossings_text.get_width() - 10, 50))

        # Turtle warning
        warning_text = self.tiny_font.render("TURTLES TURN DARK WHEN SUBMERGED!", True, COLOR_WARNING)
        warning_x = SCREEN_WIDTH // 2 - warning_text.get_width() // 2
        self.screen.blit(warning_text, (warning_x, SCREEN_HEIGHT - 25))

    def _draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("GAME OVER", True, COLOR_GAME_OVER)
        score_text = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
        crossings_text = self.small_font.render(
            f"Successful Crossings: {self.successful_crossings}", True, (200, 200, 200)
        )
        restart_text = self.small_font.render("Press SPACE to restart", True, (200, 200, 200))
        quit_text = self.small_font.render("Press ESC to quit", True, (200, 200, 200))

        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        self.screen.blit(game_over_text, (center_x - game_over_text.get_width() // 2, center_y - 80))
        self.screen.blit(score_text, (center_x - score_text.get_width() // 2, center_y - 30))
        self.screen.blit(crossings_text, (center_x - crossings_text.get_width() // 2, center_y + 10))
        self.screen.blit(restart_text, (center_x - restart_text.get_width() // 2, center_y + 60))
        self.screen.blit(quit_text, (center_x - quit_text.get_width() // 2, center_y + 90))

    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
