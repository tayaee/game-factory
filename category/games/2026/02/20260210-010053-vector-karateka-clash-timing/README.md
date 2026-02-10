# Vector Karateka Clash Timing

A 2D side-view martial arts duel focused on timing and state-based combat.

## Description

Master the art of karate by timing your strikes and blocks in a minimalist duel. Two fighters face each other on a single plane, each with a stance, health bar (Ki), and three primary actions: High Strike, Low Strike, and Block.

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run main.py
```

## How to Stop

Press `ESC` or close the window.

## How to Play

**Goal**: Reduce the opponent's health to zero. Best of 3 rounds wins the match.

- **Left/Right Arrow Keys**: Move character
- **A Key**: High Punch (targets upper body)
- **S Key**: Low Kick (targets legs)
- **D Key**: Block (reduces incoming strike damage)
- **SPACE**: Restart game (when game over)

**Scoring**: 100 points for a successful hit, 500 points for winning a round. Penalties applied for taking damage.

## Technical Details

- **Language**: Python 3.12+
- **Rendering**: pygame-ce
- **State Space**: Player position, Enemy position, Player stance, Enemy stance, Animation frame index
- **Action Space**: Move Left, Move Right, High Punch, Low Kick, Block, Idle
