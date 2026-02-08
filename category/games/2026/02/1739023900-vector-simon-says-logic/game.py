"""Main game loop and rendering."""

import pygame
import random
import time
from enum import Enum
from config import *


class Panel(Enum):
    """Game panel positions."""
    RED = 0
    BLUE = 1
    GREEN = 2
    YELLOW = 3


class GameState(Enum):
    """Game states."""
    IDLE = "idle"
    SHOWING_SEQUENCE = "showing_sequence"
    WAITING_INPUT = "waiting_input"
    GAME_OVER = "game_over"


class Game:
    """Main game class managing Simon Says logic and rendering."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Simon Says Logic")
        self.clock = pygame.time.Clock()
        self.running = True

        # Game state
        self.state = GameState.IDLE
        self.sequence = []
        self.player_input = []
        self.score = 0
        self.round_number = 1
        self.high_score = 0

        # Animation state
        self.lit_panel = None
        self.flash_end_time = 0
        self.sequence_index = 0
        self.last_flash_time = 0
        self.input_start_time = 0

        # Panel rectangles for click detection
        self.panel_rects = self._create_panel_rects()

        # Keyboard mapping
        self.key_mapping = {
            pygame.K_q: Panel.RED,
            pygame.K_w: Panel.BLUE,
            pygame.K_a: Panel.GREEN,
            pygame.K_s: Panel.YELLOW
        }

        # Fonts
        self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
        self.status_font = pygame.font.Font(None, STATUS_FONT_SIZE)
        self.instruction_font = pygame.font.Font(None, INSTRUCTION_FONT_SIZE)

    def _create_panel_rects(self):
        """Create collision rectangles for each panel."""
        rects = {}
        half_size = PANEL_SIZE // 2

        # Red (Top-Left)
        rects[Panel.RED] = pygame.Rect(
            GRID_OFFSET_X,
            GRID_OFFSET_Y,
            PANEL_SIZE,
            PANEL_SIZE
        )

        # Blue (Top-Right)
        rects[Panel.BLUE] = pygame.Rect(
            GRID_OFFSET_X + PANEL_SIZE + PANEL_PADDING,
            GRID_OFFSET_Y,
            PANEL_SIZE,
            PANEL_SIZE
        )

        # Green (Bottom-Left)
        rects[Panel.GREEN] = pygame.Rect(
            GRID_OFFSET_X,
            GRID_OFFSET_Y + PANEL_SIZE + PANEL_PADDING,
            PANEL_SIZE,
            PANEL_SIZE
        )

        # Yellow (Bottom-Right)
        rects[Panel.YELLOW] = pygame.Rect(
            GRID_OFFSET_X + PANEL_SIZE + PANEL_PADDING,
            GRID_OFFSET_Y + PANEL_SIZE + PANEL_PADDING,
            PANEL_SIZE,
            PANEL_SIZE
        )

        return rects

    def reset_game(self):
        """Reset game to initial state."""
        self.sequence = []
        self.player_input = []
        self.score = 0
        self.round_number = 1
        self.state = GameState.IDLE
        self.lit_panel = None

    def start_round(self):
        """Start a new round by adding to the sequence."""
        self.sequence.append(random.choice(list(Panel)))
        self.player_input = []
        self.sequence_index = 0
        self.last_flash_time = time.time() * 1000
        self.state = GameState.SHOWING_SEQUENCE

    def get_panel_color(self, panel):
        """Get the color for a panel (lit or unlit)."""
        colors = {
            Panel.RED: (PANEL_RED_LIT if self.lit_panel == panel else PANEL_RED),
            Panel.BLUE: (PANEL_BLUE_LIT if self.lit_panel == panel else PANEL_BLUE),
            Panel.GREEN: (PANEL_GREEN_LIT if self.lit_panel == panel else PANEL_GREEN),
            Panel.YELLOW: (PANEL_YELLOW_LIT if self.lit_panel == panel else PANEL_YELLOW)
        }
        return colors[panel]

    def handle_input(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_mouse_click(event.pos)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self._handle_space_press()
                elif event.key in self.key_mapping:
                    self._handle_panel_input(self.key_mapping[event.key])

    def _handle_mouse_click(self, pos):
        """Handle mouse click on a panel."""
        if self.state == GameState.WAITING_INPUT:
            for panel, rect in self.panel_rects.items():
                if rect.collidepoint(pos):
                    self._handle_panel_input(panel)
                    break

    def _handle_space_press(self):
        """Handle space bar for game flow."""
        if self.state == GameState.IDLE or self.state == GameState.GAME_OVER:
            if self.state == GameState.GAME_OVER and self.score > self.high_score:
                self.high_score = self.score
            self.reset_game()
            self.start_round()

    def _handle_panel_input(self, panel):
        """Handle panel selection during gameplay."""
        if self.state == GameState.WAITING_INPUT:
            self.lit_panel = panel
            self.flash_end_time = time.time() * 1000 + FLASH_DURATION // 2

            # Check if correct
            expected = self.sequence[len(self.player_input)]
            if panel == expected:
                self.player_input.append(panel)

                # Check if round complete
                if len(self.player_input) == len(self.sequence):
                    self.score += POINTS_PER_ROUND
                    self.round_number += 1
                    self.state = GameState.IDLE
                    pygame.time.set_timer(pygame.USEREVENT, 1000, loops=1)
            else:
                # Wrong input - game over
                self.state = GameState.GAME_OVER

    def update(self):
        """Update game state."""
        current_time = time.time() * 1000

        # Handle flash timer
        if self.lit_panel is not None:
            if current_time >= self.flash_end_time:
                self.lit_panel = None

        # Handle sequence playback
        if self.state == GameState.SHOWING_SEQUENCE:
            if current_time - self.last_flash_time >= BETWEEN_FLASH_DELAY:
                if self.lit_panel is None:
                    # Flash next panel
                    self.lit_panel = self.sequence[self.sequence_index]
                    self.flash_end_time = current_time + FLASH_DURATION
                    self.last_flash_time = current_time
                else:
                    # Move to next panel
                    self.sequence_index += 1
                    self.lit_panel = None
                    self.last_flash_time = current_time

                    if self.sequence_index >= len(self.sequence):
                        self.state = GameState.WAITING_INPUT
                        self.input_start_time = current_time

        # Handle input timeout
        if self.state == GameState.WAITING_INPUT:
            if current_time - self.input_start_time >= INPUT_TIMEOUT:
                self.state = GameState.GAME_OVER

    def render(self):
        """Render the game."""
        self.screen.fill(BACKGROUND)

        # Draw panels
        for panel, rect in self.panel_rects.items():
            color = self.get_panel_color(panel)
            pygame.draw.rect(self.screen, color, rect, border_radius=15)

            # Add border
            border_color = (
                PANEL_RED_LIT if panel == Panel.RED else
                PANEL_BLUE_LIT if panel == Panel.BLUE else
                PANEL_GREEN_LIT if panel == Panel.GREEN else
                PANEL_YELLOW_LIT
            )
            pygame.draw.rect(self.screen, border_color, rect, width=4, border_radius=15)

        # Draw score
        score_text = self.score_font.render(str(self.score), True, TEXT_COLOR)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(score_text, score_rect)

        # Draw round number
        round_text = self.status_font.render(f"Round: {self.round_number}", True, TEXT_COLOR)
        round_rect = round_text.get_rect(center=(SCREEN_WIDTH // 2, 130))
        self.screen.blit(round_text, round_text.get_rect(center=(SCREEN_WIDTH // 2, 130)))

        # Draw high score
        high_score_text = self.instruction_font.render(f"Best: {self.high_score}", True, (150, 150, 150))
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, 160))
        self.screen.blit(high_score_text, high_score_rect)

        # Draw status messages
        if self.state == GameState.IDLE:
            msg = "Press SPACE to start"
            msg_text = self.status_font.render(msg, True, TEXT_COLOR)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
            self.screen.blit(msg_text, msg_rect)
        elif self.state == GameState.GAME_OVER:
            msg = "Game Over! Press SPACE to restart"
            msg_text = self.status_font.render(msg, True, GAME_OVER_COLOR)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
            self.screen.blit(msg_text, msg_rect)
        elif self.state == GameState.SHOWING_SEQUENCE:
            msg = "Watch the sequence..."
            msg_text = self.instruction_font.render(msg, True, (180, 180, 180))
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
            self.screen.blit(msg_text, msg_rect)
        elif self.state == GameState.WAITING_INPUT:
            msg = "Repeat the sequence!"
            remaining = max(0, INPUT_TIMEOUT - int((time.time() * 1000 - self.input_start_time) / 100) / 10)
            msg_text = self.instruction_font.render(f"Repeat! ({remaining:.1f}s)", True, (100, 200, 100))
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
            self.screen.blit(msg_text, msg_rect)

        # Draw controls hint
        controls = "Controls: Q (Red) | W (Blue) | A (Green) | S (Yellow) | Mouse"
        controls_text = self.instruction_font.render(controls, True, (100, 100, 100))
        controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 25))
        self.screen.blit(controls_text, controls_rect)

        pygame.display.flip()

    def step_ai(self, action):
        """
        Execute an AI action and return observation, reward, done.

        Args:
            action: 0-3 corresponding to RED, BLUE, GREEN, YELLOW panels

        Returns:
            (observation, reward, done)
        """
        if self.state == GameState.IDLE:
            self.start_round()

        if self.state == GameState.WAITING_INPUT:
            panel = list(Panel)[action]
            prev_score = self.score
            self._handle_panel_input(panel)

            reward = 0
            done = False

            if self.state == GameState.GAME_OVER:
                reward = REWARD_WRONG
                done = True
            elif self.score > prev_score:
                reward = REWARD_ROUND_COMPLETE
                # Auto-start next round for AI
                self.start_round()
            else:
                reward = REWARD_CORRECT

            return self.get_observation(), reward, done

        return self.get_observation(), 0, False

    def get_observation(self):
        """Return current game state for AI."""
        return {
            "sequence": [p.value for p in self.sequence],
            "sequence_length": len(self.sequence),
            "player_progress": len(self.player_input),
            "state": self.state.value,
            "lit_panel": self.lit_panel.value if self.lit_panel else -1,
            "score": self.score,
            "round": self.round_number
        }

    def run(self):
        """Main game loop."""
        def auto_start_round(event):
            if self.state == GameState.IDLE and self.round_number > 1:
                self.start_round()

        pygame.USEREVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(pygame.USEREVENT, 0)
        pygame.time.set_timer(pygame.USEREVENT, 0)

        while self.running:
            self.handle_input()
            self.update()
            self.render()
            self.clock.tick(FPS)

            # Auto-start next round after completion
            if self.state == GameState.IDLE and self.round_number > 1:
                self.start_round()

        pygame.quit()
