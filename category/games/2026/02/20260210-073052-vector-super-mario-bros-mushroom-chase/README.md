# Vector Super Mario Bros: Mushroom Chase

Catch the magic mushroom across moving platforms before it falls into the abyss.

## Rationale

This game focuses on tracking a dynamic objective while navigating complex terrain. It targets users who enjoy classic platforming mechanics and serves as an excellent environment for AI agents to learn predictive movement and spatial navigation.

## Details

The game is a single-screen platformer. A Super Mushroom spawns at a random location and moves horizontally, bouncing off walls and falling due to gravity. The player (Mario) must catch the mushroom to score points. The environment consists of multiple floating platforms with gaps. If the mushroom falls off the bottom of the screen, it is lost and a new one spawns with a score penalty. The game features 2D vector graphics with a professional monochrome or high-contrast dual-tone palette.

**Game Rules:**
- Catching a mushroom: +100 points
- Mushroom falling off-screen: -50 points
- Win condition: Reach 1000 points
- Lose condition: Lose 5 mushrooms
- Gravity affects both player and mushroom
- Mushroom reverses direction upon hitting walls

## Technical Specs

| Property | Value |
|----------|-------|
| Game Engine | pygame |
| Resolution | 800x600 |
| FPS | 60 |

## Build / Run / Play

```bash
# Install dependencies
uv sync

# Run
uv run main.py

# Stop
Press ESC or close the window
```

### Controls

| Action | Key |
|--------|-----|
| Move Left | Left Arrow |
| Move Right | Right Arrow |
| Jump | Space |
| Restart (Game Over) | Space |
| Quit | ESC |

### Objective

Catch the bouncing mushroom to score points. Each catch grants +100 points. If the mushroom falls off the bottom of the screen, you lose it (-50 points) and a new one spawns. The game ends when you reach 1000 points (win) or lose 5 mushrooms (game over).

## AI Integration

### State Space
- Player position (x, y)
- Player velocity (vx, vy)
- Player on_ground flag
- Mushroom position (x, y)
- Mushroom velocity (vx, vy)
- Mushroom on_ground flag
- Score
- Mushrooms lost

### Action Space
- **Discrete**: Left, Right, Jump

### Reward Structure
- `+1.0` for catching a mushroom
- `-0.5` for losing a mushroom
- `+0.01` for being close to the mushroom
- `-0.001` per step to encourage speed

### API Methods

```python
game = Game()

# Get current state
state = game.get_state()

# Set action for AI player
game.set_action([move_x, jump])

# Get reward
reward = game.get_reward()

# Check if game is over
done = game.is_done()
```

## Cleanup

```bash
rm -rf .venv
```
