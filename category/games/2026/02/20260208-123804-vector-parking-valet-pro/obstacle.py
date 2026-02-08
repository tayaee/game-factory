"""Obstacle module for parking lot objects."""

import math
import pygame
from config import *


class Obstacle:
    """Static obstacle in the parking lot."""

    def __init__(self, x, y, width, height, obstacle_type="barrier"):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = obstacle_type  # "barrier", "car", "wall"

    def draw(self, surface):
        """Draw the obstacle."""
        if self.type == "barrier":
            pygame.draw.rect(surface, DARK_GRAY, self.rect)
            pygame.draw.rect(surface, GRAY, self.rect, 2)
            # Draw stripes
            for i in range(0, self.rect.width + self.rect.height, 20):
                pygame.draw.line(surface, YELLOW, self.rect.topleft,
                                (min(self.rect.right, self.rect.left + i),
                                 min(self.rect.bottom, self.rect.top + i)), 2)

        elif self.type == "car":
            # Draw parked car
            pygame.draw.rect(surface, RED, self.rect, border_radius=5)
            pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=5)

        elif self.type == "wall":
            pygame.draw.rect(surface, (60, 60, 70), self.rect)
            pygame.draw.rect(surface, (100, 100, 110), self.rect, 2)


class ParkingSpot:
    """Target parking spot."""

    def __init__(self, x, y, angle=0):
        self.x = x
        self.y = y
        self.angle = angle  # desired parking angle in degrees
        self.width = SPOT_WIDTH
        self.length = SPOT_LENGTH

    def get_rect(self):
        """Get the parking spot as a rotated rectangle (simplified to rect)."""
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.length // 2,
            self.width,
            self.length
        )

    def get_center(self):
        """Return center position."""
        return (self.x, self.y)

    def is_car_parked(self, car):
        """Check if car is properly parked in this spot.

        Returns:
            tuple: (is_parked: bool, score: float)
        """
        # Distance to center
        dx = car.x - self.x
        dy = car.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # Angle difference
        angle_diff = abs(car.angle - self.angle)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff

        # Check if within tolerance
        position_ok = distance < SPOT_TOLERANCE
        angle_ok = angle_diff < 15  # 15 degree tolerance
        stopped = car.is_stopped()

        # Calculate parking score (0-1)
        dist_score = max(0, 1 - distance / SPOT_TOLERANCE)
        angle_score = max(0, 1 - angle_diff / 15)

        is_parked = position_ok and angle_ok and stopped
        score = (dist_score * 0.5 + angle_score * 0.5)

        return is_parked, score

    def draw(self, surface):
        """Draw the parking spot."""
        # Draw spot outline
        rect = self.get_rect()

        # Green tinted area
        s = pygame.Surface((self.width, self.length), pygame.SRCALPHA)
        s.fill((*GREEN, 50))  # Transparent green
        surface.blit(s, rect.topleft)

        # Border
        pygame.draw.rect(surface, GREEN, rect, 3)

        # Draw 'P' for parking
        font = pygame.font.Font(None, 36)
        text = font.render("P", True, GREEN)
        text_rect = text.get_rect(center=(self.x, self.y))
        surface.blit(text, text_rect)

        # Draw small arrow indicating direction
        rad_angle = math.radians(self.angle)
        arrow_len = 20
        end_x = self.x + math.cos(rad_angle) * arrow_len
        end_y = self.y + math.sin(rad_angle) * arrow_len
        pygame.draw.line(surface, GREEN, (self.x, self.y), (end_x, end_y), 2)
