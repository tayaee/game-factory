# Word Scramble

Unscramble letters to form words in this vocabulary puzzle game.

## Description

Word Scramble is a classic word puzzle game where players must unscramble jumbled letters to form valid words. The game presents scrambled letters that players must rearrange correctly. Features include interactive letter tiles, a hint system for when you're stuck, multiple lives, and progressive difficulty that increases as you solve more words.

## Features

- Interactive letter tiles that respond to mouse clicks
- Hint system revealing one letter at a time (limited uses)
- Multiple lives allowing for mistakes
- Progressive difficulty with level increases
- Score system based on word length
- Reset option to try different letter arrangements

## How to Build

```bash
uv sync
```

## How to Run

```bash
uv run main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `run.sh`

## How to Stop

Close the game window or press Escape.

## Controls

- **Mouse Click**: Select letter tiles in order
- **Enter**: Submit your answer
- **Backspace**: Remove last letter
- **H**: Use a hint (limited)
- **Space**: Reset current word selection
- **R**: Restart game (when game over)
- **Escape**: Quit game

## Rules

- Unscramble the given letters to form a valid word
- Click on letters in the correct order or type them directly
- Submit your answer by pressing Enter
- You have 3 lives - incorrect answers cost a life
- Use hints sparingly - each hint reveals one letter but costs points
- Progress through levels by solving words correctly
- Each level grants 3 additional hints

## Scoring

- Correct word: 10 points per letter + 50 bonus points
- Hint usage: -20 points
- Wrong answer: -10 points

## Tips

- Look for common letter combinations (TH, CH, SH, etc.)
- Try to identify the word's theme from the letters
- Some words have multiple valid solutions
- Save hints for difficult words
- Watch your word length - longer words earn more points

## How to Cleanup

```bash
rm -rf .venv
```
