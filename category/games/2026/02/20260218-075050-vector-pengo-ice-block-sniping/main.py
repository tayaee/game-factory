import pygame
import sys
from enum import Enum
from typing import List, Tuple, Optional

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    WAIT = (0, 0)

class EntityType(Enum):
    EMPTY = 0
    WALL = 1
    ICE_BLOCK = 2
    PLAYER = 3
    ENEMY = 4

class EnemyMovePattern(Enum):
    HORIZONTAL = 0
    VERTICAL = 1
    SQUARE = 2

class Enemy:
    def __init__(self, x: int, y: int, pattern: EnemyMovePattern, bounds: Tuple[int, int]):
        self.x = x
        self.y = y
        self.pattern = pattern
        self.bounds = bounds
        self.move_step = 0
        self.speed = 1
        self.direction = 1

    def update(self):
        self.move_step += 1
        if self.move_step >= self.speed:
            self.move_step = 0
            self._move()

    def _move(self):
        width, height = self.bounds
        if self.pattern == EnemyMovePattern.HORIZONTAL:
            new_x = self.x + self.direction
            if new_x <= 1 or new_x >= width - 2:
                self.direction *= -1
            else:
                self.x = new_x
        elif self.pattern == EnemyMovePattern.VERTICAL:
            new_y = self.y + self.direction
            if new_y <= 1 or new_y >= height - 2:
                self.direction *= -1
            else:
                self.y = new_y
        elif self.pattern == EnemyMovePattern.SQUARE:
            if self.direction == 1:  # Right
                if self.x < width - 2:
                    self.x += 1
                else:
                    self.direction = 2
            elif self.direction == 2:  # Down
                if self.y < height - 2:
                    self.y += 1
                else:
                    self.direction = 3
            elif self.direction == 3:  # Left
                if self.x > 1:
                    self.x -= 1
                else:
                    self.direction = 4
            elif self.direction == 4:  # Up
                if self.y > 1:
                    self.y -= 1
                else:
                    self.direction = 1

class GameState:
    def __init__(self, level: int = 1):
        self.grid_width = 16
        self.grid_height = 16
        self.cell_size = 40
        self.screen_width = self.grid_width * self.cell_size
        self.screen_height = self.grid_height * self.cell_size + 60
        self.score = 0
        self.level = level
        self.game_over = False
        self.level_complete = False
        self.steps = 0
        self.setup_level()

    def setup_level(self):
        self.grid = [[EntityType.EMPTY for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.enemies: List[Enemy] = []
        self.player_pos = (1, 1)

        # Walls around the arena
        for x in range(self.grid_width):
            self.grid[0][x] = EntityType.WALL
            self.grid[self.grid_height - 1][x] = EntityType.WALL
        for y in range(self.grid_height):
            self.grid[y][0] = EntityType.WALL
            self.grid[y][self.grid_width - 1] = EntityType.WALL

        # Internal obstacles
        for i in range(3, 6):
            self.grid[i][8] = EntityType.WALL
            self.grid[i][8] = EntityType.WALL

        for i in range(9, 12):
            self.grid[i][8] = EntityType.WALL

        # Ice blocks
        block_positions = [(5, 5), (6, 8), (10, 5), (8, 10), (4, 11), (11, 4)]
        for bx, by in block_positions:
            self.grid[by][bx] = EntityType.ICE_BLOCK

        # Enemies
        self.enemies.append(Enemy(7, 3, EnemyMovePattern.HORIZONTAL, (self.grid_width, self.grid_height)))
        self.enemies.append(Enemy(12, 7, EnemyMovePattern.VERTICAL, (self.grid_width, self.grid_height)))
        self.enemies.append(Enemy(3, 9, EnemyMovePattern.SQUARE, (self.grid_width, self.grid_height)))
        if self.level > 1:
            self.enemies.append(Enemy(10, 12, EnemyMovePattern.HORIZONTAL, (self.grid_width, self.grid_height)))

    def can_move(self, x: int, y: int) -> bool:
        if not (0 <= x < self.grid_width and 0 <= y < self.grid_height):
            return False
        cell = self.grid[y][x]
        return cell in (EntityType.EMPTY, EntityType.ENEMY)

    def slide_block(self, start_x: int, start_y: int, dx: int, dy: int) -> Tuple[int, int]:
        x, y = start_x + dx, start_y + dy
        hit_enemies = []

        while True:
            if not (0 <= x < self.grid_width and 0 <= y < self.grid_height):
                x -= dx
                y -= dy
                break

            cell = self.grid[y][x]
            if cell == EntityType.WALL:
                x -= dx
                y -= dy
                break
            elif cell == EntityType.ICE_BLOCK:
                x -= dx
                y -= dy
                break

            for enemy in self.enemies:
                if enemy.x == x and enemy.y == y:
                    hit_enemies.append(enemy)

            x += dx
            y += dy

        x -= dx
        y -= dy

        for enemy in hit_enemies:
            self.enemies.remove(enemy)
            self.score += 100

        return x, y

    def move_player(self, direction: Direction) -> int:
        if self.game_over or self.level_complete:
            return 0

        dx, dy = direction.value
        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy

        if not (0 <= new_x < self.grid_width and 0 <= new_y < self.grid_height):
            return 0

        target_cell = self.grid[new_y][new_x]

        if target_cell == EntityType.ICE_BLOCK:
            final_x, final_y = self.slide_block(new_x, new_y, dx, dy)
            if (final_x, final_y) != (new_x, new_y):
                self.grid[new_y][new_x] = EntityType.EMPTY
                self.grid[final_y][final_x] = EntityType.ICE_BLOCK
            else:
                return 0

        if target_cell in (EntityType.EMPTY, EntityType.ENEMY):
            self.player_pos = (new_x, new_y)
            self.steps += 1
            self.score -= 1

        if target_cell == EntityType.ENEMY:
            self.game_over = True
            return -1000

        if not self.enemies:
            self.score += 500
            self.level_complete = True

        reward = -1
        enemies_before = len(self.enemies)
        self.update_enemies()
        enemies_after = len(self.enemies)
        if enemies_before > enemies_after:
            reward += 100 * (enemies_before - enemies_after)

        if self.game_over:
            reward = -1000
        elif self.level_complete:
            reward = 500

        return reward

    def update_enemies(self):
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.x == self.player_pos[0] and enemy.y == self.player_pos[1]:
                self.game_over = True
                self.enemies.clear()

    def get_action_space(self) -> List[int]:
        return [0, 1, 2, 3, 4]

    def get_state(self):
        state = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x] == EntityType.WALL:
                    state[y][x] = 1
                elif self.grid[y][x] == EntityType.ICE_BLOCK:
                    state[y][x] = 2
        state[self.player_pos[1]][self.player_pos[0]] = 3
        for enemy in self.enemies:
            state[enemy.y][enemy.x] = 4
        return state

class Renderer:
    COLORS = {
        'background': (20, 20, 30),
        'wall': (100, 100, 100),
        'ice_block': (100, 150, 255),
        'player': (100, 255, 100),
        'enemy': (255, 80, 80),
        'text': (255, 255, 255),
        'ui_bg': (40, 40, 50),
    }

    def __init__(self, game_state: GameState):
        pygame.init()
        pygame.display.set_caption("Vector Pengo: Ice Block Sniping")
        self.screen = pygame.display.set_mode((game_state.screen_width, game_state.screen_height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def draw_cell(self, x: int, y: int, cell_type: EntityType, cell_size: int):
        rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)

        if cell_type == EntityType.WALL:
            pygame.draw.rect(self.screen, self.COLORS['wall'], rect)
            pygame.draw.rect(self.screen, (80, 80, 80), rect, 2)
        elif cell_type == EntityType.ICE_BLOCK:
            pygame.draw.rect(self.screen, self.COLORS['ice_block'], rect)
            pygame.draw.rect(self.screen, (150, 200, 255), rect, 3)
            pygame.draw.line(self.screen, (150, 200, 255), (rect.left + 5, rect.top + 5), (rect.right - 5, rect.bottom - 5), 2)
            pygame.draw.line(self.screen, (150, 200, 255), (rect.right - 5, rect.top + 5), (rect.left + 5, rect.bottom - 5), 2)

    def draw_player(self, x: int, y: int, cell_size: int):
        rect = pygame.Rect(x * cell_size + 5, y * cell_size + 5, cell_size - 10, cell_size - 10)
        pygame.draw.rect(self.screen, self.COLORS['player'], rect)

    def draw_enemy(self, x: int, y: int, cell_size: int):
        center = (x * cell_size + cell_size // 2, y * cell_size + cell_size // 2)
        radius = cell_size // 2 - 5
        pygame.draw.circle(self.screen, self.COLORS['enemy'], center, radius)
        pygame.draw.circle(self.screen, (200, 50, 50), center, radius - 3)

    def draw(self, game_state: GameState):
        self.screen.fill(self.COLORS['background'])

        for y in range(game_state.grid_height):
            for x in range(game_state.grid_width):
                cell = game_state.grid[y][x]
                if cell in (EntityType.WALL, EntityType.ICE_BLOCK):
                    self.draw_cell(x, y, cell, game_state.cell_size)

        for enemy in game_state.enemies:
            self.draw_enemy(enemy.x, enemy.y, game_state.cell_size)

        self.draw_player(game_state.player_pos[0], game_state.player_pos[1], game_state.cell_size)

        ui_height = 60
        ui_rect = pygame.Rect(0, game_state.screen_height - ui_height, game_state.screen_width, ui_height)
        pygame.draw.rect(self.screen, self.COLORS['ui_bg'], ui_rect)

        score_text = self.font.render(f"Score: {game_state.score}", True, self.COLORS['text'])
        level_text = self.small_font.render(f"Level: {game_state.level}", True, self.COLORS['text'])
        enemies_text = self.small_font.render(f"Enemies: {len(game_state.enemies)}", True, self.COLORS['text'])

        self.screen.blit(score_text, (10, game_state.screen_height - 50))
        self.screen.blit(level_text, (200, game_state.screen_height - 40))
        self.screen.blit(enemies_text, (200, game_state.screen_height - 20))

        if game_state.game_over:
            game_over_text = self.font.render("GAME OVER - Press R to Restart", True, (255, 100, 100))
            text_rect = game_over_text.get_rect(center=(game_state.screen_width // 2, game_state.screen_height // 2))
            pygame.draw.rect(self.screen, (0, 0, 0), text_rect.inflate(20, 20))
            self.screen.blit(game_over_text, text_rect)
        elif game_state.level_complete:
            complete_text = self.font.render("LEVEL COMPLETE - Press N for Next Level", True, (100, 255, 100))
            text_rect = complete_text.get_rect(center=(game_state.screen_width // 2, game_state.screen_height // 2))
            pygame.draw.rect(self.screen, (0, 0, 0), text_rect.inflate(20, 20))
            self.screen.blit(complete_text, text_rect)

        pygame.display.flip()

class Game:
    def __init__(self):
        self.game_state = GameState()
        self.renderer = Renderer(self.game_state)

    def handle_input(self) -> Optional[int]:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_r and self.game_state.game_over:
                    self.game_state = GameState()
                    return 0
                if event.key == pygame.K_n and self.game_state.level_complete:
                    self.game_state = GameState(self.game_state.level + 1)
                    return 0
                if event.key == pygame.K_UP:
                    return self.game_state.move_player(Direction.UP)
                if event.key == pygame.K_DOWN:
                    return self.game_state.move_player(Direction.DOWN)
                if event.key == pygame.K_LEFT:
                    return self.game_state.move_player(Direction.LEFT)
                if event.key == pygame.K_RIGHT:
                    return self.game_state.move_player(Direction.RIGHT)
        return 0

    def step(self, action: int) -> Tuple[int, bool]:
        if self.game_state.game_over or self.game_state.level_complete:
            return 0, True

        direction = list(Direction)[action]
        reward = self.game_state.move_player(direction)
        done = self.game_state.game_over or self.game_state.level_complete
        return reward, done

    def reset(self):
        self.game_state = GameState()

    def run(self):
        while True:
            self.renderer.draw(self.game_state)
            self.renderer.clock.tick(60)

            result = self.handle_input()
            if result is None:
                pygame.quit()
                sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
