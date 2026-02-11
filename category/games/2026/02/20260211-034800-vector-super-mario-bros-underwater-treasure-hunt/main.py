"""
Vector Super Mario Bros Underwater Treasure Hunt
Navigate the deep sea to collect coins while dodging Bloopers and Cheep Cheeps.
"""

import pygame
import sys
import random
import math
from enum import Enum

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WATER_LEVEL = 600

# Colors
COLOR_BG = (10, 30, 60)
COLOR_BG_DEEP = (5, 20, 40)
COLOR_WATER_SURFACE = (20, 60, 100)
COLOR_PLAYER = (255, 100, 50)
COLOR_PLAYER_ACCENT = (255, 150, 100)
COLOR_COIN = (255, 215, 0)
COLOR_COIN_SHINE = (255, 235, 100)
COLOR_BLOOPER = (240, 240, 255)
COLOR_BLOOPER_TENTACLE = (200, 200, 220)
COLOR_CHEEP_CHEEP = (255, 80, 60)
COLOR_CHEEP_FIN = (200, 50, 40)
COLOR_CORAL = (255, 120, 150)
COLOR_PIPE = (100, 200, 100)
COLOR_PIPE_DARK = (70, 150, 70)
COLOR_TEXT = (255, 255, 255)
COLOR_HUD_BG = (0, 0, 0, 150)

# Physics
GRAVITY = 0.15
SINK_SPEED = 0.8
SWIM_FORCE = -4.5
HORIZONTAL_SPEED = 3
MAX_FALL_SPEED = 4
SCROLL_SPEED_BASE = 2

# Game elements
COIN_SIZE = 12
PLAYER_SIZE = 32
BLOOPER_SIZE = 40
CHEEP_CHEEP_SIZE = 28

# Scoring
COIN_POINTS = 100
DISTANCE_POINTS = 1

# Spawning
BLOOPER_SPAWN_INTERVAL = 120
CHEEP_CHEEP_SPAWN_INTERVAL = 90
COIN_SPAWN_INTERVAL = 60
OBSTACLE_SPAWN_INTERVAL = 150


class GameState(Enum):
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2


class Player:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.vx = 0
        self.vy = 0
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.swimming = False
        self.swim_frame = 0
        self.facing_right = True

    def swim(self):
        self.vy = SWIM_FORCE
        self.swimming = True
        self.swim_frame = 8

    def move_left(self):
        self.vx = -HORIZONTAL_SPEED
        self.facing_right = False

    def move_right(self):
        self.vx = HORIZONTAL_SPEED
        self.facing_right = True

    def stop_horizontal(self):
        self.vx = 0

    def update(self):
        # Apply natural sinking
        self.vy += GRAVITY
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Screen boundaries
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
        if self.y < 20:
            self.y = 20
            self.vy = 0
        if self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.vy = 0

        # Update swim animation
        if self.swim_frame > 0:
            self.swim_frame -= 1
        else:
            self.swimming = False

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        rect = self.get_rect()

        # Body (Mario-like diver)
        body_rect = pygame.Rect(rect.x + 4, rect.y + 8, rect.width - 8, rect.height - 12)
        pygame.draw.ellipse(surface, COLOR_PLAYER, body_rect)

        # Hat
        hat_color = (200, 50, 50)
        pygame.draw.ellipse(surface, hat_color, (rect.x + 6, rect.y + 2, rect.width - 12, 12))

        # Face
        face_x = rect.x + (rect.width // 2 + (6 if self.facing_right else -6))
        pygame.draw.circle(surface, COLOR_PLAYER_ACCENT, (face_x, rect.y + 10), 6)

        # Eye
        eye_x = face_x + (2 if self.facing_right else -2)
        pygame.draw.circle(surface, (0, 0, 0), (eye_x, rect.y + 9), 2)

        # Mustache
        mustache_y = rect.y + 13
        pygame.draw.line(surface, (50, 30, 10), (face_x - 3, mustache_y), (face_x + 2, mustache_y), 2)
        pygame.draw.line(surface, (50, 30, 10), (face_x + 2, mustache_y), (face_x + 5, mustache_y), 2)

        # Arms and legs animation based on swimming
        leg_offset = math.sin(self.swim_frame * 0.5) * 3 if self.swimming else 0

        # Arms
        arm_y = rect.y + 18 + leg_offset
        arm_dir = 1 if self.facing_right else -1
        pygame.draw.line(surface, COLOR_PLAYER_ACCENT,
                       (rect.centerx, arm_y),
                       (rect.centerx + arm_dir * 10, arm_y - 3), 3)

        # Flippers
        flipper_color = (50, 100, 150)
        flipper_y = rect.y + rect.height - 6
        pygame.draw.ellipse(surface, flipper_color,
                          (rect.x + 2 - leg_offset, flipper_y, 10, 6))
        pygame.draw.ellipse(surface, flipper_color,
                          (rect.x + rect.width - 12 + leg_offset, flipper_y, 10, 6))

        # Bubbles when swimming
        if self.swimming:
            for i in range(3):
                bubble_x = rect.x + random.randint(0, rect.width)
                bubble_y = rect.y + rect.height + random.randint(0, 10)
                bubble_size = random.randint(2, 5)
                pygame.draw.circle(surface, (150, 200, 255), (bubble_x, bubble_y), bubble_size, 1)


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = COIN_SIZE
        self.height = COIN_SIZE
        self.collected = False
        self.bob_offset = random.random() * 6.28
        self.bob_speed = 0.05

    def update(self):
        self.bob_offset += self.bob_speed

    def get_rect(self):
        bob_y = self.y + math.sin(self.bob_offset) * 3
        return pygame.Rect(self.x, bob_y, self.width, self.height)

    def draw(self, surface):
        rect = self.get_rect()
        center = rect.center

        # Outer ring
        pygame.draw.circle(surface, COLOR_COIN, center, self.width // 2)
        pygame.draw.circle(surface, (200, 150, 0), center, self.width // 2, 2)

        # Inner shine
        shine_offset = int(self.bob_offset * 5) % 6 - 3
        pygame.draw.circle(surface, COLOR_COIN_SHINE,
                         (center[0] + shine_offset, center[1] - 2), 3)


class Blooper:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = BLOOPER_SIZE
        self.height = BLOOPER_SIZE
        self.speed = 1.5
        self.lunge_cooldown = 0
        self.tentacle_offset = random.random() * 6.28

    def update(self, player_y):
        # Slowly drift towards player
        if self.y < player_y:
            self.y += self.speed * 0.5
        elif self.y > player_y:
            self.y -= self.speed * 0.5

        # Lunge towards player periodically
        if self.lunge_cooldown > 0:
            self.lunge_cooldown -= 1
        else:
            # Lunge
            if self.y < player_y:
                self.y += self.speed * 3
            else:
                self.y -= self.speed * 3
            self.lunge_cooldown = 60

        self.tentacle_offset += 0.15

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        rect = self.get_rect()
        center_x = rect.x + rect.width // 2
        center_y = rect.y + rect.height // 2

        # Tentacles (animated)
        for i in range(6):
            tentacle_x = rect.x + 8 + i * 5
            wave_offset = math.sin(self.tentacle_offset + i * 0.5) * 3
            tentacle_end = (tentacle_x + wave_offset, rect.y + rect.height + 10)
            pygame.draw.line(surface, COLOR_BLOOPER_TENTACLE,
                           (tentacle_x, rect.y + rect.height - 5),
                           tentacle_end, 2)

        # Body (white squid)
        pygame.draw.ellipse(surface, COLOR_BLOOPER,
                          (rect.x + 5, rect.y, rect.width - 10, rect.height - 10))

        # Eyes
        eye_size = 5
        pygame.draw.circle(surface, (0, 0, 0), (center_x - 6, center_y - 2), eye_size)
        pygame.draw.circle(surface, (0, 0, 0), (center_x + 6, center_y - 2), eye_size)
        pygame.draw.circle(surface, (255, 255, 255), (center_x - 7, center_y - 3), 2)
        pygame.draw.circle(surface, (255, 255, 255), (center_x + 5, center_y - 3), 2)

        # Mouth line
        pygame.draw.line(surface, (50, 50, 80),
                       (center_x - 5, center_y + 8),
                       (center_x + 5, center_y + 8), 2)


class CheepCheep:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction  # 1 for right, -1 for left
        self.width = CHEEP_CHEEP_SIZE
        self.height = CHEEP_CHEEP_SIZE
        self.speed = 2
        self.wave_offset = random.random() * 6.28

    def update(self):
        self.x += self.speed * self.direction
        self.wave_offset += 0.1
        self.y += math.sin(self.wave_offset) * 0.5

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        rect = self.get_rect()
        center_x = rect.x + rect.width // 2
        center_y = rect.y + rect.height // 2

        # Body
        body_direction = 1 if self.direction > 0 else -1
        body_rect = pygame.Rect(rect.x, rect.y + 4, rect.width, rect.height - 8)
        pygame.draw.ellipse(surface, COLOR_CHEEP_CHEEP, body_rect)

        # Tail
        tail_points = [
            (rect.x + (rect.width if body_direction > 0 else 0), center_y),
            (rect.x + ((rect.width + 10) * body_direction), center_y - 5),
            (rect.x + ((rect.width + 10) * body_direction), center_y + 5)
        ]
        pygame.draw.polygon(surface, COLOR_CHEEP_FIN, tail_points)

        # Dorsal fin
        fin_x = center_x + body_direction * 3
        pygame.draw.polygon(surface, COLOR_CHEEP_FIN,
                          [(fin_x, rect.y + 4), (fin_x - 3, rect.y - 2), (fin_x + 3, rect.y - 2)])

        # Eye
        eye_x = center_x + (5 * body_direction)
        pygame.draw.circle(surface, (255, 255, 255), (eye_x, center_y), 4)
        pygame.draw.circle(surface, (0, 0, 0), (eye_x + (1 * body_direction), center_y), 2)

        # Mouth
        mouth_x = eye_x + (5 * body_direction)
        pygame.draw.circle(surface, (150, 30, 30), (mouth_x, center_y + 2), 2)


class Obstacle:
    def __init__(self, x, y, obs_type):
        self.x = x
        self.y = y
        self.type = obs_type  # 'coral' or 'pipe'
        self.width = 40 if obs_type == 'coral' else 50
        self.height = 50 if obs_type == 'coral' else 80

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        rect = self.get_rect()

        if self.type == 'coral':
            # Draw coral
            for i in range(5):
                branch_x = rect.x + i * 8
                branch_height = 20 + random.randint(0, 15)
                pygame.draw.line(surface, COLOR_CORAL,
                               (branch_x, rect.y + rect.height),
                               (branch_x, rect.y + rect.height - branch_height), 4)
                pygame.draw.circle(surface, COLOR_CORAL,
                               (branch_x, rect.y + rect.height - branch_height), 5)
        else:  # pipe
            # Pipe body
            pygame.draw.rect(surface, COLOR_PIPE, rect)
            pygame.draw.rect(surface, COLOR_PIPE_DARK,
                           (rect.x + 3, rect.y, rect.width - 6, rect.height))

            # Pipe top
            top_rect = pygame.Rect(rect.x - 5, rect.y, rect.width + 10, 15)
            pygame.draw.rect(surface, COLOR_PIPE, top_rect)
            pygame.draw.rect(surface, COLOR_PIPE_DARK,
                           (top_rect.x + 3, top_rect.y, top_rect.width - 6, top_rect.height))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Super Mario Bros Underwater Treasure Hunt")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 28)
        self.reset()

    def reset(self):
        self.player = Player()
        self.coins = []
        self.bloopers = []
        self.cheeps = []
        self.obstacles = []
        self.bubbles = []
        self.score = 0
        self.distance = 0
        self.state = GameState.MENU
        self.blooper_timer = 0
        self.cheep_timer = 0
        self.coin_timer = 0
        self.obstacle_timer = 0
        self.bg_offset = 0

        # Spawn some initial coins
        for i in range(5):
            self.spawn_coin(200 + i * 150)

    def spawn_coin(self, x=None):
        if x is None:
            x = SCREEN_WIDTH + random.randint(0, 100)
        y = random.randint(50, SCREEN_HEIGHT - 80)
        self.coins.append(Coin(x, y))

    def spawn_blooper(self):
        y = random.randint(100, SCREEN_HEIGHT - 100)
        self.bloopers.append(Blooper(SCREEN_WIDTH + 50, y))

    def spawn_cheep_cheep(self):
        direction = random.choice([-1, 1])
        if direction == 1:
            x = -50
            y = random.randint(50, SCREEN_HEIGHT - 100)
        else:
            x = SCREEN_WIDTH + 50
            y = random.randint(50, SCREEN_HEIGHT - 100)
        self.cheeps.append(CheepCheep(x, y, direction))

    def spawn_obstacle(self):
        obs_type = random.choice(['coral', 'pipe'])
        y = SCREEN_HEIGHT - (50 if obs_type == 'coral' else 80)
        self.obstacles.append(Obstacle(SCREEN_WIDTH, y, obs_type))

    def spawn_bubble(self):
        self.bubbles.append({
            'x': random.randint(0, SCREEN_WIDTH),
            'y': SCREEN_HEIGHT + 10,
            'size': random.randint(3, 8),
            'speed': random.uniform(0.5, 1.5)
        })

    def check_collisions(self):
        player_rect = self.player.get_rect()

        # Check coins
        for coin in self.coins[:]:
            if not coin.collected and player_rect.colliderect(coin.get_rect()):
                coin.collected = True
                self.score += COIN_POINTS
                self.coins.remove(coin)

        # Check bloopers
        for blooper in self.bloopers:
            if player_rect.colliderect(blooper.get_rect()):
                return True

        # Check cheeps
        for cheep in self.cheeps:
            if player_rect.colliderect(cheep.get_rect()):
                return True

        # Check obstacles
        for obstacle in self.obstacles:
            if player_rect.colliderect(obstacle.get_rect()):
                return True

        return False

    def handle_input(self):
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if self.state == GameState.MENU:
                        self.state = GameState.PLAYING
                    elif self.state == GameState.PLAYING:
                        self.player.swim()
                    elif self.state == GameState.GAME_OVER:
                        self.reset()
                elif event.key == pygame.K_ESCAPE:
                    return False

        # Continuous input handling
        if self.state == GameState.PLAYING:
            if keys[pygame.K_LEFT]:
                self.player.move_left()
            elif keys[pygame.K_RIGHT]:
                self.player.move_right()
            else:
                self.player.stop_horizontal()

        return True

    def update(self):
        if self.state != GameState.PLAYING:
            return

        # Update player
        self.player.update()

        # Update distance and score
        self.distance += DISTANCE_POINTS
        self.bg_offset = (self.bg_offset + SCROLL_SPEED_BASE) % SCREEN_WIDTH

        # Spawn timers
        self.blooper_timer += 1
        self.cheep_timer += 1
        self.coin_timer += 1
        self.obstacle_timer += 1

        # Spawn bloopers
        if self.blooper_timer >= BLOOPER_SPAWN_INTERVAL:
            self.spawn_blooper()
            self.blooper_timer = 0

        # Spawn cheeps
        if self.cheep_timer >= CHEEP_CHEEP_SPAWN_INTERVAL:
            self.spawn_cheep_cheep()
            self.cheep_timer = 0

        # Spawn coins
        if self.coin_timer >= COIN_SPAWN_INTERVAL:
            self.spawn_coin()
            self.coin_timer = 0

        # Spawn obstacles
        if self.obstacle_timer >= OBSTACLE_SPAWN_INTERVAL:
            self.spawn_obstacle()
            self.obstacle_timer = 0

        # Spawn ambient bubbles
        if random.random() < 0.02:
            self.spawn_bubble()

        # Update coins
        for coin in self.coins:
            coin.x -= SCROLL_SPEED_BASE
            coin.update()

        # Update bloopers
        for blooper in self.bloopers:
            blooper.x -= SCROLL_SPEED_BASE
            blooper.update(self.player.y)

        # Update cheeps
        for cheep in self.cheeps:
            cheep.update()

        # Update obstacles
        for obstacle in self.obstacles:
            obstacle.x -= SCROLL_SPEED_BASE

        # Update bubbles
        for bubble in self.bubbles[:]:
            bubble['y'] -= bubble['speed']
            bubble['x'] += math.sin(bubble['y'] * 0.05) * 0.3
            if bubble['y'] < -20:
                self.bubbles.remove(bubble)

        # Remove off-screen entities
        self.coins = [c for c in self.coins if c.x > -50]
        self.bloopers = [b for b in self.bloopers if b.x > -100]
        self.cheeps = [c for c in self.cheeps if -100 < c.x < SCREEN_WIDTH + 100]
        self.obstacles = [o for o in self.obstacles if o.x > -100]

        # Check collisions
        if self.check_collisions():
            self.state = GameState.GAME_OVER

    def draw_background(self):
        # Gradient background
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            color = (
                int(COLOR_BG[0] * (1 - ratio) + COLOR_BG_DEEP[0] * ratio),
                int(COLOR_BG[1] * (1 - ratio) + COLOR_BG_DEEP[1] * ratio),
                int(COLOR_BG[2] * (1 - ratio) + COLOR_BG_DEEP[2] * ratio)
            )
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

        # Water surface effect
        pygame.draw.rect(self.screen, COLOR_WATER_SURFACE, (0, 0, SCREEN_WIDTH, 30))

        # Ambient bubbles
        for bubble in self.bubbles:
            pygame.draw.circle(self.screen, (100, 150, 200),
                           (int(bubble['x']), int(bubble['y'])), bubble['size'], 1)

        # Seaweed at bottom
        for i in range(0, SCREEN_WIDTH + 50, 50):
            seaweed_x = i - self.bg_offset % 50
            for j in range(3):
                height = 30 + j * 15
                sway = math.sin(self.bg_offset * 0.02 + j) * 5
                pygame.draw.line(self.screen, (30, 80, 50),
                               (seaweed_x + j * 10, SCREEN_HEIGHT),
                               (seaweed_x + j * 10 + sway, SCREEN_HEIGHT - height), 3)

    def draw_hud(self):
        # Score background
        pygame.draw.rect(self.screen, COLOR_HUD_BG, (10, 10, 200, 60), border_radius=5)

        # Score text
        score_text = self.small_font.render(f"SCORE: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (20, 15))

        # Distance text
        dist_text = self.small_font.render(f"DIST: {self.distance}m", True, COLOR_TEXT)
        self.screen.blit(dist_text, (20, 40))

    def draw_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Title
        title = self.font.render("UNDERWATER", True, (100, 200, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        subtitle = self.font.render("TREASURE HUNT", True, (255, 200, 100))
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 130))
        self.screen.blit(subtitle, sub_rect)

        # Instructions
        instructions = [
            "PRESS SPACE TO START",
            "",
            "CONTROLS:",
            "SPACE / UP - Swim Up",
            "LEFT / RIGHT - Move Horizontal",
            "",
            "Collect coins, avoid enemies!",
            "Watch out for Bloopers & Cheeps!",
        ]

        y = 200
        for line in instructions:
            if line == "PRESS SPACE TO START":
                color = (255, 255, 255)
                font = self.font
            elif line.startswith("CONTROLS"):
                color = (255, 200, 50)
                font = self.small_font
            else:
                color = (180, 180, 180)
                font = self.small_font

            text = font.render(line, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, rect)
            y += 30

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Game over text
        game_over = self.font.render("GAME OVER", True, (255, 100, 100))
        go_rect = game_over.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(game_over, go_rect)

        # Final score
        score_text = self.font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(score_text, score_rect)

        # Distance
        dist_text = self.small_font.render(f"Distance: {self.distance}m", True, (200, 200, 200))
        dist_rect = dist_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.screen.blit(dist_text, dist_rect)

        # Restart prompt
        restart = self.small_font.render("PRESS SPACE TO RESTART", True, (255, 200, 50))
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, 320))
        self.screen.blit(restart, restart_rect)

    def draw(self):
        self.draw_background()

        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        # Draw coins
        for coin in self.coins:
            coin.draw(self.screen)

        # Draw bloopers
        for blooper in self.bloopers:
            blooper.draw(self.screen)

        # Draw cheeps
        for cheep in self.cheeps:
            cheep.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw HUD
        self.draw_hud()

        # Draw overlays
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
