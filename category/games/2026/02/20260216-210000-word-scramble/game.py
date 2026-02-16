"""
Word Scramble - Game Logic
Unscramble letters to form words.
"""

import random
import pygame
import sys
from config import *


class LetterTile:
    def __init__(self, char, x, y, size=60):
        self.char = char
        self.x = x
        self.y = y
        self.size = size
        self.target_x = x
        self.target_y = y
        self.selected = False
        self.used = False
        self.rect = pygame.Rect(x, y, size, size)

    def update(self):
        self.x += (self.target_x - self.x) * 0.2
        self.y += (self.target_y - self.y) * 0.2
        self.rect.topleft = (int(self.x), int(self.y))

    def draw(self, surface, font):
        color = COLOR_LETTER_SELECTED if self.selected else COLOR_LETTER
        if self.used:
            color = COLOR_HINT
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_ACCENT, self.rect, 3, border_radius=8)

        text = font.render(self.char, True, COLOR_TEXT)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)


class WordScrambleGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Word Scramble")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)

        self.score = 0
        self.lives = 3
        self.level = 1
        self.hints_remaining = MAX_HINTS
        self.words_solved = 0

        self.new_word()
        self.letter_tiles = []
        self.selected_letters = []
        self.user_input = ""

        self.message = ""
        self.message_timer = 0
        self.message_color = COLOR_TEXT

        self.game_over = False
        self.victory = False

    def new_word(self):
        self.current_word_data = random.choice(WORDS)
        if isinstance(self.current_word_data[1], tuple):
            self.scrambled = self.current_word_data[0]
            self.solutions = self.current_word_data[1]
        else:
            self.scrambled = self.current_word_data[0]
            self.solutions = self.current_word_data[1]
        self.letters = list(self.scrambled)

    def create_letter_tiles(self):
        self.letter_tiles = []
        tile_size = 60
        spacing = 10
        total_width = len(self.letters) * (tile_size + spacing) - spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = SCREEN_HEIGHT // 2 - 50

        for i, char in enumerate(self.letters):
            x = start_x + i * (tile_size + spacing)
            self.letter_tiles.append(LetterTile(char, x, start_y, tile_size))

    def check_answer(self, answer):
        if isinstance(self.solutions, tuple):
            return answer in self.solutions
        return answer == self.solutions

    def submit_answer(self):
        if not self.user_input:
            return

        if self.check_answer(self.user_input):
            self.score += len(self.user_input) * POINTS_PER_LETTER + BONUS_POINTS
            self.words_solved += 1
            self.show_message("Correct!", COLOR_CORRECT)

            if self.words_solved >= 10 * self.level:
                self.level += 1
                self.hints_remaining = MAX_HINTS
                self.show_message(f"Level {self.level}!", COLOR_CORRECT)

            self.new_word()
            self.create_letter_tiles()
            self.selected_letters = []
            self.user_input = ""
        else:
            self.lives -= 1
            self.score -= TIME_PENALTY_PER_WRONG
            self.show_message("Try again!", COLOR_WRONG)

            if self.lives <= 0:
                self.game_over = True

    def use_hint(self):
        if self.hints_remaining <= 0 or self.game_over:
            return

        self.hints_remaining -= 1
        self.score -= TIME_PENALTY_PER_HINT

        if isinstance(self.solutions, tuple):
            solution = self.solutions[0]
        else:
            solution = self.solutions

        for i, tile in enumerate(self.letter_tiles):
            if tile.used:
                continue
            if tile.char == solution[len(self.selected_letters)]:
                tile.used = True
                self.selected_letters.append(tile)
                self.user_input += tile.char
                self.arrange_letters()
                break

    def show_message(self, message, color):
        self.message = message
        self.message_color = color
        self.message_timer = 60

    def arrange_letters(self):
        tile_size = 60
        spacing = 10

        # Arrange unused tiles in bottom row
        unused_tiles = [t for t in self.letter_tiles if not t.used]
        total_width = len(unused_tiles) * (tile_size + spacing) - spacing
        start_x = (SCREEN_WIDTH - total_width) // 2 if unused_tiles else SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2 - 50

        for i, tile in enumerate(unused_tiles):
            tile.target_x = start_x + i * (tile_size + spacing)
            tile.target_y = start_y

        # Arrange used tiles in top row
        used_tiles = [t for t in self.letter_tiles if t.used]
        total_width = len(used_tiles) * (tile_size + spacing) - spacing
        start_x = (SCREEN_WIDTH - total_width) // 2 if used_tiles else SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2 + 100

        for i, tile in enumerate(used_tiles):
            tile.target_x = start_x + i * (tile_size + spacing)
            tile.target_y = start_y

    def handle_letter_click(self, pos):
        if self.game_over:
            return

        for tile in self.letter_tiles:
            if tile.rect.collidepoint(pos) and not tile.used:
                tile.used = True
                self.selected_letters.append(tile)
                self.user_input += tile.char
                self.arrange_letters()
                return

    def handle_backspace(self):
        if not self.selected_letters or self.game_over:
            return

        tile = self.selected_letters.pop()
        tile.used = False
        self.user_input = self.user_input[:-1]
        self.arrange_letters()

    def reset_current_word(self):
        for tile in self.letter_tiles:
            tile.used = False
        self.selected_letters = []
        self.user_input = ""
        self.create_letter_tiles()

    def restart(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.hints_remaining = MAX_HINTS
        self.words_solved = 0
        self.game_over = False
        self.victory = False
        self.new_word()
        self.create_letter_tiles()
        self.selected_letters = []
        self.user_input = ""

    def handle_input(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.handle_letter_click(event.pos)

        if event.type == pygame.KEYDOWN:
            if self.game_over:
                if event.key == pygame.K_r:
                    self.restart()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                return

            if event.key == pygame.K_RETURN:
                self.submit_answer()
            elif event.key == pygame.K_BACKSPACE:
                self.handle_backspace()
            elif event.key == pygame.K_h:
                self.use_hint()
            elif event.key == pygame.K_SPACE:
                self.reset_current_word()
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1

        for tile in self.letter_tiles:
            tile.update()

    def draw(self):
        self.screen.fill(COLOR_BG)

        # Draw title
        title = self.font_large.render("WORD SCRAMBLE", True, COLOR_ACCENT)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # Draw score and info
        score_text = self.font_medium.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (20, 20))

        lives_text = self.font_medium.render(f"Lives: {self.lives}", True, COLOR_TEXT)
        self.screen.blit(lives_text, (20, 60))

        level_text = self.font_medium.render(f"Level: {self.level}", True, COLOR_TEXT)
        self.screen.blit(level_text, (SCREEN_WIDTH - 150, 20))

        hints_text = self.font_medium.render(f"Hints: {self.hints_remaining}", True, COLOR_TEXT)
        self.screen.blit(hints_text, (SCREEN_WIDTH - 150, 60))

        # Draw instructions
        if not self.game_over:
            inst1 = self.font_small.render("Click letters to form a word", True, COLOR_HINT)
            inst1_rect = inst1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            self.screen.blit(inst1, inst1_rect)

            inst2 = self.font_small.render("ENTER: Submit | BACKSPACE: Undo | H: Hint | SPACE: Reset", True, COLOR_HINT)
            inst2_rect = inst2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 70))
            self.screen.blit(inst2, inst2_rect)

        # Draw letter tiles
        for tile in self.letter_tiles:
            tile.draw(self.screen, self.font_large)

        # Draw current input
        input_bg = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 130, 400, 50)
        pygame.draw.rect(self.screen, COLOR_ACCENT, input_bg, border_radius=8)
        input_text = self.font_medium.render(self.user_input, True, COLOR_TEXT)
        input_text_rect = input_text.get_rect(center=input_bg.center)
        self.screen.blit(input_text, input_text_rect)

        # Draw message
        if self.message_timer > 0:
            msg_text = self.font_medium.render(self.message, True, self.message_color)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 130))
            self.screen.blit(msg_text, msg_rect)

        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font_large.render("GAME OVER", True, COLOR_WRONG)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(game_over_text, game_over_rect)

            final_score_text = self.font_medium.render(f"Final Score: {self.score}", True, COLOR_TEXT)
            final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(final_score_text, final_score_rect)

            restart_text = self.font_small.render("Press R to restart or ESC to quit", True, COLOR_TEXT)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def run(self):
        self.create_letter_tiles()

        while True:
            for event in pygame.event.get():
                self.handle_input(event)

            self.update()
            self.draw()
            self.clock.tick(60)


# Alias for backwards compatibility
Game = WordScrambleGame
