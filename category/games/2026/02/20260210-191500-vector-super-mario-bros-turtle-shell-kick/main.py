try:
    import pygame
except ImportError:
    import pygame_ce as pygame
import random
from typing import List, Optional, Tuple

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 200)
YELLOW = (255, 200, 0)
BROWN = (150, 100, 50)
ORANGE = (255, 140, 0)

# Physics
GRAVITY = 0.5
PLAYER_SPEED = 5
PLAYER_JUMP = 12
KOOPA_SPEED = 1.5
SHELL_SPEED = 10
FLOOR_Y = SCREEN_HEIGHT - 50


class Entity:
    def __init__(self, x: float, y: float, width: int, height: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.vx = 0
        self.vy = 0

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, self.get_rect())


class Player(Entity):
    def __init__(self):
        super().__init__(SCREEN_WIDTH // 2, FLOOR_Y - 40, 30, 40, RED)
        self.on_ground = True
        self.alive = True

    def update(self, keys):
        if not self.alive:
            return

        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.vx = -PLAYER_SPEED
        elif keys[pygame.K_RIGHT]:
            self.vx = PLAYER_SPEED
        else:
            self.vx = 0

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = -PLAYER_JUMP
            self.on_ground = False

        # Apply gravity
        self.vy += GRAVITY

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Boundary checks
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width

        # Ground check
        if self.y + self.height >= FLOOR_Y:
            self.y = FLOOR_Y - self.height
            self.vy = 0
            self.on_ground = True


class Koopa(Entity):
    def __init__(self, from_left: bool = True):
        x = -30 if from_left else SCREEN_WIDTH
        super().__init__(x, FLOOR_Y - 35, 25, 35, GREEN)
        self.direction = 1 if from_left else -1
        self.vx = KOOPA_SPEED * self.direction
        self.in_shell = False

    def update(self):
        if self.in_shell:
            self.vx = 0
            return

        self.x += self.vx

        # Bounce off edges
        if self.x <= 0:
            self.x = 0
            self.vx = KOOPA_SPEED
        elif self.x + self.width >= SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
            self.vx = -KOOPA_SPEED

    def to_shell(self):
        self.in_shell = True
        self.color = YELLOW
        self.height = 25
        self.y = FLOOR_Y - self.height

    def draw(self, surface: pygame.Surface):
        rect = self.get_rect()
        if self.in_shell:
            # Draw shell as oval
            pygame.draw.ellipse(surface, self.color, rect)
            pygame.draw.ellipse(surface, BROWN, rect, 2)
        else:
            # Draw koopa body
            pygame.draw.rect(surface, self.color, rect)
            # Draw eyes
            eye_y = int(self.y) + 10
            eye_x = int(self.x) + (5 if self.vx > 0 else 12)
            pygame.draw.circle(surface, WHITE, (eye_x, eye_y), 4)
            pygame.draw.circle(surface, BLACK, (eye_x + (1 if self.vx > 0 else -1), eye_y), 2)


class Shell(Entity):
    def __init__(self, x: float, y: float, direction: int):
        super().__init__(x, y, 25, 25, YELLOW)
        self.vx = SHELL_SPEED * direction
        self.kill_count = 0

    def update(self):
        self.x += self.vx

        # Bounce off edges
        if self.x <= 0:
            self.x = 0
            self.vx = SHELL_SPEED
        elif self.x + self.width >= SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
            self.vx = -SHELL_SPEED

    def draw(self, surface: pygame.Surface):
        rect = self.get_rect()
        pygame.draw.ellipse(surface, self.color, rect)
        pygame.draw.ellipse(surface, BROWN, rect, 2)
        # Show movement indication
        offset = int(pygame.time.get_ticks() / 50) % 5
        start_x = int(self.x + self.width // 2)
        start_y = int(self.y + self.height // 2)
        end_x = start_x + (5 if self.vx > 0 else -5)
        pygame.draw.line(surface, BROWN, (start_x, start_y), (end_x, start_y), 2)


class Particle:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -2)
        self.color = color
        self.life = 30
        self.size = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.life -= 1

    def draw(self, surface: pygame.Surface):
        if self.life > 0:
            alpha = min(255, self.life * 8)
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
            surface.blit(s, (int(self.x) - self.size, int(self.y) - self.size))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Turtle Shell Kick")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset()

    def reset(self):
        self.player = Player()
        self.koopas: List[Koopa] = []
        self.shells: List[Shell] = []
        self.particles: List[Particle] = []
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.spawn_timer = 0
        self.spawn_interval = 180  # frames
        self.combo_multiplier = 1

    def spawn_koopa(self):
        from_left = random.choice([True, False])
        self.koopas.append(Koopa(from_left))

    def create_particles(self, x: float, y: float, color: Tuple[int, int, int], count: int = 10):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def check_collisions(self):
        player_rect = self.player.get_rect()

        # Check koopas
        for koopa in self.koopas[:]:
            koopa_rect = koopa.get_rect()

            if koopa.in_shell:
                # Check if player kicks the shell
                if player_rect.colliderect(koopa_rect):
                    # Create shell projectile
                    direction = 1 if self.player.x + self.player.width // 2 > koopa.x + koopa.width // 2 else -1
                    shell = Shell(koopa.x, koopa.y, direction)
                    shell.kill_count = 0
                    self.shells.append(shell)
                    self.koopas.remove(koopa)
                    self.combo_multiplier = 1
                    self.create_particles(koopa.x + koopa.width // 2, koopa.y + koopa.height // 2, YELLOW)
            else:
                # Check if player stomps koopa
                if player_rect.colliderect(koopa_rect):
                    # Stomp detection: player falling onto koopa
                    if (self.player.vy > 0 and
                        self.player.y + self.player.height < koopa.y + koopa.height // 2):
                        koopa.to_shell()
                        self.player.vy = -6  # Bounce
                        self.create_particles(koopa.x + koopa.width // 2, koopa.y + koopa.height // 2, GREEN)
                    else:
                        # Player gets hit
                        self.game_over = True

        # Check shells
        for shell in self.shells[:]:
            shell_rect = shell.get_rect()

            # Check if shell hits player
            if player_rect.colliderect(shell_rect):
                self.game_over = True
                continue

            # Check if shell hits koopas
            for koopa in self.koopas[:]:
                if not koopa.in_shell and shell_rect.colliderect(koopa.get_rect()):
                    self.koopas.remove(koopa)
                    shell.kill_count += 1
                    points = 100 * (2 ** (shell.kill_count - 1))
                    self.score += points
                    self.create_particles(koopa.x + koopa.width // 2, koopa.y + koopa.height // 2, GREEN, 15)

    def update(self):
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys)

        # Update koopas
        for koopa in self.koopas:
            koopa.update()

        # Update shells
        for shell in self.shells:
            shell.update()

        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

        # Spawn new koopas
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_koopa()
            self.spawn_timer = 0
            # Gradually increase difficulty
            if self.spawn_interval > 60:
                self.spawn_interval -= 2

        self.check_collisions()

        if self.score > self.high_score:
            self.high_score = self.score

    def draw(self):
        # Background
        self.screen.fill(BLUE)

        # Draw floor
        pygame.draw.rect(self.screen, BROWN, (0, FLOOR_Y, SCREEN_WIDTH, SCREEN_HEIGHT - FLOOR_Y))
        pygame.draw.line(self.screen, GREEN, (0, FLOOR_Y), (SCREEN_WIDTH, FLOOR_Y), 3)

        # Draw entities
        for koopa in self.koopas:
            koopa.draw(self.screen)

        for shell in self.shells:
            shell.draw(self.screen)

        for particle in self.particles:
            particle.draw(self.screen)

        if self.player.alive:
            self.player.draw(self.screen)

        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        high_text = self.small_font.render(f"High: {self.high_score}", True, YELLOW)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(high_text, (10, 50))

        if self.game_over:
            over_text = self.font.render("GAME OVER", True, WHITE)
            restart_text = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)
            over_rect = over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(over_text, over_rect)
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def run(self):
        running = True

        while running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset()

            self.update()
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
