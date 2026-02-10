# Vector Ice Hockey Slapshot

A fast-paced 1v1 ice hockey duel focusing on physics-based puck control and strategic positioning.

## Rationale

This game targets casual players and AI researchers. It provides a clean environment for testing multi-agent reinforcement learning (MARL) where agents must coordinate movement and shot timing in a low-friction physics environment.

## Details

The game consists of a rectangular rink with two goals on opposite ends. Two circular players (Home and Away) move in a 2D space. A puck starts at the center. Players use physics-based momentum to bump the puck into the opponent's goal.

**Rules:**
1. Friction is extremely low to simulate ice
2. Players cannot cross the center line (simplified version)
3. First to 5 points wins
4. Puck bounces off walls with elastic collisions

## Technical Specs

| Property | Value |
|----------|-------|
| Game Engine | pygame |
| Resolution | 800x400 |
| FPS | 60 |

## Build / Run / Play

```bash
# Build (install dependencies)
uv sync

# Run
uv run main.py

# Stop
Press 'ESC' or close the window
```

### Controls

| Player | Movement | Slapshot |
|--------|----------|----------|
| Player 1 (Blue) | Arrow Keys | Space |
| Player 2 (Red) | WASD | Left Shift |

### Objective

Hit the puck into the enemy goal. Each goal grants 1 point. First to 5 points wins. Scoring a goal resets the puck to the center.

## AI Integration

### State Space
- Player positions (x, y)
- Player velocities (vx, vy)
- Puck position (x, y)
- Puck velocity (vx, vy)
- Scores

### Action Space
- **Continuous**: 2D force vector + slapshot trigger
- **Discrete**: Up, Down, Left, Right, Slapshot

### Reward Structure
- `+1.0` for scoring a goal
- `-1.0` for conceding a goal
- `+0.1` for puck contact
- `-0.01` per step to encourage speed

### API Methods

```python
game = Game()

# Get current state
state = game.get_state()

# Set action for AI player (1 or 2)
game.set_action(player_id=1, action=[vx, vy, slapshot])

# Get reward
reward = game.get_reward(player_id=1)

# Check if game is over
done = game.is_done()
```

## Cleanup

```bash
rm -rf .venv
```
