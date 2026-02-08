import pygame
from config import *

class Frog:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy

        # Keep within horizontal bounds
        if 0 <= new_x <= SCREEN_WIDTH - FROG_SIZE:
            self.x = new_x

        # Keep within vertical bounds
        if 0 <= new_y <= SCREEN_HEIGHT - FROG_SIZE:
            self.y = new_y

    def get_rect(self):
        return pygame.Rect(self.x, self.y, FROG_SIZE, FROG_SIZE)

    def draw(self, screen):
        # Draw frog body (green circle)
        center_x = self.x + FROG_SIZE // 2
        center_y = self.y + FROG_SIZE // 2
        pygame.draw.circle(screen, FROG_COLOR, (center_x, center_y), FROG_SIZE // 2)

        # Draw eyes
        eye_offset = FROG_SIZE // 4
        eye_size = FROG_SIZE // 6
        pygame.draw.circle(screen, (255, 255, 255), (center_x - eye_offset, center_y - eye_offset), eye_size)
        pygame.draw.circle(screen, (255, 255, 255), (center_x + eye_offset, center_y - eye_offset), eye_size)
        pygame.draw.circle(screen, (0, 0, 0), (center_x - eye_offset, center_y - eye_offset), eye_size // 2)
        pygame.draw.circle(screen, (0, 0, 0), (center_x + eye_offset, center_y - eye_offset), eye_size // 2)


class Obstacle:
    def __init__(self, x, y, width, height, speed, obstacle_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.type = obstacle_type

    def update(self):
        self.x += self.speed

        # Wrap around screen
        if self.speed > 0 and self.x > SCREEN_WIDTH:
            self.x = -self.width
        elif self.speed < 0 and self.x < -self.width:
            self.x = SCREEN_WIDTH

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if self.type == "river":
            # Draw log (brown rounded rectangle)
            rect = pygame.Rect(self.x, self.y + 5, self.width, self.height - 10)
            pygame.draw.rect(screen, LOG_COLOR, rect, border_radius=5)
            # Wood grain detail
            pygame.draw.line(screen, (101, 67, 33),
                           (self.x + 10, self.y + 10),
                           (self.x + self.width - 10, self.y + 10), 2)
        else:
            # Draw car
            car_body = pygame.Rect(self.x + 2, self.y + 8, self.width - 4, self.height - 16)
            color = CAR_COLORS[hash(str(self.x)) % len(CAR_COLORS)]
            pygame.draw.rect(screen, color, car_body, border_radius=3)
            # Windows
            pygame.draw.rect(screen, (135, 206, 235),
                           (self.x + self.width // 3, self.y + 10, self.width // 4, self.height - 20))
