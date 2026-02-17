"""
Vector Mappy Rhythm Run
A rhythm-based side-scrolling platformer featuring Mappy.
Jump over obstacles synchronized to music beats.
"""

import pygame
import sys
import random
import time
import math
from enum import Enum

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60
BPM = 120
BEAT_INTERVAL = 60 / BPM  # Seconds per beat
BEAT_FRAMES = int(BEAT_INTERVAL * FPS)
PERFECT_WINDOW_MS = 50

# Colors
COLOR_BG = (25, 25, 35)
COLOR_GRID = (40, 40, 50)
COLOR_GRID_NEON = (60, 60, 80)
COLOR_FLOOR = (50, 50, 60)
COLOR_FLOOR_LINE = (0, 255, 255)
COLOR_PLAYER = (50, 180, 255)
COLOR_PLAYER_EARS = (30, 140, 200)
COLOR_PLAYER_ACCENT = (0, 255, 255)
COLOR_CAT = (255, 100, 80)
COLOR_PIT = (15, 15, 20)
COLOR_TEXT = (255, 255, 255)
COLOR_PERFECT = (0, 255, 100)
COLOR_GOOD = (255, 200, 0)
COLOR_MISS = (255, 50, 50)

# Game physics
SCROLL_SPEED = 4
JUMP_FORCE = -13
GRAVITY = 0.5
PLAYER_SIZE = 30
OBSTACLE_WIDTH = 35
OBSTACLE_HEIGHT = 40
PIT_WIDTH = 80

# Rhythm system
BEAT_PULSE_DURATION = 0.15  # Seconds

class GameState(Enum):
    PLAYING = 0
    GAME_OVER = 1
    START = 2


class ObstacleType(Enum):
    CAT = 0
    PIT = 1


class Obstacle:
    def __init__(self, x, obstacle_type):
        self.x = x
        self.y = SCREEN_HEIGHT - OBSTACLE_HEIGHT - 10
        self.type = obstacle_type
        self.width = OBSTACLE_WIDTH if obstacle_type == ObstacleType.CAT else PIT_WIDTH
        self.height = OBSTACLE_HEIGHT if obstacle_type == ObstacleType.CAT else 20
        self.passed = False
        self.jump_timestamp = 0
        self.jump_scored = False
        # Animation offset
        self.bob_offset = random.random() * 6.28

    def update(self):
        self.x -= SCROLL_SPEED
        self.bob_offset += 0.1

    def draw(self, surface):
        if self.type == ObstacleType.CAT:
            bob_y = int(self.y + math.sin(self.bob_offset) * 2)
            # Body
            pygame.draw.ellipse(surface, COLOR_CAT, (self.x, bob_y + 15, self.width, self.height - 15))
            # Head
            pygame.draw.circle(surface, COLOR_CAT, (int(self.x + self.width // 2), int(bob_y + 10)), 10)
            # Ears
            pygame.draw.polygon(surface, (200, 60, 40), [
                (self.x + 8, bob_y + 5),
                (self.x + 4, bob_y - 8),
                (self.x + 12, bob_y + 3)
            ])
            pygame.draw.polygon(surface, (200, 60, 40), [
                (self.x + self.width - 8, bob_y + 5),
                (self.x + self.width - 4, bob_y - 8),
                (self.x + self.width - 12, bob_y + 3)
            ])
            # Eyes (menacing)
            pygame.draw.circle(surface, (255, 255, 200), (int(self.x + 10), int(bob_y + 8)), 3)
            pygame.draw.circle(surface, (255, 255, 200), (int(self.x + self.width - 10), int(bob_y + 8)), 3)
            pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 10), int(bob_y + 8)), 1)
            pygame.draw.circle(surface, (0, 0, 0), (int(self.x + self.width - 10), int(bob_y + 8)), 1)
            # Name tag "Nyamco"
            font = pygame.font.Font(None, 16)
            nyamco_text = font.render("Nyamco", True, (200, 200, 200))
            surface.blit(nyamco_text, (self.x - 5, bob_y - 20))
        else:
            # Pit
            pit_rect = pygame.Rect(self.x, self.y + 15, self.width, self.height)
            pygame.draw.rect(surface, COLOR_PIT, pit_rect)
            # Danger lines
            for i in range(0, self.width, 10):
                pygame.draw.line(surface, (80, 20, 20),
                               (self.x + i, self.y + 18),
                               (self.x + i + 5, self.y + 32), 2)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Player:
    def __init__(self):
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.x = 100
        self.y = SCREEN_HEIGHT - self.height - 10
        self.vel_y = 0
        self.is_jumping = False
        self.on_ground = True
        self.alive = True
        self.score = 0
        self.combo = 1
        self.max_combo = 1
        self.perfect_jumps = 0
        self.total_jumps = 0
        self.jump_feedback = None
        self.jump_feedback_timer = 0
        self.run_frame = 0
        self.ear_flop_offset = 0

    def update(self, floor_y):
        if not self.alive:
            return

        # Gravity
        if not self.on_ground:
            self.vel_y += GRAVITY
            self.y += self.vel_y

            # Check landing
            if self.y >= floor_y - self.height:
                self.y = floor_y - self.height
                self.vel_y = 0
                self.on_ground = True
                self.is_jumping = False

        # Animation
        self.run_frame += 1
        if self.is_jumping:
            self.ear_flop_offset = math.sin(self.run_frame * 0.2) * 2
        elif self.on_ground:
            self.ear_flop_offset = math.sin(self.run_frame * 0.3) * 3

        # Update feedback timer
        if self.jump_feedback_timer > 0:
            self.jump_feedback_timer -= 1
            if self.jump_feedback_timer == 0:
                self.jump_feedback = None

    def jump(self, beat_offset_ms):
        if self.on_ground and self.alive:
            self.vel_y = JUMP_FORCE
            self.on_ground = False
            self.is_jumping = True
            self.total_jumps += 1

            # Calculate timing score
            abs_offset = abs(beat_offset_ms)
            if abs_offset <= PERFECT_WINDOW_MS:
                self.jump_feedback = "PERFECT"
                self.jump_feedback_timer = 30
                self.perfect_jumps += 1
                self.combo += 1
                if self.combo > self.max_combo:
                    self.max_combo = self.combo
                return "perfect"
            elif abs_offset <= PERFECT_WINDOW_MS * 2:
                self.jump_feedback = "GOOD"
                self.jump_feedback_timer = 20
                return "good"
            else:
                self.jump_feedback = "EARLY/LATE"
                self.jump_feedback_timer = 15
                self.combo = 1
                return "miss"

        return None

    def get_rect(self):
        # Hitbox is slightly smaller than visual size
        return pygame.Rect(self.x + 4, self.y + 4, self.width - 8, self.height - 8)

    def draw(self, surface):
        if not self.alive:
            return

        # Run bob animation
        run_bob = int(math.sin(self.run_frame * 0.5) * 2) if self.on_ground else 0
        draw_y = self.y + run_bob

        # Tail
        tail_start = (self.x + self.width // 2, draw_y + 24)
        tail_end = (self.x + self.width // 2 + 12, draw_y + 28)
        pygame.draw.line(surface, COLOR_PLAYER_EARS, tail_start, tail_end, 3)

        # Body
        body_rect = pygame.Rect(self.x, draw_y + 12, self.width, self.height - 12)
        pygame.draw.ellipse(surface, COLOR_PLAYER, body_rect)

        # Body neon outline
        pygame.draw.ellipse(surface, COLOR_PLAYER_ACCENT, body_rect, 2)

        # Head
        pygame.draw.circle(surface, COLOR_PLAYER, (int(self.x + self.width // 2), int(draw_y + 12)), 10)
        pygame.draw.circle(surface, COLOR_PLAYER_ACCENT, (int(self.x + self.width // 2), int(draw_y + 12)), 10, 1)

        # Ears (large mouse ears)
        ear_y = draw_y + 3 + self.ear_flop_offset
        pygame.draw.circle(surface, COLOR_PLAYER_EARS, (int(self.x + 5), int(ear_y)), 6)
        pygame.draw.circle(surface, COLOR_PLAYER_EARS, (int(self.x + self.width - 5), int(ear_y)), 6)
        pygame.draw.circle(surface, (200, 230, 255), (int(self.x + 5), int(ear_y)), 3)
        pygame.draw.circle(surface, (200, 230, 255), (int(self.x + self.width - 5), int(ear_y)), 3)

        # Eyes
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 10), int(draw_y + 10)), 3)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + self.width - 10), int(draw_y + 10)), 3)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 10), int(draw_y + 10)), 1)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + self.width - 10), int(draw_y + 10)), 1)

        # Nose
        pygame.draw.circle(surface, (255, 150, 180), (int(self.x + self.width // 2), int(draw_y + 15)), 2)

        # Jump feedback text
        if self.jump_feedback:
            font = pygame.font.Font(None, 28)
            color = COLOR_PERFECT if self.jump_feedback == "PERFECT" else (COLOR_GOOD if self.jump_feedback == "GOOD" else COLOR_MISS)
            text = font.render(self.jump_feedback, True, color)
            text_rect = text.get_rect(center=(self.x + self.width // 2, draw_y - 20))
            surface.blit(text, text_rect)


class RhythmSystem:
    def __init__(self):
        self.bpm = BPM
        self.beat_interval = BEAT_INTERVAL
        self.beat_counter = 0
        self.beat_pulse = 0
        self.last_beat_time = 0
        self.beat_phase = 0  # 0 to 1 within a beat

    def update(self, dt):
        self.last_beat_time = time.time()

        # Calculate beat phase (0 to 1)
        self.beat_phase = (time.time() * self.bpm / 60) % 1

        # Update beat counter
        current_beat = int(time.time() * self.bpm / 60)
        if current_beat > self.beat_counter:
            self.beat_counter = current_beat
            self.beat_pulse = 1

        # Decay beat pulse
        if self.beat_pulse > 0:
            self.beat_pulse -= dt / BEAT_PULSE_DURATION
            if self.beat_pulse < 0:
                self.beat_pulse = 0

    def get_beat_offset_ms(self):
        # Get offset from nearest beat in milliseconds
        beat_time = self.beat_phase * self.beat_interval
        offset_to_next = beat_time
        offset_to_prev = self.beat_interval - beat_time
        return min(offset_to_next, offset_to_prev) * 1000

    def is_on_beat(self, tolerance_ms=PERFECT_WINDOW_MS):
        return self.get_beat_offset_ms() <= tolerance_ms


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Mappy Rhythm Run")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)

        # Create synthetic beat sounds
        self.beat_sound = self.create_beat_sound()
        self.jump_sound = self.create_jump_sound()
        self.success_sound = self.create_success_sound()

        self.reset_game()

    def create_beat_sound(self):
        # Create a simple kick drum sound
        duration = 0.1
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        sound_array = [0] * num_samples
        for i in range(num_samples):
            t = i / sample_rate
            # Exponentially decaying sine wave
            sound_array[i] = int(32767 * 0.8 * math.sin(2 * math.pi * 60 * t) * math.exp(-t * 20))

        # Convert to mono bytes (duplicate for stereo effect)
        byte_array = []
        for val in sound_array:
            byte_array.append(val & 0xFF)
            byte_array.append((val >> 8) & 0xFF)

        return pygame.mixer.Sound(buffer=bytes(byte_array))

    def create_jump_sound(self):
        # Create a jump sound (rising pitch)
        duration = 0.15
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        sound_array = [0] * num_samples
        for i in range(num_samples):
            t = i / sample_rate
            # Rising pitch sine wave
            freq = 200 + t * 400
            sound_array[i] = int(16383 * math.sin(2 * math.pi * freq * t) * (1 - t / duration))

        # Convert to stereo bytes
        byte_array = []
        for val in sound_array:
            val16 = val + 32768
            byte_array.append(val16 & 0xFF)
            byte_array.append((val16 >> 8) & 0xFF)

        return pygame.mixer.Sound(buffer=bytes(byte_array))

    def create_success_sound(self):
        # Create a success sound (two-tone)
        duration = 0.2
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        sound_array = [0] * num_samples
        for i in range(num_samples):
            t = i / sample_rate
            # Two-tone melody
            freq = 523 if i < num_samples // 2 else 659
            sound_array[i] = int(16383 * math.sin(2 * math.pi * freq * t) * (1 - t / duration))

        # Convert to stereo bytes
        byte_array = []
        for val in sound_array:
            val16 = val + 32768
            byte_array.append(val16 & 0xFF)
            byte_array.append((val16 >> 8) & 0xFF)

        return pygame.mixer.Sound(buffer=bytes(byte_array))

    def reset_game(self):
        self.player = Player()
        self.obstacles = []
        self.rhythm = RhythmSystem()
        self.state = GameState.START
        self.floor_y = SCREEN_HEIGHT - 10
        self.spawn_timer = 0
        self.last_beat_played = -1

    def spawn_obstacle(self):
        # Spawn obstacles synchronized with beats
        beat = self.rhythm.beat_counter
        if beat > self.last_beat_played + random.randint(2, 4):
            self.last_beat_played = beat

            # Decide between cat or pit
            if random.random() < 0.3:
                obs_type = ObstacleType.PIT
            else:
                obs_type = ObstacleType.CAT

            obstacle = Obstacle(SCREEN_WIDTH + 50, obs_type)
            self.obstacles.append(obstacle)

    def update(self):
        dt = self.clock.get_time() / 1000.0

        if self.state == GameState.START:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.state = GameState.PLAYING
            return

        if self.state == GameState.GAME_OVER:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                self.reset_game()
            return

        # Update rhythm
        self.rhythm.update(dt)

        # Play beat sound on beat
        if self.rhythm.beat_pulse > 0.9:
            self.beat_sound.play()

        # Spawn obstacles
        self.spawn_timer += 1
        if self.spawn_timer >= 30:
            self.spawn_timer = 0
            self.spawn_obstacle()

        # Update obstacles
        for obstacle in self.obstacles:
            obstacle.update()

            # Check if player passed obstacle
            if not obstacle.passed and obstacle.x < self.player.x - obstacle.width:
                obstacle.passed = True
                self.player.score += 10 * self.player.combo

        # Remove off-screen obstacles
        self.obstacles = [o for o in self.obstacles if o.x > -100]

        # Update player
        self.player.update(self.floor_y)

        # Check collisions
        player_rect = self.player.get_rect()
        for obstacle in self.obstacles:
            obs_rect = obstacle.get_rect()
            if player_rect.colliderect(obs_rect):
                self.player.alive = False
                self.state = GameState.GAME_OVER
                break

        # Fall in pit check
        if self.player.y > SCREEN_HEIGHT:
            self.player.alive = False
            self.state = GameState.GAME_OVER

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.state == GameState.PLAYING:
                    beat_offset = self.rhythm.get_beat_offset_ms()
                    # Determine if we're before or after the beat
                    beat_phase = self.rhythm.beat_phase
                    if beat_phase > 0.5:
                        beat_offset = -beat_offset

                    result = self.player.jump(beat_offset)

                    self.jump_sound.play()

                    if result == "perfect":
                        self.success_sound.play()

    def draw_grid(self):
        # Draw neon grid background
        grid_size = 40

        # Vertical lines
        for x in range(0, SCREEN_WIDTH, grid_size):
            color = COLOR_GRID if x % (grid_size * 4) != 0 else COLOR_GRID_NEON
            pygame.draw.line(self.screen, color, (x, 0), (x, SCREEN_HEIGHT), 1)

        # Horizontal lines
        for y in range(0, SCREEN_HEIGHT, grid_size):
            color = COLOR_GRID if y % (grid_size * 4) != 0 else COLOR_GRID_NEON
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y), 1)

        # Beat pulse effect on grid
        if self.rhythm.beat_pulse > 0:
            pulse_alpha = int(self.rhythm.beat_pulse * 50)
            pulse_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pulse_surface.fill((100, 100, 150, pulse_alpha))
            self.screen.blit(pulse_surface, (0, 0))

    def draw(self):
        self.screen.fill(COLOR_BG)

        # Draw grid
        self.draw_grid()

        # Draw floor
        pygame.draw.rect(self.screen, COLOR_FLOOR, (0, self.floor_y, SCREEN_WIDTH, 10))
        pygame.draw.line(self.screen, COLOR_FLOOR_LINE, (0, self.floor_y), (SCREEN_WIDTH, self.floor_y), 2)

        # Draw beat indicator
        beat_y = self.floor_y + 20
        beat_x = 50 + self.rhythm.beat_phase * (SCREEN_WIDTH - 100)
        pygame.draw.circle(self.screen, COLOR_PLAYER_ACCENT, (int(beat_x), beat_y), 8)
        pygame.draw.circle(self.screen, COLOR_PLAYER_ACCENT, (int(beat_x), beat_y), 12, 2)

        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw HUD
        self.draw_hud()

        # Draw start screen
        if self.state == GameState.START:
            self.draw_start_screen()

        # Draw game over screen
        if self.state == GameState.GAME_OVER:
            self.draw_game_over()

        pygame.display.flip()

    def draw_hud(self):
        # Top bar background
        pygame.draw.rect(self.screen, (20, 20, 30), (0, 0, SCREEN_WIDTH, 45))
        pygame.draw.line(self.screen, COLOR_PLAYER_ACCENT, (0, 45), (SCREEN_WIDTH, 45), 1)

        # Score
        score_text = self.small_font.render(f"Score: {self.player.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        # Combo
        combo_color = COLOR_PERFECT if self.player.combo > 1 else COLOR_TEXT
        combo_text = self.small_font.render(f"Combo: x{self.player.combo}", True, combo_color)
        self.screen.blit(combo_text, (150, 10))

        # Perfect ratio
        if self.player.total_jumps > 0:
            perfect_pct = int(self.player.perfect_jumps / self.player.total_jumps * 100)
            perfect_text = self.small_font.render(f"Perfect: {perfect_pct}%", True, COLOR_PERFECT)
            self.screen.blit(perfect_text, (280, 10))

        # BPM indicator
        bpm_text = self.small_font.render(f"{BPM} BPM", True, COLOR_PLAYER_ACCENT)
        self.screen.blit(bpm_text, (420, 10))

        # Beat indicator text
        on_beat = self.rhythm.is_on_beat()
        beat_text = "ON BEAT!" if on_beat else ""
        if beat_text:
            beat_color = COLOR_PERFECT if on_beat else COLOR_TEXT
            beat_surface = self.small_font.render(beat_text, True, beat_color)
            self.screen.blit(beat_surface, (500, 10))

        # Controls hint
        hint_text = self.tiny_font.render("SPACE: Jump | Jump on the beat for bonus!", True, (120, 120, 130))
        self.screen.blit(hint_text, (SCREEN_WIDTH - 320, 12))

    def draw_start_screen(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Title
        title_text = self.font.render("VECTOR MAPPY RHYTHM RUN", True, COLOR_PLAYER_ACCENT)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(title_text, title_rect)

        # Subtitle
        subtitle_text = self.small_font.render("Dash to the beat of the music!", True, COLOR_TEXT)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(subtitle_text, subtitle_rect)

        # Instructions
        inst1 = self.small_font.render("Press SPACE to start", True, COLOR_PERFECT)
        inst1_rect = inst1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(inst1, inst1_rect)

        inst2 = self.tiny_font.render("Jump on the beat (+/-50ms) for Perfect jumps and combo bonus!", True, (150, 150, 150))
        inst2_rect = inst2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(inst2, inst2_rect)

        # Beat visualization
        beat_y = SCREEN_HEIGHT // 2 + 100
        for i in range(8):
            x = SCREEN_WIDTH // 2 - 150 + i * 40
            pygame.draw.circle(self.screen, COLOR_PLAYER_ACCENT if i % 2 == 0 else COLOR_GRID, (x, beat_y), 10)
            pygame.draw.circle(self.screen, COLOR_PLAYER_ACCENT, (x, beat_y), 10, 1)

    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        game_over_text = self.font.render("GAME OVER", True, COLOR_MISS)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)

        # Score
        score_text = self.small_font.render(f"Final Score: {self.player.score}", True, COLOR_TEXT)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        # Combo
        combo_text = self.small_font.render(f"Max Combo: x{self.player.max_combo}", True, COLOR_PERFECT)
        combo_rect = combo_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(combo_text, combo_rect)

        # Perfect ratio
        if self.player.total_jumps > 0:
            perfect_pct = int(self.player.perfect_jumps / self.player.total_jumps * 100)
            perfect_text = self.small_font.render(f"Perfect: {perfect_pct}% ({self.player.perfect_jumps}/{self.player.total_jumps})", True, COLOR_PERFECT)
            perfect_rect = perfect_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            self.screen.blit(perfect_text, perfect_rect)

        # Restart instruction
        restart_text = self.small_font.render("Press R to restart", True, COLOR_PLAYER_ACCENT)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        running = True

        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self.handle_event(event)

            # Update
            self.update()

            # Draw
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    import math
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
