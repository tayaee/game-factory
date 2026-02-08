# Vector Golf Solitaire Classic

Clear all cards from the tableau by matching numbers in a fast-paced strategic solitaire variant.

## Description

Golf Solitaire is a classic card game that balances luck with strategic decision-making. It is ideal for players who enjoy puzzle-solving and quick gameplay sessions. For AI agents, it provides a discrete state-space challenge for pathfinding and sequence optimization.

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run python main.py
```

## How to Stop

Press ESC or close the window.

## How to Play

**Goal**: Clear all 35 cards from the 7 tableau columns.

**Rules**:
- 35 cards are dealt face-up into 7 columns (5 cards each)
- 17 cards remain in the draw pile
- One card is flipped to the waste pile as the base card
- Click a card at the bottom of any column to play it on the waste pile
- The played card must be exactly one rank higher or lower than the current waste card (e.g., 4 or 6 can be played on 5)
- Aces are low (can only play on 2), Kings are high (can only play on Queen)
- If no moves are available, click the draw pile to get a new base card
- Win by clearing all tableau cards

**Controls**:
- Left-click on a column to play that card
- Left-click on the draw pile to draw a new card
- SPACE: New game (when game over)
- ESC: Quit

**Scoring**:
- +10 points for each card cleared
- +500 bonus for winning
- -50 penalty per card remaining when game ends

## AI Integration

**Observation Space**: State of 7 columns (variable length lists), waste pile top card, and count of remaining draw pile.

**Action Space**: Discrete(8): Click column 0-6 or draw from pile (action 7).

**Reward Structure**:
- +10 for each card cleared
- -1 for drawing from pile
- -5 for invalid move attempt
- +500 for winning
- -100 for losing

## Project Structure

```
category/
└── games/
    └── 2026/
        └── 02/
            └── 1739025611-vector-golf-solitaire-classic/
                ├── main.py
                ├── game.py
                ├── config.py
                ├── pyproject.toml
                ├── README.md
                └── appinfo.json
```

## How to Cleanup

```bash
rm -rf .venv
```
