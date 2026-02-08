import pygame
import sys
import time
from typing import Tuple, Optional
from config import *
from board import Board, Ship
from ai import BattleshipAI


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Battleship: Strategic Fleet")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.title_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 22)
        self.reset_game()

    def reset_game(self):
        self.player_board = Board()
        self.enemy_board = Board()
        self.player_board.place_ships_randomly()
        self.enemy_board.place_ships_randomly()
        self.ai = BattleshipAI(self.player_board)
        self.game_over = False
        self.winner = None
        self.player_turn = True
        self.mouse_pos = (0, 0)
        self.last_shot_result = None
        self.last_shot_pos = None
        self.player_score = 0
        self.enemy_score = 0
        self.ships_sunk = {"player": 0, "enemy": 0}
        self.ai_timer = 0
        self.ai_pending_shot = None
        self.message = "Your turn! Click on the enemy board to fire."

    def handle_input(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE and self.game_over:
                    self.reset_game()

            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                if event.button == 1 and self.player_turn:
                    self.handle_player_click(event.pos)

        return True

    def handle_player_click(self, pos: Tuple[int, int]) -> None:
        cell = self.enemy_board.get_cell_from_pos(pos[0], pos[1], ENEMY_BOARD_OFFSET_X)
        if not cell:
            return

        row, col = cell
        if self.enemy_board.is_shot_at(row, col):
            return

        self.fire_at_enemy(row, col)

    def fire_at_enemy(self, row: int, col: int) -> None:
        hit, ship = self.enemy_board.fire_at(row, col)
        self.last_shot_pos = (row, col)
        self.last_shot_result = hit

        if hit:
            self.player_score += REWARD_HIT
            if ship and ship.is_sunk:
                self.player_score += REWARD_SINK
                self.ships_sunk["player"] += 1
                self.message = f"You sunk the enemy {ship.name}!"
            else:
                self.message = "Hit! Fire again!"
        else:
            self.player_score += REWARD_MISS
            self.message = "Miss. Enemy's turn..."
            self.player_turn = False
            self.ai_timer = pygame.time.get_ticks()

        self.check_game_over()

    def ai_turn(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.ai_timer < AI_THINK_DELAY:
            return

        if self.ai_pending_shot is None:
            row, col = self.ai.get_next_shot()
            self.ai_pending_shot = (row, col)
            return

        row, col = self.ai_pending_shot
        hit, ship = self.player_board.fire_at(row, col)
        self.ai.process_shot_result(row, col, hit, ship and ship.is_sunk)

        if hit:
            self.enemy_score += REWARD_HIT
            if ship and ship.is_sunk:
                self.enemy_score += REWARD_SINK
                self.ships_sunk["enemy"] += 1
                self.message = f"Enemy sunk your {ship.name}!"
            else:
                self.message = "Enemy hit your ship! Their turn..."
        else:
            self.enemy_score += REWARD_MISS
            self.message = "Enemy missed. Your turn!"
            self.player_turn = True

        self.ai_pending_shot = None
        self.check_game_over()

    def check_game_over(self):
        if self.enemy_board.all_ships_sunk():
            self.game_over = True
            self.winner = "player"
            self.player_score += REWARD_WIN
            self.enemy_score += REWARD_LOSS
            self.message = "Victory! You sunk the entire enemy fleet!"
        elif self.player_board.all_ships_sunk():
            self.game_over = True
            self.winner = "enemy"
            self.enemy_score += REWARD_WIN
            self.player_score += REWARD_LOSS
            self.message = "Defeat! Your fleet has been sunk."

    def draw(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_title()
        self.draw_board(self.enemy_board, ENEMY_BOARD_OFFSET_X, "Enemy Fleet", show_ships=False)
        self.draw_board(self.player_board, PLAYER_BOARD_OFFSET_X, "Your Fleet", show_ships=True)
        self.draw_ui()
        self.draw_score_panel()

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_title(self) -> None:
        title = "Vector Battleship"
        subtitle = "Strategic Fleet Command"
        title_surf = self.title_font.render(title, True, TITLE_COLOR)
        subtitle_surf = self.font.render(subtitle, True, SUBTEXT_COLOR)

        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        subtitle_rect = subtitle_surf.get_rect(center=(SCREEN_WIDTH // 2, 65))

        self.screen.blit(title_surf, title_rect)
        self.screen.blit(subtitle_surf, subtitle_rect)

    def draw_board(self, board: Board, offset_x: int, label: str, show_ships: bool) -> None:
        board_width = GRID_SIZE * CELL_SIZE
        board_height = GRID_SIZE * CELL_SIZE

        label_surf = self.font.render(label, True, TEXT_COLOR)
        label_rect = label_surf.get_rect(center=(offset_x + board_width // 2, BOARD_OFFSET_Y - 30))
        self.screen.blit(label_surf, label_rect)

        board_rect = pygame.Rect(
            offset_x - 5,
            BOARD_OFFSET_Y - 5,
            board_width + 10,
            board_height + 10
        )
        pygame.draw.rect(self.screen, BOARD_COLOR, board_rect, border_radius=5)

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                self.draw_cell(board, row, col, offset_x, show_ships)

        pygame.draw.rect(self.screen, GRID_COLOR, board_rect, 2, border_radius=5)

    def draw_cell(self, board: Board, row: int, col: int, offset_x: int, show_ships: bool) -> None:
        x, y, size = offset_x + col * CELL_SIZE, BOARD_OFFSET_Y + row * CELL_SIZE, CELL_SIZE
        cell_value = board.get_cell(row, col)

        is_hovered = False
        cell = board.get_cell_from_pos(self.mouse_pos[0], self.mouse_pos[1], offset_x)
        if cell == (row, col) and self.player_turn and not self.game_over:
            if show_ships or (board == self.enemy_board and not board.is_shot_at(row, col)):
                is_hovered = True

        bg_color = BOARD_COLOR
        if is_hovered:
            bg_color = HOVER_COLOR
        elif cell_value == SHIP and show_ships:
            bg_color = SHIP_COLOR

        pygame.draw.rect(self.screen, bg_color, (x + 1, y + 1, size - 2, size - 2))

        if cell_value == MISS:
            self.draw_mark(x, y, size, MISS_COLOR, "miss")
        elif cell_value == HIT:
            self.draw_mark(x, y, size, HIT_COLOR, "hit")
        elif cell_value == SUNK:
            self.draw_mark(x, y, size, SUNK_COLOR, "sunk")
        elif cell_value == SHIP and show_ships:
            pygame.draw.rect(self.screen, (80, 100, 120), (x + 5, y + 5, size - 10, size - 10))

        pygame.draw.rect(self.screen, GRID_COLOR, (x, y, size, size), 1)

    def draw_mark(self, x: int, y: int, size: int, color: Tuple[int, int, int], mark_type: str) -> None:
        center_x, center_y = x + size // 2, y + size // 2
        radius = size // 3

        if mark_type == "miss":
            pygame.draw.circle(self.screen, color, (center_x, center_y), 3)
        elif mark_type == "hit":
            pygame.draw.circle(self.screen, color, (center_x, center_y), radius, 3)
        elif mark_type == "sunk":
            pygame.draw.line(self.screen, color, (center_x - radius, center_y - radius), (center_x + radius, center_y + radius), 3)
            pygame.draw.line(self.screen, color, (center_x + radius, center_y - radius), (center_x - radius, center_y + radius), 3)

    def draw_ui(self) -> None:
        message_surf = self.font.render(self.message, True, TEXT_COLOR)
        message_rect = message_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        self.screen.blit(message_surf, message_rect)

        help_text = "[ESC] Quit  [SPACE] Restart"
        help_surf = self.small_font.render(help_text, True, SUBTEXT_COLOR)
        help_rect = help_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(help_surf, help_rect)

    def draw_score_panel(self) -> None:
        panel_x = 880
        panel_y = 150

        lines = [
            "Score",
            f"You: {self.player_score}",
            f"Enemy: {self.enemy_score}",
            "",
            "Ships Sunk",
            f"You: {self.ships_sunk['player']}/5",
            f"Enemy: {self.ships_sunk['enemy']}/5",
            "",
            "Remaining",
            f"You: {self.player_board.get_remaining_health()}",
            f"Enemy: {self.enemy_board.get_remaining_health()}"
        ]

        for i, line in enumerate(lines):
            color = HIGHLIGHT_COLOR if i == 0 else TEXT_COLOR
            if "You:" in line and i > 0:
                color = SHIP_COLOR if "Ships" not in line else (80, 120, 180)
            elif "Enemy:" in line:
                color = (180, 80, 80)

            surf = self.small_font.render(line, True, color)
            self.screen.blit(surf, (panel_x, panel_y + i * 25))

    def draw_game_over(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        if self.winner == "player":
            result_text = "VICTORY!"
            color = HIGHLIGHT_COLOR
        else:
            result_text = "DEFEAT"
            color = HIT_COLOR

        result_surf = self.title_font.render(result_text, True, color)
        result_rect = result_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(result_surf, result_rect)

        score_surf = self.font.render(f"Final Score: {self.player_score}", True, (220, 220, 220))
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(score_surf, score_rect)

        restart_surf = self.font.render("Press SPACE to play again", True, HIGHLIGHT_COLOR)
        restart_rect = restart_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(restart_surf, restart_rect)

    def run(self) -> None:
        running = True
        while running:
            running = self.handle_input()

            if not self.player_turn and not self.game_over:
                self.ai_turn()

            self.draw()
            self.clock.tick(FPS)
