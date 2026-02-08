import pygame
import random
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

SHAPE_TYPES = ['circle', 'triangle', 'square', 'star']
SHAPE_COLORS = {
    'circle': (255, 100, 100),
    'triangle': (100, 255, 100),
    'square': (100, 100, 255),
    'star': (255, 255, 100)
}
SHAPE_SIZE = 50
BIN_WIDTH = 150
BIN_HEIGHT = 100
BIN_Y = SCREEN_HEIGHT - BIN_HEIGHT - 20
BASE_SPEED = 2
SPEED_INCREMENT = 0.2
DROP_SPEED = 15

class Shape:
    def __init__(self, shape_type, x, y):
        self.type = shape_type
        self.x = x
        self.y = y
        self.speed = BASE_SPEED
        self.falling_fast = False
        self.landed = False
        self.scored = False

    def update(self):
        speed = DROP_SPEED if self.falling_fast else self.speed
        self.y += speed
        return self.y >= BIN_Y

    def draw(self, screen):
        color = SHAPE_COLORS[self.type]
        if self.type == 'circle':
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), SHAPE_SIZE // 2)
        elif self.type == 'square':
            rect = pygame.Rect(self.x - SHAPE_SIZE // 2, self.y - SHAPE_SIZE // 2, SHAPE_SIZE, SHAPE_SIZE)
            pygame.draw.rect(screen, color, rect)
        elif self.type == 'triangle':
            points = [
                (self.x, self.y - SHAPE_SIZE // 2),
                (self.x - SHAPE_SIZE // 2, self.y + SHAPE_SIZE // 2),
                (self.x + SHAPE_SIZE // 2, self.y + SHAPE_SIZE // 2)
            ]
            pygame.draw.polygon(screen, color, points)
        elif self.type == 'star':
            self._draw_star(screen, color, self.x, self.y, 5, SHAPE_SIZE // 2, SHAPE_SIZE // 4)

    def _draw_star(self, screen, color, x, y, points, outer_radius, inner_radius):
        angle = -math.pi / 2
        step = math.pi / points
        star_points = []
        for i in range(2 * points):
            radius = outer_radius if i % 2 == 0 else inner_radius
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius
            star_points.append((px, py))
            angle += step
        pygame.draw.polygon(screen, color, star_points)

    def get_rect(self):
        return pygame.Rect(self.x - SHAPE_SIZE // 2, self.y - SHAPE_SIZE // 2, SHAPE_SIZE, SHAPE_SIZE)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Geometric Shape Sorter Pro")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.shapes = []
        self.current_shape = None
        self.bins = self._create_bins()
        self.spawn_timer = 0
        self.spawn_delay = 120
        self.game_over = False
        self.combo = 0
        self.spawn_shape()

    def _create_bins(self):
        bins = []
        bin_count = len(SHAPE_TYPES)
        spacing = SCREEN_WIDTH // bin_count
        for i, shape_type in enumerate(SHAPE_TYPES):
            x = spacing // 2 + i * spacing
            bins.append({'type': shape_type, 'x': x, 'y': BIN_Y})
        return bins

    def spawn_shape(self):
        shape_type = random.choice(SHAPE_TYPES)
        x = random.randint(SHAPE_SIZE, SCREEN_WIDTH - SHAPE_SIZE)
        self.current_shape = Shape(shape_type, x, 50)
        self.current_shape.speed = BASE_SPEED + (self.level - 1) * SPEED_INCREMENT

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                else:
                    if event.key == pygame.K_SPACE:
                        self.current_shape.falling_fast = True
        return True

    def update(self):
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.current_shape.x -= 7
        if keys[pygame.K_RIGHT]:
            self.current_shape.x += 7

        self.current_shape.x = max(SHAPE_SIZE // 2, min(SCREEN_WIDTH - SHAPE_SIZE // 2, self.current_shape.x))

        landed = self.current_shape.update()

        if landed:
            self._check_collision()
            if not self.current_shape.scored and not self.game_over:
                self.lives -= 1
                self.combo = 0
                if self.lives <= 0:
                    self.game_over = True
            self.spawn_shape()

    def _check_collision(self):
        shape_rect = self.current_shape.get_rect()
        for bin_obj in self.bins:
            bin_rect = pygame.Rect(bin_obj['x'] - BIN_WIDTH // 2, bin_obj['y'], BIN_WIDTH, BIN_HEIGHT)
            if shape_rect.colliderect(bin_rect):
                if bin_obj['type'] == self.current_shape.type:
                    self.score += 10 + self.combo * 5
                    self.combo += 1
                    self.current_shape.scored = True

                    if self.combo > 0 and self.combo % 5 == 0:
                        self.level += 1
                break

    def draw_bin(self, bin_obj):
        x = bin_obj['x']
        y = bin_obj['y']
        shape_type = bin_obj['type']

        rect = pygame.Rect(x - BIN_WIDTH // 2, y, BIN_WIDTH, BIN_HEIGHT)
        pygame.draw.rect(self.screen, (80, 80, 80), rect)
        pygame.draw.rect(self.screen, (150, 150, 150), rect, 3)

        color = (60, 60, 60)
        if shape_type == 'circle':
            pygame.draw.circle(self.screen, color, (x, y + BIN_HEIGHT // 2), SHAPE_SIZE // 2, 3)
        elif shape_type == 'square':
            rect = pygame.Rect(x - SHAPE_SIZE // 2, y + BIN_HEIGHT // 2 - SHAPE_SIZE // 2, SHAPE_SIZE, SHAPE_SIZE)
            pygame.draw.rect(self.screen, color, rect, 3)
        elif shape_type == 'triangle':
            points = [
                (x, y + BIN_HEIGHT // 2 - SHAPE_SIZE // 2),
                (x - SHAPE_SIZE // 2, y + BIN_HEIGHT // 2 + SHAPE_SIZE // 2),
                (x + SHAPE_SIZE // 2, y + BIN_HEIGHT // 2 + SHAPE_SIZE // 2)
            ]
            pygame.draw.polygon(self.screen, color, points, 3)
        elif shape_type == 'star':
            self._draw_star_outline(self.screen, color, x, y + BIN_HEIGHT // 2, 5, SHAPE_SIZE // 2, SHAPE_SIZE // 4)

    def _draw_star_outline(self, screen, color, x, y, points, outer_radius, inner_radius):
        angle = -math.pi / 2
        step = math.pi / points
        star_points = []
        for i in range(2 * points):
            radius = outer_radius if i % 2 == 0 else inner_radius
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius
            star_points.append((px, py))
            angle += step
        pygame.draw.polygon(screen, color, star_points, 3)

    def draw(self):
        self.screen.fill((30, 30, 40))

        for bin_obj in self.bins:
            self.draw_bin(bin_obj)

        if self.current_shape:
            self.current_shape.draw(self.screen)

        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        lives_text = self.font.render(f"Lives: {self.lives}", True, (255, 100, 100))
        level_text = self.font.render(f"Level: {self.level}", True, (100, 200, 255))

        if self.combo > 1:
            combo_text = self.font.render(f"Combo: {self.combo}x", True, (255, 255, 100))
            self.screen.blit(combo_text, (SCREEN_WIDTH // 2 - combo_text.get_width() // 2, 10))

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))
        self.screen.blit(level_text, (SCREEN_WIDTH - level_text.get_width() - 10, 10))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.large_font.render("GAME OVER", True, (255, 100, 100))
            final_score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            restart_text = self.font.render("Press R to Restart", True, (150, 150, 150))

            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
