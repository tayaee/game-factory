"""Main game loop and rendering."""

import pygame
import random
from config import *
from ball import Ball
from flipper import Flipper
from table import Bumper, Slingshot, Wall


class Game:
    """Main game class managing rendering and game loop."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Pinball Gravity Physics")
        self.clock = pygame.time.Clock()
        self.running = True

        self.ball = Ball()
        self.left_flipper = Flipper(*LEFT_FLIPPER_PIVOT, is_left=True)
        self.right_flipper = Flipper(*RIGHT_FLIPPER_PIVOT, is_left=False)
        self.bumpers = []
        self.slingshots = []
        self.walls = []

        self.score = 0
        self.high_score = 0
        self.game_state = "ready"  # ready, playing, game_over
        self.ball_count = 3

        self.setup_table()

        # Fonts
        self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
        self.message_font = pygame.font.Font(None, MESSAGE_FONT_SIZE)

    def setup_table(self):
        """Create the pinball table layout."""
        # Bumpers
        self.bumpers = [
            Bumper(200, 200, color=CYAN),
            Bumper(150, 150, color=YELLOW),
            Bumper(250, 150, color=YELLOW),
            Bumper(100, 250, color=ORANGE),
            Bumper(300, 250, color=ORANGE),
            Bumper(200, 300, color=PURPLE),
        ]

        # Slingshots
        self.slingshots = [
            Slingshot(80, 400, color=GREEN),
            Slingshot(320, 400, color=GREEN),
        ]

        # Walls
        self.walls = [
            # Left side
            Wall(0, 100, 0, 500),
            Wall(0, 500, 100, 530),
            # Right side
            Wall(400, 100, 400, 500),
            Wall(400, 500, 300, 530),
            # Top corners
            Wall(0, 0, 100, 100),
            Wall(400, 0, 300, 100),
            # Top curve approximation
            Wall(100, 100, 150, 50),
            Wall(150, 50, 200, 30),
            Wall(200, 30, 250, 50),
            Wall(250, 50, 300, 100),
            # Drain guides
            Wall(100, 530, 140, 560),
            Wall(300, 530, 260, 560),
        ]

    def reset_ball(self):
        """Reset ball to starting position."""
        self.ball = Ball()
        self.ball.launch()

    def reset_game(self):
        """Reset game to initial state."""
        self.score = 0
        self.ball_count = 3
        self.game_state = "ready"
        self.reset_ball()

    def handle_input(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.left_flipper.activate()
                elif event.key == pygame.K_RIGHT:
                    self.right_flipper.activate()
                elif event.key == pygame.K_SPACE:
                    self.handle_action()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.left_flipper.deactivate()
                elif event.key == pygame.K_RIGHT:
                    self.right_flipper.deactivate()

    def handle_action(self):
        """Handle start/restart action."""
        if self.game_state == "ready":
            self.game_state = "playing"
            self.reset_ball()
        elif self.game_state == "game_over":
            if self.score > self.high_score:
                self.high_score = self.score
            self.reset_game()

    def update(self):
        """Update game state."""
        if self.game_state == "playing":
            # Update flippers
            self.left_flipper.update()
            self.right_flipper.update()

            # Update ball
            self.ball.update()

            # Check collisions with bumpers
            for bumper in self.bumpers:
                bumper.update()
                if bumper.check_collision(self.ball):
                    self.score += bumper.points

            # Check collisions with slingshots
            for slingshot in self.slingshots:
                slingshot.update()
                if slingshot.check_collision(self.ball):
                    self.score += slingshot.points

            # Check collisions with walls
            for wall in self.walls:
                wall.check_collision(self.ball)

            # Check collisions with flippers
            self.left_flipper.check_collision(self.ball)
            self.right_flipper.check_collision(self.ball)

            # Check if ball is lost
            if self.ball.is_lost():
                self.ball_count -= 1
                if self.ball_count > 0:
                    self.reset_ball()
                else:
                    self.game_state = "game_over"

    def render(self):
        """Render the game."""
        self.screen.fill(BLACK)

        # Draw walls
        for wall in self.walls:
            wall.draw(self.screen)

        # Draw bumpers
        for bumper in self.bumpers:
            bumper.draw(self.screen)

        # Draw slingshots
        for slingshot in self.slingshots:
            slingshot.draw(self.screen)

        # Draw flippers
        self.left_flipper.draw(self.screen)
        self.right_flipper.draw(self.screen)

        # Draw ball
        self.ball.draw(self.screen)

        # Draw drain line
        pygame.draw.line(self.screen, RED, (140, 560), (260, 560), 2)

        # Draw score
        score_text = self.score_font.render(f"{self.score:06d}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(score_text, score_rect)

        # Draw high score
        high_score_text = self.message_font.render(f"HIGH: {self.high_score:06d}", True, YELLOW)
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(high_score_text, high_score_rect)

        # Draw ball count
        balls_text = self.message_font.render(f"BALLS: {self.ball_count}", True, WHITE)
        balls_rect = balls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        self.screen.blit(balls_text, balls_rect)

        # Draw messages
        if self.game_state == "ready":
            msg = "Press SPACE to start"
            msg_text = self.message_font.render(msg, True, WHITE)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(msg_text, msg_rect)

            controls = "Left/Right Arrows: Flippers"
            controls_text = self.message_font.render(controls, True, GRAY)
            controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            self.screen.blit(controls_text, controls_rect)
        elif self.game_state == "game_over":
            msg = "GAME OVER"
            msg_text = self.score_font.render(msg, True, RED)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(msg_text, msg_rect)

            score_msg = f"Final Score: {self.score}"
            score_msg_text = self.message_font.render(score_msg, True, WHITE)
            score_msg_rect = score_msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(score_msg_text, score_msg_rect)

            restart_msg = "Press SPACE to restart"
            restart_text = self.message_font.render(restart_msg, True, GRAY)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def step_ai(self, action):
        """
        Execute an AI action and return observation, reward, done.

        Args:
            action: 0 = idle, 1 = left flipper, 2 = right flipper, 3 = both

        Returns:
            (observation, reward, done)
        """
        prev_score = self.score

        # Execute action
        if action == 1:
            self.left_flipper.activate()
        elif action == 2:
            self.right_flipper.activate()
        elif action == 3:
            self.left_flipper.activate()
            self.right_flipper.activate()

        self.update()

        # Deactivate flippers after update
        self.left_flipper.deactivate()
        self.right_flipper.deactivate()

        reward = 0
        done = False

        if self.game_state == "playing":
            reward += REWARD_SURVIVAL_FRAME
            reward += (self.score - prev_score)
        elif self.game_state == "game_over":
            reward = REWARD_BALL_LOST
            done = True

        return self.get_observation(), reward, done

    def get_observation(self):
        """Return current game state for AI."""
        return {
            "ball_x": self.ball.x,
            "ball_y": self.ball.y,
            "ball_vx": self.ball.vx,
            "ball_vy": self.ball.vy,
            "left_flipper_angle": self.left_flipper.get_angle_for_observation(),
            "right_flipper_angle": self.right_flipper.get_angle_for_observation(),
            "score": self.score,
            "ball_count": self.ball_count,
            "game_state": self.game_state
        }

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_input()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
