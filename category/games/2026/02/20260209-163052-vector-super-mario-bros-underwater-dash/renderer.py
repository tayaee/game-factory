"""Renderer for Vector Super Mario Bros Underwater Dash."""

import pygame
from game import GameState, Vec2


class Renderer:
    def __init__(self, state: GameState):
        self.state = state
        self.screen = pygame.display.set_mode((state.width, state.height))
        pygame.display.set_caption("Vector Super Mario Bros Underwater Dash")
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Colors - underwater theme
        self.bg_top = (0, 80, 150)
        self.bg_bottom = (0, 40, 100)
        self.platform_color = (60, 100, 80)
        self.platform_highlight = (80, 130, 100)
        self.player_color = (255, 100, 100)
        self.player_highlight = (255, 150, 150)
        self.blooper_color = (180, 180, 200)
        self.blooper_dark = (100, 100, 140)
        self.cheep_color = (255, 150, 50)
        self.cheep_dark = (200, 100, 30)
        self.coin_color = (255, 215, 0)
        self.coin_shine = (255, 255, 200)
        self.flag_color = (50, 200, 50)
        self.flag_pole_color = (150, 150, 150)
        self.bubble_color = (200, 230, 255)
        self.text_color = (255, 255, 255)

    def render(self):
        # Draw gradient background
        for y in range(self.state.height):
            t = y / self.state.height
            r = int(self.bg_top[0] * (1 - t) + self.bg_bottom[0] * t)
            g = int(self.bg_top[1] * (1 - t) + self.bg_bottom[1] * t)
            b = int(self.bg_top[2] * (1 - t) + self.bg_bottom[2] * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.state.width, y))

        # Draw platforms
        for plat in self.state.platforms:
            rect = (plat['x'], plat['y'], plat['w'], plat['h'])
            pygame.draw.rect(self.screen, self.platform_color, rect)
            # Platform edge highlight
            pygame.draw.rect(self.screen, self.platform_highlight,
                           (plat['x'], plat['y'], plat['w'], 3))

        # Draw coins
        for coin in self.state.coins:
            if not coin.collected:
                cy = int(coin.pos.y + 3 * (coin.bob_offset % 2 - 1))
                pygame.draw.circle(self.screen, self.coin_color,
                                 (int(coin.pos.x), cy), coin.radius)
                pygame.draw.circle(self.screen, self.coin_shine,
                                 (int(coin.pos.x - 3), cy - 3), 3)

        # Draw Bloopers
        for blooper in self.state.bloopers:
            if blooper.alive:
                bx, by = int(blooper.pos.x), int(blooper.pos.y)

                # Body
                pygame.draw.ellipse(self.screen, self.blooper_color,
                                   (bx, by, blooper.width, blooper.height))

                # Tentacles
                for i in range(4):
                    tx = bx + 4 + i * 7
                    ty = by + blooper.height - 5
                    sway = int(5 * (blooper.phase + i * 0.5))
                    pygame.draw.line(self.screen, self.blooper_dark,
                                    (tx, ty), (tx + sway, ty + 15), 3)

                # Eyes
                pygame.draw.circle(self.screen, (255, 255, 255), (bx + 10, by + 12), 6)
                pygame.draw.circle(self.screen, (255, 255, 255), (bx + 22, by + 12), 6)
                pygame.draw.circle(self.screen, (0, 0, 0), (bx + 10, by + 12), 3)
                pygame.draw.circle(self.screen, (0, 0, 0), (bx + 22, by + 12), 3)

        # Draw Cheep Cheeps
        for cheep in self.state.cheeps:
            if cheep.alive:
                cx, cy = int(cheep.pos.x), int(cheep.pos.y)

                # Body (fish shape)
                body_points = [
                    (cx, cy),
                    (cx + cheep.width, cy + cheep.height // 2),
                    (cx, cy + cheep.height),
                ]
                if cheep.vel.x < 0:
                    body_points = [
                        (cx + cheep.width, cy),
                        (cx, cy + cheep.height // 2),
                        (cx + cheep.width, cy + cheep.height),
                    ]

                pygame.draw.polygon(self.screen, self.cheep_color, body_points)

                # Tail
                if cheep.vel.x > 0:
                    pygame.draw.polygon(self.screen, self.cheep_dark,
                                       [(cx, cy + 4), (cx - 10, cy + cheep.height // 2),
                                        (cx, cy + cheep.height - 4)])
                else:
                    pygame.draw.polygon(self.screen, self.cheep_dark,
                                       [(cx + cheep.width, cy + 4),
                                        (cx + cheep.width + 10, cy + cheep.height // 2),
                                        (cx + cheep.width, cy + cheep.height - 4)])

                # Eye
                ex = cx + 20 if cheep.vel.x > 0 else cx + 8
                pygame.draw.circle(self.screen, (255, 255, 255), (ex, cy + 10), 5)
                pygame.draw.circle(self.screen, (0, 0, 0), (ex, cy + 10), 2)

                # Fin
                fx = cx + 12 if cheep.vel.x > 0 else cx + 16
                pygame.draw.polygon(self.screen, self.cheep_dark,
                                   [(fx, cy + cheep.height // 2),
                                    (fx - 5, cy + cheep.height + 4),
                                    (fx + 5, cy + cheep.height + 4)])

        # Draw flag
        pole_start = (int(self.state.flag_x), int(self.state.flag_y - 80))
        pole_end = (int(self.state.flag_x), int(self.state.flag_y + 80))
        pygame.draw.line(self.screen, self.flag_pole_color, pole_start, pole_end, 4)
        flag_points = [
            pole_start,
            (int(self.state.flag_x) - 40, int(self.state.flag_y - 60)),
            (int(self.state.flag_x), int(self.state.flag_y - 40))
        ]
        pygame.draw.polygon(self.screen, self.flag_color, flag_points)

        # Draw player
        if self.state.player.alive:
            px, py = int(self.state.player.pos.x), int(self.state.player.pos.y)
            pw, ph = self.state.player.width, self.state.player.height

            # Swimming animation
            leg_offset = int(4 * (self.state.player.swim_frame % 2))

            # Body
            pygame.draw.rect(self.screen, self.player_color, (px, py, pw, ph))

            # Face
            face_x = px + 6 if self.state.player.facing_right else px + 4
            eye_x = px + 16 if self.state.player.facing_right else px + 6
            pygame.draw.circle(self.screen, (255, 200, 180), (face_x, py + 8), 5)
            pygame.draw.circle(self.screen, (0, 0, 0), (eye_x, py + 8), 2)

            # Hat
            pygame.draw.rect(self.screen, (200, 50, 50), (px + 2, py - 3, pw - 4, 7))

            # Legs (swimming motion)
            pygame.draw.line(self.screen, (150, 50, 50),
                           (px + 6, py + ph - 5 + leg_offset),
                           (px + 6, py + ph + 5 + leg_offset), 4)
            pygame.draw.line(self.screen, (150, 50, 50),
                           (px + pw - 6, py + ph - 5 - leg_offset),
                           (px + pw - 6, py + ph + 5 - leg_offset), 4)

        # Draw bubbles
        for bubble in self.state.player.bubbles:
            alpha = int(255 * (1 - bubble[2]))
            bubble_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(bubble_surf, (*self.bubble_color, alpha), (4, 4), 3)
            self.screen.blit(bubble_surf, (int(bubble[0]), int(bubble[1])))

        # Draw HUD
        score_text = self.font.render(f"Score: {self.state.score}", True, self.text_color)
        self.screen.blit(score_text, (10, 10))

        # Game over / win message
        if self.state.game_over:
            if self.state.win:
                msg = "COMPLETE! Press R to restart"
                color = (100, 255, 100)
            else:
                msg = "GAME OVER! Press R to restart"
                color = (255, 100, 100)

            text = self.font.render(msg, True, color)
            rect = text.get_rect(center=(self.state.width // 2, self.state.height // 2))
            self.screen.blit(text, rect)

        pygame.display.flip()
