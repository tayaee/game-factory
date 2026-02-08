"""Main game loop and rendering."""

import pygame
import random
import time
from enum import Enum
from config import *


class GameState(Enum):
    """Game states."""
    PLAYING = "playing"
    WIN = "win"


class Pipe:
    """Represents a pipe segment with type and rotation."""

    # Connection directions for each pipe type at rotation 0
    # Order: North, East, South, West
    CONNECTIONS = {
        PIPE_EMPTY: (0, 0, 0, 0),
        PIPE_STRAIGHT: (1, 0, 1, 0),
        PIPE_ELBOW: (1, 1, 0, 0),
        PIPE_TEE: (1, 1, 0, 1),
        PIPE_CROSS: (1, 1, 1, 1),
        PIPE_SOURCE: (0, 1, 0, 0),
        PIPE_DRAIN: (0, 0, 0, 1),
    }

    def __init__(self, pipe_type, rotation=0):
        self.type = pipe_type
        self.rotation = rotation  # 0, 1, 2, 3 (x90 degrees)

    def rotate(self):
        """Rotate pipe 90 degrees clockwise."""
        self.rotation = (self.rotation + 1) % 4

    def get_connections(self):
        """Get connection directions as bitmask."""
        base_n, base_e, base_s, base_w = self.CONNECTIONS[self.type]

        # Rotate the connections
        dirs = [base_n, base_e, base_s, base_w]
        for _ in range(self.rotation):
            dirs = [dirs[3], dirs[0], dirs[1], dirs[2]]  # Rotate clockwise

        return (DIR_NORTH * dirs[0] | DIR_EAST * dirs[1] |
                DIR_SOUTH * dirs[2] | DIR_WEST * dirs[3])

    def to_int(self):
        """Encode pipe as integer for AI state representation."""
        return self.type * 4 + self.rotation

    @staticmethod
    def from_int(value):
        """Decode integer to pipe."""
        return Pipe(value // 4, value % 4)


class Game:
    """Main game class managing pipe connector logic and rendering."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Plumber Pipe Connector")
        self.clock = pygame.time.Clock()
        self.running = True

        # Game state
        self.state = GameState.PLAYING
        self.grid = [[Pipe(PIPE_EMPTY) for _ in range(GRID_SIZE)]
                     for _ in range(GRID_SIZE)]
        self.source_pos = (0, 0)
        self.drain_pos = (GRID_SIZE - 1, GRID_SIZE - 1)
        self.moves = 0
        self.start_time = 0
        self.elapsed_time = 0
        self.level = 1

        # Animation state
        self.animating_cell = None
        self.animation_progress = 0
        self.animation_start_rotation = 0

        # Cell rectangles for click detection
        self.cell_rects = self._create_cell_rects()

        # Connected cells for rendering
        self.connected_cells = set()

        # Fonts
        self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
        self.status_font = pygame.font.Font(None, STATUS_FONT_SIZE)
        self.instruction_font = pygame.font.Font(None, INSTRUCTION_FONT_SIZE)

        # Initialize first level
        self._generate_level()

    def _create_cell_rects(self):
        """Create collision rectangles for each cell."""
        rects = {}
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = GRID_OFFSET_X + col * CELL_SIZE
                y = GRID_OFFSET_Y + row * CELL_SIZE
                rects[(row, col)] = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        return rects

    def _generate_level(self):
        """Generate a new random level."""
        self.grid = [[Pipe(PIPE_EMPTY) for _ in range(GRID_SIZE)]
                     for _ in range(GRID_SIZE)]

        # Set random source and drain positions
        self.source_pos = (random.randint(0, GRID_SIZE - 1),
                           random.randint(0, GRID_SIZE - 1))
        self.drain_pos = (random.randint(0, GRID_SIZE - 1),
                          random.randint(0, GRID_SIZE - 1))

        while self.drain_pos == self.source_pos:
            self.drain_pos = (random.randint(0, GRID_SIZE - 1),
                              random.randint(0, GRID_SIZE - 1))

        # Place source and drain
        sr, sc = self.source_pos
        dr, dc = self.drain_pos

        self.grid[sr][sc] = Pipe(PIPE_SOURCE, random.randint(0, 3))
        self.grid[dr][dc] = Pipe(PIPE_DRAIN, random.randint(0, 3))

        # Fill remaining cells with random pipes
        pipe_types = [PIPE_STRAIGHT, PIPE_ELBOW, PIPE_TEE, PIPE_CROSS]
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col].type == PIPE_EMPTY:
                    ptype = random.choice(pipe_types)
                    self.grid[row][col] = Pipe(ptype, random.randint(0, 3))

        self.moves = 0
        self.start_time = time.time()
        self.elapsed_time = 0
        self.state = GameState.PLAYING
        self._update_connections()

    def _update_connections(self):
        """Update which cells are connected to source."""
        self.connected_cells = set()

        # BFS from source to find all connected cells
        sr, sc = self.source_pos
        queue = [(sr, sc)]
        visited = {(sr, sc)}

        while queue:
            r, c = queue.pop(0)
            self.connected_cells.add((r, c))

            current = self.grid[r][c].get_connections()

            # Check all four directions
            for dr, dc, dir_mask, opp_mask in [
                (-1, 0, DIR_NORTH, DIR_SOUTH),
                (0, 1, DIR_EAST, DIR_WEST),
                (1, 0, DIR_SOUTH, DIR_NORTH),
                (0, -1, DIR_WEST, DIR_EAST)
            ]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                    if (nr, nc) not in visited:
                        neighbor = self.grid[nr][nc].get_connections()
                        if (current & dir_mask) and (neighbor & opp_mask):
                            visited.add((nr, nc))
                            queue.append((nr, nc))

        # Check if drain is connected
        if self.drain_pos in self.connected_cells:
            self.state = GameState.WIN

    def _get_opposite_direction(self, direction):
        """Get opposite direction."""
        opposites = {
            DIR_NORTH: DIR_SOUTH,
            DIR_SOUTH: DIR_NORTH,
            DIR_EAST: DIR_WEST,
            DIR_WEST: DIR_EAST
        }
        return opposites.get(direction, 0)

    def handle_input(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.animating_cell is None:
                    self._handle_mouse_click(event.pos)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.state == GameState.WIN:
                        self.level += 1
                        self._generate_level()
                    elif self.animating_cell is None:
                        self.level += 1
                        self._generate_level()

    def _handle_mouse_click(self, pos):
        """Handle mouse click on a cell."""
        for (row, col), rect in self.cell_rects.items():
            if rect.collidepoint(pos):
                # Don't rotate source or drain
                if (row, col) not in [self.source_pos, self.drain_pos]:
                    self._start_rotation(row, col)
                break

    def _start_rotation(self, row, col):
        """Start rotation animation for a cell."""
        self.animating_cell = (row, col)
        self.animation_start_rotation = self.grid[row][col].rotation
        self.animation_progress = 0

    def update(self):
        """Update game state."""
        # Update time
        if self.state == GameState.PLAYING:
            self.elapsed_time = time.time() - self.start_time

        # Handle rotation animation
        if self.animating_cell is not None:
            self.animation_progress += ROTATION_ANIMATION_SPEED
            if self.animation_progress >= 1.0:
                # Animation complete
                row, col = self.animating_cell
                self.grid[row][col].rotate()
                self.moves += 1
                self.animating_cell = None
                self.animation_progress = 0
                self._update_connections()

    def _draw_pipe(self, surface, x, y, size, pipe, is_connected):
        """Draw a pipe segment."""
        center = size // 2
        pipe_width = size // 5

        # Get base color
        if pipe.type == PIPE_SOURCE:
            base_color = SOURCE_COLOR
        elif pipe.type == PIPE_DRAIN:
            base_color = DRAIN_COLOR
        elif is_connected:
            base_color = CONNECTED_COLOR
        else:
            base_color = PIPE_COLOR

        # Draw background
        pygame.draw.rect(surface, (40, 40, 45),
                        (x + 2, y + 2, size - 4, size - 4),
                        border_radius=5)

        # Apply rotation for animation
        rotation = pipe.rotation
        if self.animating_cell is not None:
            # Drawing is handled separately for animated cell
            pass

        # Get connections at current rotation
        connections = pipe.get_connections()

        # Draw pipe center
        pygame.draw.circle(surface, base_color, (x + center, y + center), pipe_width // 2)

        # Draw connections
        if connections & DIR_NORTH:
            pygame.draw.rect(surface, base_color,
                            (x + center - pipe_width // 2, y,
                             pipe_width, center))
        if connections & DIR_SOUTH:
            pygame.draw.rect(surface, base_color,
                            (x + center - pipe_width // 2, y + center,
                             pipe_width, center))
        if connections & DIR_EAST:
            pygame.draw.rect(surface, base_color,
                            (x + center, y + center - pipe_width // 2,
                             center, pipe_width))
        if connections & DIR_WEST:
            pygame.draw.rect(surface, base_color,
                            (x, y + center - pipe_width // 2,
                             center, pipe_width))

        # Draw border
        pygame.draw.rect(surface, base_color,
                        (x + 2, y + 2, size - 4, size - 4),
                        width=2, border_radius=5)

        # Draw indicators for source/drain
        if pipe.type == PIPE_SOURCE:
            text = self.instruction_font.render("IN", True, (255, 255, 255))
            text_rect = text.get_rect(center=(x + center, y + center))
            surface.blit(text, text_rect)
        elif pipe.type == PIPE_DRAIN:
            text = self.instruction_font.render("OUT", True, (255, 255, 255))
            text_rect = text.get_rect(center=(x + center, y + center))
            surface.blit(text, text_rect)

    def _draw_pipe_animated(self, surface, x, y, size, pipe, is_connected):
        """Draw an animating pipe segment."""
        center = size // 2
        pipe_width = size // 5

        # Calculate animated rotation
        current_rotation = self.animation_start_rotation + self.animation_progress

        # Get connections at interpolated rotation
        start_pipe = Pipe(pipe.type, self.animation_start_rotation)
        end_pipe = Pipe(pipe.type, (self.animation_start_rotation + 1) % 4)

        start_conns = start_pipe.get_connections()
        end_conns = end_pipe.get_connections()

        # Interpolate connections for smooth animation
        # We'll draw both states and blend them
        alpha = int(self.animation_progress * 255)

        # Draw background
        pygame.draw.rect(surface, (40, 40, 45),
                        (x + 2, y + 2, size - 4, size - 4),
                        border_radius=5)

        # Create a temporary surface for the animation
        temp_surface = pygame.Surface((size, size), pygame.SRCALPHA)

        base_color = CONNECTED_COLOR if is_connected else PIPE_COLOR

        # Draw interpolated pipe
        progress = self.animation_progress

        # Draw center
        pygame.draw.circle(temp_surface, base_color, (center, center), pipe_width // 2)

        # Draw animated connections
        for direction, (dx, dy, is_h) in [
            (DIR_NORTH, (0, -1, False)),
            (DIR_SOUTH, (0, 1, False)),
            (DIR_EAST, (1, 0, True)),
            (DIR_WEST, (-1, 0, True)),
        ]:
            has_start = bool(start_conns & direction)
            has_end = bool(end_conns & direction)

            # Interpolate
            if has_start and has_end:
                # Connection exists in both
                if is_h:
                    pygame.draw.rect(temp_surface, base_color,
                                    (center, center - pipe_width // 2,
                                     center, pipe_width))
                    if dx == -1:
                        pygame.draw.rect(temp_surface, base_color,
                                        (0, center - pipe_width // 2, center, pipe_width))
                    else:
                        pygame.draw.rect(temp_surface, base_color,
                                        (center, center - pipe_width // 2,
                                         center, pipe_width))
                else:
                    pygame.draw.rect(temp_surface, base_color,
                                    (center - pipe_width // 2, center,
                                     pipe_width, center))
                    if dy == -1:
                        pygame.draw.rect(temp_surface, base_color,
                                        (center - pipe_width // 2, 0, pipe_width, center))
                    else:
                        pygame.draw.rect(temp_surface, base_color,
                                        (center - pipe_width // 2, center,
                                         pipe_width, center))
            elif has_start:
                # Fading out
                fade_alpha = int((1 - progress) * 255)
                faded_color = (*base_color, fade_alpha)
                if is_h:
                    if dx == -1:
                        pygame.draw.rect(temp_surface, faded_color,
                                        (0, center - pipe_width // 2, center, pipe_width))
                    else:
                        pygame.draw.rect(temp_surface, faded_color,
                                        (center, center - pipe_width // 2,
                                         center, pipe_width))
                else:
                    if dy == -1:
                        pygame.draw.rect(temp_surface, faded_color,
                                        (center - pipe_width // 2, 0, pipe_width, center))
                    else:
                        pygame.draw.rect(temp_surface, faded_color,
                                        (center - pipe_width // 2, center,
                                         pipe_width, center))
            elif has_end:
                # Fading in
                fade_alpha = int(progress * 255)
                faded_color = (*base_color, fade_alpha)
                if is_h:
                    if dx == -1:
                        pygame.draw.rect(temp_surface, faded_color,
                                        (0, center - pipe_width // 2, center, pipe_width))
                    else:
                        pygame.draw.rect(temp_surface, faded_color,
                                        (center, center - pipe_width // 2,
                                         center, pipe_width))
                else:
                    if dy == -1:
                        pygame.draw.rect(temp_surface, faded_color,
                                        (center - pipe_width // 2, 0, pipe_width, center))
                    else:
                        pygame.draw.rect(temp_surface, faded_color,
                                        (center - pipe_width // 2, center,
                                         pipe_width, center))

        # Draw border
        pygame.draw.rect(temp_surface, base_color,
                        (2, 2, size - 4, size - 4),
                        width=2, border_radius=5)

        surface.blit(temp_surface, (x, y))

    def render(self):
        """Render the game."""
        self.screen.fill(BACKGROUND)

        # Draw title
        title_text = self.status_font.render("PIPE CONNECTOR", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(title_text, title_rect)

        # Draw grid
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = GRID_OFFSET_X + col * CELL_SIZE
                y = GRID_OFFSET_Y + row * CELL_SIZE

                # Draw cell background
                is_connected = (row, col) in self.connected_cells

                # Highlight if connected
                if is_connected:
                    pygame.draw.rect(self.screen, (40, 50, 45),
                                    (x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4),
                                    border_radius=5)

                # Draw pipe
                if self.animating_cell == (row, col):
                    self._draw_pipe_animated(self.screen, x, y, CELL_SIZE,
                                            self.grid[row][col], is_connected)
                else:
                    self._draw_pipe(self.screen, x, y, CELL_SIZE,
                                   self.grid[row][col], is_connected)

        # Draw stats
        moves_text = self.score_font.render(f"Moves: {self.moves}", True, TEXT_COLOR)
        self.screen.blit(moves_text, (50, SCREEN_HEIGHT - 80))

        time_text = self.score_font.render(f"Time: {self.elapsed_time:.1f}s", True, TEXT_COLOR)
        self.screen.blit(time_text, (50, SCREEN_HEIGHT - 50))

        level_text = self.score_font.render(f"Level: {self.level}", True, TEXT_COLOR)
        self.screen.blit(level_text, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 80))

        # Draw status message
        if self.state == GameState.WIN:
            msg = "CONNECTED! Press SPACE for next level"
            msg_text = self.status_font.render(msg, True, CONNECTED_COLOR)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
            self.screen.blit(msg_text, msg_rect)
        else:
            msg = "Connect IN to OUT"
            msg_text = self.instruction_font.render(msg, True, (150, 150, 150))
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
            self.screen.blit(msg_text, msg_rect)

        # Draw controls hint
        controls = "Click to rotate pipes | SPACE: New level | ESC: Quit"
        controls_text = self.instruction_font.render(controls, True, (100, 100, 100))
        controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 25))
        self.screen.blit(controls_text, controls_rect)

        pygame.display.flip()

    def get_observation(self):
        """Return current game state for AI."""
        grid_state = [[self.grid[row][col].to_int()
                       for col in range(GRID_SIZE)]
                      for row in range(GRID_SIZE)]

        return {
            "grid": grid_state,
            "source": self.source_pos,
            "drain": self.drain_pos,
            "connected": list(self.connected_cells),
            "moves": self.moves,
            "time": self.elapsed_time,
            "state": self.state.value,
            "level": self.level
        }

    def step_ai(self, action):
        """
        Execute an AI action and return observation, reward, done.

        Args:
            action: 0-48 corresponding to grid cell (row * 7 + col)

        Returns:
            (observation, reward, done)
        """
        row = action // GRID_SIZE
        col = action % GRID_SIZE

        if self.state == GameState.WIN:
            self.level += 1
            self._generate_level()
            return self.get_observation(), 0, False

        # Skip if source or drain
        if (row, col) in [self.source_pos, self.drain_pos]:
            return self.get_observation(), REWARD_ROTATION, False

        # Rotate the pipe
        prev_connected = self.drain_pos in self.connected_cells
        self.grid[row][col].rotate()
        self.moves += 1
        self._update_connections()

        now_connected = self.drain_pos in self.connected_cells

        reward = REWARD_ROTATION
        done = False

        if now_connected and not prev_connected:
            reward = REWARD_CONNECT
            done = True

        return self.get_observation(), reward, done

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_input()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
