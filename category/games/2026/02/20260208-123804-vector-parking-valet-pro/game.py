"""Main game loop and rendering."""

import pygame
import math
from config import *
from car import Car
from obstacle import Obstacle, ParkingSpot
from levels import LEVELS, load_level, get_level_count


class Game:
    """Main game class managing rendering and game loop."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Parking Valet Pro")
        self.clock = pygame.time.Clock()
        self.running = True

        self.current_level = 0
        self.game_state = "menu"  # menu, playing, paused, level_complete, game_over, victory
        self.score = 0
        self.total_score = 0

        # Fonts
        self.ui_font = pygame.font.Font(None, UI_FONT_SIZE)
        self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE)

        # Input state
        self.inputs = {'up': False, 'down': False, 'left': False, 'right': False}

        # AI training mode
        self.ai_mode = False
        self.last_ai_action = None

        self.load_level(self.current_level)

    def load_level(self, level_index):
        """Load a level by index."""
        level = load_level(level_index)
        if level is None:
            self.game_state = "victory"
            return

        self.level_data = level
        self.car = Car(*level["car_start"])
        self.parking_spot = ParkingSpot(*level["parking_spot"])

        # Create obstacle copies
        self.obstacles = [Obstacle(o.rect.x, o.rect.y, o.rect.width, o.rect.height, o.type)
                         for o in level["obstacles"]]

        self.time_remaining = level["time_limit"]
        self.start_time = pygame.time.get_ticks()
        self.last_update_time = pygame.time.get_ticks()

    def handle_input(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "playing":
                        self.game_state = "menu"
                    else:
                        self.running = False

                # Menu navigation
                if self.game_state == "menu":
                    if event.key == pygame.K_SPACE:
                        self.game_state = "playing"
                        self.load_level(self.current_level)
                    elif event.key == pygame.K_RIGHT and self.current_level < get_level_count() - 1:
                        self.current_level += 1
                        self.load_level(self.current_level)
                    elif event.key == pygame.K_LEFT and self.current_level > 0:
                        self.current_level -= 1
                        self.load_level(self.current_level)

                # Level complete
                elif self.game_state == "level_complete":
                    if event.key == pygame.K_SPACE:
                        if self.current_level < get_level_count() - 1:
                            self.current_level += 1
                            self.game_state = "playing"
                            self.load_level(self.current_level)
                        else:
                            self.game_state = "victory"

                # Game over
                elif self.game_state == "game_over":
                    if event.key == pygame.K_SPACE:
                        self.game_state = "playing"
                        self.load_level(self.current_level)

                # Victory
                elif self.game_state == "victory":
                    if event.key == pygame.K_SPACE:
                        self.current_level = 0
                        self.game_state = "menu"
                        self.load_level(self.current_level)

                # Movement keys
                if event.key == pygame.K_UP:
                    self.inputs['up'] = True
                elif event.key == pygame.K_DOWN:
                    self.inputs['down'] = True
                elif event.key == pygame.K_LEFT:
                    self.inputs['left'] = True
                elif event.key == pygame.K_RIGHT:
                    self.inputs['right'] = True

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.inputs['up'] = False
                elif event.key == pygame.K_DOWN:
                    self.inputs['down'] = False
                elif event.key == pygame.K_LEFT:
                    self.inputs['left'] = False
                elif event.key == pygame.K_RIGHT:
                    self.inputs['right'] = False

    def update(self):
        """Update game state."""
        if self.game_state != "playing":
            return

        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_update_time) / 1000.0
        self.last_update_time = current_time

        # Update timer
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.game_state = "game_over"
            return

        # Update car
        self.car.update(self.inputs)

        # Check collisions
        car_corners = self.car.get_corners()
        car_center = self.car.get_center()

        for obstacle in self.obstacles:
            if obstacle.rect.collidepoint(car_center):
                self.game_state = "game_over"
                return

        # Check boundary collision
        if (self.car.x < 20 or self.car.x > SCREEN_WIDTH - 20 or
            self.car.y < 20 or self.car.y > SCREEN_HEIGHT - 20):
            self.game_state = "game_over"
            return

        # Check parking
        is_parked, park_score = self.parking_spot.is_car_parked(self.car)
        if is_parked:
            # Calculate level score
            time_bonus = int(self.time_remaining * 10)
            distance_penalty = int(self.car.distance_traveled / 10)
            self.score = max(0, 1000 + time_bonus - distance_penalty)
            self.total_score += self.score
            self.game_state = "level_complete"

    def render(self):
        """Render the game."""
        self.screen.fill(ASPHALT)

        if self.game_state == "menu":
            self.render_menu()
        elif self.game_state == "playing":
            self.render_game()
        elif self.game_state == "level_complete":
            self.render_game()
            self.render_level_complete()
        elif self.game_state == "game_over":
            self.render_game()
            self.render_game_over()
        elif self.game_state == "victory":
            self.render_victory()

        pygame.display.flip()

    def render_game(self):
        """Render the gameplay."""
        # Draw parking spot
        self.parking_spot.draw(self.screen)

        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        # Draw car
        self.car.draw(self.screen)

        # Draw UI
        self.draw_hud()

    def draw_hud(self):
        """Draw heads-up display."""
        # Level info
        level_text = self.ui_font.render(
            f"Level {self.current_level + 1}/{get_level_count()}: {self.level_data['name']}",
            True, WHITE
        )
        self.screen.blit(level_text, (10, 10))

        # Timer
        timer_color = WHITE if self.time_remaining > 10 else RED
        timer_text = self.ui_font.render(f"Time: {self.time_remaining:.1f}s", True, timer_color)
        self.screen.blit(timer_text, (10, 40))

        # Distance traveled
        dist_text = self.ui_font.render(f"Distance: {int(self.car.distance_traveled)}", True, GRAY)
        self.screen.blit(dist_text, (10, 70))

        # Total score
        score_text = self.ui_font.render(f"Score: {self.total_score}", True, YELLOW)
        self.screen.blit(score_text, (SCREEN_WIDTH - 150, 10))

        # Controls hint
        hint_text = self.ui_font.render("ARROWS: Drive | ESC: Menu", True, GRAY)
        self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 30))

    def render_menu(self):
        """Render main menu."""
        # Preview level
        if self.level_data:
            self.parking_spot.draw(self.screen)
            for obstacle in self.obstacles:
                obstacle.draw(self.screen)
            self.car.draw(self.screen)

        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Title
        title = self.title_font.render("PARKING VALET PRO", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        # Level info
        level_name = self.ui_font.render(
            f"Level {self.current_level + 1}: {self.level_data['name']}",
            True, WHITE
        )
        level_rect = level_name.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(level_name, level_rect)

        description = self.ui_font.render(self.level_data['description'], True, GRAY)
        desc_rect = description.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(description, desc_rect)

        # Instructions
        start_text = self.ui_font.render("Press SPACE to Start", True, GREEN)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, 320))
        self.screen.blit(start_text, start_rect)

        nav_text = self.ui_font.render("Use LEFT/RIGHT to select level", True, GRAY)
        nav_rect = nav_text.get_rect(center=(SCREEN_WIDTH // 2, 360))
        self.screen.blit(nav_text, nav_rect)

        # Controls
        controls = [
            "Controls:",
            "UP - Accelerate",
            "DOWN - Brake/Reverse",
            "LEFT/RIGHT - Steer"
        ]
        for i, line in enumerate(controls):
            color = WHITE if i == 0 else GRAY
            text = self.ui_font.render(line, True, color)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - 60, 450 + i * 30))

    def render_level_complete(self):
        """Render level complete screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        complete_text = self.title_font.render("PARKED!", True, GREEN)
        complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(complete_text, complete_rect)

        score_text = self.ui_font.render(f"Score: {self.score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        total_text = self.ui_font.render(f"Total: {self.total_score}", True, WHITE)
        total_rect = total_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(total_text, total_rect)

        continue_text = self.ui_font.render("Press SPACE to continue", True, GRAY)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(continue_text, continue_rect)

    def render_game_over(self):
        """Render game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((50, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        over_text = self.title_font.render("CRASH!", True, RED)
        over_rect = over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(over_text, over_rect)

        retry_text = self.ui_font.render("Press SPACE to retry", True, GRAY)
        retry_rect = retry_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(retry_text, retry_rect)

    def render_victory(self):
        """Render victory screen."""
        self.screen.fill(ASPHALT)

        victory_text = self.title_font.render("CHAMPION!", True, YELLOW)
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(victory_text, victory_rect)

        final_text = self.ui_font.render(f"Final Score: {self.total_score}", True, WHITE)
        final_rect = final_text.get_rect(center=(SCREEN_WIDTH // 2, 260))
        self.screen.blit(final_text, final_rect)

        congrats_text = self.ui_font.render("You have mastered the art of parking!", True, GRAY)
        congrats_rect = congrats_text.get_rect(center=(SCREEN_WIDTH // 2, 320))
        self.screen.blit(congrats_text, congrats_rect)

        restart_text = self.ui_font.render("Press SPACE to play again", True, GREEN)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(restart_text, restart_rect)

    def step_ai(self, action):
        """Execute an AI action and return observation, reward, done.

        Args:
            action: dict with 'accelerate', 'brake', 'left', 'right' keys (float 0-1)

        Returns:
            (observation, reward, done)
        """
        # Convert action to input format
        self.inputs = {
            'up': action.get('accelerate', 0) > 0.5,
            'down': action.get('brake', 0) > 0.5,
            'left': action.get('left', 0) > 0.5,
            'right': action.get('right', 0) > 0.5
        }

        prev_dist = self._distance_to_target()
        prev_game_state = self.game_state

        self.update()

        # Calculate reward
        reward = 0

        if self.game_state == "level_complete":
            reward = REWARD_TARGET_REACHED
        elif self.game_state == "game_over":
            reward = REWARD_COLLISION
        else:
            # Distance progress reward
            curr_dist = self._distance_to_target()
            if curr_dist < prev_dist:
                reward += REWARD_DISTANCE_PROGRESS

            # Time penalty
            reward += REWARD_TIME_PENALTY

            # Alignment bonus
            is_parked, park_score = self.parking_spot.is_car_parked(self.car)
            if park_score > 0.8:
                reward += park_score * REWARD_ALIGNMENT / 100

        done = self.game_state in ["level_complete", "game_over"]

        return self.get_observation(), reward, done

    def _distance_to_target(self):
        """Calculate distance to parking spot."""
        dx = self.car.x - self.parking_spot.x
        dy = self.car.y - self.parking_spot.y
        return (dx ** 2 + dy ** 2) ** 0.5

    def get_observation(self):
        """Return current game state for AI."""
        # Get sensor readings
        sensors = self.car.cast_sensors(self.obstacles, self.parking_spot)

        # Calculate target info
        dx = self.parking_spot.x - self.car.x
        dy = self.parking_spot.y - self.car.y
        target_dist = (dx ** 2 + dy ** 2) ** 0.5
        target_angle = math.degrees(math.atan2(dy, dx))

        angle_to_target = target_angle - self.car.angle
        while angle_to_target > 180:
            angle_to_target -= 360
        while angle_to_target < -180:
            angle_to_target += 360

        obs = {
            "car_x": self.car.x / SCREEN_WIDTH,
            "car_y": self.car.y / SCREEN_HEIGHT,
            "car_angle": self.car.angle / 360,
            "car_speed": self.car.speed / MAX_SPEED,
            "target_dist": target_dist / 500,
            "target_angle": angle_to_target / 180,
            "sensors": sensors,
            "time_remaining": self.time_remaining / self.level_data["time_limit"],
            "game_state": self.game_state
        }

        return obs

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_input()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
