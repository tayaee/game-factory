import pygame
import sys

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

# Physics constants
GRAVITY = 0.8
MAX_RUN_SPEED = 6.0
ACCELERATION = 0.3
FRICTION = 0.85
JUMP_IMPULSE = -12.0
MIN_JUMP_VELOCITY = -6.0

# Colors
COLOR_BG = (135, 206, 235)  # Sky blue
COLOR_PLATFORM = (139, 69, 19)  # Brown
COLOR_PLATFORM_TOP = (34, 139, 34)  # Green
COLOR_PLAYER = (255, 0, 0)  # Red
COLOR_PLAYER_OVERALLS = (0, 0, 255)  # Blue
COLOR_TEXT = (255, 255, 255)
COLOR_PIT = (50, 50, 80)  # Dark blue/gray

# Game settings
PLATFORM_HEIGHT = 40
PLATFORM_Y = SCREEN_HEIGHT - PLATFORM_HEIGHT - 50
PLAYER_SIZE = 24
INITIAL_PIT_WIDTH = 80
PIT_WIDTH_INCREMENT = 20
MAX_PIT_WIDTH = 300

# Action space constants
ACTION_NOOP = 0
ACTION_MOVE_RIGHT = 1
ACTION_JUMP = 2
ACTION_MOVE_RIGHT_AND_JUMP = 3


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.is_grounded = False
        self.is_jumping = False
        self.jump_held = False
        self.jump_timer = 0

    def update(self, moving_right, jumping):
        # Apply horizontal input
        if moving_right:
            self.vel_x = min(self.vel_x + ACCELERATION, MAX_RUN_SPEED)
        else:
            self.vel_x *= FRICTION
            if abs(self.vel_x) < 0.1:
                self.vel_x = 0

        # Apply gravity
        self.vel_y += GRAVITY

        # Variable jump height
        if jumping and not self.jump_held and self.is_grounded:
            self.vel_y = JUMP_IMPULSE
            self.is_jumping = True
            self.is_grounded = False
            self.jump_held = True
            self.jump_timer = 0

        # Cut jump short if key released early
        if self.is_jumping and not jumping and self.vel_y < MIN_JUMP_VELOCITY:
            self.vel_y = MIN_JUMP_VELOCITY

        # Update position
        self.x += self.vel_x
        self.y += self.vel_y

        # Update jump timer
        if self.is_jumping:
            self.jump_timer += 1

        # Reset jump held when key released
        if not jumping:
            self.jump_held = False

    def land(self, y_pos):
        self.y = y_pos
        self.vel_y = 0
        self.is_grounded = True
        self.is_jumping = False

    def get_state(self):
        return {
            'player_x_velocity': self.vel_x,
            'player_y_velocity': self.vel_y,
            'is_grounded': self.is_grounded
        }

    def draw(self, surface, offset_x=0):
        draw_x = int(self.x - offset_x)
        draw_y = int(self.y)

        # Draw player (Mario-style: red hat, blue overalls)
        # Hat
        pygame.draw.rect(surface, COLOR_PLAYER, (draw_x, draw_y, self.width, self.height // 3))
        # Face
        pygame.draw.rect(surface, (255, 200, 150), (draw_x + 4, draw_y + self.height // 3, self.width - 8, self.height // 4))
        # Overalls
        pygame.draw.rect(surface, COLOR_PLAYER_OVERALLS, (draw_x, draw_y + self.height // 2, self.width, self.height // 2))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Super Mario Bros Jump Distance Challenge")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.total_distance = 0
        self.pit_width = INITIAL_PIT_WIDTH

        # Create initial platforms
        self.start_platform_width = 200
        self.landing_platform_width = 200
        self.platform_gap = self.pit_width

        # Player starts on left platform
        self.player = Player(100, PLATFORM_Y - PLAYER_SIZE)

        # Level state
        self.camera_x = 0
        self.target_camera_x = 0
        self.game_over = False
        self.successful_landing = False

    def get_level_geometry(self):
        """Returns the geometry of current level: (start_x, start_width, pit_x, pit_width, landing_x, landing_width)"""
        start_x = 0
        start_width = self.start_platform_width
        pit_x = start_width
        pit_width = self.platform_gap
        landing_x = pit_x + pit_width
        landing_width = self.landing_platform_width

        return start_x, start_width, pit_x, pit_width, landing_x, landing_width

    def update_camera(self):
        # Smooth camera follow
        target_x = self.player.x - SCREEN_WIDTH // 3
        self.camera_x += (target_x - self.camera_x) * 0.1
        if self.camera_x < 0:
            self.camera_x = 0

    def check_collisions(self):
        start_x, start_width, pit_x, pit_width, landing_x, landing_width = self.get_level_geometry()

        # Check if player is grounded
        player_bottom = self.player.y + self.player.height
        player_right = self.player.x + self.player.width

        # Check start platform collision
        if (self.player.x < start_x + start_width and
            player_right > start_x and
            player_bottom >= PLATFORM_Y and
            player_bottom <= PLATFORM_Y + 20 and
            self.player.vel_y >= 0):
            self.player.land(PLATFORM_Y - self.player.height)

        # Check landing platform collision
        elif (self.player.x < landing_x + landing_width and
              player_right > landing_x and
              player_bottom >= PLATFORM_Y and
              player_bottom <= PLATFORM_Y + 20 and
              self.player.vel_y >= 0):
            self.player.land(PLATFORM_Y - self.player.height)

            # Check for successful landing (player was on start platform before)
            if not self.successful_landing and self.player.x > landing_x:
                self.successful_landing = True
                self.score += 1
                self.total_distance += self.pit_width
                # Increase difficulty
                self.pit_width = min(self.pit_width + PIT_WIDTH_INCREMENT, MAX_PIT_WIDTH)
                self.platform_gap = self.pit_width

        else:
            # Player is in the air or falling
            self.player.is_grounded = False

        # Check if player fell into pit
        if self.player.y > SCREEN_HEIGHT:
            self.game_over = True

    def get_state(self):
        start_x, start_width, pit_x, pit_width, landing_x, landing_width = self.get_level_geometry()

        return {
            'player_x_velocity': self.player.vel_x,
            'player_y_velocity': self.player.vel_y,
            'distance_to_pit': pit_x - (self.player.x + self.player.width),
            'pit_width': pit_width,
            'is_grounded': self.player.is_grounded
        }

    def get_reward(self):
        if self.game_over:
            return -100

        reward = 0

        # Small reward for moving right while in air
        if not self.player.is_grounded and self.player.vel_x > 0:
            reward += 0.1

        # Bonus for successful landing
        if self.successful_landing:
            reward += self.pit_width
            self.successful_landing = False  # Reset for next jump

        return reward

    def step(self, action):
        moving_right = False
        jumping = False

        if action == ACTION_MOVE_RIGHT:
            moving_right = True
        elif action == ACTION_JUMP:
            jumping = True
        elif action == ACTION_MOVE_RIGHT_AND_JUMP:
            moving_right = True
            jumping = True

        self.player.update(moving_right, jumping)
        self.check_collisions()
        self.update_camera()

        return self.get_state(), self.get_reward(), self.game_over

    def reset(self):
        self.reset_game()
        return self.get_state()

    def draw(self):
        self.screen.fill(COLOR_BG)

        start_x, start_width, pit_x, pit_width, landing_x, landing_width = self.get_level_geometry()

        # Draw pit (dark rectangle below)
        pit_screen_x = pit_x - self.camera_x
        pygame.draw.rect(self.screen, COLOR_PIT,
                        (pit_screen_x, PLATFORM_Y + 10, pit_width, SCREEN_HEIGHT - PLATFORM_Y))

        # Draw start platform
        start_screen_x = start_x - self.camera_x
        pygame.draw.rect(self.screen, COLOR_PLATFORM,
                        (start_screen_x, PLATFORM_Y + 10, start_width, PLATFORM_HEIGHT))
        pygame.draw.rect(self.screen, COLOR_PLATFORM_TOP,
                        (start_screen_x, PLATFORM_Y + 10, start_width, 8))

        # Draw landing platform
        landing_screen_x = landing_x - self.camera_x
        pygame.draw.rect(self.screen, COLOR_PLATFORM,
                        (landing_screen_x, PLATFORM_Y + 10, landing_width, PLATFORM_HEIGHT))
        pygame.draw.rect(self.screen, COLOR_PLATFORM_TOP,
                        (landing_screen_x, PLATFORM_Y + 10, landing_width, 8))

        # Draw player
        self.player.draw(self.screen, self.camera_x)

        # Draw UI
        score_text = self.font.render(f"Pits: {self.score}", True, COLOR_TEXT)
        distance_text = self.small_font.render(f"Distance: {self.total_distance}", True, COLOR_TEXT)
        pit_text = self.small_font.render(f"Pit Width: {self.pit_width}", True, COLOR_TEXT)

        # Add shadow for readability
        self.screen.blit(score_text, (12, 12))
        self.screen.blit(distance_text, (12, 52))
        self.screen.blit(pit_text, (12, 77))

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(distance_text, (10, 50))
        self.screen.blit(pit_text, (10, 75))

        # Draw velocity meter
        vel_text = self.small_font.render(f"Speed: {self.player.vel_x:.1f}", True, COLOR_TEXT)
        pygame.draw.rect(self.screen, (0, 0, 0), (SCREEN_WIDTH - 120, 10, 100, 20))
        vel_bar_width = int((self.player.vel_x / MAX_RUN_SPEED) * 100)
        pygame.draw.rect(self.screen, (0, 255, 0), (SCREEN_WIDTH - 120, 10, vel_bar_width, 20))
        self.screen.blit(vel_text, (SCREEN_WIDTH - 120, 35))

        # Game over overlay
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
            restart_text = self.small_font.render("Press SPACE to restart", True, COLOR_TEXT)

            self.screen.blit(game_over_text,
                            (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
            self.screen.blit(restart_text,
                            (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

        pygame.display.flip()

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
                    elif event.key == pygame.K_SPACE and self.game_over:
                        self.reset_game()

            # Get input
            keys = pygame.key.get_pressed()
            moving_right = keys[pygame.K_RIGHT]
            jumping = keys[pygame.K_SPACE]

            # Update game
            if not self.game_over:
                self.player.update(moving_right, jumping)
                self.check_collisions()
                self.update_camera()

            # Draw
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
