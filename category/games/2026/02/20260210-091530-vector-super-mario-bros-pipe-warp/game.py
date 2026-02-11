"""Main game logic for Vector Super Mario Bros Pipe Warp."""

import pygame
import random
import math
from config import *


class Camera:
    """Handles vertical scrolling of the game world."""

    def __init__(self):
        self.offset_y = 0

    def update(self, player_y):
        """Update camera offset based on player position."""
        target_y = player_y - SCROLL_THRESHOLD
        if target_y > self.offset_y:
            self.offset_y = target_y

    def world_to_screen(self, x, y):
        """Convert world coordinates to screen coordinates."""
        return x, y - self.offset_y

    def get_height_reached(self):
        """Get the current height reached."""
        return int(self.offset_y)


class Pipe:
    """Represents a pipe in the game."""

    def __init__(self, x, y, height, has_piranha=False, is_gold=False):
        self.x = x
        self.y = y
        self.height = height
        self.has_piranha = has_piranha
        self.is_gold = is_gold
        self.width = PIPE_WIDTH

        # Piranha plant state
        if self.has_piranha:
            self.piranha_y = y
            self.piranha_target_y = y
            self.piranha_state = "rising"  # rising, waiting, lowering
            self.piranha_wait_timer = random.randint(PIRANHA_MIN_WAIT, PIRANCHA_MAX_WAIT)

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y - self.height, self.width, self.height)

    def update(self):
        """Update pipe state (piranha plant animation)."""
        if not self.has_piranha:
            return

        if self.piranha_state == "rising":
            self.piranha_y -= PIRANHA_SPEED
            if self.piranha_y <= self.y - PIRANHA_MAX_HEIGHT:
                self.piranha_y = self.y - PIRANHA_MAX_HEIGHT
                self.piranha_state = "waiting"

        elif self.piranha_state == "waiting":
            self.piranha_wait_timer -= 1
            if self.piranha_wait_timer <= 0:
                self.piranha_state = "lowering"

        elif self.piranha_state == "lowering":
            self.piranha_y += PIRANHA_SPEED
            if self.piranha_y >= self.y:
                self.piranha_y = self.y
                self.piranha_state = "rising"
                self.piranha_wait_timer = random.randint(PIRANHA_MIN_WAIT, PIRANCHA_MAX_WAIT)

    def get_piranha_rect(self):
        """Get the collision rect for the piranha plant."""
        if not self.has_piranha:
            return None
        plant_height = self.y - self.piranha_y
        return pygame.Rect(
            self.x + (PIPE_WIDTH - PIRANHA_WIDTH) // 2,
            self.piranha_y - plant_height + 4,
            PIRANHA_WIDTH,
            plant_height
        )

    def draw(self, surface, camera):
        """Draw the pipe."""
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        pipe_screen_y = screen_y - self.height

        # Don't draw if off screen
        if pipe_screen_y > WINDOW_HEIGHT or screen_y < 0:
            return

        # Pipe body
        body_color = COLOR_GOLD_PIPE if self.is_gold else COLOR_PIPE_BODY
        dark_color = COLOR_GOLD_PIPE_RIM if self.is_gold else COLOR_PIPE_DARK
        rim_color = COLOR_GOLD_PIPE_RIM if self.is_gold else COLOR_PIPE_RIM

        pygame.draw.rect(surface, dark_color,
                        (screen_x + 4, pipe_screen_y, self.width - 8, self.height))
        pygame.draw.rect(surface, body_color,
                        (screen_x + 2, pipe_screen_y, self.width - 4, self.height))

        # Pipe rim at top
        pygame.draw.rect(surface, dark_color,
                        (screen_x - 4, pipe_screen_y, self.width + 8, PIPE_RIM_HEIGHT))
        pygame.draw.rect(surface, rim_color,
                        (screen_x - 3, pipe_screen_y + 1, self.width + 6, PIPE_RIM_HEIGHT - 2))

        # Draw piranha plant if present
        if self.has_piranha:
            self._draw_piranha(surface, camera)

    def _draw_piranha(self, surface, camera):
        """Draw the piranha plant."""
        piranha_rect = self.get_piranha_rect()
        if piranha_rect is None:
            return

        screen_x, screen_y = camera.world_to_screen(piranha_rect.x, piranha_rect.y)
        plant_height = piranha_rect.height

        # Body
        body_rect = pygame.Rect(
            screen_x + 4,
            screen_y,
            PIRANHA_WIDTH - 8,
            plant_height
        )
        pygame.draw.ellipse(surface, COLOR_PIRANHA_HEAD, body_rect)

        # Spots
        pygame.draw.circle(surface, COLOR_PIRANHA_SPOT,
                          (screen_x + 8, screen_y + 8), 3)
        pygame.draw.circle(surface, COLOR_PIRANHA_SPOT,
                          (screen_x + PIRANHA_WIDTH - 8, screen_y + 8), 3)

        # Teeth
        for i in range(3):
            tooth_x = screen_x + 6 + i * 7
            tooth_y = screen_y + plant_height - 6
            pygame.draw.polygon(surface, COLOR_PIRANHA_TEETH,
                              [(tooth_x, tooth_y), (tooth_x + 3, tooth_y + 4), (tooth_x + 6, tooth_y)])

        # Eyes
        pygame.draw.circle(surface, (255, 255, 255),
                          (screen_x + 8, screen_y + 12), 4)
        pygame.draw.circle(surface, (255, 255, 255),
                          (screen_x + PIRANHA_WIDTH - 8, screen_y + 12), 4)
        pygame.draw.circle(surface, (0, 0, 0),
                          (screen_x + 9, screen_y + 12), 2)
        pygame.draw.circle(surface, (0, 0, 0),
                          (screen_x + PIRANHA_WIDTH - 7, screen_y + 12), 2)


class Coin:
    """Represents a collectible coin."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False
        self.anim_offset = random.random() * 6.28

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, COIN_SIZE, COIN_SIZE)

    def update(self):
        """Update coin animation."""
        self.anim_offset = (self.anim_offset + 0.15) % 6.28

    def draw(self, surface, camera):
        """Draw the coin."""
        if self.collected:
            return

        screen_x, screen_y = camera.world_to_screen(self.x, self.y)

        # Don't draw if off screen
        if screen_y > WINDOW_HEIGHT or screen_y < -COIN_SIZE:
            return

        # Spinning effect
        width_scale = abs(math.cos(self.anim_offset))
        current_width = int(COIN_SIZE * width_scale)
        if current_width < 2:
            current_width = 2

        coin_rect = pygame.Rect(
            screen_x + (COIN_SIZE - current_width) // 2,
            screen_y,
            current_width,
            COIN_SIZE
        )

        pygame.draw.ellipse(surface, COLOR_COIN, coin_rect)
        pygame.draw.ellipse(surface, (255, 180, 0), coin_rect, 2)


class Player:
    """Represents the player (Mario)."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.max_height = 0

    def update(self, keys):
        """Update player physics."""
        # Horizontal movement
        accel_x = 0
        if keys[pygame.K_LEFT]:
            accel_x = -PLAYER_ACCEL
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            accel_x = PLAYER_ACCEL
            self.facing_right = True

        self.vel_x += accel_x
        self.vel_x *= PLAYER_FRICTION
        self.vel_x = max(-PLAYER_SPEED, min(PLAYER_SPEED, self.vel_x))

        # Apply gravity
        self.vel_y += GRAVITY
        self.vel_y = min(MAX_FALL_SPEED, self.vel_y)

        # Update position
        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)

        # Track max height
        current_height = -self.rect.y
        if current_height > self.max_height:
            self.max_height = current_height

        # Check if fell off bottom of screen
        fell_off = self.rect.y > WINDOW_HEIGHT + 100

        return fell_off, current_height

    def jump(self):
        """Make the player jump."""
        if self.on_ground:
            self.vel_y = PLAYER_JUMP_SPEED
            self.on_ground = False
            return True
        return False

    def handle_collision(self, pipes, camera):
        """Handle collision with pipes."""
        self.on_ground = False

        # Get visible pipe rects
        visible_pipes = []
        for pipe in pipes:
            screen_x, screen_y = camera.world_to_screen(pipe.x, pipe.y)
            if -PIPE_MAX_HEIGHT < screen_y < WINDOW_HEIGHT + 100:
                visible_pipes.append(pipe)

        for pipe in visible_pipes:
            pipe_rect = pipe.rect

            # Horizontal collision
            if self.rect.colliderect(pipe_rect):
                if self.vel_x > 0:
                    self.rect.right = pipe_rect.left
                    self.vel_x = 0
                elif self.vel_x < 0:
                    self.rect.left = pipe_rect.right
                    self.vel_x = 0

            # Vertical collision
            if self.rect.colliderect(pipe_rect):
                if self.vel_y > 0:
                    # Landing on top
                    self.rect.bottom = pipe_rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    # Hitting from below
                    self.rect.top = pipe_rect.bottom
                    self.vel_y = 0

    def draw(self, surface, camera):
        """Draw the player."""
        screen_x, screen_y = camera.world_to_screen(self.rect.x, self.rect.y)

        # Don't draw if off screen
        if screen_y > WINDOW_HEIGHT or screen_y < -PLAYER_HEIGHT:
            return

        draw_rect = pygame.Rect(screen_x, screen_y, PLAYER_WIDTH, PLAYER_HEIGHT)

        # Body (overalls)
        pygame.draw.rect(surface, COLOR_PLAYER_OVERALLS,
                        (screen_x + 4, screen_y + 14, PLAYER_WIDTH - 8, 14))

        # Head/skin
        pygame.draw.rect(surface, COLOR_PLAYER_SKIN,
                        (screen_x + 4, screen_y + 4, PLAYER_WIDTH - 8, 12))

        # Hat
        hat_rect = pygame.Rect(screen_x - 1, screen_y + 2, PLAYER_WIDTH + 2, 6)
        pygame.draw.rect(surface, COLOR_PLAYER_HAT, hat_rect)

        # Eye
        eye_x = screen_x + (12 if self.facing_right else 6)
        pygame.draw.circle(surface, (0, 0, 0), (eye_x, screen_y + 8), 2)

        # Mustache
        mustache_y = screen_y + 12
        mustache_x = screen_x + (10 if self.facing_right else 4)
        pygame.draw.rect(surface, (50, 30, 20),
                        (mustache_x, mustache_y, 8, 3))

        # Buttons on overalls
        pygame.draw.circle(surface, (255, 220, 0),
                          (screen_x + PLAYER_WIDTH // 2, screen_y + 18), 2)


class Game:
    """Main game class for Vector Super Mario Bros Pipe Warp."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Vector Super Mario Bros: Pipe Warp")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 56)

        self.setup_level()
        self.reset_game_state()

    def setup_level(self):
        """Setup the level with pipes and coins."""
        self.pipes = []
        self.coins = []

        # Starting platform
        start_pipe = Pipe(100, WINDOW_HEIGHT - 20, 40, has_piranha=False)
        self.pipes.append(start_pipe)

        # Generate vertical maze of pipes
        current_y = WINDOW_HEIGHT - 20
        platforms_reached = 0

        while current_y > GOLD_PIPE_Y - WIN_HEIGHT:
            current_y -= random.randint(70, 120)
            platforms_reached += 1

            # Varying number of pipes per row
            num_pipes = random.randint(1, 3)
            positions = []

            if num_pipes == 1:
                positions.append(random.randint(20, WINDOW_WIDTH - 60))
            elif num_pipes == 2:
                pos1 = random.randint(20, WINDOW_WIDTH // 2 - 40)
                pos2 = random.randint(WINDOW_WIDTH // 2 + 20, WINDOW_WIDTH - 60)
                positions.extend([pos1, pos2])
            else:
                positions.extend([
                    random.randint(20, 100),
                    random.randint(150, 250),
                    random.randint(300, WINDOW_WIDTH - 60)
                ])

            for pos in positions:
                height = random.randint(PIPE_MIN_HEIGHT, PIPE_MAX_HEIGHT)
                # Add piranha plants to some pipes
                has_piranha = random.random() < 0.4 and platforms_reached > 2
                self.pipes.append(Pipe(pos, current_y, height, has_piranha))

                # Add coins above some pipes
                if random.random() < 0.3:
                    self.coins.append(Coin(pos + PIPE_WIDTH // 2 - COIN_SIZE // 2,
                                          current_y - height - 30))

        # Golden pipe at the top (warp zone)
        gold_pipe_x = WINDOW_WIDTH // 2 - PIPE_WIDTH // 2
        self.gold_pipe = Pipe(gold_pipe_x, GOLD_PIPE_Y, 80, has_piranha=False, is_gold=True)
        self.pipes.append(self.gold_pipe)

    def reset_game_state(self):
        """Reset game state."""
        self.camera = Camera()
        self.player = Player(120, WINDOW_HEIGHT - 100)
        self.score = 0
        self.game_over = False
        self.won = False
        self.running = True
        self.message_timer = 0
        self.current_message = ""
        self.last_platform_y = WINDOW_HEIGHT - 20

        # Reset coins
        for coin in self.coins:
            coin.collected = False

    def run(self):
        """Main game loop."""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        if not self.game_over:
                            self.player.jump()
                        else:
                            # Restart game
                            self.reset_game_state()

            if not self.game_over:
                # Get key states
                keys = pygame.key.get_pressed()

                # Update player
                fell_off, current_height = self.player.update(keys)

                # Update camera
                self.camera.update(self.player.rect.y)

                # Update pipes
                for pipe in self.pipes:
                    pipe.update()

                # Update coins
                for coin in self.coins:
                    coin.update()

                # Handle collisions
                self.player.handle_collision(self.pipes, self.camera)

                # Check coin collection
                for coin in self.coins:
                    if not coin.collected:
                        coin_screen_y = coin.y - self.camera.offset_y
                        if 0 <= coin_screen_y <= WINDOW_HEIGHT:
                            player_screen_y = self.player.rect.y - self.camera.offset_y
                            if self.player.rect.colliderect(coin.rect):
                                coin.collected = True
                                self.score += COIN_VALUE
                                self.show_message(f"+{COIN_VALUE}!", 30)

                # Check piranha collision
                for pipe in self.pipes:
                    if pipe.has_piranha:
                        piranha_rect = pipe.get_piranha_rect()
                        if piranha_rect and self.player.rect.colliderect(piranha_rect):
                            self.game_over = True
                            self.won = False
                            self.show_message("Caught by Piranha!", 60)

                # Check if player fell off
                if fell_off:
                    self.game_over = True
                    self.won = False
                    self.show_message("Fell into the abyss!", 60)

                # Check for reaching new platforms (scoring)
                player_y = self.player.rect.y
                if player_y < self.last_platform_y - 50:
                    self.score += SCORE_PER_PLATFORM
                    self.last_platform_y = player_y

                # Check win condition (reached golden pipe)
                if self.player.rect.y < GOLD_PIPE_Y + 50:
                    self.game_over = True
                    self.won = True
                    self.show_message("WARP ZONE REACHED!", 120)

            # Draw everything
            self.draw()

            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

    def show_message(self, message, duration):
        """Show a temporary message."""
        self.current_message = message
        self.message_timer = duration

    def draw(self):
        """Draw the game."""
        self.screen.fill(COLOR_BG)

        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen, self.camera)

        # Draw coins
        for coin in self.coins:
            coin.draw(self.screen, self.camera)

        # Draw player
        self.player.draw(self.screen, self.camera)

        # Draw UI
        self.draw_ui()

        # Draw message
        if self.message_timer > 0:
            self.draw_message()
            self.message_timer -= 1

        # Draw game over screen
        if self.game_over:
            self.draw_game_over()

    def draw_ui(self):
        """Draw the user interface."""
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_SCORE)
        self.screen.blit(score_text, (10, 10))

        # Height
        height = self.camera.get_height_reached()
        height_text = self.font.render(f"Height: {height}", True, COLOR_TEXT)
        self.screen.blit(height_text, (10, 45))

        # Goal indicator
        goal_text = self.font.render("Reach the Golden Pipe!", True, COLOR_GOLD_PIPE)
        goal_rect = goal_text.get_rect(center=(WINDOW_WIDTH // 2, 20))
        self.screen.blit(goal_text, goal_rect)

    def draw_message(self):
        """Draw temporary message."""
        msg_text = self.font.render(self.current_message, True, COLOR_SCORE)
        msg_rect = msg_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
        self.screen.blit(msg_text, msg_rect)

    def draw_game_over(self):
        """Draw game over screen."""
        # Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        if self.won:
            title = "WARP ZONE!"
            color = COLOR_GOLD_PIPE
            subtitle = "You reached the secret warp!"
        else:
            title = "GAME OVER"
            color = COLOR_WARNING
            subtitle = "Try again!"

        title_text = self.large_font.render(title, True, color)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(title_text, title_rect)

        score_text = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
        self.screen.blit(score_text, score_rect)

        height_text = self.font.render(f"Height Reached: {self.camera.get_height_reached()}", True, COLOR_TEXT)
        height_rect = height_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 45))
        self.screen.blit(height_text, height_rect)

        restart_text = self.font.render("Press SPACE to restart or ESC to quit", True, COLOR_TEXT)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 90))
        self.screen.blit(restart_text, restart_rect)

    # AI Interface Methods for RL Integration

    def get_state(self):
        """Get current game state as a vector for AI input."""
        piranha_states = []
        for pipe in self.pipes:
            if pipe.has_piranha:
                piranha_rect = pipe.get_piranha_rect()
                if piranha_rect:
                    piranha_states.append({
                        "x": pipe.x,
                        "y": pipe.y,
                        "piranha_y": pipe.piranha_y,
                        "state": pipe.piranha_state
                    })

        coin_positions = [(c.x, c.y) for c in self.coins if not c.collected]

        return {
            "player_pos": (self.player.rect.centerx, self.player.rect.centery),
            "player_vel": (self.player.vel_x, self.player.vel_y),
            "player_on_ground": self.player.on_ground,
            "camera_offset": self.camera.offset_y,
            "piranha_states": piranha_states,
            "coin_positions": coin_positions,
            "score": self.score,
        }

    def set_action(self, action):
        """Set action for AI-controlled player."""
        if action == "left":
            self.player.vel_x = -PLAYER_SPEED
        elif action == "right":
            self.player.vel_x = PLAYER_SPEED
        elif action == "jump" and self.player.on_ground:
            self.player.jump()
        elif action == "idle":
            pass

    def get_reward(self):
        """Calculate reward for the current step."""
        reward = REWARD_STRUCTURE["per_step"]
        reward += self.camera.get_height_reached() * REWARD_STRUCTURE["height_gain"]
        if self.game_over and not self.won:
            reward = REWARD_STRUCTURE["death"]
        return reward

    def is_done(self):
        """Check if the game is over."""
        return self.game_over


def main():
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
