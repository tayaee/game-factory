"""Main game loop and rendering."""

import pygame
from config import *
from level import Level
from agent import Agent


class Game:
    """Main game class managing rendering and game loop."""

    def __init__(self):
        """Initialize the game."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Lemmings: Path Bridge")
        self.clock = pygame.time.Clock()
        self.running = True

        self.level = Level()
        self.agents = []
        self.spawn_timer = 0
        self.agents_spawned = 0
        self.agents_saved = 0
        self.agents_dead = 0

        self.selected_skill = SKILL_BUILDER
        self.skill_inventory = {
            SKILL_BLOCKER: BLOCKER_COUNT,
            SKILL_BUILDER: BUILDER_COUNT,
            SKILL_BASHER: BASHER_COUNT
        }

        self.game_state = "ready"  # ready, playing, won, lost
        self.game_timer = GAME_TIME_LIMIT
        self.last_time = pygame.time.get_ticks()

        # Fonts
        self.ui_font = pygame.font.Font(None, UI_FONT_SIZE)
        self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
        self.message_font = pygame.font.Font(None, MESSAGE_FONT_SIZE)

    def reset_game(self):
        """Reset game to initial state."""
        self.level = Level()
        self.agents = []
        self.spawn_timer = 0
        self.agents_spawned = 0
        self.agents_saved = 0
        self.agents_dead = 0

        self.selected_skill = SKILL_BUILDER
        self.skill_inventory = {
            SKILL_BLOCKER: BLOCKER_COUNT,
            SKILL_BUILDER: BUILDER_COUNT,
            SKILL_BASHER: BASHER_COUNT
        }

        self.game_state = "ready"
        self.game_timer = GAME_TIME_LIMIT

    def spawn_agent(self):
        """Spawn a new agent at the entry point."""
        if self.agents_spawned >= TOTAL_AGENTS:
            return

        entry_x, entry_y = self.level.get_entry_pixel_pos()
        agent = Agent(entry_x, entry_y, self.agents_spawned)
        self.agents.append(agent)
        self.agents_spawned += 1

    def handle_input(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.game_state == "ready":
                        self.game_state = "playing"
                    elif self.game_state in ("won", "lost"):
                        self.reset_game()
                elif event.key == pygame.K_1:
                    self.selected_skill = SKILL_BLOCKER
                elif event.key == pygame.K_2:
                    self.selected_skill = SKILL_BUILDER
                elif event.key == pygame.K_3:
                    self.selected_skill = SKILL_BASHER
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.game_state == "ready":
                        self.game_state = "playing"
                    elif self.game_state == "playing":
                        self.handle_skill_click(event.pos)

    def handle_skill_click(self, pos):
        """Handle clicking on an agent to apply a skill."""
        if self.selected_skill == SKILL_NONE:
            return

        if self.skill_inventory[self.selected_skill] <= 0:
            return

        mouse_rect = pygame.Rect(pos[0] - 10, pos[1] - 10, 20, 20)

        for agent in self.agents:
            if agent.alive and not agent.saved:
                if mouse_rect.colliderect(agent.get_rect()):
                    if agent.assign_skill(self.selected_skill):
                        self.skill_inventory[self.selected_skill] -= 1
                        break

    def update(self):
        """Update game state."""
        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_time) / 1000.0
        self.last_time = current_time

        if self.game_state == "playing":
            # Update timer
            self.game_timer -= dt
            if self.game_timer <= 0:
                self.game_state = "lost"
                return

            # Spawn agents
            self.spawn_timer += 1
            if self.spawn_timer >= SPAWN_INTERVAL:
                self.spawn_timer = 0
                self.spawn_agent()

            # Get blockers
            blockers = [a for a in self.agents if a.state == "blocked"]

            # Update agents
            for agent in self.agents:
                if agent.alive and not agent.saved:
                    prev_saved = agent.saved
                    agent.update(self.level, blockers)

                    # Check if agent was saved
                    if agent.saved and not prev_saved:
                        self.agents_saved += 1
                    elif not agent.alive:
                        self.agents_dead += 1

            # Check win/lose conditions
            total_spawned = self.agents_spawned
            if total_spawned >= TOTAL_AGENTS:
                active_agents = sum(1 for a in self.agents if a.alive and not a.saved)
                if active_agents == 0:
                    # All agents accounted for
                    saved_ratio = self.agents_saved / TOTAL_AGENTS
                    if saved_ratio >= REQUIRED_SAVED_PERCENTAGE:
                        self.game_state = "won"
                    else:
                        self.game_state = "lost"

    def render(self):
        """Render the game."""
        self.screen.fill(SKY_BLUE)

        # Draw level
        self.level.draw(self.screen)

        # Draw agents
        for agent in self.agents:
            agent.draw(self.screen)

        # Draw UI
        self._draw_ui()

        # Draw game state messages
        if self.game_state == "ready":
            msg = "Press SPACE or CLICK to start"
            self._draw_centered_message(msg, WHITE)
        elif self.game_state == "won":
            msg = f"Victory! {self.agents_saved}/{TOTAL_AGENTS} saved!"
            self._draw_centered_message(msg, GRASS_GREEN)
            sub_msg = "Press SPACE to play again"
            self._draw_centered_message(sub_msg, WHITE, offset=40)
        elif self.game_state == "lost":
            msg = f"Game Over! {self.agents_saved}/{TOTAL_AGENTS} saved"
            self._draw_centered_message(msg, HAZARD_RED)
            sub_msg = "Press SPACE to try again"
            self._draw_centered_message(sub_msg, WHITE, offset=40)

        pygame.display.flip()

    def _draw_ui(self):
        """Draw the UI elements."""
        # Top bar background
        pygame.draw.rect(
            self.screen,
            DARK_GRAY,
            (0, 0, SCREEN_WIDTH, 50)
        )

        # Timer
        minutes = int(self.game_timer // 60)
        seconds = int(self.game_timer % 60)
        timer_text = self.ui_font.render(
            f"Time: {minutes:02d}:{seconds:02d}",
            True,
            WHITE
        )
        self.screen.blit(timer_text, (10, 15))

        # Score
        score_text = self.ui_font.render(
            f"Saved: {self.agents_saved}/{TOTAL_AGENTS}",
            True,
            GRASS_GREEN if self.agents_saved >= TOTAL_AGENTS * REQUIRED_SAVED_PERCENTAGE else WHITE
        )
        self.screen.blit(score_text, (150, 15))

        # Required indicator
        required = int(TOTAL_AGENTS * REQUIRED_SAVED_PERCENTAGE)
        req_text = self.ui_font.render(
            f"Need: {required}",
            True,
            GOLD
        )
        self.screen.blit(req_text, (300, 15))

        # Skill palette
        base_x = 450
        for skill_id in [SKILL_BLOCKER, SKILL_BUILDER, SKILL_BASHER]:
            count = self.skill_inventory[skill_id]
            color = SKILL_COLORS[skill_id]

            # Highlight selected skill
            if skill_id == self.selected_skill:
                pygame.draw.rect(
                    self.screen,
                    WHITE,
                    (base_x - 5, 10, 80, 30),
                    2
                )

            # Skill box
            pygame.draw.rect(
                self.screen,
                color,
                (base_x, 12, 15, 15)
            )

            # Skill name and count
            skill_text = self.ui_font.render(
                f"{SKILL_NAMES[skill_id]}: {count}",
                True,
                WHITE
            )
            self.screen.blit(skill_text, (base_x + 20, 15))

            # Key hint
            key_num = skill_id
            key_text = self.ui_font.render(f"[{key_num}]", True, GRAY)
            self.screen.blit(key_text, (base_x + 70, 15))

            base_x += 110

        # Instructions
        if self.game_state == "playing":
            inst_text = self.ui_font.render("Click agent to use skill", True, GRAY)
            self.screen.blit(inst_text, (SCREEN_WIDTH - 200, 15))

    def _draw_centered_message(self, message, color, offset=0):
        """Draw a centered message on screen."""
        text = self.message_font.render(message, True, color)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + offset))
        self.screen.blit(text, rect)

    def step_ai(self, action):
        """
        Execute an AI action and return observation, reward, done.

        Args:
            action: tuple (agent_index, skill_id) to apply skill to agent
                   or (-1, -1) to do nothing

        Returns:
            (observation, reward, done)
        """
        prev_saved = self.agents_saved
        prev_dead = self.agents_dead

        agent_idx, skill_id = action

        if agent_idx >= 0 and skill_id > 0:
            if 0 <= agent_idx < len(self.agents):
                agent = self.agents[agent_idx]
                if agent.alive and not agent.saved:
                    if self.skill_inventory.get(skill_id, 0) > 0:
                        if agent.assign_skill(skill_id):
                            self.skill_inventory[skill_id] -= 1

        self.update()

        reward = 0
        done = False

        if self.game_state == "playing":
            reward += REWARD_PER_FRAME
            reward += (self.agents_saved - prev_saved) * REWARD_AGENT_SAVED
            reward += (self.agents_dead - prev_dead) * REWARD_AGENT_DIED
        elif self.game_state == "won":
            reward = REWARD_WIN
            done = True
        elif self.game_state == "lost":
            reward = REWARD_LOSE
            done = True

        return self.get_observation(), reward, done

    def get_observation(self):
        """Return current game state for AI."""
        agents_data = []
        for agent in self.agents:
            if agent.alive and not agent.saved:
                agents_data.append({
                    "id": agent.id,
                    "x": agent.x / SCREEN_WIDTH,
                    "y": agent.y / SCREEN_HEIGHT,
                    "vx": agent.vx,
                    "vy": agent.vy,
                    "state": agent.state
                })

        exit_rect = self.level.get_exit_rect()

        return {
            "agents": agents_data,
            "exit": {
                "x": exit_rect.x / SCREEN_WIDTH,
                "y": exit_rect.y / SCREEN_HEIGHT,
                "width": exit_rect.width / SCREEN_WIDTH,
                "height": exit_rect.height / SCREEN_HEIGHT
            },
            "saved": self.agents_saved,
            "dead": self.agents_dead,
            "total": TOTAL_AGENTS,
            "time_remaining": self.game_timer,
            "skills": self.skill_inventory.copy(),
            "game_state": self.game_state
        }

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_input()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
