import pygame
import sys
from enum import Enum


class Stance(Enum):
    IDLE = "idle"
    HIGH_PUNCH = "high_punch"
    LOW_KICK = "low_kick"
    BLOCK = "block"
    HIT = "hit"


class Fighter:
    def __init__(self, x, y, color, facing_right=True):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 100
        self.color = color
        self.facing_right = facing_right
        self.velocity_x = 0
        self.speed = 4

        self.health = 100
        self.max_health = 100
        self.stance = Stance.IDLE
        self.stance_timer = 0
        self.stance_duration = 0
        self.recovery_timer = 0

        self.score = 0
        self.hits_landed = 0

    def update(self, bounds_width):
        self.x += self.velocity_x
        self.x = max(0, min(self.x, bounds_width - self.width))

        if self.stance_timer > 0:
            self.stance_timer -= 1
            if self.stance_timer == 0:
                if self.stance == Stance.HIT:
                    self.stance = Stance.IDLE
                elif self.recovery_timer > 0:
                    self.recovery_timer -= 1
                else:
                    self.stance = Stance.IDLE

    def move(self, direction):
        if self.stance == Stance.IDLE:
            self.velocity_x = direction * self.speed
        else:
            self.velocity_x = 0

    def stop_moving(self):
        self.velocity_x = 0

    def attack(self, attack_type):
        if self.stance == Stance.IDLE and self.recovery_timer == 0:
            self.stance = attack_type
            self.stance_timer = 20
            self.recovery_timer = 15
            return True
        return False

    def block(self):
        if self.stance == Stance.IDLE:
            self.stance = Stance.BLOCK
            self.stance_timer = 30
            return True
        return False

    def take_damage(self, amount, blocked=False):
        if blocked:
            amount = amount // 4
        self.health -= amount
        self.health = max(0, self.health)
        self.stance = Stance.HIT
        self.stance_timer = 15
        return amount

    def get_hitbox(self):
        if self.stance == Stance.HIGH_PUNCH:
            offset = 30 if self.facing_right else -30
            return pygame.Rect(
                self.x + offset if self.facing_right else self.x,
                self.y + 10,
                40,
                30
            )
        elif self.stance == Stance.LOW_KICK:
            offset = 35 if self.facing_right else -35
            return pygame.Rect(
                self.x + offset if self.facing_right else self.x,
                self.y + 60,
                45,
                25
            )
        return None

    def get_body_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def is_blocking(self):
        return self.stance == Stance.BLOCK

    def draw(self, surface):
        rect = self.get_body_rect()

        if self.stance == Stance.HIT:
            color = (255, 100, 100)
        elif self.stance == Stance.BLOCK:
            color = (100, 150, 255)
        else:
            color = self.color

        pygame.draw.rect(surface, color, rect)

        head_rect = pygame.Rect(self.x + 10, self.y - 20, 30, 25)
        pygame.draw.rect(surface, color, head_rect)

        if self.stance == Stance.HIGH_PUNCH and self.stance_timer > 10:
            offset = 30 if self.facing_right else -30
            arm_rect = pygame.Rect(
                self.x + offset if self.facing_right else self.x - 10,
                self.y + 15,
                40,
                15
            )
            pygame.draw.rect(surface, (200, 200, 200), arm_rect)

        if self.stance == Stance.LOW_KICK and self.stance_timer > 10:
            offset = 35 if self.facing_right else -35
            leg_rect = pygame.Rect(
                self.x + offset if self.facing_right else self.x - 15,
                self.y + 65,
                45,
                15
            )
            pygame.draw.rect(surface, (150, 150, 150), leg_rect)

        if self.stance == Stance.BLOCK:
            shield_rect = pygame.Rect(self.x - 5, self.y - 5, self.width + 10, self.height + 5)
            pygame.draw.rect(surface, (100, 150, 255), shield_rect, 3)


class AIController:
    def __init__(self, fighter):
        self.fighter = fighter
        self.reaction_delay = 0
        self.decision_timer = 0
        self.aggression = 0.6

    def update(self, opponent):
        self.decision_timer += 1

        distance = abs(self.fighter.x - opponent.x)

        if self.reaction_delay > 0:
            self.reaction_delay -= 1
            self.fighter.stop_moving()
            return

        opponent_attacking = opponent.stance in [Stance.HIGH_PUNCH, Stance.LOW_KICK]
        opponent_active_frame = opponent.stance_timer > 10

        if opponent_attacking and opponent_active_frame and distance < 100:
            if self.fighter.stance == Stance.IDLE:
                self.fighter.block()
                self.reaction_delay = 20
            return

        if self.fighter.stance != Stance.IDLE:
            return

        if self.decision_timer < 15:
            return

        self.decision_timer = 0

        if distance > 200:
            direction = -1 if self.fighter.x > opponent.x else 1
            self.fighter.move(direction)
        elif distance < 80:
            if self.fighter.x > opponent.x:
                self.fighter.move(-1)
            else:
                self.fighter.move(1)
        else:
            self.fighter.stop_moving()

            if distance < 120 and opponent.stance != Stance.BLOCK:
                import random
                roll = random.random()
                if roll < self.aggression:
                    attack = Stance.HIGH_PUNCH if roll < 0.4 else Stance.LOW_KICK
                    self.fighter.attack(attack)


class Game:
    def __init__(self):
        pygame.init()
        self.width = 800
        self.height = 400
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Vector Karateka - Clash Timing")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)

        self.floor_y = self.height - 50

        self.player = Fighter(150, self.floor_y - 100, (70, 130, 180), facing_right=True)
        self.enemy = Fighter(550, self.floor_y - 100, (180, 70, 70), facing_right=False)
        self.ai = AIController(self.enemy)

        self.round_winner = None
        self.game_over = False
        self.round_over_timer = 0
        self.player_wins = 0
        self.enemy_wins = 0

    def check_collisions(self):
        player_hitbox = self.player.get_hitbox()
        enemy_hitbox = self.enemy.get_hitbox()

        if player_hitbox and self.player.stance_timer > 10:
            if enemy_hitbox and self.enemy.stance_timer > 10:
                if player_hitbox.colliderect(enemy_hitbox):
                    self.player.stance = Stance.IDLE
                    self.player.stance_timer = 0
                    self.enemy.stance = Stance.IDLE
                    self.enemy.stance_timer = 0
                    return

            if player_hitbox.colliderect(self.enemy.get_body_rect()):
                damage = 10
                blocked = self.enemy.is_blocking()
                actual_damage = self.enemy.take_damage(damage, blocked)
                self.player.score += 100 if not blocked else 10
                if not blocked:
                    self.player.hits_landed += 1

        if enemy_hitbox and self.enemy.stance_timer > 10:
            if enemy_hitbox.colliderect(self.player.get_body_rect()):
                damage = 10
                blocked = self.player.is_blocking()
                actual_damage = self.player.take_damage(damage, blocked)
                self.enemy.score += 100 if not blocked else 10
                if not blocked:
                    self.enemy.hits_landed += 1

    def update(self):
        if self.game_over:
            return

        if self.round_winner is not None:
            self.round_over_timer -= 1
            if self.round_over_timer <= 0:
                self.reset_round()
            return

        self.player.update(self.width)
        self.enemy.update(self.width)
        self.ai.update(self.player)

        self.check_collisions()

        if self.player.health <= 0:
            self.round_winner = "enemy"
            self.enemy_wins += 1
            self.enemy.score += 500
            self.round_over_timer = 120
        elif self.enemy.health <= 0:
            self.round_winner = "player"
            self.player_wins += 1
            self.player.score += 500
            self.round_over_timer = 120

        if self.player_wins >= 2:
            self.game_over = True
            self.round_winner = "player"
        elif self.enemy_wins >= 2:
            self.game_over = True
            self.round_winner = "enemy"

    def reset_round(self):
        self.player.x = 150
        self.player.health = self.player.max_health
        self.player.stance = Stance.IDLE
        self.player.recovery_timer = 0
        self.player.velocity_x = 0

        self.enemy.x = 550
        self.enemy.health = self.enemy.max_health
        self.enemy.stance = Stance.IDLE
        self.enemy.recovery_timer = 0
        self.enemy.velocity_x = 0

        self.round_winner = None

    def reset_game(self):
        self.player_wins = 0
        self.enemy_wins = 0
        self.player.score = 0
        self.enemy.score = 0
        self.game_over = False
        self.round_winner = None
        self.reset_round()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.game_over and event.key == pygame.K_SPACE:
                    self.reset_game()

                if not self.game_over and self.round_winner is None:
                    if event.key == pygame.K_a:
                        self.player.attack(Stance.HIGH_PUNCH)
                    elif event.key == pygame.K_s:
                        self.player.attack(Stance.LOW_KICK)
                    elif event.key == pygame.K_d:
                        self.player.block()

            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    self.player.stop_moving()

        keys = pygame.key.get_pressed()
        if self.round_winner is None and not self.game_over:
            if keys[pygame.K_LEFT]:
                self.player.move(-1)
            elif keys[pygame.K_RIGHT]:
                self.player.move(1)
            elif not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
                if self.player.stance == Stance.IDLE:
                    self.player.stop_moving()

        return True

    def draw_health_bar(self, x, y, health, max_health, color):
        bar_width = 200
        bar_height = 20
        fill_width = int((health / max_health) * bar_width)

        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, bar_width, bar_height))
        pygame.draw.rect(self.screen, color, (x, y, fill_width, bar_height))
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)

    def draw(self):
        self.screen.fill((30, 30, 35))

        pygame.draw.rect(self.screen, (60, 50, 40), (0, self.floor_y, self.width, 50))

        self.draw_health_bar(20, 20, self.player.health, self.player.max_health, (70, 130, 180))
        self.draw_health_bar(self.width - 220, 20, self.enemy.health, self.enemy.max_health, (180, 70, 70))

        player_label = self.font.render(f"P1: {self.player.score}", True, (200, 200, 200))
        enemy_label = self.font.render(f"CPU: {self.enemy.score}", True, (200, 200, 200))
        self.screen.blit(player_label, (20, 50))
        self.screen.blit(enemy_label, (self.width - 150, 50))

        wins_text = self.font.render(f"{self.player_wins} - {self.enemy_wins}", True, (255, 200, 100))
        self.screen.blit(wins_text, (self.width // 2 - 30, 20))

        self.player.draw(self.screen)
        self.enemy.draw(self.screen)

        if self.round_winner:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

            winner_text = "YOU WIN!" if self.round_winner == "player" else "ENEMY WINS!"
            text = self.large_font.render(winner_text, True, (255, 200, 100))
            text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(text, text_rect)

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            winner_text = "VICTORY!" if self.round_winner == "player" else "DEFEAT!"
            text = self.large_font.render(winner_text, True, (255, 200, 100))
            text_rect = text.get_rect(center=(self.width // 2, self.height // 2 - 30))
            self.screen.blit(text, text_rect)

            restart_text = self.font.render("Press SPACE to play again", True, (200, 200, 200))
            restart_rect = restart_text.get_rect(center=(self.width // 2, self.height // 2 + 30))
            self.screen.blit(restart_text, restart_rect)

        controls = [
            "Arrow Keys: Move",
            "A: High Punch",
            "S: Low Kick",
            "D: Block",
            "ESC: Quit"
        ]
        for i, line in enumerate(controls):
            text = pygame.font.Font(None, 20).render(line, True, (100, 100, 100))
            self.screen.blit(text, (10, self.height - 110 + i * 18))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
