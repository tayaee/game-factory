# App of the Day

A collection of small applications, each demonstrating different programming concepts and techniques.

## Apps

### Games

| App Name | Description | Folder |
|----------|-------------|--------|
| [Color Flood Puzzle](category/games/2026-02-06-23-color-flood-puzzle/) | An addictive strategy puzzle game to unify all tiles to one color in minimum moves. | `category/games/2026-02-06-23-color-flood-puzzle/` |
| [Neon Snake Retro](category/games/2026-02-06-22-neon-snake-retro/) | Classic snake game with neon visual style. Navigate a snake to eat food while avoiding walls and your own body. | `category/games/2026-02-06-22-neon-snake-retro/` |

## Project Structure

```
app-of-the-day/
├── category/
│   ├── games/
│   │   ├── 2026-02-06-23-color-flood-puzzle/
│   │   │   ├── index.html
│   │   │   ├── style.css
│   │   │   ├── game.js
│   │   │   ├── pyproject.toml
│   │   │   └── README.md
│   │   └── 2026-02-06-22-neon-snake-retro/
│   │       ├── main.py
│   │       ├── pyproject.toml
│   │       └── README.md
│   └── ... (more categories)
└── README.md
```

## Running the Apps

Each app is self-contained with its own dependencies. Navigate to the app's folder and follow the instructions in its README.md.

## Contributing

Apps are organized by category and dated. When adding a new app:

1. Create a new directory following the naming convention: `category/{category}/{YYYY-MM-DD}-{index}-{app-name}/`
2. Include a `main.py` (or appropriate entry point)
3. Add a `README.md` with the app description, how to build/run, and examples
4. Update this root `README.md` to include the new app

## License

MIT
