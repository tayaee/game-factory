"""Main game logic for Vector Ice Hockey Classic."""

import pygame
from config import *
from entities import Vector, Puck, Player, AIOpponent, RINK_MARGIN


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Ice Hockey Classic")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 28)
        self.tiny_font = pygame.font.Font(None, 20)

        self.reset_game()

    def reset_game(self):
        """Reset the entire game state."""
        self.puck = Puck()
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.25, COLOR_PLAYER)
        self.opponent = AIOpponent(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.75)

        self.player_score = 0
        self.opponent_score = 0
        self.game_time = MATCH_TIME_SECONDS
        self.game_over = False
        self.goal_scored = False
        self.goal_timer = 0
        self.goal_message = ""
        self.last_frame_time = pygame.time.get_ticks()

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

        # Handle continuous key input for player movement
        if not self.game_over and not self.goal_scored:
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_LEFT]:
                dx = -1
            elif keys[pygame.K_RIGHT]:
                dx = 1
            if keys[pygame.K_UP]:
                dy = -1
            elif keys[pygame.K_DOWN]:
                dy = 1

            # Normalize diagonal movement
            if dx != 0 and dy != 0:
                dx *= 0.707
                dy *= 0.707

            self.player.move(dx, dy)

        return True

    def update(self):
        """Update game state."""
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - self.last_frame_time) / 1000.0
        self.last_frame_time = current_time

        if self.game_over:
            return

        # Handle goal scored delay
        if self.goal_scored:
            self.goal_timer += 1
            if self.goal_timer > 120:  # 2 seconds at 60 FPS
                self._reset_positions()
                self.goal_scored = False
                self.goal_timer = 0
            return

        # Update timer
        self.game_time -= delta_time
        if self.game_time <= 0:
            self.game_time = 0
            self.game_over = True

        # Update entities
        self.player.update()
        self.opponent.update()
        self.opponent.update_ai(self.puck)
        self.puck.update()

        # Check collisions
        self._check_player_puck_collision(self.player)
        self._check_player_puck_collision(self.opponent)

        # Check goals
        self._check_goals()

    def _check_player_puck_collision(self, player):
        """Handle collision between player and puck."""
        dist_vec = self.puck.pos - player.pos
        distance = dist_vec.magnitude()
        min_dist = self.puck.radius + player.radius

        if distance < min_dist:
            # Normalize the collision vector
            normal = dist_vec.normalize()

            # Separate puck from player
            overlap = min_dist - distance
            self.puck.pos = self.puck.pos + (normal * overlap)

            # Transfer velocity
            player_speed = player.vel.magnitude()
            if player_speed > 0:
                # Add player's velocity to puck
                hit_force = player_vel_to_puck = player.vel * 1.5
                self.puck.vel = self.puck.vel + hit_force

            # Ensure minimum puck speed on hit
            if self.puck.vel.magnitude() < 2:
                self.puck.vel = normal * 3

    def _check_goals(self):
        """Check if puck entered a goal."""
        goal_left = SCREEN_WIDTH / 2 - GOAL_WIDTH / 2
        goal_right = SCREEN_WIDTH / 2 + GOAL_WIDTH / 2

        # Check opponent's goal (top) - player scores
        if (self.puck.pos.y < RINK_MARGIN and
                goal_left < self.puck.pos.x < goal_right):
            self.player_score += SCORE_GOAL
            self._trigger_goal("GOAL!")

        # Check player's goal (bottom) - opponent scores
        elif (self.puck.pos.y > SCREEN_HEIGHT - RINK_MARGIN and
              goal_left < self.puck.pos.x < goal_right):
            self.opponent_score += SCORE_GOAL
            self._trigger_goal("OPPONENT SCORES!")

    def _trigger_goal(self, message):
        """Handle goal scored."""
        self.goal_scored = True
        self.goal_message = message
        self.goal_timer = 0

        # Stop the puck
        self.puck.vel = Vector(0, 0)

    def _reset_positions(self):
        """Reset positions after a goal."""
        self.puck.reset()
        self.player.reset()
        self.opponent.reset()

    def draw(self):
        """Render the game."""
        self.screen.fill(COLOR_RINK)

        # Draw rink
        self._draw_rink()

        # Draw entities
        self.player.draw(self.screen)
        self.opponent.draw(self.screen)
        self.puck.draw(self.screen)

        # Draw UI
        self._draw_ui()

        # Draw goal message
        if self.goal_scored:
            self._draw_goal_message()

        # Draw game over screen
        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_rink(self):
        """Draw the hockey rink."""
        # Draw rink border
        border_rect = pygame.Rect(
            RINK_MARGIN - 5, RINK_MARGIN - 5,
            SCREEN_WIDTH - RINK_MARGIN * 2 + 10,
            SCREEN_HEIGHT - RINK_MARGIN * 2 + 10
        )
        pygame.draw.rect(self.screen, COLOR_RINK_BORDER, border_rect, 5)

        # Draw center line
        pygame.draw.line(
            self.screen, COLOR_CENTER_LINE,
            (RINK_MARGIN, SCREEN_HEIGHT / 2),
            (SCREEN_WIDTH - RINK_MARGIN, SCREEN_HEIGHT / 2),
            3
        )

        # Draw center circle
        pygame.draw.circle(
            self.screen, COLOR_CENTER_LINE,
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            60, 3
        )

        # Draw center dot
        pygame.draw.circle(
            self.screen, COLOR_LINES,
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            8
        )

        # Draw goals
        goal_left = SCREEN_WIDTH / 2 - GOAL_WIDTH / 2

        # Top goal (opponent's)
        top_goal_rect = pygame.Rect(
            goal_left, RINK_MARGIN - 10,
            GOAL_WIDTH, 15
        )
        pygame.draw.rect(self.screen, COLOR_GOAL, top_goal_rect)

        # Bottom goal (player's)
        bottom_goal_rect = pygame.Rect(
            goal_left, SCREEN_HEIGHT - RINK_MARGIN - 5,
            GOAL_WIDTH, 15
        )
        pygame.draw.rect(self.screen, COLOR_GOAL, bottom_goal_rect)

        # Draw goal creases
        crease_width = 80
        crease_depth = 30

        # Top crease
        top_crease = pygame.Rect(
            SCREEN_WIDTH / 2 - crease_width / 2,
            RINK_MARGIN,
            crease_width,
            crease_depth
        )
        pygame.draw.rect(self.screen, COLOR_LINES, top_crease, 2)

        # Bottom crease
        bottom_crease = pygame.Rect(
            SCREEN_WIDTH / 2 - crease_width / 2,
            SCREEN_HEIGHT - RINK_MARGIN - crease_depth,
            crease_width,
            crease_depth
        )
        pygame.draw.rect(self.screen, COLOR_LINES, bottom_crease, 2)

    def _draw_ui(self):
        """Draw user interface."""
        # Draw scores
        player_text = self.font.render(str(self.player_score), True, COLOR_PLAYER)
        opponent_text = self.font.render(str(self.opponent_score), True, COLOR_OPPONENT)

        self.screen.blit(player_text, (50, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(opponent_text, (50, SCREEN_HEIGHT // 2 + 30))

        # Draw time
        minutes = int(self.game_time // 60)
        seconds = int(self.game_time % 60)
        time_text = self.font.render(
            f"{minutes}:{seconds:02d}",
            True, COLOR_TEXT
        )
        self.screen.blit(
            time_text,
            (SCREEN_WIDTH - time_text.get_width() - 30, SCREEN_HEIGHT // 2 - time_text.get_height() // 2)
        )

        # Draw labels
        player_label = self.tiny_font.render("YOU", True, COLOR_TEXT)
        opponent_label = self.tiny_font.render("OPPONENT", True, COLOR_TEXT)
        time_label = self.tiny_font.render("TIME", True, COLOR_TEXT)

        self.screen.blit(player_label, (50, SCREEN_HEIGHT // 2 - 90))
        self.screen.blit(opponent_label, (50, SCREEN_HEIGHT // 2 + 65))
        self.screen.blit(time_label, (SCREEN_WIDTH - time_label.get_width() - 30, SCREEN_HEIGHT // 2 - 50))

    def _draw_goal_message(self):
        """Draw goal scored message."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(100)
        overlay.fill((255, 255, 255))
        self.screen.blit(overlay, (0, 0))

        goal_text = self.font.render(self.goal_message, True, COLOR_LINES)
        self.screen.blit(
            goal_text,
            (SCREEN_WIDTH // 2 - goal_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50)
        )

        score_text = self.small_font.render(
            f"{self.player_score} - {self.opponent_score}",
            True, COLOR_TEXT
        )
        self.screen.blit(
            score_text,
            (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10)
        )

    def _draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Determine winner
        if self.player_score > self.opponent_score:
            result_text = "YOU WIN!"
            result_color = (50, 200, 50)
        elif self.opponent_score > self.player_score:
            result_text = "YOU LOSE!"
            result_color = (200, 50, 50)
        else:
            result_text = "IT'S A TIE!"
            result_color = (200, 200, 50)

        result_render = self.font.render(result_text, True, result_color)
        score_render = self.font.render(
            f"Final Score: {self.player_score} - {self.opponent_score}",
            True, (255, 255, 255)
        )
        restart_render = self.small_font.render("Press SPACE to restart", True, (200, 200, 200))
        quit_render = self.small_font.render("Press ESC to quit", True, (200, 200, 200))

        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        self.screen.blit(result_render, (center_x - result_render.get_width() // 2, center_y - 60))
        self.screen.blit(score_render, (center_x - score_render.get_width() // 2, center_y))
        self.screen.blit(restart_render, (center_x - restart_render.get_width() // 2, center_y + 60))
        self.screen.blit(quit_render, (center_x - quit_render.get_width() // 2, center_y + 90))

    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
