"""Main game logic for Vector Frogger."""

import pygame
from config import *
from entities import Frog, Lane, Lilypad


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Frogger Road Cross")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        """Reset the entire game state."""
        self.frog = Frog()
        self.lanes = []
        self.lilypads = []
        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_over = False
        self.level_complete = False
        self.high_score = 0

        self._init_lanes()
        self._init_lilypads()

    def _init_lanes(self):
        """Initialize obstacle lanes."""
        self.lanes = []
        for row, lane_type, speed, size_type, spacing in LANES:
            self.lanes.append(Lane(row, lane_type, speed, size_type, spacing))

    def _init_lilypads(self):
        """Initialize goal lilypads."""
        self.lilypads = []
        for i in range(NUM_LILYPADS):
            x = (i + 1) * LILYPAD_GAP
            self.lilypads.append(Lilypad(x))

    def handle_input(self):
        """Handle keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                    elif event.key == pygame.K_r:
                        self.reset_game()
                elif self.level_complete:
                    if event.key == pygame.K_SPACE:
                        self._next_level()
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

                    if moved and self.frog.grid_y < START_ROW:
                        self.score += SCORE_FORWARD

        return True

    def update(self):
        """Update game state."""
        if self.game_over or self.level_complete:
            return

        self.frog.update()

        # Update lanes with speed multiplier based on level
        speed_multiplier = 1.0 + (self.level - 1) * 0.2
        for lane in self.lanes:
            lane.update(speed_multiplier)

        # Check collisions
        self._check_collisions()

        # Check if frog reached goal
        if self.frog.grid_y == GOAL_ROW:
            self._check_goal()

    def _check_collisions(self):
        """Check frog collisions with obstacles."""
        frog_rect = self.frog.get_rect()
        frog_row = self.frog.grid_y

        # Check if in water zone
        if WATER_START <= frog_row <= WATER_END:
            on_log = False
            for lane in self.lanes:
                if lane.row == frog_row and lane.type == 'log':
                    obs = lane.check_collision(frog_rect)
                    if obs:
                        on_log = True
                        # Move frog with log
                        self.frog.x += obs.speed * (1.0 + (self.level - 1) * 0.2)
                        self.frog.grid_x = int(self.frog.x // GRID_SIZE)

                        # Check if carried off screen
                        if self.frog.x < 0 or self.frog.x > SCREEN_WIDTH:
                            self._death()
                        break

            if not on_log:
                self._death()

        # Check if in road zone
        elif ROAD_START <= frog_row <= ROAD_END:
            for lane in self.lanes:
                if lane.row == frog_row and lane.type in ['car', 'truck']:
                    if lane.check_collision(frog_rect):
                        self._death()
                        break

    def _check_goal(self):
        """Check if frog reached a lilypad."""
        frog_rect = self.frog.get_rect()

        for lilypad in self.lilypads:
            if not lilypad.filled and lilypad.get_rect().colliderect(frog_rect):
                lilypad.filled = True
                self.score += SCORE_GOAL

                # Check if all lilypads filled
                if all(lp.filled for lp in self.lilypads):
                    self.level_complete = True
                else:
                    self.frog.reset()
                return

        # Missed all lilypads
        self._death()

    def _death(self):
        """Handle frog death."""
        self.lives -= 1
        self.score += PENALTY_DEATH

        if self.lives <= 0:
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
        else:
            self.frog.reset()

    def _next_level(self):
        """Advance to next level."""
        self.level += 1
        self.score += SCORE_LEVEL_BONUS
        self._init_lilypads()
        self.frog.reset()
        self.level_complete = False

    def draw(self):
        """Render the game."""
        self.screen.fill(COLOR_BG)

        # Draw zones
        self._draw_zones()

        # Draw lilypads
        for lilypad in self.lilypads:
            lilypad.draw(self.screen)

        # Draw lanes
        for lane in self.lanes:
            lane.draw(self.screen)

        # Draw frog
        self.frog.draw(self.screen)

        # Draw UI
        self._draw_ui()

        # Draw game over or level complete screen
        if self.game_over:
            self._draw_game_over()
        elif self.level_complete:
            self._draw_level_complete()

        pygame.display.flip()

    def _draw_zones(self):
        """Draw background zones."""
        # Goal zone (top)
        goal_rect = pygame.Rect(0, 0, SCREEN_WIDTH, GRID_SIZE)
        pygame.draw.rect(self.screen, COLOR_SAFE_ZONE, goal_rect)

        # Water zone
        water_rect = pygame.Rect(
            0, WATER_START * GRID_SIZE,
            SCREEN_WIDTH, (WATER_END - WATER_START + 1) * GRID_SIZE
        )
        pygame.draw.rect(self.screen, COLOR_WATER, water_rect)

        # Road zone
        road_rect = pygame.Rect(
            0, ROAD_START * GRID_SIZE,
            SCREEN_WIDTH, (ROAD_END - ROAD_START + 1) * GRID_SIZE
        )
        pygame.draw.rect(self.screen, COLOR_ROAD, road_rect)

        # Start zone (bottom)
        start_rect = pygame.Rect(0, START_ROW * GRID_SIZE, SCREEN_WIDTH, GRID_SIZE)
        pygame.draw.rect(self.screen, COLOR_GRASS, start_rect)

        # Draw lane dividers for road
        for row in range(ROAD_START, ROAD_END + 1):
            y = row * GRID_SIZE + GRID_SIZE
            pygame.draw.line(self.screen, (60, 60, 70), (0, y), (SCREEN_WIDTH, y), 2)

        # Draw middle safety zone
        middle_y = (ROAD_START - 1) * GRID_SIZE
        middle_rect = pygame.Rect(0, middle_y, SCREEN_WIDTH, GRID_SIZE)
        pygame.draw.rect(self.screen, COLOR_GRASS, middle_rect)

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
            high_text = self.small_font.render(f"High: {self.high_score}", True, (150, 150, 150))
            self.screen.blit(high_text, (10, 50))

    def _draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("GAME OVER", True, COLOR_GAME_OVER)
        score_text = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
        restart_text = self.small_font.render("Press SPACE to restart", True, (200, 200, 200))
        quit_text = self.small_font.render("Press ESC to quit", True, (200, 200, 200))

        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                                          SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2,
                                      SCREEN_HEIGHT // 2))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                                        SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2,
                                     SCREEN_HEIGHT // 2 + 80))

    def _draw_level_complete(self):
        """Draw level complete screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        complete_text = self.font.render(f"LEVEL {self.level} COMPLETE!", True, COLOR_LILYPAD_FILLED)
        bonus_text = self.font.render(f"Bonus: +{SCORE_LEVEL_BONUS}", True, COLOR_TEXT)
        continue_text = self.small_font.render("Press SPACE to continue", True, (200, 200, 200))

        self.screen.blit(complete_text, (SCREEN_WIDTH // 2 - complete_text.get_width() // 2,
                                         SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(bonus_text, (SCREEN_WIDTH // 2 - bonus_text.get_width() // 2,
                                      SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2,
                                         SCREEN_HEIGHT // 2 + 60))

    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
