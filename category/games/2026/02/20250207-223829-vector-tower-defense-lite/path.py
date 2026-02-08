import pygame
from config import PATH_POINTS, PATH_COLOR, GRID_SIZE


class Path:
    def __init__(self):
        self.points = PATH_POINTS
        self.segments = self._create_segments()
        self.rects = self._create_collision_rects()

    def _create_segments(self):
        segments = []
        for i in range(len(self.points) - 1):
            start = self.points[i]
            end = self.points[i + 1]
            segments.append((start, end))
        return segments

    def _create_collision_rects(self):
        rects = []
        path_width = GRID_SIZE
        for start, end in self.segments:
            if start[0] == end[0]:  # Vertical segment
                y1, y2 = min(start[1], end[1]), max(start[1], end[1])
                rects.append(pygame.Rect(start[0] - path_width // 2, y1, path_width, y2 - y1))
            else:  # Horizontal segment
                x1, x2 = min(start[0], end[0]), max(start[0], end[0])
                rects.append(pygame.Rect(x1, start[1] - path_width // 2, x2 - x1, path_width))
        return rects

    def is_on_path(self, x, y, margin=5):
        point = pygame.Rect(x - margin, y - margin, margin * 2, margin * 2)
        for rect in self.rects:
            if rect.colliderect(point):
                return True
        return False

    def get_position_at_distance(self, distance):
        total_length = 0
        for start, end in self.segments:
            segment_length = ((end[0] - start[0])**2 + (end[1] - start[1])**2)**0.5
            if total_length + segment_length >= distance:
                progress = (distance - total_length) / segment_length
                x = start[0] + (end[0] - start[0]) * progress
                y = start[1] + (end[1] - start[1]) * progress
                return x, y
            total_length += segment_length
        return self.points[-1]

    def get_total_length(self):
        total = 0
        for start, end in self.segments:
            total += ((end[0] - start[0])**2 + (end[1] - start[1])**2)**0.5
        return total

    def draw(self, screen):
        path_width = GRID_SIZE
        for start, end in self.segments:
            if start[0] == end[0]:  # Vertical
                y1, y2 = min(start[1], end[1]), max(start[1], end[1])
                pygame.draw.rect(screen, PATH_COLOR, (start[0] - path_width // 2, y1, path_width, y2 - y1))
            else:  # Horizontal
                x1, x2 = min(start[0], end[0]), max(start[0], end[0])
                pygame.draw.rect(screen, PATH_COLOR, (x1, start[1] - path_width // 2, x2 - x1, path_width))

        # Draw direction arrows
        for i, point in enumerate(self.points[1:-1]):
            prev_point = self.points[i]
            next_point = self.points[i + 2]
            arrow_pos = (point[0], point[1])
            pygame.draw.circle(screen, (80, 80, 90), arrow_pos, 8)
