"""Main game loop and rendering."""

import pygame
import array
from config import *
from board import GameBoard


class SoundGenerator:
    """Generates simple tones using pygame.sndarray."""

    def __init__(self):
        self.sample_rate = 44100
        pygame.mixer.pre_init(self.sample_rate, -16, 1, 512)
        pygame.mixer.init()

    def generate_tone(self, frequency, duration=0.2):
        """Generate a square wave tone."""
        n_samples = int(self.sample_rate * duration)
        period = self.sample_rate // frequency

        # Generate square wave
        samples = array.array('h', [0] * n_samples)
        amplitude = 16000  # Max amplitude for 16-bit signed

        for i in range(n_samples):
            # Apply simple envelope to avoid clicking
            envelope = 1.0
            if i < 500:
                envelope = i / 500
            elif i > n_samples - 500:
                envelope = (n_samples - i) / 500

            value = amplitude * envelope if (i // (period // 2)) % 2 else -amplitude * envelope
            samples[i] = int(value)

        return pygame.mixer.Sound(buffer=samples)


class Game:
    """Main game class managing rendering and game loop."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Memory Pattern Match")
        self.clock = pygame.time.Clock()
        self.running = True

        self.sound_gen = SoundGenerator()
        self.sounds = [
            self.sound_gen.generate_tone(freq)
            for freq in TONE_FREQUENCIES
        ]
        self.game_over_sound = self.sound_gen.generate_tone(100, 0.5)

        self.board = GameBoard(BOARD_X, BOARD_Y, TILE_SIZE, TILE_GAP)

        # Fonts
        self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
        self.message_font = pygame.font.Font(None, MESSAGE_FONT_SIZE)

    def handle_input(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    pos = pygame.mouse.get_pos()

                    if self.board.game_state == "ready":
                        self.board.start_new_round()
                    elif self.board.game_state == "game_over":
                        self.board.reset_game()
                    elif self.board.game_state == "playing":
                        self.board.handle_tile_click(pos)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.board.game_state == "ready":
                        self.board.start_new_round()
                    elif self.board.game_state == "game_over":
                        self.board.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        """Update game state."""
        self.board.update()

    def render(self):
        """Render the game."""
        self.screen.fill(BLACK)

        # Draw title
        title_text = self.score_font.render("Memory Pattern Match", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title_text, title_rect)

        # Draw tiles
        for tile in self.board.tiles:
            color = tile.flash_color if tile.is_lit else tile.base_color
            pygame.draw.rect(
                self.screen,
                color,
                tile.rect,
                border_radius=10
            )

            # Draw glow effect when lit
            if tile.is_lit:
                glow_rect = [
                    tile.rect[0] - 5,
                    tile.rect[1] - 5,
                    tile.rect[2] + 10,
                    tile.rect[3] + 10
                ]
                pygame.draw.rect(
                    self.screen,
                    [min(255, c + 50) for c in tile.flash_color],
                    glow_rect,
                    2,
                    border_radius=15
                )

        # Draw score
        score_text = self.score_font.render(f"Score: {self.board.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        self.screen.blit(score_text, score_rect)

        # Draw messages
        if self.board.game_state == "ready":
            msg = "Press SPACE or click to start"
            msg_text = self.message_font.render(msg, True, WHITE)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 130))
            self.screen.blit(msg_text, msg_rect)
        elif self.board.game_state == "showing_sequence":
            msg = "Watch the pattern..."
            msg_text = self.score_font.render(msg, True, GRAY)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 130))
            self.screen.blit(msg_text, msg_rect)
        elif self.board.game_state == "playing":
            msg = "Your turn!"
            msg_text = self.score_font.render(msg, True, WHITE)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 130))
            self.screen.blit(msg_text, msg_rect)
        elif self.board.game_state == "game_over":
            msg = "Game Over! Press SPACE to restart"
            msg_text = self.message_font.render(msg, True, (255, 100, 100))
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 130))
            self.screen.blit(msg_text, msg_rect)

        pygame.display.flip()

    def play_sound(self, index):
        """Play a sound by tile index."""
        if 0 <= index < len(self.sounds):
            self.sounds[index].play()

    def run(self):
        """Main game loop."""
        previous_lit_tiles = set()

        while self.running:
            self.handle_input()
            self.update()

            # Check for newly lit tiles to play sounds
            current_lit_tiles = {
                i for i, tile in enumerate(self.board.tiles)
                if tile.is_lit
            }

            newly_lit = current_lit_tiles - previous_lit_tiles
            for tile_idx in newly_lit:
                self.play_sound(tile_idx)

            previous_lit_tiles = current_lit_tiles
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
