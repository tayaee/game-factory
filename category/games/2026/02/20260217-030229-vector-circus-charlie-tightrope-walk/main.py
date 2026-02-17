"""
Vector Circus Charlie Tightrope Walk
A circus tightrope balance and timing challenge.
"""

import pygame
import sys
import random
from enum import Enum

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60
ROPE_Y = 250
WORLD_WIDTH = 2000
GOAL_X = 1900

# Colors
COLOR_BG = (15, 15, 25)
COLOR_ROPE = (139, 90, 43)
COLOR_ROPE_SHADOW = (100, 60, 30)
COLOR_PERFORMER = (255, 255, 255)
COLOR_PERFORMER_ACCENT = (220, 220, 220)
COLOR_MONKEY = (139, 69, 19)
COLOR_MONKEY_FACE = (205, 133, 63)
COLOR_GOAL = (50, 205, 50)
COLOR_TEXT = (255, 255, 255)
COLOR_HUD_BG = (0, 0, 0, 150)

# Physics
GRAVITY = 0.8
JUMP_STRENGTH = -12
MOVEMENT_SPEED = 4

# Sizes
PERFORMER_WIDTH = 32
PERFORMER_HEIGHT = 48
MONKEY_WIDTH = 24
MONKEY_HEIGHT = 24

# Scoring
SCORE_PER_DISTANCE = 1
SCORE_PER_MONKEY = 100
SCORE_GOAL_BONUS = 1000


class GameState(Enum):
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    VICTORY = 3


class Performer:
    def __init__(self):
        self.x = 50
        self.y = ROPE_Y
        self.vy = 0
        self.on_rope = True
        self.width = PERFORMER_WIDTH
        self.height = PERFORMER_HEIGHT
        self.moving = False
        self.facing_right = True
        self.anim_frame = 0

    def jump(self):
        if self.on_rope:
            self.vy = JUMP_STRENGTH
            self.on_rope = False

    def move_right(self):
        self.moving = True
        self.facing_right = True
        if self.on_rope and self.x < WORLD_WIDTH - self.width:
            self.x += MOVEMENT_SPEED

    def stop_moving(self):
        self.moving = False

    def update(self):
        # Apply gravity when not on rope
        if not self.on_rope:
            self.vy += GRAVITY
            self.y += self.vy

            # Rope collision (land on rope)
            if self.y >= ROPE_Y:
                self.y = ROPE_Y
                self.vy = 0
                self.on_rope = True
            # Fall below rope (game over)
            elif self.y > SCREEN_HEIGHT:
                return False  # Fell off

        # Keep within world bounds
        self.x = max(0, min(self.x, WORLD_WIDTH - self.width))

        # Animation
        if self.moving:
            self.anim_frame = (self.anim_frame + 1) % 10

        return True  # Still alive

    def get_rect(self):
        return pygame.Rect(self.x, self.y - self.height, self.width, self.height)

    def draw(self, surface, camera_x):
        screen_x = self.x - camera_x
        rect = pygame.Rect(screen_x, self.y - self.height, self.width, self.height)

        # Simple vector art performer on tightrope

        # Balance pole
        pole_y = self.y - self.height + 15
        pole_length = 60
        pygame.draw.line(surface, COLOR_PERFORMER_ACCENT,
                        (screen_x - pole_length // 2, pole_y),
                        (screen_x + self.width + pole_length // 2, pole_y), 3)

        # Body
        body_rect = pygame.Rect(screen_x + 8, self.y - self.height + 20, 16, 20)
        pygame.draw.rect(surface, COLOR_PERFORMER, body_rect)

        # Head
        head_center = (screen_x + 16, self.y - self.height + 10)
        pygame.draw.circle(surface, COLOR_PERFORMER, head_center, 10)

        # Top hat
        pygame.draw.rect(surface, COLOR_PERFORMER_ACCENT,
                        (screen_x + 8, self.y - self.height - 5, 16, 8))
        pygame.draw.line(surface, COLOR_PERFORMER_ACCENT,
                        (screen_x + 6, self.y - self.height + 3),
                        (screen_x + 26, self.y - self.height + 3), 2)

        # Arms
        arm_offset = 2 if self.on_rope else -5
        pygame.draw.line(surface, COLOR_PERFORMER,
                        (screen_x + 8, self.y - self.height + 25),
                        (screen_x + 2, self.y - self.height + 35 + arm_offset), 3)
        pygame.draw.line(surface, COLOR_PERFORMER,
                        (screen_x + 24, self.y - self.height + 25),
                        (screen_x + 30, self.y - self.height + 35 + arm_offset), 3)

        # Legs
        leg_sway = 0 if self.on_rope else (1 if self.anim_frame < 5 else -1) * 3
        pygame.draw.line(surface, COLOR_PERFORMER,
                        (screen_x + 12, self.y - 10),
                        (screen_x + 10 + leg_sway, self.y), 3)
        pygame.draw.line(surface, COLOR_PERFORMER,
                        (screen_x + 20, self.y - 10),
                        (screen_x + 22 - leg_sway, self.y), 3)

        # Feet on rope
        if self.on_rope:
            pygame.draw.ellipse(surface, COLOR_PERFORMER,
                               (screen_x + 8, self.y - 4, 16, 8))


class Monkey:
    def __init__(self, x, speed):
        self.x = x
        self.y = ROPE_Y - MONKEY_HEIGHT
        self.speed = speed
        self.width = MONKEY_WIDTH
        self.height = MONKEY_HEIGHT
        self.anim_frame = random.randint(0, 10)

    def update(self):
        self.x -= self.speed
        self.anim_frame = (self.anim_frame + 1) % 15

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface, camera_x):
        screen_x = self.x - camera_x

        # Simple vector art monkey

        # Body
        body_y = self.y + 8
        pygame.draw.ellipse(surface, COLOR_MONKEY,
                           (screen_x + 4, body_y, 16, 14))

        # Head
        head_center = (screen_x + 12, self.y + 5)
        pygame.draw.circle(surface, COLOR_MONKEY, head_center, 8)

        # Face
        pygame.draw.circle(surface, COLOR_MONKEY_FACE, head_center, 5)

        # Eyes
        eye_offset = 3
        pygame.draw.circle(surface, (0, 0, 0),
                           (screen_x + 12 - eye_offset, self.y + 4), 2)
        pygame.draw.circle(surface, (0, 0, 0),
                           (screen_x + 12 + eye_offset, self.y + 4), 2)

        # Ears
        pygame.draw.circle(surface, COLOR_MONKEY, (screen_x + 2, self.y + 5), 4)
        pygame.draw.circle(surface, COLOR_MONKEY, (screen_x + 22, self.y + 5), 4)

        # Tail
        tail_sway = int(pygame.math.Vector2(
            1, 0
        ).rotate(self.anim_frame * 15).x * 8)
        tail_end = (screen_x - 5 + tail_sway, body_y + 7)
        pygame.draw.lines(surface, COLOR_MONKEY, False,
                          [(screen_x + 4, body_y + 7), tail_end], 2)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Circus Charlie Tightrope Walk")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 28)
        self.reset()

    def reset(self):
        self.performer = Performer()
        self.monkeys = []
        self.camera_x = 0
        self.score = 0
        self.state = GameState.MENU
        self.monkeys_spawned = 0
        self.spawn_timer = 0
        self.bg_offset = 0

    def spawn_monkey(self):
        # Spawn monkeys at varying speeds and positions
        min_x = max(self.performer.x + 200, SCREEN_WIDTH)
        max_x = min(self.performer.x + 600, WORLD_WIDTH - 100)
        spawn_x = random.randint(min_x, max_x)
        speed = random.uniform(2, 5)
        self.monkeys.append(Monkey(spawn_x, speed))
        self.monkeys_spawned += 1

    def check_collisions(self):
        performer_rect = self.performer.get_rect()

        for monkey in self.monkeys:
            monkey_rect = monkey.get_rect()

            if performer_rect.colliderect(monkey_rect):
                # Shrink hitbox slightly for fairer gameplay
                hitbox_margin = 4
                p_hitbox = performer_rect.inflate(-hitbox_margin * 2, -hitbox_margin * 2)
                m_hitbox = monkey_rect.inflate(-hitbox_margin, -hitbox_margin)

                if p_hitbox.colliderect(m_hitbox):
                    return True

        return False

    def update_camera(self):
        # Camera follows performer with smooth scrolling
        target_x = self.performer.x - SCREEN_WIDTH // 3
        target_x = max(0, min(target_x, WORLD_WIDTH - SCREEN_WIDTH))
        self.camera_x += (target_x - self.camera_x) * 0.1

    def handle_input(self):
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == GameState.MENU:
                        self.state = GameState.PLAYING
                    elif self.state == GameState.PLAYING:
                        self.performer.jump()
                    elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                        self.reset()
                elif event.key == pygame.K_ESCAPE:
                    return False

        # Continuous input handling
        if self.state == GameState.PLAYING:
            if keys[pygame.K_RIGHT]:
                self.performer.move_right()
            else:
                self.performer.stop_moving()

        return True

    def update(self):
        if self.state != GameState.PLAYING:
            return

        # Update performer
        alive = self.performer.update()
        if not alive:
            self.state = GameState.GAME_OVER
            return

        # Check goal
        if self.performer.x >= GOAL_X:
            self.state = GameState.VICTORY
            self.score += SCORE_GOAL_BONUS
            return

        # Update score based on distance
        new_score = int(self.performer.x * SCORE_PER_DISTANCE / 10)
        if new_score > self.score:
            self.score = new_score

        # Spawn monkeys
        self.spawn_timer += 1
        if self.spawn_timer >= 120:  # Spawn every 2 seconds
            if self.performer.x + 600 < WORLD_WIDTH:  # Don't spawn past goal area
                self.spawn_monkey()
            self.spawn_timer = 0

        # Update monkeys
        for monkey in self.monkeys:
            monkey.update()

            # Score for passing monkeys
            if monkey.x + monkey.width < self.performer.x and not hasattr(monkey, 'passed'):
                monkey.passed = True
                self.score += SCORE_PER_MONKEY

        # Remove off-screen monkeys
        self.monkeys = [m for m in self.monkeys if m.x > -50]

        # Check collisions
        if self.check_collisions():
            self.state = GameState.GAME_OVER

        # Update camera
        self.update_camera()

        # Update background
        self.bg_offset = (self.bg_offset + 2) % SCREEN_WIDTH

    def draw_background(self):
        self.screen.fill(COLOR_BG)

        # Draw circus tent pattern in background
        for i in range(6):
            tent_x = (i * 150 - self.bg_offset * 0.3) % (SCREEN_WIDTH + 300) - 150
            tent_height = 80 + (i % 3) * 30
            tent_color = (25 + i * 5, 25 + i * 5, 35 + i * 5)
            pygame.draw.polygon(self.screen, tent_color, [
                (tent_x, ROPE_Y + 50),
                (tent_x + 30, ROPE_Y + 50 - tent_height),
                (tent_x + 60, ROPE_Y + 50)
            ])

        # Draw rope
        pygame.draw.line(self.screen, COLOR_ROPE_SHADOW,
                         (0, ROPE_Y + 3), (SCREEN_WIDTH, ROPE_Y + 3), 4)
        pygame.draw.line(self.screen, COLOR_ROPE,
                         (0, ROPE_Y), (SCREEN_WIDTH, ROPE_Y), 4)

        # Draw rope texture
        for x in range(0, SCREEN_WIDTH, 10):
            offset = (x + int(self.bg_offset * 0.5)) % 20
            if offset < 10:
                pygame.draw.line(self.screen, COLOR_ROPE_SHADOW,
                                (x, ROPE_Y), (x + 5, ROPE_Y), 2)

        # Draw goal platform
        goal_screen_x = GOAL_X - self.camera_x
        if -100 < goal_screen_x < SCREEN_WIDTH + 100:
            pygame.draw.rect(self.screen, COLOR_GOAL,
                           (goal_screen_x, ROPE_Y, 100, 20))
            pygame.draw.polygon(self.screen, (30, 180, 30), [
                (goal_screen_x + 10, ROPE_Y),
                (goal_screen_x + 30, ROPE_Y - 60),
                (goal_screen_x + 50, ROPE_Y)
            ])
            goal_text = self.small_font.render("GOAL", True, (255, 255, 255))
            self.screen.blit(goal_text, (goal_screen_x + 20, ROPE_Y + 25))

        # Draw progress bar
        bar_width = SCREEN_WIDTH - 40
        bar_height = 8
        progress = min(1, self.performer.x / GOAL_X)
        pygame.draw.rect(self.screen, (50, 50, 50),
                         (20, 20, bar_width, bar_height))
        pygame.draw.rect(self.screen, (50, 205, 50),
                         (20, 20, bar_width * progress, bar_height))

    def draw_hud(self):
        # Score background
        pygame.draw.rect(self.screen, COLOR_HUD_BG, (10, 35, 150, 40), border_radius=5)

        # Score text
        score_text = self.font.render(str(self.score), True, COLOR_TEXT)
        self.screen.blit(score_text, (20, 40))

        # Distance indicator
        distance = min(100, int(self.performer.x / GOAL_X * 100))
        dist_text = self.small_font.render(f"DST: {distance}%", True, (150, 150, 150))
        self.screen.blit(dist_text, (20, 75))

    def draw_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Title
        title = self.font.render("TIGHTROPE WALK", True, (255, 200, 50))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        subtitle = self.small_font.render("CIRCUS CHARLIE", True, (200, 150, 50))
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(subtitle, sub_rect)

        # Instructions
        instructions = [
            "PRESS SPACE TO START",
            "",
            "CONTROLS:",
            "RIGHT ARROW - Move Forward",
            "SPACEBAR - Jump",
            "",
            "Jump over incoming monkeys!",
            "Reach the goal to win!",
            "Don't fall off the rope!",
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
        game_over = self.font.render("GAME OVER", True, (255, 50, 50))
        go_rect = game_over.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(game_over, go_rect)

        # Final score
        score_text = self.font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(score_text, score_rect)

        # Restart prompt
        restart = self.small_font.render("PRESS SPACE TO RESTART", True, (255, 200, 50))
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self.screen.blit(restart, restart_rect)

    def draw_victory(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Victory text
        victory = self.font.render("VICTORY!", True, (50, 255, 50))
        v_rect = victory.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(victory, v_rect)

        # Final score
        score_text = self.font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(score_text, score_rect)

        # Restart prompt
        restart = self.small_font.render("PRESS SPACE TO PLAY AGAIN", True, (255, 200, 50))
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self.screen.blit(restart, restart_rect)

    def draw(self):
        self.draw_background()

        # Draw monkeys
        for monkey in self.monkeys:
            monkey.draw(self.screen, self.camera_x)

        # Draw performer
        self.performer.draw(self.screen, self.camera_x)

        # Draw HUD
        self.draw_hud()

        # Draw overlays
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.VICTORY:
            self.draw_victory()

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
