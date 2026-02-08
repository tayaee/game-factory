"""Main game loop and rendering."""

import pygame
import random
import time
from enum import Enum
from config import *


class GameState(Enum):
    """Game states."""
    PLAYING = "playing"
    WIN = "win"
    LOSE = "lose"


class Card:
    """Represents a playing card."""

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = RANK_VALUES[rank]
        self.face_up = True

    def is_red(self):
        """Check if card is red suit."""
        return self.suit in ['HEARTS', 'DIAMONDS']

    def can_play_on(self, other_card):
        """Check if this card can be played on another card."""
        if other_card is None:
            return True
        return abs(self.value - other_card.value) == 1

    def to_int(self):
        """Encode card as integer for AI state representation."""
        suit_index = SUITS.index(self.suit)
        return self.value * 4 + suit_index

    @staticmethod
    def from_int(value):
        """Decode integer to card."""
        rank = RANKS[value // 4]
        suit = SUITS[value % 4]
        return Card(rank, suit)


class Game:
    """Main game class managing Golf Solitaire logic and rendering."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Golf Solitaire Classic")
        self.clock = pygame.time.Clock()
        self.running = True

        # Game state
        self.state = GameState.PLAYING
        self.tableau = [[] for _ in range(NUM_COLUMNS)]
        self.draw_pile = []
        self.waste_pile = []
        self.score = 0
        self.moves = 0
        self.start_time = 0
        self.elapsed_time = 0
        self.message = ""
        self.message_timer = 0

        # Card rectangles for click detection
        self.column_rects = []
        self.draw_pile_rect = None
        self.waste_pile_rect = None

        # Highlighted card
        self.highlighted_column = None

        # Fonts
        self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
        self.status_font = pygame.font.Font(None, STATUS_FONT_SIZE)
        self.card_font = pygame.font.SysFont('segoeui', CARD_FONT_SIZE)
        self.instruction_font = pygame.font.Font(None, INSTRUCTION_FONT_SIZE)

        # Initialize game
        self._create_card_rects()
        self._new_game()

    def _create_card_rects(self):
        """Create collision rectangles for columns."""
        self.column_rects = []
        for col in range(NUM_COLUMNS):
            x = COLUMN_START_X + col * CARD_SPACING_X
            y = COLUMN_START_Y
            rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
            self.column_rects.append(rect)

        self.draw_pile_rect = pygame.Rect(DRAW_PILE_X, DRAW_PILE_Y,
                                          CARD_WIDTH, CARD_HEIGHT)
        self.waste_pile_rect = pygame.Rect(WASTE_X, WASTE_Y,
                                           CARD_WIDTH, CARD_HEIGHT)

    def _create_deck(self):
        """Create a standard 52-card deck."""
        deck = []
        for suit in SUITS:
            for rank in RANKS:
                deck.append(Card(rank, suit))
        random.shuffle(deck)
        return deck

    def _new_game(self):
        """Start a new game."""
        deck = self._create_deck()

        # Deal tableau: 5 cards per column, face up
        self.tableau = [[] for _ in range(NUM_COLUMNS)]
        for _ in range(CARDS_PER_COLUMN):
            for col in range(NUM_COLUMNS):
                if deck:
                    card = deck.pop()
                    card.face_up = True
                    self.tableau[col].append(card)

        # Remaining cards go to draw pile
        self.draw_pile = deck
        for card in self.draw_pile:
            card.face_up = False

        # Draw one card to waste pile
        self.waste_pile = []
        if self.draw_pile:
            card = self.draw_pile.pop()
            card.face_up = True
            self.waste_pile.append(card)

        self.score = 0
        self.moves = 0
        self.start_time = time.time()
        self.elapsed_time = 0
        self.state = GameState.PLAYING
        self.message = ""
        self._check_game_state()

    def _check_game_state(self):
        """Check if game is won or lost."""
        # Check win condition
        if all(len(col) == 0 for col in self.tableau):
            self.state = GameState.WIN
            self.score += WIN_BONUS
            self.message = "ALL CLEARED!"
            return

        # Check if any moves available
        if not self._any_valid_moves():
            self.state = GameState.LOSE
            # Penalty for remaining cards
            remaining = sum(len(col) for col in self.tableau)
            self.score -= remaining * PENALTY_PER_REMAINING
            self.message = f"GAME OVER - {remaining} cards left"
            return

    def _any_valid_moves(self):
        """Check if any valid moves are available."""
        waste_card = self.waste_pile[-1] if self.waste_pile else None

        # Check tableau moves
        for col in self.tableau:
            if col:
                top_card = col[-1]
                if top_card.can_play_on(waste_card):
                    return True

        # Check if can draw
        if self.draw_pile:
            return True

        return False

    def get_valid_columns(self):
        """Get list of columns with valid moves."""
        valid = []
        waste_card = self.waste_pile[-1] if self.waste_pile else None

        for col_idx, col in enumerate(self.tableau):
            if col:
                top_card = col[-1]
                if top_card.can_play_on(waste_card):
                    valid.append(col_idx)

        return valid

    def handle_input(self):
        """Handle user input."""
        mouse_pos = pygame.mouse.get_pos()
        self.highlighted_column = None

        # Check column highlights
        valid_cols = self.get_valid_columns()
        for col_idx in valid_cols:
            if self.column_rects[col_idx].collidepoint(mouse_pos):
                self.highlighted_column = col_idx
                break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == GameState.PLAYING:
                    self._handle_mouse_click(event.pos)
                elif self.state in [GameState.WIN, GameState.LOSE]:
                    self._new_game()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.state in [GameState.WIN, GameState.LOSE]:
                        self._new_game()
                    else:
                        self._draw_card()

    def _handle_mouse_click(self, pos):
        """Handle mouse click."""
        # Check draw pile
        if self.draw_pile_rect.collidepoint(pos):
            self._draw_card()
            return

        # Check waste pile (can't click, just visual)
        if self.waste_pile_rect.collidepoint(pos):
            return

        # Check columns
        waste_card = self.waste_pile[-1] if self.waste_pile else None

        for col_idx, rect in enumerate(self.column_rects):
            if rect.collidepoint(pos):
                if self.tableau[col_idx]:
                    top_card = self.tableau[col_idx][-1]
                    if top_card.can_play_on(waste_card):
                        self._play_card(col_idx)
                        return

    def _play_card(self, col_idx):
        """Play a card from tableau to waste pile."""
        card = self.tableau[col_idx].pop()
        card.face_up = True
        self.waste_pile.append(card)
        self.score += SCORE_PER_CARD
        self.moves += 1
        self._check_game_state()

    def _draw_card(self):
        """Draw a card from draw pile to waste pile."""
        if not self.draw_pile:
            return

        card = self.draw_pile.pop()
        card.face_up = True
        self.waste_pile.append(card)
        self.moves += 1

        if not self._any_valid_moves():
            self._check_game_state()

    def _draw_card_face(self, surface, rect, card, highlight=False):
        """Draw a single card."""
        # Draw card background
        bg_color = (250, 250, 250) if card.face_up else CARD_BACK
        pygame.draw.rect(surface, bg_color, rect, border_radius=5)

        if card.face_up:
            # Draw border
            border_color = HIGHLIGHT_COLOR if highlight else CARD_BORDER
            pygame.draw.rect(surface, border_color, rect, width=2, border_radius=5)

            # Draw suit symbol and rank
            color = SUIT_RED if card.is_red() else SUIT_BLACK
            symbol = SUIT_SYMBOLS[card.suit]

            # Top corner
            rank_text = self.card_font.render(card.rank, True, color)
            suit_text = self.card_font.render(symbol, True, color)

            surface.blit(rank_text, (rect.x + 5, rect.y + 5))
            surface.blit(suit_text, (rect.x + 5, rect.y + 25))

            # Bottom corner (rotated)
            bottom_rank = pygame.transform.rotate(rank_text, 180)
            bottom_suit = pygame.transform.rotate(suit_text, 180)
            surface.blit(bottom_rank, (rect.right - 20, rect.bottom - 25))
            surface.blit(bottom_suit, (rect.right - 20, rect.bottom - 45))

            # Center suit (large)
            center_font = pygame.font.SysFont('segoeui', 48)
            center_symbol = center_font.render(symbol, True, color)
            center_rect = center_symbol.get_rect(center=rect.center)
            surface.blit(center_symbol, center_rect)
        else:
            # Draw card back pattern
            pygame.draw.rect(surface, (80, 100, 150),
                           (rect.x + 5, rect.y + 5,
                            rect.width - 10, rect.height - 10),
                           border_radius=3)
            # Draw crosshatch pattern
            for i in range(0, rect.width, 10):
                pygame.draw.line(surface, (70, 90, 140),
                               (rect.x + i, rect.y),
                               (rect.x + i, rect.bottom))
            for i in range(0, rect.height, 10):
                pygame.draw.line(surface, (70, 90, 140),
                               (rect.x, rect.y + i),
                               (rect.right, rect.y + i))

    def render(self):
        """Render the game."""
        self.screen.fill(BACKGROUND)

        # Draw title
        title_text = self.status_font.render("GOLF SOLITAIRE", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 25))
        self.screen.blit(title_text, title_rect)

        # Draw tableau columns
        valid_cols = self.get_valid_columns()
        for col_idx, col in enumerate(self.tableau):
            rect = self.column_rects[col_idx]

            # Draw empty slot placeholder
            pygame.draw.rect(self.screen, (40, 40, 45), rect, border_radius=5)
            pygame.draw.rect(self.screen, (60, 60, 70), rect, width=1, border_radius=5)

            if col:
                top_card = col[-1]
                is_valid = col_idx in valid_cols
                is_highlighted = (col_idx == self.highlighted_column)

                if is_highlighted and is_valid:
                    # Draw highlight glow
                    glow_rect = rect.inflate(10, 10)
                    pygame.draw.rect(self.screen, (100, 150, 100), glow_rect, border_radius=8)

                self._draw_card_face(self.screen, rect, top_card,
                                    highlight=is_highlighted and is_valid)

                # Show count indicator if multiple cards
                if len(col) > 1:
                    count_text = self.instruction_font.render(f"({len(col)})", True, (150, 150, 150))
                    count_rect = count_text.get_rect(midbottom=(rect.centerx, rect.bottom - 5))
                    self.screen.blit(count_text, count_rect)

        # Draw draw pile
        if self.draw_pile:
            # Draw stacked cards effect
            for i in range(min(3, len(self.draw_pile))):
                offset = i * 2
                stack_rect = self.draw_pile_rect.move(-offset, -offset)
                pygame.draw.rect(self.screen, CARD_BACK, stack_rect, border_radius=5)
                pygame.draw.rect(self.screen, (100, 120, 160), stack_rect, width=2, border_radius=5)

            # Draw top card back
            self._draw_card_face(self.screen, self.draw_pile_rect, self.draw_pile[-1])
        else:
            # Empty draw pile
            pygame.draw.rect(self.screen, (35, 35, 40), self.draw_pile_rect, border_radius=5)
            pygame.draw.rect(self.screen, (50, 50, 60), self.draw_pile_rect, width=1, border_radius=5)

        # Draw waste pile
        if self.waste_pile:
            self._draw_card_face(self.screen, self.waste_pile_rect, self.waste_pile[-1])
        else:
            pygame.draw.rect(self.screen, (35, 35, 40), self.waste_pile_rect, border_radius=5)
            pygame.draw.rect(self.screen, (50, 50, 60), self.waste_pile_rect, width=1, border_radius=5)

        # Draw labels
        draw_label = self.instruction_font.render("DRAW", True, (150, 150, 150))
        draw_label_rect = draw_label.get_rect(center=(self.draw_pile_rect.centerx, self.draw_pile_rect.bottom + 20))
        self.screen.blit(draw_label, draw_label_rect)

        waste_label = self.instruction_font.render("BASE", True, (150, 150, 150))
        waste_label_rect = waste_label.get_rect(center=(self.waste_pile_rect.centerx, self.waste_pile_rect.bottom + 20))
        self.screen.blit(waste_label, waste_label_rect)

        # Draw stats
        score_text = self.score_font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (50, SCREEN_HEIGHT - 80))

        moves_text = self.score_font.render(f"Moves: {self.moves}", True, TEXT_COLOR)
        self.screen.blit(moves_text, (50, SCREEN_HEIGHT - 50))

        remaining = sum(len(col) for col in self.tableau)
        remain_text = self.score_font.render(f"Cards: {remaining}", True, TEXT_COLOR)
        self.screen.blit(remain_text, (250, SCREEN_HEIGHT - 80))

        deck_text = self.score_font.render(f"Deck: {len(self.draw_pile)}", True, TEXT_COLOR)
        self.screen.blit(deck_text, (250, SCREEN_HEIGHT - 50))

        # Draw status message
        if self.state == GameState.WIN:
            msg_text = self.status_font.render(self.message, True, VALID_MOVE_COLOR)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 70))
            self.screen.blit(msg_text, msg_rect)

            sub_msg = "Press SPACE or click to play again"
            sub_text = self.instruction_font.render(sub_msg, True, (150, 150, 150))
            sub_rect = sub_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
            self.screen.blit(sub_text, sub_rect)

        elif self.state == GameState.LOSE:
            msg_text = self.status_font.render(self.message, True, INVALID_MOVE_COLOR)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 70))
            self.screen.blit(msg_text, msg_rect)

            sub_msg = "Press SPACE or click to try again"
            sub_text = self.instruction_font.render(sub_msg, True, (150, 150, 150))
            sub_rect = sub_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
            self.screen.blit(sub_text, sub_rect)

        else:
            # Draw instructions
            valid_count = len(valid_cols)
            if valid_count > 0:
                hint = f"{valid_count} valid move{'s' if valid_count > 1 else ''} available"
                hint_text = self.instruction_font.render(hint, True, VALID_MOVE_COLOR)
            else:
                hint = "Click DRAW pile for new base card"
                hint_text = self.instruction_font.render(hint, True, (180, 180, 100))

            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
            self.screen.blit(hint_text, hint_rect)

            controls = "Click card to play | Click DRAW for new card | ESC: Quit"
            controls_text = self.instruction_font.render(controls, True, (100, 100, 100))
            controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 35))
            self.screen.blit(controls_text, controls_rect)

        pygame.display.flip()

    def get_observation(self):
        """Return current game state for AI."""
        tableau_state = []
        for col in self.tableau:
            col_state = [card.to_int() for card in col]
            tableau_state.append(col_state)

        waste_card = self.waste_pile[-1].to_int() if self.waste_pile else -1

        return {
            "tableau": tableau_state,
            "waste_card": waste_card,
            "draw_pile_count": len(self.draw_pile),
            "score": self.score,
            "moves": self.moves,
            "state": self.state.value
        }

    def step_ai(self, action):
        """
        Execute an AI action and return observation, reward, done.

        Args:
            action: 0-6 for column selection, 7 for draw from pile

        Returns:
            (observation, reward, done)
        """
        if self.state in [GameState.WIN, GameState.LOSE]:
            self._new_game()
            return self.get_observation(), 0, False

        reward = 0
        done = False

        if action == 7:  # Draw from pile
            if self.draw_pile:
                self._draw_card()
                reward = REWARD_DRAW
            else:
                reward = REWARD_INVALID_MOVE
        else:  # Play from column
            if 0 <= action < NUM_COLUMNS and self.tableau[action]:
                waste_card = self.waste_pile[-1] if self.waste_pile else None
                top_card = self.tableau[action][-1]

                if top_card.can_play_on(waste_card):
                    prev_score = self.score
                    self._play_card(action)
                    reward = REWARD_CARD_CLEARED
                else:
                    reward = REWARD_INVALID_MOVE
            else:
                reward = REWARD_INVALID_MOVE

        # Check terminal states
        if self.state == GameState.WIN:
            reward = REWARD_WIN
            done = True
        elif self.state == GameState.LOSE:
            reward = REWARD_LOSE
            done = True

        return self.get_observation(), reward, done

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_input()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
