"""Renderer for Vector Sky Ski Slalom."""

import pygame
from config import *


class Renderer:
    def __init__(self, game):
        self.game = game
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Sky Ski Slalom")
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def render(self):
        self.screen.fill(WHITE)

        # Draw slope lines (creating sense of movement)
        offset = (self.game.distance * 0.5) % 50
        for y in range(int(-offset), SCREEN_HEIGHT, 50):
            pygame.draw.line(
                self.screen,
                LIGHT_BLUE,
                (0, y),
                (SCREEN_WIDTH, y),
                1
            )

        # Draw gates
        for gate in self.game.gates:
            self.draw_gate(gate)

        # Draw obstacles
        for obstacle in self.game.obstacles:
            self.draw_obstacle(obstacle)

        # Draw player
        self.draw_player()

        # Draw HUD
        self.draw_hud()

        # Draw game over screen
        if self.game.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_player(self):
        p = self.game.player
        # Simple vector-style skier
        points = [
            (p.x, p.y - p.height // 2),      # Head
            (p.x - p.width // 2, p.y + p.height // 2),  # Left ski
            (p.x + p.width // 2, p.y + p.height // 2),  # Right ski
        ]

        pygame.draw.polygon(self.screen, BLUE, points)
        pygame.draw.polygon(self.screen, BLACK, points, 2)

        # Draw skis
        pygame.draw.line(
            self.screen,
            DARK_BLUE,
            (p.x - p.width // 2 - 5, p.y + p.height // 2 + 3),
            (p.x - p.width // 2 + 10, p.y + p.height // 2 + 5),
            3
        )
        pygame.draw.line(
            self.screen,
            DARK_BLUE,
            (p.x + p.width // 2 - 10, p.y + p.height // 2 + 5),
            (p.x + p.width // 2 + 5, p.y + p.height // 2 + 3),
            3
        )

    def draw_obstacle(self, obstacle):
        if obstacle.obstacle_type == 'tree':
            # Draw pine tree
            points = [
                (obstacle.x, obstacle.y - obstacle.height // 2),     # Top
                (obstacle.x - obstacle.width // 2, obstacle.y + obstacle.height // 2),  # Bottom left
                (obstacle.x + obstacle.width // 2, obstacle.y + obstacle.height // 2),  # Bottom right
            ]
            pygame.draw.polygon(self.screen, DARK_BLUE, points)
            pygame.draw.polygon(self.screen, BLACK, points, 2)
            # Trunk
            pygame.draw.rect(
                self.screen,
                (80, 50, 30),
                (obstacle.x - 4, obstacle.y + obstacle.height // 2 - 5, 8, 10)
            )
        else:  # snowmobile
            rect = obstacle.get_rect()
            pygame.draw.rect(self.screen, DARK_BLUE, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
            # Windshield
            pygame.draw.polygon(
                self.screen,
                LIGHT_BLUE,
                [
                    (rect.left + 10, rect.top),
                    (rect.right - 5, rect.top),
                    (rect.right - 10, rect.top + 12),
                ]
            )

    def draw_gate(self, gate):
        # Draw poles
        left_rect = gate.get_left_pole_rect()
        right_rect = gate.get_right_pole_rect()

        color = RED if not gate.passed else (100, 100, 100)

        pygame.draw.rect(self.screen, color, left_rect)
        pygame.draw.rect(self.screen, BLACK, left_rect, 2)
        pygame.draw.rect(self.screen, color, right_rect)
        pygame.draw.rect(self.screen, BLACK, right_rect, 2)

        # Draw flags on poles
        if gate.passed:
            flag_color = (150, 150, 150)
        else:
            flag_color = RED

        pygame.draw.polygon(
            self.screen,
            flag_color,
            [
                (left_rect.right, left_rect.top),
                (left_rect.right + 10, left_rect.top + 5),
                (left_rect.right, left_rect.top + 10),
            ]
        )
        pygame.draw.polygon(
            self.screen,
            flag_color,
            [
                (right_rect.left, right_rect.top),
                (right_rect.left - 10, right_rect.top + 5),
                (right_rect.left, right_rect.top + 10),
            ]
        )

    def draw_hud(self):
        # Score
        score_text = self.font.render(f"Score: {self.game.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))

        # Speed indicator
        speed_pct = int((self.game.scroll_speed - BASE_SCROLL_SPEED) /
                       (MAX_SCROLL_SPEED - BASE_SCROLL_SPEED) * 100)
        speed_text = self.small_font.render(f"Speed: {speed_pct}%", True, DARK_BLUE)
        self.screen.blit(speed_text, (10, 50))

    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(WHITE)
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        game_over_text = self.font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(game_over_text, text_rect)

        # Final score
        score_text = self.font.render(f"Final Score: {self.game.score}", True, BLACK)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(score_text, score_rect)

        # Restart instruction
        restart_text = self.small_font.render("Press R to restart or ESC to quit", True, DARK_BLUE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(restart_text, restart_rect)
