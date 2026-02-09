"""
Vector Excitebike Stunt Jump
A side-scrolling motocross racer with physics-based stunts and heat management.
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
TRACK_SEGMENT_WIDTH = 40

# Colors
COLOR_BG = (135, 206, 235)  # Sky blue
COLOR_GROUND = (34, 139, 34)  # Forest green
COLOR_TRACK = (160, 82, 45)  # Sienna
COLOR_TRACK_EDGE = (139, 69, 19)
COLOR_MUD = (101, 67, 33)
COLOR_BIKE_FRAME = (220, 20, 60)
COLOR_BIKE_WHEEL = (30, 30, 30)
COLOR_BIKE_SEAT = (50, 50, 50)
COLOR_PLAYER_HELMET = (255, 215, 0)
COLOR_PLAYER_BODY = (70, 130, 180)
COLOR_HEAT_BAR_BG = (80, 80, 80)
COLOR_HEAT_BAR_SAFE = (0, 200, 0)
COLOR_HEAT_BAR_WARNING = (255, 165, 0)
COLOR_HEAT_BAR_DANGER = (255, 0, 0)
COLOR_TEXT = (20, 20, 20)
COLOR_HUD_BG = (255, 255, 255, 180)

# Physics
GRAVITY = 0.4
NORMAL_ACCEL = 0.15
TURBO_ACCEL = 0.35
FRICTION = 0.02
AIR_RESISTANCE = 0.005
MAX_SPEED = 12
TURBO_MAX_SPEED = 16
TILT_SPEED = 3

# Heat system
HEAT_GAIN_TURBO = 0.8
HEAT_COOLING = 0.15
HEAT_COOLING_STOPPED = 0.4
MAX_HEAT = 100
OVERHEAT_PENALTY = 180  # frames

# Track generation
MIN_GROUND_Y = 350
MAX_GROUND_Y = 500
RAMP_HEIGHT = 60
HURDLE_HEIGHT = 25

# Scoring
TIME_LIMIT = 120  # seconds


class GameState(Enum):
    MENU = 0
    PLAYING = 1
    OVERHEATED = 2
    GAME_OVER = 3
    CRASHED = 4


class TrackSegment:
    def __init__(self, x, y_start, y_end, segment_type):
        self.x = x
        self.y_start = y_start
        self.y_end = y_end
        self.type = segment_type  # 'flat', 'ramp_up', 'ramp_down', 'mud', 'hurdle'
        self.width = TRACK_SEGMENT_WIDTH

    def get_y_at(self, local_x):
        """Get ground Y position relative to segment start"""
        if self.type == 'flat':
            return 0
        elif self.type == 'mud':
            return 0
        elif self.type == 'hurdle':
            if local_x < 10 or local_x > 30:
                return 0
            return -HURDLE_HEIGHT
        elif self.type == 'ramp_up':
            return -(local_x / self.width) * RAMP_HEIGHT
        elif self.type == 'ramp_down':
            return -((self.width - local_x) / self.width) * RAMP_HEIGHT
        return 0

    def get_slope_at(self, local_x):
        """Get slope angle in radians"""
        if self.type == 'flat' or self.type == 'mud' or self.type == 'hurdle':
            return 0
        elif self.type == 'ramp_up':
            return -math.atan(RAMP_HEIGHT / self.width)
        elif self.type == 'ramp_down':
            return math.atan(RAMP_HEIGHT / self.width)
        return 0

    def is_mud(self):
        return self.type == 'mud'

    def is_hurdle(self, local_x):
        return self.type == 'hurdle' and 10 <= local_x <= 30


class Bike:
    def __init__(self):
        self.x = 150
        self.y = 300
        self.vx = 0
        self.vy = 0
        self.pitch = 0  # Angle in degrees, negative = leaning forward
        self.on_ground = True
        self.heat = 0
        self.overheat_timer = 0
        self.crashed = False
        self.lane = 1  # 0, 1, 2 (top, middle, bottom)
        self.target_lane = 1
        self.lane_y_offset = 0

    def update(self, track_segments, input_state):
        if self.crashed:
            return

        # Handle overheating
        if self.overheat_timer > 0:
            self.overheat_timer -= 1
            self.heat = max(0, self.heat - HEAT_COOLING_STOPPED)
            if self.overheat_timer == 0:
                self.heat = 0
            return

        # Lane changing
        lane_offset = (self.target_lane - 1) * 60
        self.lane_y_offset += (lane_offset - self.lane_y_offset) * 0.1

        # Get current track segment
        segment = self.get_current_segment(track_segments)
        local_x = (self.x - segment.x) % TRACK_SEGMENT_WIDTH

        # Ground detection
        ground_y = segment.y_start + segment.get_y_at(local_x) - 25 + self.lane_y_offset
        slope = segment.get_slope_at(local_x)

        # Check if landing
        was_airborne = not self.on_ground
        self.on_ground = self.y >= ground_y - 5

        if self.on_ground:
            self.y = ground_y

            # Landing impact
            if was_airborne:
                # Check landing angle
                if abs(self.pitch) > 30:
                    self.crashed = True
                    return

                # Speed reduction on landing
                self.vx *= 0.85

                # Smooth out pitch on ground
                target_pitch = -math.degrees(slope)
                self.pitch += (target_pitch - self.pitch) * 0.3

            # Physics on ground
            if input_state['accelerate']:
                accel = TURBO_ACCEL if input_state['turbo'] else NORMAL_ACCEL
                max_spd = TURBO_MAX_SPEED if input_state['turbo'] else MAX_SPEED

                # Mud slows you down
                if segment.is_mud():
                    accel *= 0.3
                    max_spd *= 0.5

                # Hurdle collision
                if segment.is_hurdle(local_x) and self.vx < 3:
                    self.vx *= 0.5
                    self.crashed = random.random() < 0.3
                    if self.crashed:
                        return

                self.vx += accel
                self.vx = min(self.vx, max_spd)

                # Heat buildup
                if input_state['turbo']:
                    self.heat += HEAT_GAIN_TURBO
                    if self.heat >= MAX_HEAT:
                        self.overheat_timer = OVERHEAT_PENALTY
            else:
                self.vx -= FRICTION
                self.vx = max(0, self.vx)

            # Slope effect
            self.vx -= math.sin(slope) * 0.1

            # Cooling
            self.heat -= HEAT_COOLING if self.vx > 0 else HEAT_COOLING_STOPPED
            self.heat = max(0, min(MAX_HEAT, self.heat))

            # Tilt on ground
            if input_state['tilt_left']:
                self.pitch = min(20, self.pitch + TILT_SPEED)
            elif input_state['tilt_right']:
                self.pitch = max(-20, self.pitch - TILT_SPEED)
            else:
                self.pitch += (-math.degrees(slope) - self.pitch) * 0.2

        else:
            # Air physics
            self.vy += GRAVITY
            self.vx -= AIR_RESISTANCE * self.vx

            # Tilt in air affects trajectory
            tilt_factor = math.sin(math.radians(self.pitch))
            self.vy -= tilt_factor * 0.15
            self.vx -= abs(tilt_factor) * 0.05

            # Air control
            if input_state['tilt_left']:
                self.pitch = min(60, self.pitch + TILT_SPEED)
            elif input_state['tilt_right']:
                self.pitch = max(-60, self.pitch - TILT_SPEED)

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Keep bike on screen horizontally
        if self.x < 50:
            self.x = 50
            self.vx = 0

    def get_current_segment(self, track_segments):
        for seg in track_segments:
            if seg.x <= self.x < seg.x + seg.width:
                return seg
        return track_segments[-1]

    def draw(self, surface, camera_x):
        screen_x = self.x - camera_x + self.lane_y_offset * 0.3
        screen_y = self.y

        # Draw bike
        bike_surf = pygame.Surface((60, 40), pygame.SRCALPHA)

        # Rotate based on pitch
        rotated_surf = pygame.transform.rotate(bike_surf, self.pitch)
        rect = rotated_surf.get_rect(center=(screen_x + 30, screen_y + 20))

        # Draw wheels
        wheel_radius = 10
        back_wheel = (screen_x + 10, screen_y + 30)
        front_wheel = (screen_x + 50, screen_y + 25)
        pygame.draw.circle(surface, COLOR_BIKE_WHEEL, back_wheel, wheel_radius)
        pygame.draw.circle(surface, COLOR_BIKE_WHEEL, front_wheel, wheel_radius)
        pygame.draw.circle(surface, (100, 100, 100), back_wheel, wheel_radius - 3)
        pygame.draw.circle(surface, (100, 100, 100), front_wheel, wheel_radius - 3)

        # Draw frame (simple line)
        frame_start = (screen_x + 10, screen_y + 30)
        frame_end = (screen_x + 50, screen_y + 25)
        pygame.draw.line(surface, COLOR_BIKE_FRAME, frame_start, (screen_x + 30, screen_y + 10), 4)
        pygame.draw.line(surface, COLOR_BIKE_FRAME, (screen_x + 30, screen_y + 10), frame_end, 4)

        # Draw seat
        pygame.draw.ellipse(surface, COLOR_BIKE_SEAT, (screen_x + 20, screen_y + 5, 20, 8))

        # Draw rider
        # Body
        body_center = (screen_x + 30, screen_y - 5)
        pygame.draw.ellipse(surface, COLOR_PLAYER_BODY, (body_center[0] - 8, body_center[1] - 12, 16, 20))

        # Helmet
        helmet_center = (screen_x + 30, screen_y - 20)
        pygame.draw.circle(surface, COLOR_PLAYER_HELMET, helmet_center, 10)

        # Arms (handlebars)
        pygame.draw.line(surface, COLOR_PLAYER_BODY, (screen_x + 30, screen_y - 5),
                        (screen_x + 45, screen_y + 5), 3)
        pygame.draw.line(surface, COLOR_PLAYER_BODY, (screen_x + 30, screen_y - 5),
                        (screen_x + 15, screen_y + 8), 3)

        # Legs
        pygame.draw.line(surface, COLOR_PLAYER_BODY, (screen_x + 30, screen_y + 5),
                        (screen_x + 20, screen_y + 20), 3)
        pygame.draw.line(surface, COLOR_PLAYER_BODY, (screen_x + 30, screen_y + 5),
                        (screen_x + 40, screen_y + 18), 3)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Excitebike Stunt Jump")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset()

    def reset(self):
        self.bike = Bike()
        self.track_segments = []
        self.camera_x = 0
        self.distance = 0
        self.time_left = TIME_LIMIT * FPS
        self.state = GameState.MENU
        self.score = 0
        self.generate_track(100)

    def generate_track(self, num_segments):
        current_y = MIN_GROUND_Y + random.randint(0, 50)

        for i in range(num_segments):
            x = i * TRACK_SEGMENT_WIDTH

            # Determine segment type
            rand = random.random()
            if rand < 0.5:
                seg_type = 'flat'
            elif rand < 0.65:
                seg_type = 'ramp_up'
            elif rand < 0.8:
                seg_type = 'ramp_down'
            elif rand < 0.9:
                seg_type = 'mud'
            else:
                seg_type = 'hurdle'

            # Adjust Y for ramps
            if seg_type == 'ramp_up':
                current_y = min(MAX_GROUND_Y, current_y + RAMP_HEIGHT)
            elif seg_type == 'ramp_down':
                current_y = max(MIN_GROUND_Y, current_y - RAMP_HEIGHT)

            segment = TrackSegment(x, current_y, current_y, seg_type)
            self.track_segments.append(segment)

    def extend_track(self):
        """Generate more track as player progresses"""
        last_seg = self.track_segments[-1]
        self.generate_track(50)

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Tilt only works when airborne
        is_airborne = not self.bike.on_ground

        input_state = {
            'accelerate': keys[pygame.K_RIGHT] and not is_airborne,
            'turbo': keys[pygame.K_z],
            'tilt_left': keys[pygame.K_LEFT] and is_airborne,
            'tilt_right': keys[pygame.K_RIGHT] and is_airborne,
        }

        # Lane switching
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.bike.target_lane > 0:
                    self.bike.target_lane -= 1
                elif event.key == pygame.K_DOWN and self.bike.target_lane < 2:
                    self.bike.target_lane += 1
                elif event.key == pygame.K_r:
                    self.reset()
                elif event.key == pygame.K_SPACE and self.state == GameState.MENU:
                    self.state = GameState.PLAYING
                elif event.key == pygame.K_ESCAPE:
                    return False

        return input_state

    def update(self, input_state):
        if self.state == GameState.PLAYING:
            # Update bike
            self.bike.update(self.track_segments, input_state)

            # Check for crash
            if self.bike.crashed:
                self.state = GameState.CRASHED
                return

            # Check for overheating
            if self.bike.overheat_timer > 0:
                self.state = GameState.OVERHEATED

            # Update camera
            target_camera_x = self.bike.x - 150
            self.camera_x += (target_camera_x - self.camera_x) * 0.1

            # Update distance and score
            new_distance = int(self.bike.x / 10)
            if new_distance > self.distance:
                self.score += (new_distance - self.distance) * 10
                self.distance = new_distance

            # Update time
            self.time_left -= 1

            # Extend track if needed
            if self.bike.x > len(self.track_segments) * TRACK_SEGMENT_WIDTH - 500:
                self.extend_track()

            # Check time limit
            if self.time_left <= 0:
                self.state = GameState.GAME_OVER

    def draw_track(self):
        for segment in self.track_segments:
            screen_x = segment.x - self.camera_x

            # Skip off-screen segments
            if screen_x < -TRACK_SEGMENT_WIDTH or screen_x > SCREEN_WIDTH:
                continue

            # Draw segment
            points = []
            for i in range(TRACK_SEGMENT_WIDTH + 1, 0, -5):
                y_offset = segment.get_y_at(i - 1)
                screen_y = segment.y_start + y_offset
                points.append((screen_x + i - 1, screen_y))

            if len(points) > 1:
                # Draw segment surface
                color = COLOR_MUD if segment.is_mud() else COLOR_TRACK
                poly_points = points + [(points[-1][0], SCREEN_HEIGHT), (points[0][0], SCREEN_HEIGHT)]
                pygame.draw.polygon(self.screen, color, poly_points)
                pygame.draw.lines(self.screen, COLOR_TRACK_EDGE, False, points, 2)

                # Draw hurdle
                if segment.type == 'hurdle':
                    hurdle_x = screen_x + 20
                    hurdle_y = segment.y_start - HURDLE_HEIGHT
                    pygame.draw.rect(self.screen, (200, 50, 50), (hurdle_x, hurdle_y, 8, HURDLE_HEIGHT))

    def draw_hud(self):
        # Background panel
        hud_surface = pygame.Surface((SCREEN_WIDTH, 80), pygame.SRCALPHA)
        hud_surface.fill(COLOR_HUD_BG)
        self.screen.blit(hud_surface, (0, 0))

        # Score
        score_text = self.font.render(f"SCORE: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (20, 10))

        # Distance
        dist_text = self.small_font.render(f"DISTANCE: {self.distance}m", True, COLOR_TEXT)
        self.screen.blit(dist_text, (20, 45))

        # Time
        time_seconds = max(0, self.time_left // FPS)
        time_color = (255, 0, 0) if time_seconds < 10 else COLOR_TEXT
        time_text = self.font.render(f"TIME: {time_seconds}", True, time_color)
        self.screen.blit(time_text, (SCREEN_WIDTH // 2 - 40, 10))

        # Heat bar
        heat_x = SCREEN_WIDTH - 220
        heat_y = 15
        heat_width = 200
        heat_height = 20

        # Background
        pygame.draw.rect(self.screen, COLOR_HEAT_BAR_BG, (heat_x, heat_y, heat_width, heat_height))

        # Fill
        fill_width = int((self.bike.heat / MAX_HEAT) * heat_width)
        if self.bike.heat < 50:
            fill_color = COLOR_HEAT_BAR_SAFE
        elif self.bike.heat < 80:
            fill_color = COLOR_HEAT_BAR_WARNING
        else:
            fill_color = COLOR_HEAT_BAR_DANGER

        if fill_width > 0:
            pygame.draw.rect(self.screen, fill_color, (heat_x, heat_y, fill_width, heat_height))

        # Border
        pygame.draw.rect(self.screen, (50, 50, 50), (heat_x, heat_y, heat_width, heat_height), 2)

        # Label
        heat_label = self.small_font.render("HEAT", True, COLOR_TEXT)
        self.screen.blit(heat_label, (heat_x, heat_y + 25))

        # Turbo indicator
        turbo_text = self.small_font.render("Z: TURBO", True, (255, 100, 0))
        self.screen.blit(turbo_text, (SCREEN_WIDTH - 100, 50))

    def draw_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Title
        title = self.font.render("EXCITEBIKE STUNT JUMP", True, (255, 215, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        # Instructions
        instructions = [
            "PRESS SPACE TO START",
            "",
            "CONTROLS:",
            "RIGHT ARROW - Accelerate",
            "Z - Turbo Boost (Watch Heat!)",
            "UP/DOWN - Change Lane",
            "LEFT/RIGHT - Tilt in Air",
            "",
            "Land flat on ramps to maintain speed!",
            "Avoid overheating your engine!",
        ]

        y = 220
        for line in instructions:
            if line == "PRESS SPACE TO START":
                color = (255, 255, 255)
                font = self.font
            elif line.startswith("CONTROLS"):
                color = (255, 215, 0)
                font = self.font
            else:
                color = (200, 200, 200)
                font = self.small_font

            text = font.render(line, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, rect)
            y += 30

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        if self.state == GameState.CRASHED:
            title = "CRASHED!"
            color = (255, 50, 50)
        else:
            title = "TIME'S UP!"
            color = (255, 255, 255)

        title_text = self.font.render(title, True, color)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_text, title_rect)

        score_text = self.font.render(f"FINAL SCORE: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 260))
        self.screen.blit(score_text, score_rect)

        dist_text = self.small_font.render(f"Distance: {self.distance}m", True, (200, 200, 200))
        dist_rect = dist_text.get_rect(center=(SCREEN_WIDTH // 2, 310))
        self.screen.blit(dist_text, dist_rect)

        restart_text = self.small_font.render("Press R to Restart", True, (255, 215, 0))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, 380))
        self.screen.blit(restart_text, restart_rect)

    def draw(self):
        # Draw background
        self.screen.fill(COLOR_BG)

        # Draw clouds
        for i in range(5):
            cloud_x = (i * 200 - self.camera_x * 0.2) % (SCREEN_WIDTH + 100) - 50
            cloud_y = 50 + i * 30
            pygame.draw.ellipse(self.screen, (255, 255, 255), (cloud_x, cloud_y, 80, 40))
            pygame.draw.ellipse(self.screen, (255, 255, 255), (cloud_x + 20, cloud_y - 10, 60, 35))

        # Draw track
        self.draw_track()

        # Draw bike
        self.bike.draw(self.screen, self.camera_x)

        # Draw HUD
        self.draw_hud()

        # Draw overlays
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state in (GameState.GAME_OVER, GameState.CRASHED):
            self.draw_game_over()
        elif self.state == GameState.OVERHEATED:
            overheat_text = self.font.render("OVERHEATED!", True, (255, 0, 0))
            text_rect = overheat_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(overheat_text, text_rect)

    def run(self):
        running = True
        while running:
            input_state = self.handle_input()
            if input_state is False:
                running = False
            elif isinstance(input_state, dict):
                self.update(input_state)

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
