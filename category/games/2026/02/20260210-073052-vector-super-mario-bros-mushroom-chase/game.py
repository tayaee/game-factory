"""Main game logic for Vector Super Mario Bros Mushroom Chase."""

import pygame
import random
from config import *


class Platform:
    """Represents a platform in the game."""

    def __init__(self, x, y, width, height, is_ground=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_ground = is_ground

    def draw(self, surface):
        color = COLOR_PLATFORM if not self.is_ground else (180, 180, 180)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (150, 150, 150), self.rect, 2)


class Player:
    """Represents the player (Mario)."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True

    def update(self, keys):
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

        # Clamp horizontal speed
        self.vel_x = max(-PLAYER_SPEED, min(PLAYER_SPEED, self.vel_x))

        # Apply gravity
        self.vel_y += GRAVITY
        self.vel_y = min(MAX_FALL_SPEED, self.vel_y)

        # Update position
        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)

        # Keep within screen bounds
        self.rect.x = max(0, min(WINDOW_WIDTH - PLAYER_WIDTH, self.rect.x))

        # Check if fell off screen
        return self.rect.y > WINDOW_HEIGHT

    def jump(self):
        if self.on_ground:
            self.vel_y = PLAYER_JUMP_SPEED
            self.on_ground = False
            return True
        return False

    def handle_platform_collision(self, platforms):
        self.on_ground = False

        # Check horizontal collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right

        # Check vertical collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    # Landing on top
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    # Hitting from below
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

    def draw(self, surface):
        # Draw body
        pygame.draw.rect(surface, COLOR_PLAYER, self.rect)
        pygame.draw.rect(surface, COLOR_PLAYER_OUTLINE, self.rect, 2)

        # Draw hat
        hat_rect = pygame.Rect(
            self.rect.x - 2,
            self.rect.y - 4,
            PLAYER_WIDTH + 4,
            8
        )
        pygame.draw.rect(surface, (200, 50, 50), hat_rect)
        pygame.draw.rect(surface, (150, 30, 30), hat_rect, 2)

        # Draw face
        face_y = self.rect.y + 10
        face_x = self.rect.x + (12 if self.facing_right else 4)
        pygame.draw.circle(surface, (255, 220, 180), (face_x, face_y), 5)
        pygame.draw.circle(surface, (0, 0, 0), (face_x + (2 if self.facing_right else -2), face_y), 2)


class Mushroom:
    """Represents the Super Mushroom."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, MUSHROOM_WIDTH, MUSHROOM_HEIGHT)
        self.vel_x = MUSHROOM_SPEED * (1 if random.random() > 0.5 else -1)
        self.vel_y = 0
        self.on_ground = False
        self.anim_offset = 0

    def update(self, platforms):
        # Apply gravity
        self.vel_y += GRAVITY
        self.vel_y = min(MAX_FALL_SPEED, self.vel_y)

        # Update position
        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)

        self.on_ground = False

        # Wall collisions (bounce)
        if self.rect.left <= 0:
            self.rect.left = 0
            self.vel_x *= -1
        elif self.rect.right >= WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
            self.vel_x *= -1

        # Platform collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    # Landing on top
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    # Add bounce when landing
                    if random.random() < 0.3:
                        self.vel_y = -MUSHROOM_BOUNCE_SPEED
                elif self.vel_y < 0:
                    # Hitting from below
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

        # Check if fell off screen
        return self.rect.y > WINDOW_HEIGHT

    def draw(self, surface):
        self.anim_offset = (self.anim_offset + 0.2) % 6.28

        # Mushroom cap
        cap_y = self.rect.y + 2 + int(self.anim_offset)
        cap_rect = pygame.Rect(self.rect.x, cap_y, MUSHROOM_WIDTH, MUSHROOM_HEIGHT - 4)

        pygame.draw.ellipse(surface, COLOR_MUSHROOM_CAP, cap_rect)
        pygame.draw.ellipse(surface, (200, 30, 30), cap_rect, 2)

        # White dots on cap
        dot_offset = int(self.anim_offset * 0.5)
        pygame.draw.circle(
            surface, COLOR_MUSHROOM_DOTS,
            (self.rect.centerx, cap_y + 6 + dot_offset), 3
        )
        pygame.draw.circle(
            surface, COLOR_MUSHROOM_DOTS,
            (self.rect.x + 5, cap_y + 8), 2
        )
        pygame.draw.circle(
            surface, COLOR_MUSHROOM_DOTS,
            (self.rect.right - 5, cap_y + 8), 2
        )

        # Stem
        stem_rect = pygame.Rect(
            self.rect.x + 5,
            self.rect.y + 10 + int(self.anim_offset),
            MUSHROOM_WIDTH - 10, 8
        )
        pygame.draw.rect(surface, (240, 240, 220), stem_rect)


class Game:
    """Main game class for Vector Super Mario Bros Mushroom Chase."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Vector Super Mario Bros: Mushroom Chase")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)

        self.setup_level()

        # Game state
        self.score = 0
        self.mushrooms_lost = 0
        self.game_over = False
        self.won = False
        self.message_timer = 0
        self.current_message = ""
        self.running = True

    def setup_level(self):
        """Setup the level with platforms."""
        self.platforms = []

        # Ground
        self.platforms.append(Platform(0, WINDOW_HEIGHT - 40, 250, 40, is_ground=True))
        self.platforms.append(Platform(350, WINDOW_HEIGHT - 40, 200, 40, is_ground=True))
        self.platforms.append(Platform(600, WINDOW_HEIGHT - 40, 200, 40, is_ground=True))

        # Floating platforms
        self.platforms.append(Platform(50, 450, 120, 20))
        self.platforms.append(Platform(250, 400, 100, 20))
        self.platforms.append(Platform(400, 450, 100, 20))
        self.platforms.append(Platform(550, 400, 120, 20))
        self.platforms.append(Platform(680, 450, 100, 20))

        self.platforms.append(Platform(100, 300, 150, 20))
        self.platforms.append(Platform(300, 250, 100, 20))
        self.platforms.append(Platform(450, 300, 100, 20))
        self.platforms.append(Platform(600, 250, 120, 20))

        self.platforms.append(Platform(50, 150, 100, 20))
        self.platforms.append(Platform(200, 100, 150, 20))
        self.platforms.append(Platform(400, 150, 100, 20))
        self.platforms.append(Platform(550, 100, 120, 20))
        self.platforms.append(Platform(700, 150, 80, 20))

        # Create player
        self.player = Player(100, WINDOW_HEIGHT - 100)

        # Create first mushroom
        self.spawn_mushroom()

    def spawn_mushroom(self):
        """Spawn a mushroom at a random platform."""
        platform = random.choice(self.platforms)
        x = platform.rect.x + random.randint(10, platform.rect.width - MUSHROOM_WIDTH - 10)
        y = platform.rect.y - MUSHROOM_HEIGHT - 50
        self.mushroom = Mushroom(x, y)

    def show_message(self, message, duration=60):
        """Show a temporary message."""
        self.current_message = message
        self.message_timer = duration

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
                            self.setup_level()
                            self.score = 0
                            self.mushrooms_lost = 0
                            self.game_over = False
                            self.won = False

            if not self.game_over:
                # Get key states
                keys = pygame.key.get_pressed()

                # Update player
                player_fell = self.player.update(keys)
                self.player.handle_platform_collision(self.platforms)

                # Update mushroom
                mushroom_fell = self.mushroom.update(self.platforms)

                # Check mushroom collision with player
                caught = False
                if self.player.rect.colliderect(self.mushroom.rect):
                    caught = True
                    self.score += SCORE_CATCH
                    self.show_message(f"+{SCORE_CATCH}!", 30)
                    self.spawn_mushroom()

                # Check if mushroom fell
                if mushroom_fell:
                    self.mushrooms_lost += 1
                    self.score += SCORE_PENALTY
                    self.show_message(f"Mushroom lost! {SCORE_PENALTY}", 60)

                    if self.mushrooms_lost >= MAX_MUSHROOMS_LOST:
                        self.game_over = True
                        self.won = False
                    else:
                        self.spawn_mushroom()

                # Check win condition
                if self.score >= WIN_SCORE:
                    self.game_over = True
                    self.won = True

                # Check if player fell
                if player_fell:
                    self.player.rect.x = 100
                    self.player.rect.y = WINDOW_HEIGHT - 100
                    self.player.vel_x = 0
                    self.player.vel_y = 0

            # Draw everything
            self.draw()

            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

    def draw(self):
        """Draw the game."""
        self.screen.fill(COLOR_BG)

        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)

        # Draw mushroom
        self.mushroom.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

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

        # Mushrooms lost
        lost_color = COLOR_WARNING if self.mushrooms_lost > 2 else COLOR_TEXT
        lost_text = self.font.render(f"Lost: {self.mushrooms_lost}/{MAX_MUSHROOMS_LOST}", True, lost_color)
        self.screen.blit(lost_text, (10, 50))

        # Goal
        goal_text = self.font.render(f"Goal: {WIN_SCORE}", True, COLOR_TEXT)
        goal_rect = goal_text.get_rect(right=WINDOW_WIDTH - 10, top=10)
        self.screen.blit(goal_text, goal_rect)

    def draw_message(self):
        """Draw temporary message."""
        msg_text = self.font.render(self.current_message, True, COLOR_SCORE)
        msg_rect = msg_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(msg_text, msg_rect)

    def draw_game_over(self):
        """Draw game over screen."""
        # Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        if self.won:
            title = "YOU WIN!"
            color = (100, 255, 100)
        else:
            title = "GAME OVER"
            color = COLOR_WARNING

        title_text = self.large_font.render(title, True, color)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(title_text, title_rect)

        score_text = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
        self.screen.blit(score_text, score_rect)

        restart_text = self.font.render("Press SPACE to restart or ESC to quit", True, COLOR_TEXT)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 70))
        self.screen.blit(restart_text, restart_rect)

    # AI Interface Methods for RL Integration

    def get_state(self):
        """Get current game state as a vector for AI input."""
        return {
            "player_pos": (self.player.rect.centerx, self.player.rect.centery),
            "player_vel": (self.player.vel_x, self.player.vel_y),
            "player_on_ground": self.player.on_ground,
            "mushroom_pos": (self.mushroom.rect.centerx, self.mushroom.rect.centery),
            "mushroom_vel": (self.mushroom.vel_x, self.mushroom.vel_y),
            "mushroom_on_ground": self.mushroom.on_ground,
            "score": self.score,
            "mushrooms_lost": self.mushrooms_lost,
        }

    def set_action(self, action):
        """Set action for AI-controlled player."""
        if len(action) >= 2:
            if action[0] < -0.3:
                self.player.vel_x = -PLAYER_SPEED
            elif action[0] > 0.3:
                self.player.vel_x = PLAYER_SPEED

            if action[1] > 0.5 and self.player.on_ground:
                self.player.jump()

    def get_reward(self):
        """Calculate reward for the current step."""
        reward = REWARD_STRUCTURE["per_step"]

        # Distance-based reward
        dist = abs(self.player.rect.centerx - self.mushroom.rect.centerx)
        if dist < 100:
            reward += REWARD_STRUCTURE["close_to_mushroom"]

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
