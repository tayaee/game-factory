import pygame
import sys
import random

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

# Physics constants
GRAVITY = 0.3
CLIMB_SPEED = 3.0
SIDE_SWITCH_SPEED = 4.0
SCROLL_SPEED = 0.5

# Colors
COLOR_BG = (135, 206, 235)  # Sky blue
COLOR_VINE = (34, 139, 34)  # Forest green
COLOR_VINE_DARK = (20, 100, 20)
COLOR_PLAYER = (255, 0, 0)  # Red
COLOR_PLAYER_OVERALLS = (0, 0, 255)  # Blue
COLOR_TEXT = (255, 255, 255)
COLOR_STAMINA_FULL = (0, 255, 0)
COLOR_STAMINA_LOW = (255, 0, 0)
COLOR_COIN = (255, 215, 0)
COLOR_ENEMY = (139, 69, 19)

# Game settings
VINE_WIDTH = 16
VINE_X = SCREEN_WIDTH // 2 - VINE_WIDTH // 2
PLAYER_SIZE = 20
STAMINA_MAX = 100
STAMINA_DRAIN_RATE = 0.15
STAMINA_RECHARGE_RATE = 0.05
COIN_SIZE = 12
ENEMY_SIZE = 24

# Action space constants
ACTION_NOOP = 0
ACTION_UP = 1
ACTION_DOWN = 2
ACTION_LEFT = 3
ACTION_RIGHT = 4


class Player:
    def __init__(self):
        self.x = VINE_X - PLAYER_SIZE // 2
        self.y = SCREEN_HEIGHT - 100
        self.vel_y = 0.0
        self.side = -1  # -1 for left side, 1 for right side
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.is_climbing = True
        self.stamina = STAMINA_MAX
        self.score = 0
        self.altitude = 0

    def update(self, action):
        # Drain stamina if not moving
        if action == ACTION_NOOP:
            self.stamina -= STAMINA_DRAIN_RATE
        else:
            self.stamina = min(STAMINA_MAX, self.stamina + STAMINA_RECHARGE_RATE)

        # Handle actions
        if action == ACTION_UP:
            self.vel_y = -CLIMB_SPEED
            self.altitude += 1
        elif action == ACTION_DOWN:
            self.vel_y = CLIMB_SPEED
        elif action == ACTION_LEFT:
            self.side = -1
            self.vel_y = 0
        elif action == ACTION_RIGHT:
            self.side = 1
            self.vel_y = 0
        else:
            self.vel_y *= 0.8

        # Apply gravity if not actively climbing
        if action != ACTION_UP and action != ACTION_DOWN:
            self.vel_y += GRAVITY * 0.5

        # Update position
        self.y += self.vel_y

        # Keep player on vine horizontally
        if self.side == -1:
            target_x = VINE_X - self.width - 2
        else:
            target_x = VINE_X + VINE_WIDTH + 2

        # Smooth side switching
        self.x += (target_x - self.x) * 0.3

        # Keep player in bounds
        if self.y < 50:
            self.y = 50
        if self.y > SCREEN_HEIGHT - self.height - 10:
            self.y = SCREEN_HEIGHT - self.height - 10

    def get_hitbox(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface):
        # Draw player (Mario-style: red hat, blue overalls)
        # Hat
        pygame.draw.rect(surface, COLOR_PLAYER, (int(self.x), int(self.y), self.width, self.height // 3))
        # Face
        pygame.draw.rect(surface, (255, 200, 150), (int(self.x) + 3, int(self.y) + self.height // 3, self.width - 6, self.height // 4))
        # Overalls
        pygame.draw.rect(surface, COLOR_PLAYER_OVERALLS, (int(self.x), int(self.y) + self.height // 2, self.width, self.height // 2))


class Coin:
    def __init__(self, y):
        self.x = VINE_X - COIN_SIZE // 2 - random.choice([-40, 40])
        self.y = y
        self.width = COIN_SIZE
        self.height = COIN_SIZE
        self.collected = False
        self.animation_frame = 0

    def update(self, scroll_y):
        self.y += scroll_y
        self.animation_frame += 0.1

    def get_hitbox(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface):
        if self.collected:
            return

        # Animated coin
        scale = 0.8 + 0.2 * abs(self.animation_frame % 2 - 1)
        draw_width = int(self.width * scale)
        draw_height = int(self.height)
        draw_x = int(self.x + (self.width - draw_width) // 2)
        draw_y = int(self.y)

        pygame.draw.ellipse(surface, COLOR_COIN, (draw_x, draw_y, draw_width, draw_height))
        pygame.draw.ellipse(surface, (255, 255, 0), (draw_x + 2, draw_y + 2, draw_width - 4, draw_height - 4))


class Obstacle:
    def __init__(self, y):
        self.y = y
        self.width = ENEMY_SIZE
        self.height = ENEMY_SIZE
        self.direction = random.choice([-1, 1])
        self.speed = random.uniform(1.5, 3.0)
        # Determine which side to spawn on
        if self.direction == 1:
            self.x = -self.width
        else:
            self.x = SCREEN_WIDTH
        self.active = True

    def update(self, scroll_y):
        self.y += scroll_y
        self.x += self.speed * self.direction

        # Deactivate if off screen
        if (self.direction == 1 and self.x > SCREEN_WIDTH) or \
           (self.direction == -1 and self.x < -self.width):
            self.active = False

    def get_hitbox(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface):
        if not self.active:
            return

        # Draw enemy (Koopa-like)
        # Shell
        pygame.draw.ellipse(surface, COLOR_ENEMY, (int(self.x), int(self.y), self.width, self.height))
        # Shell pattern
        pygame.draw.ellipse(surface, (100, 50, 10), (int(self.x) + 4, int(self.y) + 4, self.width - 8, self.height - 8))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Super Mario Bros Vine Climb")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.camera_y = 0
        self.game_over = False
        self.scroll_accumulator = 0

        # Entities
        self.coins = []
        self.obstacles = []

        # Spawn timers
        self.coin_timer = 0
        self.obstacle_timer = 0

        # Difficulty
        self.difficulty = 1.0

    def spawn_coin(self):
        # Spawn coin above current view
        coin_y = -50
        self.coins.append(Coin(coin_y))

    def spawn_obstacle(self):
        # Spawn obstacle above current view
        obstacle_y = -50
        self.obstacles.append(Obstacle(obstacle_y))

    def update(self):
        if self.game_over:
            return

        # Auto-scroll
        self.scroll_accumulator += SCROLL_SPEED * self.difficulty
        scroll_amount = 0
        if self.scroll_accumulator >= 1.0:
            scroll_amount = int(self.scroll_accumulator)
            self.scroll_accumulator -= scroll_amount
            self.camera_y += scroll_amount

        # Update player based on input
        keys = pygame.key.get_pressed()
        action = ACTION_NOOP
        if keys[pygame.K_UP]:
            action = ACTION_UP
        elif keys[pygame.K_DOWN]:
            action = ACTION_DOWN
        elif keys[pygame.K_LEFT]:
            action = ACTION_LEFT
        elif keys[pygame.K_RIGHT]:
            action = ACTION_RIGHT

        self.player.update(action)

        # Update entities with scroll
        for coin in self.coins:
            coin.update(scroll_amount)

        for obstacle in self.obstacles:
            obstacle.update(scroll_amount)

        # Spawn new entities
        self.coin_timer += scroll_amount
        if self.coin_timer > 80:
            self.spawn_coin()
            self.coin_timer = 0

        self.obstacle_timer += scroll_amount
        obstacle_spawn_rate = max(40, 100 - int(self.difficulty * 10))
        if self.obstacle_timer > obstacle_spawn_rate:
            self.spawn_obstacle()
            self.obstacle_timer = 0

        # Check coin collection
        player_hitbox = self.player.get_hitbox()
        for coin in self.coins:
            if not coin.collected and player_hitbox.colliderect(coin.get_hitbox()):
                coin.collected = True
                self.player.score += 10

        # Check obstacle collision
        for obstacle in self.obstacles:
            if obstacle.active and player_hitbox.colliderect(obstacle.get_hitbox()):
                self.game_over = True
                return

        # Check stamina
        if self.player.stamina <= 0:
            self.game_over = True

        # Clean up off-screen entities
        self.coins = [c for c in self.coins if c.y < SCREEN_HEIGHT + 50 and not c.collected]
        self.obstacles = [o for o in self.obstacles if o.active and o.y < SCREEN_HEIGHT + 50]

        # Increase difficulty over time
        self.difficulty = 1.0 + self.player.altitude / 1000

    def get_state(self):
        return {
            'player_y': self.player.y,
            'player_vel_y': self.player.vel_y,
            'player_side': self.player.side,
            'stamina': self.player.stamina,
            'altitude': self.player.altitude
        }

    def get_reward(self):
        if self.game_over:
            return -100

        reward = 0

        # Reward for climbing
        if self.player.vel_y < 0:
            reward += 0.1

        # Reward for coin collection (handled in update)
        # Small penalty for staying still
        if self.player.vel_y == 0:
            reward -= 0.01

        return reward

    def step(self, action):
        if not self.game_over:
            self.player.update(action)
            self.update()

        return self.get_state(), self.get_reward(), self.game_over

    def reset(self):
        self.reset_game()
        return self.get_state()

    def draw(self):
        self.screen.fill(COLOR_BG)

        # Draw vine segments
        segment_height = 20
        offset = int(self.camera_y) % segment_height
        for y in range(-offset - segment_height, SCREEN_HEIGHT + segment_height, segment_height):
            # Alternate colors for vine pattern
            color = COLOR_VINE if (y + offset) // segment_height % 2 == 0 else COLOR_VINE_DARK
            pygame.draw.rect(self.screen, color, (VINE_X, y, VINE_WIDTH, segment_height))
            # Draw vine leaves
            if (y + offset) // segment_height % 3 == 0:
                leaf_y = y + segment_height // 2
                pygame.draw.ellipse(self.screen, COLOR_VINE, (VINE_X - 8, leaf_y - 4, 12, 8))
                pygame.draw.ellipse(self.screen, COLOR_VINE, (VINE_X + VINE_WIDTH - 4, leaf_y - 4, 12, 8))

        # Draw coins
        for coin in self.coins:
            coin.draw(self.screen)

        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw stamina bar
        stamina_width = 150
        stamina_height = 16
        stamina_x = 10
        stamina_y = 10

        # Background
        pygame.draw.rect(self.screen, (0, 0, 0), (stamina_x, stamina_y, stamina_width, stamina_height))

        # Fill based on stamina
        fill_width = int((self.player.stamina / STAMINA_MAX) * stamina_width)
        stamina_color = COLOR_STAMINA_FULL if self.player.stamina > 30 else COLOR_STAMINA_LOW
        pygame.draw.rect(self.screen, stamina_color, (stamina_x, stamina_y, fill_width, stamina_height))

        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), (stamina_x, stamina_y, stamina_width, stamina_height), 2)

        # Stamina label
        stamina_label = self.small_font.render("STAMINA", True, COLOR_TEXT)
        self.screen.blit(stamina_label, (stamina_x, stamina_y + stamina_height + 4))

        # Draw score and altitude
        score_text = self.font.render(f"Score: {self.player.score}", True, COLOR_TEXT)
        altitude_text = self.small_font.render(f"Altitude: {self.player.altitude}m", True, COLOR_TEXT)

        self.screen.blit(score_text, (10, 50))
        self.screen.blit(altitude_text, (10, 85))

        # Draw controls hint
        if self.player.altitude < 50:
            hint_lines = [
                "UP/DOWN: Climb",
                "LEFT/RIGHT: Switch side"
            ]
            for i, line in enumerate(hint_lines):
                hint_text = self.small_font.render(line, True, (255, 255, 0))
                self.screen.blit(hint_text, (SCREEN_WIDTH - hint_text.get_width() - 10, 10 + i * 25))

        # Game over overlay
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
            score_final_text = self.font.render(f"Final Score: {self.player.score}", True, COLOR_TEXT)
            altitude_final_text = self.small_font.render(f"Altitude Reached: {self.player.altitude}m", True, COLOR_TEXT)
            restart_text = self.small_font.render("Press SPACE to restart", True, COLOR_TEXT)

            self.screen.blit(game_over_text,
                          (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(score_final_text,
                          (SCREEN_WIDTH // 2 - score_final_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(altitude_final_text,
                          (SCREEN_WIDTH // 2 - altitude_final_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
            self.screen.blit(restart_text,
                          (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

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

            # Update game
            self.update()

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
