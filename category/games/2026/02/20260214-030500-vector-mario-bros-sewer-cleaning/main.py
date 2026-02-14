import pygame
import sys
import random
from enum import Enum


class Direction(Enum):
    LEFT = -1
    RIGHT = 1


class EntityType(Enum):
    SHELLCREEPER = 0
    SIDESTEPPER = 1


class GameState(Enum):
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    WIN = 3


class Entity:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.vx = 0
        self.vy = 0
        self.on_ground = False

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.get_rect())


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 24, 32, (255, 100, 100))
        self.speed = 3
        self.jump_power = -11
        self.gravity = 0.5
        self.lives = 3
        self.score = 0
        self.invincible = 0
        self.direction = Direction.RIGHT

    def update(self, keys, platforms, screen_width):
        self.vx = 0
        if keys[pygame.K_LEFT]:
            self.vx = -self.speed
            self.direction = Direction.LEFT
        if keys[pygame.K_RIGHT]:
            self.vx = self.speed
            self.direction = Direction.RIGHT
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False

        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

        # Screen wrap
        if self.x < -self.width:
            self.x = screen_width
        elif self.x > screen_width:
            self.x = -self.width

        self.on_ground = False
        for plat in platforms:
            if self.get_rect().colliderect(plat):
                if self.vy > 0 and self.y + self.height - self.vy <= plat.top:
                    self.y = plat.top - self.height
                    self.vy = 0
                    self.on_ground = True

        if self.invincible > 0:
            self.invincible -= 1

    def draw(self, surface):
        if self.invincible > 0 and self.invincible % 10 < 5:
            return
        rect = self.get_rect()
        pygame.draw.rect(surface, self.color, rect)
        # Eyes
        eye_offset = 4 if self.direction == Direction.RIGHT else 12
        pygame.draw.rect(surface, (255, 255, 255), (rect.x + eye_offset, rect.y + 6, 8, 6))
        pygame.draw.rect(surface, (0, 0, 0), (rect.x + eye_offset + 4, rect.y + 7, 3, 3))


class Enemy(Entity):
    def __init__(self, x, y, entity_type):
        color = (100, 200, 100) if entity_type == EntityType.SHELLCREEPER else (200, 100, 200)
        super().__init__(x, y, 24, 24, color)
        self.entity_type = entity_type
        self.speed = 1.0
        self.hits_required = 2 if entity_type == EntityType.SIDESTEPPER else 1
        self.current_hits = 0
        self.stunned = False
        self.stun_timer = 0
        self.direction = Direction.RIGHT
        self.platform = None
        self.falling = True

    def update(self, platforms, screen_width):
        if self.falling:
            self.vy += 0.3
            self.y += self.vy
            for plat in platforms:
                if self.get_rect().colliderect(plat) and self.vy > 0:
                    if self.y + self.height - self.vy <= plat.top + 5:
                        self.y = plat.top - self.height
                        self.vy = 0
                        self.falling = False
                        self.platform = plat
                        break
            return

        if self.stunned:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.stunned = False
                self.current_hits = 0
                self.speed = min(self.speed * 1.2, 2.5)
            return

        self.x += self.speed * self.direction.value

        # Check platform edges
        if self.platform:
            if self.x + self.width < self.platform.left:
                self.direction = Direction.RIGHT
            elif self.x > self.platform.right:
                self.direction = Direction.LEFT

        # Screen wrap
        if self.x < -self.width:
            self.x = screen_width
        elif self.x > screen_width:
            self.x = -self.width

    def hit_from_below(self):
        if not self.stunned:
            self.current_hits += 1
            if self.current_hits >= self.hits_required:
                self.stunned = True
                self.stun_timer = 300
                return True
        return False

    def kick(self):
        if self.stunned:
            self.stunned = False
            self.current_hits = 0
            return True
        return False

    def draw(self, surface):
        rect = self.get_rect()
        if self.stunned:
            # Draw upside down stunned enemy
            pygame.draw.rect(surface, (200, 200, 200), rect)
            # Legs up
            pygame.draw.rect(surface, self.color, (rect.x + 2, rect.y - 6, 6, 8))
            pygame.draw.rect(surface, self.color, (rect.x + 16, rect.y - 6, 6, 8))
        else:
            pygame.draw.rect(surface, self.color, rect)
            # Eyes
            eye_offset = 4 if self.direction == Direction.RIGHT else 12
            pygame.draw.rect(surface, (255, 255, 255), (rect.x + eye_offset, rect.y + 4, 6, 6))
            pygame.draw.rect(surface, (0, 0, 0), (rect.x + eye_offset + 2, rect.y + 5, 3, 3))


class Coin(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 16, 16, (255, 215, 0))
        self.vy = -4
        self.lifetime = 60

    def update(self):
        self.vy += 0.2
        self.y += self.vy
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, surface):
        rect = self.get_rect()
        pygame.draw.circle(surface, self.color, rect.center, 8)
        pygame.draw.circle(surface, (200, 150, 0), rect.center, 5)


class POWBlock(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 64, 32, (255, 200, 0))
        self.active = True
        self.flash_timer = 0

    def hit(self):
        if self.active:
            self.flash_timer = 10
            return True
        return False

    def draw(self, surface):
        if not self.active:
            return
        color = self.color if self.flash_timer == 0 else (255, 255, 255)
        pygame.draw.rect(surface, color, self.get_rect())
        pygame.draw.rect(surface, (0, 0, 0), self.get_rect(), 2)
        font = pygame.font.Font(None, 24)
        text = font.render("POW", True, (0, 0, 0))
        surface.blit(text, (self.x + 15, self.y + 5))
        if self.flash_timer > 0:
            self.flash_timer -= 1


class Game:
    def __init__(self):
        pygame.init()
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Mario Bros - Sewer Cleaning")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.state = GameState.MENU
        self.reset_level()

    def reset_level(self):
        self.player = Player(400, 300)
        self.enemies = []
        self.coins = []
        self.platforms = []
        self.pipes = []
        self.pow_block = POWBlock(368, 480)
        self.wave = 1
        self.create_level()

    def create_level(self):
        self.platforms = []
        self.enemies = []
        self.coins = []

        # Floor
        self.platforms.append(pygame.Rect(0, 550, self.SCREEN_WIDTH, 50))

        # Platforms (classic 4-tier layout)
        tier_configs = [
            (0, 400, 200), (300, 400, 200), (600, 400, 200),      # Tier 1
            (100, 300, 150), (400, 300, 150), (650, 300, 150),    # Tier 2
            (0, 200, 250), (550, 200, 250),                       # Tier 3
            (200, 120, 400),                                       # Tier 4
        ]

        for x, y, w in tier_configs:
            self.platforms.append(pygame.Rect(x, y, w, 16))

        # Pipes
        pipe_y = 550
        self.pipes = [pygame.Rect(20, pipe_y - 60, 48, 60), pygame.Rect(self.SCREEN_WIDTH - 68, pipe_y - 60, 48, 60)]

        # Spawn enemies based on wave
        num_enemies = 2 + self.wave
        for i in range(num_enemies):
            entity_type = EntityType.SIDESTEPPER if i % 3 == 0 else EntityType.SHELLCREEPER
            enemy = Enemy(50 + i * 100, 100, entity_type)
            self.enemies.append(enemy)

    def spawn_coin(self, x, y):
        self.coins.append(Coin(x, y))

    def activate_pow(self):
        if self.pow_block.hit():
            for enemy in self.enemies:
                if not enemy.falling and not enemy.stunned:
                    enemy.hit_from_below()

    def check_collisions(self):
        player_rect = self.player.get_rect()

        # Player vs Enemies
        for enemy in self.enemies[:]:
            enemy_rect = enemy.get_rect()

            # Check if player hits enemy from below
            if (self.player.vy < 0 and
                player_rect.bottom <= enemy_rect.bottom and
                player_rect.top > enemy_rect.top and
                player_rect.colliderect(enemy_rect)):
                if enemy.hit_from_below():
                    self.player.score += 10
                    self.player.vy = 2
                continue

            # Check if player touches enemy
            if player_rect.colliderect(enemy_rect):
                if enemy.stunned:
                    # Kick the enemy
                    if enemy.kick():
                        self.player.score += 500
                        self.enemies.remove(enemy)
                else:
                    # Player hurt
                    if self.player.invincible == 0:
                        self.player.lives -= 1
                        self.player.invincible = 120
                        if self.player.lives <= 0:
                            self.state = GameState.GAME_OVER

        # Player vs Coins
        for coin in self.coins[:]:
            if player_rect.colliderect(coin.get_rect()):
                self.player.score += 200
                self.coins.remove(coin)

        # Player vs POW block
        if (self.player.vy < 0 and
            self.player.get_rect().colliderect(self.pow_block.get_rect())):
            self.activate_pow()
            self.player.vy = 2

    def update(self):
        if self.state != GameState.PLAYING:
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys, self.platforms, self.SCREEN_WIDTH)

        for enemy in self.enemies:
            enemy.update(self.platforms, self.SCREEN_WIDTH)

        for coin in self.coins[:]:
            if not coin.update():
                self.coins.remove(coin)

        self.check_collisions()

        # Random coin spawning from pipes
        if random.random() < 0.005:
            pipe = random.choice(self.pipes)
            self.spawn_coin(pipe.centerx, pipe.top - 20)

        # Check win condition
        if not self.enemies:
            self.wave += 1
            self.create_level()

    def draw(self):
        self.screen.fill((20, 20, 40))

        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.WIN:
            self.draw_win()

        pygame.display.flip()

    def draw_menu(self):
        title = self.font.render("VECTOR MARIO BROS", True, (255, 100, 100))
        subtitle = self.small_font.render("SEWER CLEANING", True, (200, 200, 200))
        instructions = [
            "Arrow Keys: Move",
            "Space: Jump",
            "Hit enemies from below to flip them",
            "Kick stunned enemies to defeat them",
            "",
            "Press SPACE to Start"
        ]

        self.screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
        self.screen.blit(subtitle, (self.SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 190))

        for i, line in enumerate(instructions):
            text = self.small_font.render(line, True, (150, 150, 150))
            self.screen.blit(text, (self.SCREEN_WIDTH // 2 - text.get_width() // 2, 260 + i * 30))

    def draw_game(self):
        # Draw platforms
        for plat in self.platforms:
            pygame.draw.rect(self.screen, (100, 100, 150), plat)
            pygame.draw.rect(self.screen, (80, 80, 120), plat, 2)

        # Draw pipes
        for pipe in self.pipes:
            pygame.draw.rect(self.screen, (50, 150, 50), pipe)
            pygame.draw.rect(self.screen, (30, 100, 30), pipe, 2)
            # Pipe rim
            pygame.draw.rect(self.screen, (60, 170, 60), (pipe.x - 4, pipe.y, pipe.width + 8, 16))
            pygame.draw.rect(self.screen, (40, 120, 40), (pipe.x - 4, pipe.y, pipe.width + 8, 16), 2)

        # Draw POW block
        self.pow_block.draw(self.screen)

        # Draw coins
        for coin in self.coins:
            coin.draw(self.screen)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw HUD
        score_text = self.small_font.render(f"SCORE: {self.player.score}", True, (255, 255, 255))
        lives_text = self.small_font.render(f"LIVES: {self.player.lives}", True, (255, 255, 255))
        wave_text = self.small_font.render(f"WAVE: {self.wave}", True, (255, 255, 255))

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 35))
        self.screen.blit(wave_text, (10, 60))

    def draw_game_over(self):
        self.draw_game()
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        game_over = self.font.render("GAME OVER", True, (255, 50, 50))
        score_text = self.small_font.render(f"Final Score: {self.player.score}", True, (255, 255, 255))
        restart_text = self.small_font.render("Press SPACE to Restart", True, (150, 150, 150))

        self.screen.blit(game_over, (self.SCREEN_WIDTH // 2 - game_over.get_width() // 2, 200))
        self.screen.blit(score_text, (self.SCREEN_WIDTH // 2 - score_text.get_width() // 2, 260))
        self.screen.blit(restart_text, (self.SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 320))

    def draw_win(self):
        self.screen.fill((50, 50, 100))
        win_text = self.font.render("SEWER CLEANED!", True, (100, 255, 100))
        score_text = self.small_font.render(f"Final Score: {self.player.score}", True, (255, 255, 255))

        self.screen.blit(win_text, (self.SCREEN_WIDTH // 2 - win_text.get_width() // 2, 250))
        self.screen.blit(score_text, (self.SCREEN_WIDTH // 2 - score_text.get_width() // 2, 300))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_SPACE:
                        if self.state == GameState.MENU:
                            self.state = GameState.PLAYING
                        elif self.state == GameState.GAME_OVER:
                            self.reset_level()
                            self.state = GameState.PLAYING

            self.update()
            self.draw()
            self.clock.tick(60)


if __name__ == "__main__":
    game = Game()
    game.run()
