"""Main game loop and rendering."""

import pygame
from config import *
from bird import Bird
from pipe import PipeManager


class Game:
    """Main game class managing rendering and game loop."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Flappy Bird Classic")
        self.clock = pygame.time.Clock()
        self.running = True

        self.bird = Bird()
        self.pipe_manager = PipeManager()
        self.score = 0
        self.high_score = 0
        self.game_state = "ready"  # ready, playing, game_over

        # Fonts
        self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
        self.message_font = pygame.font.Font(None, MESSAGE_FONT_SIZE)

    def reset_game(self):
        """Reset game to initial state."""
        self.bird = Bird()
        self.pipe_manager = PipeManager()
        self.score = 0
        self.game_state = "ready"

    def handle_input(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_action()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.handle_action()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def handle_action(self):
        """Handle jump/restart action."""
        if self.game_state == "ready":
            self.game_state = "playing"
            self.bird.jump()
        elif self.game_state == "playing":
            self.bird.jump()
        elif self.game_state == "game_over":
            if self.score > self.high_score:
                self.high_score = self.score
            self.reset_game()

    def update(self):
        """Update game state."""
        if self.game_state == "playing":
            current_time = pygame.time.get_ticks()
            dt = self.clock.get_time()

            self.bird.update()
            self.pipe_manager.update(current_time, dt)

            # Check collisions
            bird_rect = self.bird.get_rect()

            # Ground collision
            if bird_rect.bottom >= SCREEN_HEIGHT - GROUND_HEIGHT:
                self.game_state = "game_over"
            # Ceiling collision
            elif bird_rect.top <= 0:
                self.game_state = "game_over"
            # Pipe collision
            elif self.pipe_manager.check_collision(bird_rect):
                self.game_state = "game_over"

            # Update score
            self.score += self.pipe_manager.update_score(self.bird.x)

    def render(self):
        """Render the game."""
        self.screen.fill(SKY_BLUE)

        # Draw ground
        pygame.draw.rect(
            self.screen,
            GROUND_COLOR,
            (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT)
        )
        pygame.draw.line(
            self.screen,
            (139, 90, 43),
            (0, SCREEN_HEIGHT - GROUND_HEIGHT),
            (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT),
            3
        )

        # Draw pipes
        self.pipe_manager.draw(self.screen)

        # Draw bird
        self.bird.draw(self.screen)

        # Draw score
        score_text = self.score_font.render(str(self.score), True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(score_text, score_rect)

        # Draw high score
        high_score_text = self.message_font.render(f"Best: {self.high_score}", True, WHITE)
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, 90))
        self.screen.blit(high_score_text, high_score_rect)

        # Draw messages
        if self.game_state == "ready":
            msg = "Press SPACE or CLICK to start"
            msg_text = self.message_font.render(msg, True, WHITE)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(msg_text, msg_rect)
        elif self.game_state == "game_over":
            msg = "Game Over! Press SPACE to restart"
            msg_text = self.message_font.render(msg, True, (255, 100, 100))
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(msg_text, msg_rect)

        pygame.display.flip()

    def step_ai(self, action):
        """
        Execute an AI action and return observation, reward, done.

        Args:
            action: 0 = do nothing, 1 = jump

        Returns:
            (observation, reward, done)
        """
        prev_score = self.score

        if action == 1:
            self.bird.jump()

        self.update()

        reward = 0
        done = False

        if self.game_state == "playing":
            reward += REWARD_PER_FRAME
            if self.score > prev_score:
                reward += REWARD_PIPE_CLEARED
        elif self.game_state == "game_over":
            reward = REWARD_COLLISION
            done = True

        return self.get_observation(), reward, done

    def get_observation(self):
        """Return current game state for AI."""
        next_pipe = self.pipe_manager.get_next_pipe(self.bird.x)

        obs = {
            "bird_y": self.bird.y,
            "bird_velocity": self.bird.velocity,
            "score": self.score,
            "game_state": self.game_state
        }

        if next_pipe:
            obs["next_pipe_dist_x"] = next_pipe.x - self.bird.x
            obs["next_pipe_gap_y"] = next_pipe.gap_y
            obs["next_pipe_gap_bottom"] = next_pipe.gap_y + PIPE_GAP
        else:
            obs["next_pipe_dist_x"] = SCREEN_WIDTH - self.bird.x
            obs["next_pipe_gap_y"] = SCREEN_HEIGHT // 2 - PIPE_GAP // 2
            obs["next_pipe_gap_bottom"] = SCREEN_HEIGHT // 2 + PIPE_GAP // 2

        return obs

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_input()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
