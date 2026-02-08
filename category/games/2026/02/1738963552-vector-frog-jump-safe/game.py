import pygame
import random
from entities import Frog, Obstacle
from config import *

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Frog Jump Safe")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()

    def reset_game(self):
        self.frog = Frog(START_X, START_Y)
        self.lanes = self.create_lanes()
        self.score = 0
        self.level = 1
        self.game_over = False
        self.won = False

    def create_lanes(self):
        lanes = []
        y = SCREEN_HEIGHT - LANE_HEIGHT - START_MARGIN

        # Create lanes from bottom to top
        for i in range(NUM_LANES):
            lane_type = "road" if i < NUM_LANES // 2 else "river"
            speed = random.choice(LANE_SPEEDS) * (1 + self.level * 0.1)
            direction = random.choice([-1, 1])
            obstacle_count = random.randint(2, 4)

            obstacles = []
            for j in range(obstacle_count):
                x = j * (SCREEN_WIDTH // obstacle_count) + random.randint(0, 50)
                width = LOG_WIDTH if lane_type == "river" else CAR_WIDTH
                obstacles.append(Obstacle(x, y, width, LANE_HEIGHT, speed * direction, lane_type))

            lanes.append({
                "type": lane_type,
                "y": y,
                "obstacles": obstacles
            })
            y -= LANE_HEIGHT

        return lanes

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.game_over or self.won:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                else:
                    if event.key == pygame.K_UP:
                        self.frog.move(0, -LANE_HEIGHT)
                    elif event.key == pygame.K_DOWN:
                        self.frog.move(0, LANE_HEIGHT)
                    elif event.key == pygame.K_LEFT:
                        self.frog.move(-GRID_SIZE, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.frog.move(GRID_SIZE, 0)
        return True

    def update(self):
        if self.game_over or self.won:
            return

        # Update obstacles
        for lane in self.lanes:
            for obstacle in lane["obstacles"]:
                obstacle.update()

        # Check if frog is out of bounds
        if (self.frog.x < 0 or self.frog.x > SCREEN_WIDTH - FROG_SIZE or
            self.frog.y < 0 or self.frog.y > SCREEN_HEIGHT - FROG_SIZE):
            self.game_over = True
            return

        # Check win condition (reached top)
        if self.frog.y <= LANE_HEIGHT:
            self.won = True
            self.score += 100
            self.level += 1
            return

        # Check lane collisions
        frog_rect = self.frog.get_rect()
        current_lane = None

        for lane in self.lanes:
            if lane["y"] <= self.frog.y < lane["y"] + LANE_HEIGHT:
                current_lane = lane
                break

        if current_lane:
            if current_lane["type"] == "road":
                # Check collision with cars
                for obstacle in current_lane["obstacles"]:
                    if frog_rect.colliderect(obstacle.get_rect()):
                        self.game_over = True
                        return
            elif current_lane["type"] == "river":
                # Must be on a log
                on_log = False
                for obstacle in current_lane["obstacles"]:
                    if frog_rect.colliderect(obstacle.get_rect()):
                        on_log = True
                        # Move with the log
                        self.frog.x += obstacle.speed
                        break
                if not on_log:
                    self.game_over = True
                    return

    def draw(self):
        # Background
        self.screen.fill(BACKGROUND_COLOR)

        # Draw lanes
        for lane in self.lanes:
            if lane["type"] == "road":
                pygame.draw.rect(self.screen, ROAD_COLOR,
                               (0, lane["y"], SCREEN_WIDTH, LANE_HEIGHT))
                # Draw lane markers
                for i in range(0, SCREEN_WIDTH, 40):
                    pygame.draw.line(self.screen, LANE_MARKER_COLOR,
                                   (i, lane["y"] + LANE_HEIGHT // 2),
                                   (i + 20, lane["y"] + LANE_HEIGHT // 2), 2)
            else:
                pygame.draw.rect(self.screen, WATER_COLOR,
                               (0, lane["y"], SCREEN_WIDTH, LANE_HEIGHT))

            # Draw obstacles
            for obstacle in lane["obstacles"]:
                obstacle.draw(self.screen)

        # Draw goal area
        pygame.draw.rect(self.screen, GRASS_COLOR,
                        (0, 0, SCREEN_WIDTH, LANE_HEIGHT))
        goal_text = self.small_font.render("GOAL", True, GOAL_TEXT_COLOR)
        self.screen.blit(goal_text, (SCREEN_WIDTH // 2 - 30, LANE_HEIGHT // 2 - 10))

        # Draw start area
        pygame.draw.rect(self.screen, GRASS_COLOR,
                        (0, SCREEN_HEIGHT - START_MARGIN, SCREEN_WIDTH, START_MARGIN))

        # Draw frog
        self.frog.draw(self.screen)

        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        level_text = self.font.render(f"Level: {self.level}", True, TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 50))

        # Draw game over or win message
        if self.game_over:
            msg = self.font.render("GAME OVER! Press SPACE to restart", True, TEXT_COLOR)
            self.screen.blit(msg, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2))
        elif self.won:
            msg = self.font.render("GOAL REACHED! Press SPACE for next level", True, TEXT_COLOR)
            self.screen.blit(msg, (SCREEN_WIDTH // 2 - 230, SCREEN_HEIGHT // 2))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
