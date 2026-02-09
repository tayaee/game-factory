# Vector Mappy Police Chase

A 2D side-scrolling platformer inspired by the classic arcade game Mappy. Navigate a multi-story mansion as a police mouse to retrieve stolen goods while avoiding agile cats.

## Description

Play as Mappy, a police mouse on a mission to recover stolen treasures scattered throughout a multi-story mansion. Use trampolines to bounce between floors, collect valuable items, and outsmart patrolling cats. Doors can be used to stun enemies or create temporary barriers.

## Controls

- **LEFT/RIGHT arrows**: Move horizontally
- **SPACE**: Jump
- **Near door**: Auto-opens/closes doors when standing close
- **R**: Restart game (when game over)
- **ESC**: Quit

## Gameplay

- **Items (gold chests)**: Collect all stolen goods to complete the level (100-500 points each)
- **Trampolines**: Bounce automatically to reach higher floors. Warning: bouncing 3+ times breaks the trampoline
- **Doors**: Auto-toggle when standing near them. Can stun cats or create barriers
- **Cats**: Patrol floors and chase you when they spot you. Touching a cat costs a life
- **Lives**: You have 3 lives. Losing all lives ends the game

## Scoring

- 100-500 points per item collected (varies by item rarity)
- +10 points per trampoline bounce
- +1000 points + level bonus for completing a level
- Time bonus decreases as you play - complete levels quickly for maximum score

## Build & Run

```bash
# Install dependencies
uv sync

# Run the game
uv run python main.py
```

## Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Technical Details

- **Resolution**: 800x600
- **Frame Rate**: 60 FPS
- **State Representation**: Player coordinates, enemy positions, item locations, trampoline states, door states
- **AI Training**: Suitable for reinforcement learning agents learning pathfinding, timing, and hazard avoidance in complex platformer environments
