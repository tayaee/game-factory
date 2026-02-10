"""Main game logic for Vector Ice Hockey Slapshot."""

import pygame
import math
from config import *


class Vector2:
    """Simple 2D vector class for physics calculations."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def distance_to(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def to_tuple(self):
        return (self.x, self.y)


class Player:
    """Represents a hockey player."""

    def __init__(self, x, y, color, is_left_side):
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.color = color
        self.is_left_side = is_left_side
        self.slapshot_cooldown = 0

    def update(self, keys, up_key, down_key, left_key, right_key, slapshot_key):
        # Movement input
        accel = Vector2(0, 0)
        if keys[up_key]:
            accel.y -= 1
        if keys[down_key]:
            accel.y += 1
        if keys[left_key]:
            accel.x -= 1
        if keys[right_key]:
            accel.x += 1

        # Normalize acceleration
        if accel.magnitude() > 0:
            accel = accel.normalize() * 0.5

        # Apply acceleration
        self.vel = self.vel + accel

        # Limit speed
        if self.vel.magnitude() > PLAYER_SPEED:
            self.vel = self.vel.normalize() * PLAYER_SPEED

        # Apply friction
        self.vel = self.vel * PLAYER_FRICTION

        # Update position
        self.pos = self.pos + self.vel

        # Rink boundaries
        half_width = WINDOW_WIDTH / 2
        if self.is_left_side:
            # Left side player
            self.pos.x = max(RINK_MARGIN + PLAYER_RADIUS, min(half_width - PLAYER_RADIUS, self.pos.x))
        else:
            # Right side player
            self.pos.x = max(half_width + PLAYER_RADIUS, min(WINDOW_WIDTH - RINK_MARGIN - PLAYER_RADIUS, self.pos.x))

        self.pos.y = max(RINK_MARGIN + PLAYER_RADIUS, min(WINDOW_HEIGHT - RINK_MARGIN - PLAYER_RADIUS, self.pos.y))

        # Update cooldown
        if self.slapshot_cooldown > 0:
            self.slapshot_cooldown -= 1

        return keys[slapshot_key] and self.slapshot_cooldown == 0

    def do_slapshot(self):
        self.slapshot_cooldown = SLAPSHOT_COOLDOWN

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), PLAYER_RADIUS)
        # Draw direction indicator
        if self.vel.magnitude() > 0.1:
            end_pos = self.pos + self.vel.normalize() * (PLAYER_RADIUS + 5)
            pygame.draw.line(surface, (0, 0, 0), self.pos.to_tuple(), end_pos.to_tuple(), 2)

        # Draw cooldown indicator
        if self.slapshot_cooldown > 0:
            ratio = self.slapshot_cooldown / SLAPSHOT_COOLDOWN
            arc_rect = (
                int(self.pos.x - PLAYER_RADIUS - 3),
                int(self.pos.y - PLAYER_RADIUS - 3),
                int(PLAYER_RADIUS * 2 + 6),
                int(PLAYER_RADIUS * 2 + 6)
            )
            pygame.draw.arc(surface, (255, 255, 0), arc_rect, 0, ratio * 6.28, 3)


class Puck:
    """Represents the hockey puck."""

    def __init__(self, x, y):
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)

    def update(self):
        # Apply velocity
        self.pos = self.pos + self.vel

        # Apply friction (very low for ice)
        self.vel = self.vel * PUCK_FRICTION

        # Wall collisions (top and bottom)
        if self.pos.y - PUCK_RADIUS < RINK_MARGIN:
            self.pos.y = RINK_MARGIN + PUCK_RADIUS
            self.vel.y *= -1
        elif self.pos.y + PUCK_RADIUS > WINDOW_HEIGHT - RINK_MARGIN:
            self.pos.y = WINDOW_HEIGHT - RINK_MARGIN - PUCK_RADIUS
            self.vel.y *= -1

        # Wall collisions (left and right - bounce except in goal area)
        goal_top = (WINDOW_HEIGHT - GOAL_WIDTH) / 2
        goal_bottom = (WINDOW_HEIGHT + GOAL_WIDTH) / 2

        # Left wall
        if self.pos.x - PUCK_RADIUS < RINK_MARGIN:
            if not (goal_top < self.pos.y < goal_bottom):
                self.pos.x = RINK_MARGIN + PUCK_RADIUS
                self.vel.x *= -1

        # Right wall
        if self.pos.x + PUCK_RADIUS > WINDOW_WIDTH - RINK_MARGIN:
            if not (goal_top < self.pos.y < goal_bottom):
                self.pos.x = WINDOW_WIDTH - RINK_MARGIN - PUCK_RADIUS
                self.vel.x *= -1

        # Limit speed
        if self.vel.magnitude() > PUCK_MAX_SPEED:
            self.vel = self.vel.normalize() * PUCK_MAX_SPEED

    def draw(self, surface):
        pygame.draw.circle(surface, COLOR_PUCK, (int(self.pos.x), int(self.pos.y)), PUCK_RADIUS)
        # Draw highlight
        pygame.draw.circle(surface, (80, 80, 80), (int(self.pos.x - 3), int(self.pos.y - 3)), PUCK_RADIUS // 3)

    def reset(self):
        self.pos = Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.vel = Vector2(0, 0)


class Game:
    """Main game class for Vector Ice Hockey Slapshot."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Vector Ice Hockey Slapshot")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)

        # Initialize entities
        self.player1 = Player(150, WINDOW_HEIGHT / 2, COLOR_P1, True)
        self.player2 = Player(WINDOW_WIDTH - 150, WINDOW_HEIGHT / 2, COLOR_P2, False)
        self.puck = Puck(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)

        # Game state
        self.p1_score = 0
        self.p2_score = 0
        self.goal_reset_timer = 0
        self.winner = None
        self.running = True

    def handle_collisions(self):
        """Handle player-puck collisions with elastic collision physics."""
        for player in [self.player1, self.player2]:
            dist = player.pos.distance_to(self.puck.pos)
            min_dist = PLAYER_RADIUS + PUCK_RADIUS

            if dist < min_dist:
                # Collision detected
                normal = (self.puck.pos - player.pos).normalize()

                # Separate puck from player
                overlap = min_dist - dist
                self.puck.pos = self.puck.pos + normal * overlap

                # Transfer momentum (elastic collision)
                relative_vel = self.puck.vel - player.vel
                vel_along_normal = relative_vel.dot(normal)

                if vel_along_normal < 0:
                    # Only resolve if objects are moving towards each other
                    restitution = 0.9  # Bounciness
                    impulse = -(1 + restitution) * vel_along_normal
                    self.puck.vel = self.puck.vel + normal * impulse

                return True  # Puck contact
        return False

    def check_goals(self):
        """Check if a goal has been scored."""
        goal_top = (WINDOW_HEIGHT - GOAL_WIDTH) / 2
        goal_bottom = (WINDOW_HEIGHT + GOAL_WIDTH) / 2

        # Left goal (Player 2 scores)
        if self.puck.pos.x < RINK_MARGIN and goal_top < self.puck.pos.y < goal_bottom:
            self.p2_score += 1
            self.goal_reset_timer = GOAL_RESET_DELAY
            if self.p2_score >= WINNING_SCORE:
                self.winner = "Player 2 (Red)"
            return "p2"

        # Right goal (Player 1 scores)
        if self.puck.pos.x > WINDOW_WIDTH - RINK_MARGIN and goal_top < self.puck.pos.y < goal_bottom:
            self.p1_score += 1
            self.goal_reset_timer = GOAL_RESET_DELAY
            if self.p1_score >= WINNING_SCORE:
                self.winner = "Player 1 (Blue)"
            return "p1"

        return None

    def draw_rink(self):
        """Draw the hockey rink."""
        self.screen.fill(COLOR_BG)

        # Draw rink border
        border_rect = (
            RINK_MARGIN,
            RINK_MARGIN,
            WINDOW_WIDTH - 2 * RINK_MARGIN,
            WINDOW_HEIGHT - 2 * RINK_MARGIN
        )
        pygame.draw.rect(self.screen, COLOR_RINK_BORDER, border_rect, 3)

        # Draw center line
        pygame.draw.line(
            self.screen,
            COLOR_CENTER_LINE,
            (WINDOW_WIDTH / 2, RINK_MARGIN),
            (WINDOW_WIDTH / 2, WINDOW_HEIGHT - RINK_MARGIN),
            3
        )

        # Draw center circle
        pygame.draw.circle(
            self.screen,
            COLOR_CENTER_LINE,
            (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2),
            50,
            3
        )

        # Draw goal areas
        goal_top = (WINDOW_HEIGHT - GOAL_WIDTH) / 2
        goal_bottom = (WINDOW_HEIGHT + GOAL_WIDTH) / 2

        # Left goal
        pygame.draw.rect(
            self.screen,
            COLOR_GOAL_LINE,
            (RINK_MARGIN - GOAL_DEPTH, goal_top, GOAL_DEPTH, GOAL_WIDTH),
            3
        )

        # Right goal
        pygame.draw.rect(
            self.screen,
            COLOR_GOAL_LINE,
            (WINDOW_WIDTH - RINK_MARGIN, goal_top, GOAL_DEPTH, GOAL_WIDTH),
            3
        )

    def draw_scores(self):
        """Draw the score display."""
        score_text = self.font.render(f"{self.p1_score} - {self.p2_score}", True, COLOR_TEXT)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH / 2, 30))
        self.screen.blit(score_text, score_rect)

    def draw_goal_message(self):
        """Draw goal score message."""
        goal_text = self.large_font.render("GOAL!", True, (255, 100, 0))
        text_rect = goal_text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 50))
        self.screen.blit(goal_text, text_rect)

    def draw_win_message(self):
        """Draw win message."""
        win_text = self.large_font.render(f"{self.winner} WINS!", True, (0, 150, 0))
        text_rect = win_text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.screen.blit(win_text, text_rect)

        restart_text = self.font.render("Press SPACE to restart or ESC to quit", True, COLOR_TEXT)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 60))
        self.screen.blit(restart_text, restart_rect)

    def reset_game(self):
        """Reset the game to initial state."""
        self.p1_score = 0
        self.p2_score = 0
        self.winner = None
        self.player1.pos = Vector2(150, WINDOW_HEIGHT / 2)
        self.player1.vel = Vector2(0, 0)
        self.player2.pos = Vector2(WINDOW_WIDTH - 150, WINDOW_HEIGHT / 2)
        self.player2.vel = Vector2(0, 0)
        self.puck.reset()

    def reset_positions(self):
        """Reset player and puck positions after goal."""
        self.player1.pos = Vector2(150, WINDOW_HEIGHT / 2)
        self.player1.vel = Vector2(0, 0)
        self.player2.pos = Vector2(WINDOW_WIDTH - 150, WINDOW_HEIGHT / 2)
        self.player2.vel = Vector2(0, 0)
        self.puck.reset()

    def handle_slapshot(self, player, direction):
        """Handle slapshot burst."""
        if player.slapshot_cooldown == 0:
            # Check if puck is in range
            dist = player.pos.distance_to(self.puck.pos)
            if dist < SLAPSHOT_RANGE:
                # Apply burst force to puck
                to_puck = (self.puck.pos - player.pos).normalize()
                self.puck.vel = self.puck.vel + to_puck * SLAPSHOT_FORCE
            player.do_slapshot()

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
                    elif self.winner and event.key == pygame.K_SPACE:
                        self.reset_game()

            if not self.winner:
                # Get key states
                keys = pygame.key.get_pressed()

                # Update Player 1 (Arrow keys + Space)
                p1_slapshot = self.player1.update(
                    keys, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE
                )
                if p1_slapshot:
                    self.handle_slapshot(self.player1, 1)

                # Update Player 2 (WASD + Shift)
                p2_slapshot = self.player2.update(
                    keys, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_LSHIFT
                )
                if p2_slapshot:
                    self.handle_slapshot(self.player2, -1)

                # Update puck
                self.puck.update()

                # Handle collisions
                self.handle_collisions()

                # Check for goals
                scorer = self.check_goals()

                # Handle goal reset
                if self.goal_reset_timer > 0:
                    self.goal_reset_timer -= 1
                    if self.goal_reset_timer == 0:
                        self.reset_positions()

            # Draw everything
            self.draw_rink()
            self.player1.draw(self.screen)
            self.player2.draw(self.screen)
            self.puck.draw(self.screen)
            self.draw_scores()

            if self.goal_reset_timer > 0:
                self.draw_goal_message()

            if self.winner:
                self.draw_win_message()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

    # AI Interface Methods for RL Integration

    def get_state(self):
        """Get current game state as a vector for AI input."""
        return {
            "player1_pos": (self.player1.pos.x, self.player1.pos.y),
            "player1_vel": (self.player1.vel.x, self.player1.vel.y),
            "player2_pos": (self.player2.pos.x, self.player2.pos.y),
            "player2_vel": (self.player2.vel.x, self.player2.vel.y),
            "puck_pos": (self.puck.pos.x, self.puck.pos.y),
            "puck_vel": (self.puck.vel.x, self.puck.vel.y),
            "scores": (self.p1_score, self.p2_score),
        }

    def set_action(self, player_id, action):
        """Set action for AI-controlled player."""
        player = self.player1 if player_id == 1 else self.player2
        if len(action) >= 2:
            player.vel.x = max(-PLAYER_SPEED, min(PLAYER_SPEED, action[0]))
            player.vel.y = max(-PLAYER_SPEED, min(PLAYER_SPEED, action[1]))
        if len(action) >= 3 and action[2] > 0.5:
            self.handle_slapshot(player, 1 if player_id == 1 else -1)

    def get_reward(self, player_id):
        """Calculate reward for the given player."""
        reward = -0.01  # Per step penalty
        if player_id == 1:
            reward += self.p1_score * REWARD_STRUCTURE["goal_scored"]
            reward += self.p2_score * REWARD_STRUCTURE["goal_conceded"]
        else:
            reward += self.p2_score * REWARD_STRUCTURE["goal_scored"]
            reward += self.p1_score * REWARD_STRUCTURE["goal_conceded"]
        return reward

    def is_done(self):
        """Check if the game is over."""
        return self.winner is not None


def main():
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
