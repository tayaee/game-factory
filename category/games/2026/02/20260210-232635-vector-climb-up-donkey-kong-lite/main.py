import pygame
import random
from enum import Enum


class Direction(Enum):
    LEFT = -1
    RIGHT = 1
    NONE = 0


class GameState(Enum):
    PLAYING = 0
    GAME_OVER = 1
    VICTORY = 2


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 32
        self.vx = 0
        self.vy = 0
        self.speed = 3
        self.climb_speed = 2
        self.jump_power = -10
        self.gravity = 0.4
        self.on_ground = False
        self.on_ladder = False
        self.is_jumping = False
        self.facing_right = True
        self.color = (0, 255, 128)

    def update(self, keys, platforms, ladders, goal_area):
        self.on_ladder = False
        self.on_ground = False

        for ladder in ladders:
            if (self.x + self.width / 2 >= ladder.x and
                self.x + self.width / 2 <= ladder.x + ladder.width and
                self.y >= ladder.y and
                self.y + self.height <= ladder.y + ladder.height):
                self.on_ladder = True
                break

        if self.on_ladder:
            self.vy = 0
            if keys[pygame.K_UP]:
                self.vy = -self.climb_speed
            elif keys[pygame.K_DOWN]:
                self.vy = self.climb_speed
        else:
            self.vx = 0
            if keys[pygame.K_LEFT]:
                self.vx = -self.speed
                self.facing_right = False
            if keys[pygame.K_RIGHT]:
                self.vx = self.speed
                self.facing_right = True

            if not self.is_jumping:
                for platform in platforms:
                    if (self.y + self.height >= platform.y and
                        self.y + self.height <= platform.y + 10 and
                        self.x + self.width > platform.x and
                        self.x < platform.x + platform.width):
                        self.on_ground = True
                        self.vy = 0
                        break

                if not self.on_ground:
                    self.vy += self.gravity
            else:
                self.vy += self.gravity

        self.x += self.vx
        self.y += self.vy

        self.x = max(0, min(self.x, 800 - self.width))
        self.y = max(0, min(self.y, 600 - self.height))

    def jump(self):
        if self.on_ground and not self.is_jumping:
            self.is_jumping = True
            self.vy = self.jump_power
            self.on_ground = False

    def land(self):
        self.is_jumping = False
        self.vy = 0

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

        eye_x = self.x + (self.width - 6) if self.facing_right else self.x + 2
        pygame.draw.rect(surface, (0, 0, 0), (eye_x, self.y + 6, 4, 4))

        pygame.draw.rect(surface, (0, 0, 0), (self.x + 4, self.y + self.height - 8, 6, 4))
        pygame.draw.rect(surface, (0, 0, 0), (self.x + self.width - 10, self.y + self.height - 8, 6, 4))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Barrel:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.vx = 2
        self.vy = 0
        self.gravity = 0.3
        self.falling = False
        self.color = (255, 100, 50)

    def update(self, platforms):
        self.vy += self.gravity

        next_y = self.y + self.vy
        next_x = self.x + self.vx

        on_platform = False
        for platform in platforms:
            if (self.y + self.height >= platform.y and
                self.y + self.height <= platform.y + 15 and
                self.x + self.width > platform.x and
                self.x < platform.x + platform.width):

                if self.vy > 0:
                    self.y = platform.y - self.height
                    self.vy = 0
                    on_platform = True
                    self.falling = False
                break

        if on_platform and not self.falling:
            at_edge = True
            for platform in platforms:
                if (self.y + self.height >= platform.y - 5 and
                    self.y + self.height <= platform.y + 10):
                    if self.vx > 0:
                        if self.x + self.width + 5 < platform.x + platform.width:
                            at_edge = False
                    else:
                        if self.x - 5 > platform.x:
                            at_edge = False
                    break

            if at_edge:
                self.falling = True
            else:
                self.x += self.vx
        else:
            self.y += self.vy
            self.x += self.vx

        if self.x < 0:
            self.x = 0
            self.vx = -self.vx
        if self.x > 800 - self.width:
            self.x = 800 - self.width
            self.vx = -self.vx

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x + self.width/2), int(self.y + self.height/2)), self.width // 2)
        pygame.draw.circle(surface, (200, 50, 0), (int(self.x + self.width/2 - 3), int(self.y + self.height/2 - 3)), 4)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Platform:
    def __init__(self, x, y, width):
        self.x = x
        self.y = y
        self.width = width
        self.height = 12
        self.color = (100, 100, 120)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        for i in range(0, self.width, 20):
            pygame.draw.line(surface, (80, 80, 100), (self.x + i, self.y), (self.x + i, self.y + self.height), 1)


class Ladder:
    def __init__(self, x, y, height):
        self.x = x
        self.y = y
        self.width = 24
        self.height = height
        self.color = (139, 90, 43)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x + 2, self.y, 4, self.height))
        pygame.draw.rect(surface, self.color, (self.x + self.width - 6, self.y, 4, self.height))

        for i in range(0, self.height, 16):
            pygame.draw.rect(surface, self.color, (self.x + 2, self.y + i, self.width - 4, 4))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Vector Climb Up - Donkey Kong Lite")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        self.player = Player(50, 520)
        self.barrels = []
        self.barrel_timer = 0
        self.barrel_spawn_delay = 180
        self.score = 0
        self.barrels_jumped = 0
        self.game_state = GameState.PLAYING

        self.platforms = [
            Platform(0, 550, 800),
            Platform(0, 420, 800),
            Platform(0, 290, 800),
            Platform(0, 160, 800),
            Platform(550, 30, 250),
        ]

        self.ladders = [
            Ladder(150, 420, 130),
            Ladder(400, 290, 130),
            Ladder(650, 160, 130),
            Ladder(100, 30, 130),
            Ladder(350, 30, 130),
        ]

        self.goal_area = pygame.Rect(600, 30, 200, 50)

        self.donkey_kong_x = 720
        self.donkey_kong_y = 50

    def spawn_barrel(self):
        barrel = Barrel(self.donkey_kong_x, self.donkey_kong_y + 30)
        barrel.vx = -2
        self.barrels.append(barrel)

    def update(self):
        if self.game_state != GameState.PLAYING:
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys, self.platforms, self.ladders, self.goal_area)

        self.barrel_timer += 1
        if self.barrel_timer >= self.barrel_spawn_delay:
            self.spawn_barrel()
            self.barrel_timer = 0

        for barrel in self.barrels[:]:
            barrel.update(self.platforms)

            if barrel.get_rect().colliderect(self.player.get_rect()):
                self.game_state = GameState.GAME_OVER

            if barrel.y > 650:
                self.barrels.remove(barrel)

        if self.goal_area.contains(self.player.get_rect()):
            self.game_state = GameState.VICTORY
            self.score += 500

        if self.player.is_jumping and self.player.vy > 0:
            for barrel in self.barrels:
                if (self.player.y + self.player.height - 10 <= barrel.y + barrel.height / 2 and
                    self.player.x + self.player.width > barrel.x and
                    self.player.x < barrel.x + barrel.width and
                    barrel.y > self.player.y):
                    self.barrels_jumped += 1
                    self.score += 10

    def draw(self):
        self.screen.fill((20, 20, 30))

        for platform in self.platforms:
            platform.draw(self.screen)

        for ladder in self.ladders:
            ladder.draw(self.screen)

        pygame.draw.rect(self.screen, (50, 200, 100), self.goal_area)
        goal_text = self.small_font.render("GOAL", True, (255, 255, 255))
        self.screen.blit(goal_text, (self.goal_area.x + 70, self.goal_area.y + 15))

        pygame.draw.rect(self.screen, (139, 69, 19), (self.donkey_kong_x, self.donkey_kong_y, 50, 40))
        pygame.draw.circle(self.screen, (50, 50, 50), (int(self.donkey_kong_x + 25), int(self.donkey_kong_y + 15)), 15)

        for barrel in self.barrels:
            barrel.draw(self.screen)

        self.player.draw(self.screen)

        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

        jumps_text = self.small_font.render(f"Barrels Jumped: {self.barrels_jumped}", True, (200, 200, 200))
        self.screen.blit(jumps_text, (10, 50))

        if self.game_state == GameState.GAME_OVER:
            overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font.render("GAME OVER", True, (255, 50, 50))
            self.screen.blit(game_over_text, (800//2 - game_over_text.get_width()//2, 250))

            restart_text = self.small_font.render("Press SPACE to restart", True, (255, 255, 255))
            self.screen.blit(restart_text, (800//2 - restart_text.get_width()//2, 300))

        elif self.game_state == GameState.VICTORY:
            overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            victory_text = self.font.render("VICTORY!", True, (50, 255, 50))
            self.screen.blit(victory_text, (800//2 - victory_text.get_width()//2, 250))

            score_final_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_final_text, (800//2 - score_final_text.get_width()//2, 300))

            restart_text = self.small_font.render("Press SPACE to restart", True, (255, 255, 255))
            self.screen.blit(restart_text, (800//2 - restart_text.get_width()//2, 350))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        if self.game_state == GameState.PLAYING:
                            self.player.jump()
                        else:
                            self.reset_game()

            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
