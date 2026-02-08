import pygame
import random
import sys
from enum import IntEnum
from typing import List, Tuple, Optional, Set


class Color(IntEnum):
    EMPTY = 0
    RED = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4


COLOR_MAP = {
    Color.EMPTY: (0, 0, 0),
    Color.RED: (220, 20, 60),
    Color.BLUE: (30, 144, 255),
    Color.GREEN: (34, 139, 34),
    Color.YELLOW: (255, 215, 0),
}

GRID_WIDTH = 6
GRID_HEIGHT = 12
CELL_SIZE = 40
SIDEBAR_WIDTH = 120
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE + SIDEBAR_WIDTH
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 60


class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other):
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))


class FallingPuyo:
    def __init__(self, x: int, y: int, color: Color):
        self.x = x
        self.y = y
        self.color = color


class PuyoPair:
    def __init__(self, x: int, colors: Tuple[Color, Color]):
        self.pivot = FallingPuyo(x, 0, colors[0])
        self.companion = FallingPuyo(x, 1, colors[1])
        self.colors = colors

    def rotate_clockwise(self):
        # Rotate companion around pivot
        dx = self.companion.x - self.pivot.x
        dy = self.companion.y - self.pivot.y

        # 90 degree clockwise rotation: (x, y) -> (-y, x)
        new_dx = -dy
        new_dy = dx

        self.companion.x = self.pivot.x + new_dx
        self.companion.y = self.pivot.y + new_dy

    def rotate_counterclockwise(self):
        # Rotate companion around pivot
        dx = self.companion.x - self.pivot.x
        dy = self.companion.y - self.pivot.y

        # 90 degree counterclockwise rotation: (x, y) -> (y, -x)
        new_dx = dy
        new_dy = -dx

        self.companion.x = self.pivot.x + new_dx
        self.companion.y = self.pivot.y + new_dy

    def get_positions(self) -> List[Tuple[int, int]]:
        return [(self.pivot.x, self.pivot.y), (self.companion.x, self.companion.y)]


class GameState:
    def __init__(self):
        self.grid: List[List[Color]] = [[Color.EMPTY] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.current_pair: Optional[PuyoPair] = None
        self.next_colors: Tuple[Color, Color] = self._generate_colors()
        self.score: int = 0
        self.chain_count: int = 0
        self.game_over: bool = False
        self.drop_timer: float = 0
        self.drop_speed: float = 800  # ms between drops
        self.lock_timer: float = 0
        self.lock_delay: float = 500  # ms to allow movement after landing
        self.is_locked: bool = False
        self.spawn_new_pair()

    def _generate_colors(self) -> Tuple[Color, Color]:
        return (
            Color(random.randint(1, len(Color) - 1)),
            Color(random.randint(1, len(Color) - 1)),
        )

    def spawn_new_pair(self):
        self.current_pair = PuyoPair(GRID_WIDTH // 2 - 1, self.next_colors)
        self.next_colors = self._generate_colors()
        self.is_locked = False

        # Check if spawn position is blocked (game over condition)
        if not self._is_valid_pair(self.current_pair):
            self.game_over = True

    def _is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT

    def _is_occupied(self, x: int, y: int) -> bool:
        if not self._is_valid_position(x, y):
            return True
        return self.grid[y][x] != Color.EMPTY

    def _is_valid_pair(self, pair: PuyoPair) -> bool:
        positions = pair.get_positions()
        for x, y in positions:
            if not self._is_valid_position(x, y) or self._is_occupied(x, y):
                return False
        return True

    def _test_rotation(self, pair: PuyoPair) -> bool:
        positions = pair.get_positions()
        for x, y in positions:
            if not self._is_valid_position(x, y) or self._is_occupied(x, y):
                return False
        return True

    def move_left(self):
        if self.current_pair is None or self.is_locked:
            return
        self.current_pair.pivot.x -= 1
        self.current_pair.companion.x -= 1
        if not self._is_valid_pair(self.current_pair):
            self.current_pair.pivot.x += 1
            self.current_pair.companion.x += 1

    def move_right(self):
        if self.current_pair is None or self.is_locked:
            return
        self.current_pair.pivot.x += 1
        self.current_pair.companion.x += 1
        if not self._is_valid_pair(self.current_pair):
            self.current_pair.pivot.x -= 1
            self.current_pair.companion.x -= 1

    def rotate_pair(self):
        if self.current_pair is None or self.is_locked:
            return

        # Try clockwise rotation
        self.current_pair.rotate_clockwise()
        if not self._is_valid_pair(self.current_pair):
            # Try wall kick offsets
            kicked = False
            for kick_x in [-1, 1, -2, 2]:
                self.current_pair.pivot.x += kick_x
                self.current_pair.companion.x += kick_x
                if self._is_valid_pair(self.current_pair):
                    kicked = True
                    break
                self.current_pair.pivot.x -= kick_x
                self.current_pair.companion.x -= kick_x

            if not kicked:
                # Revert rotation
                self.current_pair.rotate_counterclockwise()

    def soft_drop(self):
        if self.current_pair is None or self.is_locked:
            return
        self._move_down()

    def hard_drop(self):
        if self.current_pair is None:
            return

        while self._move_down():
            pass
        self._lock_pair()

    def _move_down(self) -> bool:
        if self.current_pair is None:
            return False

        self.current_pair.pivot.y += 1
        self.current_pair.companion.y += 1

        if not self._is_valid_pair(self.current_pair):
            self.current_pair.pivot.y -= 1
            self.current_pair.companion.y -= 1
            return False
        return True

    def update(self, dt: float):
        if self.game_over:
            return

        if self.current_pair and not self.is_locked:
            self.drop_timer += dt
            if self.drop_timer >= self.drop_speed:
                self.drop_timer = 0
                if not self._move_down():
                    self.is_locked = True
                    self.lock_timer = 0
        elif self.is_locked:
            self.lock_timer += dt
            if self.lock_timer >= self.lock_delay:
                self._lock_pair()

    def _lock_pair(self):
        if self.current_pair is None:
            return

        positions = self.current_pair.get_positions()
        colors = [self.current_pair.pivot.color, self.current_pair.companion.color]

        for i, (x, y) in enumerate(positions):
            if self._is_valid_position(x, y):
                self.grid[y][x] = colors[i]

        self._process_chain_reactions()
        self.spawn_new_pair()
        self.drop_timer = 0
        self.is_locked = False

    def _process_chain_reactions(self):
        chain = 0
        while self._find_and_clear_groups():
            chain += 1
            self._apply_gravity()

        if chain > 0:
            self.chain_count += chain
            # Exponential scoring: 10 * 2^chain
            self.score += 10 * (2 ** chain)
            # Increase drop speed slightly with chains
            self.drop_speed = max(100, self.drop_speed - 5)

    def _find_and_clear_groups(self) -> bool:
        visited: Set[Tuple[int, int]] = set()
        groups_found = False

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = self.grid[y][x]
                if color != Color.EMPTY and (x, y) not in visited:
                    group = self._find_group(x, y, color, visited)
                    if len(group) >= 4:
                        groups_found = True
                        for gx, gy in group:
                            self.grid[gy][gx] = Color.EMPTY

        return groups_found

    def _find_group(self, x: int, y: int, color: Color, visited: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        group: Set[Tuple[int, int]] = set()
        stack: List[Tuple[int, int]] = [(x, y)]

        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited or (cx, cy) in group:
                continue

            if 0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT:
                if self.grid[cy][cx] == color:
                    group.add((cx, cy))
                    visited.add((cx, cy))

                    # Check neighbors (up, down, left, right)
                    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                        stack.append((cx + dx, cy + dy))

        return group

    def _apply_gravity(self):
        # Make puyos fall down column by column
        for x in range(GRID_WIDTH):
            write_pos = GRID_HEIGHT - 1
            for y in range(GRID_HEIGHT - 1, -1, -1):
                if self.grid[y][x] != Color.EMPTY:
                    if write_pos != y:
                        self.grid[write_pos][x] = self.grid[y][x]
                        self.grid[y][x] = Color.EMPTY
                    write_pos -= 1


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)

    def draw(self, state: GameState):
        self.screen.fill((30, 30, 40))

        # Draw grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, (50, 50, 60), rect, 1)

                color = state.grid[y][x]
                if color != Color.EMPTY:
                    self._draw_puyo(x * CELL_SIZE + CELL_SIZE // 2,
                                   y * CELL_SIZE + CELL_SIZE // 2,
                                   COLOR_MAP[color])

        # Draw current falling pair
        if state.current_pair:
            self._draw_puyo(state.current_pair.pivot.x * CELL_SIZE + CELL_SIZE // 2,
                           state.current_pair.pivot.y * CELL_SIZE + CELL_SIZE // 2,
                           COLOR_MAP[state.current_pair.pivot.color])
            self._draw_puyo(state.current_pair.companion.x * CELL_SIZE + CELL_SIZE // 2,
                           state.current_pair.companion.y * CELL_SIZE + CELL_SIZE // 2,
                           COLOR_MAP[state.current_pair.companion.color])

        # Draw sidebar
        sidebar_x = GRID_WIDTH * CELL_SIZE
        pygame.draw.rect(self.screen, (40, 40, 50),
                        (sidebar_x, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))

        # Draw score
        score_text = self.font.render(f"Score: {state.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (sidebar_x + 10, 20))

        # Draw chain count
        chain_text = self.font.render(f"Chains: {state.chain_count}", True, (255, 255, 255))
        self.screen.blit(chain_text, (sidebar_x + 10, 50))

        # Draw next preview
        next_text = self.font.render("Next:", True, (255, 255, 255))
        self.screen.blit(next_text, (sidebar_x + 10, 90))

        preview_y = 120
        self._draw_puyo(sidebar_x + SIDEBAR_WIDTH // 2, preview_y,
                       COLOR_MAP[state.next_colors[0]], preview=True)
        self._draw_puyo(sidebar_x + SIDEBAR_WIDTH // 2, preview_y + 35,
                       COLOR_MAP[state.next_colors[1]], preview=True)

        # Draw game over
        if state.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.title_font.render("GAME OVER", True, (255, 50, 50))
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(game_over_text, text_rect)

            restart_text = self.font.render("Press R to restart", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(restart_text, restart_rect)

    def _draw_puyo(self, x: int, y: int, color: Tuple[int, int, int], preview: bool = False):
        radius = (CELL_SIZE // 2 - 2) if not preview else 15
        pygame.draw.circle(self.screen, color, (x, y), radius)

        # Add highlight for 3D effect
        highlight_offset = radius // 3
        highlight_radius = radius // 3
        highlight_color = (min(255, color[0] + 80), min(255, color[1] + 80), min(255, color[2] + 80))
        pygame.draw.circle(self.screen, highlight_color,
                          (x - highlight_offset, y - highlight_offset), highlight_radius)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Vector Puyo Chain Reaction")
    clock = pygame.time.Clock()
    renderer = Renderer(screen)

    state = GameState()

    running = True
    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif state.game_over:
                    if event.key == pygame.K_r:
                        state = GameState()
                else:
                    if event.key == pygame.K_LEFT:
                        state.move_left()
                    elif event.key == pygame.K_RIGHT:
                        state.move_right()
                    elif event.key == pygame.K_UP:
                        state.rotate_pair()
                    elif event.key == pygame.K_DOWN:
                        state.soft_drop()
                    elif event.key == pygame.K_SPACE:
                        state.hard_drop()

        state.update(dt)
        renderer.draw(state)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
