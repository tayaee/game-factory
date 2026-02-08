"""Car physics and rendering module."""

import math
import pygame
from config import *


class Car:
    """Player vehicle with realistic steering physics."""

    def __init__(self, x, y, angle=0):
        self.x = x
        self.y = y
        self.angle = angle  # degrees, 0 = facing right
        self.speed = 0.0
        self.steering_angle = 0.0
        self.distance_traveled = 0.0

    def update(self, inputs):
        """Update car physics based on input state.

        Args:
            inputs: dict with keys 'up', 'down', 'left', 'right' (bool values)
        """
        # Acceleration / Braking
        if inputs['up']:
            self.speed += ACCELERATION
        elif inputs['down']:
            self.speed -= BRAKING
        else:
            # Apply friction when not accelerating
            if self.speed > 0:
                self.speed = max(0, self.speed - FRICTION)
            elif self.speed < 0:
                self.speed = min(0, self.speed + FRICTION)

        # Clamp speed
        self.speed = max(-MAX_SPEED * 0.5, min(MAX_SPEED, self.speed))

        # Steering (only when moving)
        if abs(self.speed) > 0.1:
            steer_direction = 1 if inputs['left'] else -1 if inputs['right'] else 0

            # Reverse steering when going backward
            if self.speed < 0:
                steer_direction *= -1

            if steer_direction != 0:
                self.steering_angle += steer_direction * TURN_SPEED
                self.steering_angle = max(-MAX_TURN_ANGLE,
                                          min(MAX_TURN_ANGLE, self.steering_angle))
            else:
                # Return steering to center
                if self.steering_angle > 0:
                    self.steering_angle = max(0, self.steering_angle - TURN_SPEED)
                else:
                    self.steering_angle = min(0, self.steering_angle + TURN_SPEED)
        else:
            self.steering_angle = 0

        # Apply steering to direction (Ackermann-like)
        # Turn rate depends on speed - slower = more turning capability
        turn_factor = abs(self.speed) / MAX_SPEED
        turn_rate = self.steering_angle * turn_factor * 0.1

        if self.speed < 0:
            turn_rate *= -1

        self.angle += turn_rate

        # Move car
        rad_angle = math.radians(self.angle)
        dx = math.cos(rad_angle) * self.speed
        dy = math.sin(rad_angle) * self.speed

        self.x += dx
        self.y += dy
        self.distance_traveled += abs(self.speed)

    def get_corners(self):
        """Get the four corner points of the car for collision detection.

        Returns:
            list of 4 (x, y) tuples in order: front-left, front-right, back-right, back-left
        """
        rad_angle = math.radians(self.angle)
        cos_a = math.cos(rad_angle)
        sin_a = math.sin(rad_angle)

        # Half dimensions
        hw = CAR_WIDTH / 2
        hl = CAR_LENGTH / 2

        # Local corners relative to center
        corners = [
            (hl, -hw),   # front-left
            (hl, hw),    # front-right
            (-hl, hw),   # back-right
            (-hl, -hw)   # back-left
        ]

        # Rotate and translate
        result = []
        for cx, cy in corners:
            rx = cx * cos_a - cy * sin_a
            ry = cx * sin_a + cy * cos_a
            result.append((self.x + rx, self.y + ry))

        return result

    def get_center(self):
        """Return center position as tuple."""
        return (self.x, self.y)

    def get_heading(self):
        """Return current heading angle in degrees."""
        return self.angle

    def get_rect(self):
        """Return a pygame Rect for rough collision (axis-aligned)."""
        return pygame.Rect(
            self.x - CAR_WIDTH // 2,
            self.y - CAR_LENGTH // 2,
            CAR_WIDTH,
            CAR_LENGTH
        )

    def draw(self, surface):
        """Draw the car on the given surface."""
        corners = self.get_corners()

        # Car body
        pygame.draw.polygon(surface, BLUE, corners)
        pygame.draw.polygon(surface, WHITE, corners, 2)

        # Windshield (front)
        front_center = ((corners[0][0] + corners[1][0]) / 2,
                        (corners[0][1] + corners[1][1]) / 2)
        pygame.draw.circle(surface, CYAN, (int(front_center[0]), int(front_center[1])), 8)

        # Headlights
        for corner in [corners[0], corners[1]]:
            pygame.draw.circle(surface, YELLOW, (int(corner[0]), int(corner[1])), 4)

    def is_stopped(self):
        """Check if car is effectively stopped."""
        return abs(self.speed) < STOP_SPEED_TOLERANCE

    def cast_sensors(self, obstacles, parking_spot):
        """Cast ray sensors for AI perception.

        Args:
            obstacles: list of obstacle rectangles
            parking_spot: ParkingSpot object

        Returns:
            list of sensor distances (normalized 0-1)
        """
        sensor_readings = []

        for i in range(NUM_SENSORS):
            angle_offset = (i - NUM_SENSORS // 2) * (180 / (NUM_SENSORS - 1))
            sensor_angle = math.radians(self.angle + angle_offset)

            # Ray direction
            dx = math.cos(sensor_angle)
            dy = math.sin(sensor_angle)

            min_dist = SENSOR_MAX_DIST

            # Check against obstacles
            for obs in obstacles:
                dist = self._ray_rect_intersection(dx, dy, obs)
                if dist is not None and dist < min_dist:
                    min_dist = dist

            # Check against screen boundaries
            for boundary in [
                (0, 0, SCREEN_WIDTH, 0),  # top
                (0, SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT),  # bottom
                (0, 0, 0, SCREEN_HEIGHT),  # left
                (SCREEN_WIDTH, 0, SCREEN_WIDTH, SCREEN_HEIGHT)  # right
            ]:
                dist = self._ray_line_intersection(dx, dy, boundary)
                if dist is not None and dist < min_dist:
                    min_dist = dist

            sensor_readings.append(min_dist / SENSOR_MAX_DIST)

        return sensor_readings

    def _ray_rect_intersection(self, dx, dy, rect):
        """Calculate intersection distance with a rectangle."""
        # Simple line-rect intersection
        lines = [
            (rect.left, rect.top, rect.right, rect.top),
            (rect.right, rect.top, rect.right, rect.bottom),
            (rect.right, rect.bottom, rect.left, rect.bottom),
            (rect.left, rect.bottom, rect.left, rect.top)
        ]

        min_dist = None
        for line in lines:
            dist = self._ray_line_intersection(dx, dy, line)
            if dist is not None:
                if min_dist is None or dist < min_dist:
                    min_dist = dist

        return min_dist

    def _ray_line_intersection(self, dx, dy, line):
        """Calculate intersection distance with a line segment."""
        x1, y1, x2, y2 = line

        # Ray: P + t * D
        # Line: A + u * (B - A)
        # Solve for t, u

        ray_x, ray_y = self.x, self.y
        line_dx = x2 - x1
        line_dy = y2 - y1

        denom = dx * line_dy - dy * line_dx
        if abs(denom) < 1e-6:
            return None  # Parallel

        t = ((x1 - ray_x) * line_dy - (y1 - ray_y) * line_dx) / denom
        u = ((x1 - ray_x) * dy - (y1 - ray_y) * dx) / denom

        if t > 0 and 0 <= u <= 1:
            return t

        return None
