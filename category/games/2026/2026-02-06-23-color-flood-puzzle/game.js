// Color Flood Puzzle Game
class ColorFloodGame {
    constructor() {
        // Game colors (vibrant, accessible palette)
        this.colors = [
            { name: 'red', value: '#e74c3c' },
            { name: 'orange', value: '#f39c12' },
            { name: 'yellow', value: '#f1c40f' },
            { name: 'green', value: '#2ecc71' },
            { name: 'blue', value: '#3498db' },
            { name: 'purple', value: '#9b59b6' }
        ];

        this.boardSize = 12;
        this.board = [];
        this.moves = 0;
        this.maxMoves = 22;
        this.score = 0;
        this.floodedTiles = new Set();

        // DOM elements
        this.boardElement = document.getElementById('board');
        this.colorButtonsElement = document.getElementById('color-buttons');
        this.movesElement = document.getElementById('moves');
        this.maxMovesElement = document.getElementById('max-moves');
        this.scoreElement = document.getElementById('score');
        this.newGameBtn = document.getElementById('new-game-btn');
        this.sizeBtn = document.getElementById('size-btn');
        this.messageOverlay = document.getElementById('message-overlay');
        this.messageTitle = document.getElementById('message-title');
        this.messageText = document.getElementById('message-text');
        this.messageContent = document.querySelector('.message-content');
        this.overlayBtn = document.getElementById('overlay-btn');

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.createColorButtons();
        this.startNewGame();
    }

    setupEventListeners() {
        this.newGameBtn.addEventListener('click', () => this.startNewGame());
        this.sizeBtn.addEventListener('click', () => this.toggleBoardSize());
        this.overlayBtn.addEventListener('click', () => {
            this.messageOverlay.classList.remove('active');
            this.startNewGame();
        });
    }

    createColorButtons() {
        this.colorButtonsElement.innerHTML = '';
        this.colors.forEach((color, index) => {
            const btn = document.createElement('button');
            btn.className = 'color-btn';
            btn.style.backgroundColor = color.value;
            btn.setAttribute('aria-label', color.name);
            btn.addEventListener('click', () => this.selectColor(index));
            this.colorButtonsElement.appendChild(btn);
        });
    }

    startNewGame() {
        this.moves = 0;
        this.score = 0;
        this.maxMoves = this.boardSize === 12 ? 22 : 30;
        this.floodedTiles.clear();

        // Set max moves based on board size
        this.maxMovesElement.textContent = this.maxMoves;

        // Initialize board with random colors
        this.board = [];
        for (let row = 0; row < this.boardSize; row++) {
            this.board[row] = [];
            for (let col = 0; col < this.boardSize; col++) {
                this.board[row][col] = Math.floor(Math.random() * this.colors.length);
            }
        }

        // Start flooding from top-left corner
        this.floodArea(0, 0, this.board[0][0]);
        this.updateDisplay();
    }

    toggleBoardSize() {
        this.boardSize = this.boardSize === 12 ? 16 : 12;
        this.sizeBtn.textContent = `Board Size: ${this.boardSize}x${this.boardSize}`;
        this.boardElement.className = `board size-${this.boardSize}`;
        this.startNewGame();
    }

    selectColor(colorIndex) {
        if (this.moves >= this.maxMoves) return;

        const currentColor = this.board[0][0];
        if (currentColor === colorIndex) return;

        // Change the color of all flooded tiles
        this.floodedTiles.forEach(key => {
            const [row, col] = key.split(',').map(Number);
            this.board[row][col] = colorIndex;
        });

        // Expand the flooded area
        this.expandFloodedArea(colorIndex);
        this.moves++;

        this.updateDisplay();
        this.checkGameState();
    }

    floodArea(startRow, startCol, targetColor) {
        const visited = new Set();
        const queue = [[startRow, startCol]];

        while (queue.length > 0) {
            const [row, col] = queue.shift();
            const key = `${row},${col}`;

            if (visited.has(key)) continue;
            if (row < 0 || row >= this.boardSize || col < 0 || col >= this.boardSize) continue;
            if (this.board[row][col] !== targetColor) continue;

            visited.add(key);
            this.floodedTiles.add(key);

            // Check all adjacent tiles
            queue.push([row - 1, col]); // Up
            queue.push([row + 1, col]); // Down
            queue.push([row, col - 1]); // Left
            queue.push([row, col + 1]); // Right
        }
    }

    expandFloodedArea(newColor) {
        const newFloodedTiles = new Set();
        const queue = Array.from(this.floodedTiles).map(key => {
            const [row, col] = key.split(',').map(Number);
            return [row, col];
        });

        while (queue.length > 0) {
            const [row, col] = queue.shift();
            const key = `${row},${col}`;

            // Check all adjacent tiles
            const directions = [[-1, 0], [1, 0], [0, -1], [0, 1]];
            for (const [dr, dc] of directions) {
                const newRow = row + dr;
                const newCol = col + dc;
                const newKey = `${newRow},${newCol}`;

                if (newRow < 0 || newRow >= this.boardSize ||
                    newCol < 0 || newCol >= this.boardSize) continue;

                if (!this.floodedTiles.has(newKey) &&
                    !newFloodedTiles.has(newKey) &&
                    this.board[newRow][newCol] === newColor) {
                    newFloodedTiles.add(newKey);
                    queue.push([newRow, newCol]);
                }
            }
        }

        // Add newly flooded tiles
        newFloodedTiles.forEach(key => {
            this.floodedTiles.add(key);
        });
    }

    updateDisplay() {
        // Update info display
        this.movesElement.textContent = this.moves;
        this.scoreElement.textContent = this.score;

        // Update board
        this.boardElement.innerHTML = '';
        for (let row = 0; row < this.boardSize; row++) {
            for (let col = 0; col < this.boardSize; col++) {
                const tile = document.createElement('div');
                tile.className = 'tile';
                const colorIndex = this.board[row][col];
                tile.style.backgroundColor = this.colors[colorIndex].value;
                tile.setAttribute('data-row', row);
                tile.setAttribute('data-col', col);

                // Add flooded animation
                const key = `${row},${col}`;
                if (this.floodedTiles.has(key)) {
                    tile.classList.add('flooded');
                }

                this.boardElement.appendChild(tile);
            }
        }

        // Update color buttons (disable current color button)
        const currentColor = this.board[0][0];
        const colorBtns = this.colorButtonsElement.querySelectorAll('.color-btn');
        colorBtns.forEach((btn, index) => {
            if (index === currentColor || this.moves >= this.maxMoves) {
                btn.classList.add('disabled');
            } else {
                btn.classList.remove('disabled');
            }
        });
    }

    checkGameState() {
        // Check win condition
        if (this.floodedTiles.size === this.boardSize * this.boardSize) {
            this.calculateScore();
            this.showWinMessage();
            return;
        }

        // Check lose condition
        if (this.moves >= this.maxMoves) {
            this.showLoseMessage();
            return;
        }
    }

    calculateScore() {
        // Base score for winning
        const baseScore = 1000;

        // Bonus for remaining moves
        const remainingMoves = this.maxMoves - this.moves;
        const moveBonus = remainingMoves * 50;

        // Board size bonus
        const sizeBonus = this.boardSize === 16 ? 500 : 0;

        this.score = baseScore + moveBonus + sizeBonus;
        this.scoreElement.textContent = this.score;
    }

    showWinMessage() {
        this.messageContent.className = 'message-content win';
        this.messageTitle.textContent = 'Congratulations!';
        this.messageText.textContent = `You cleared the board in ${this.moves} moves! Score: ${this.score}`;
        this.messageOverlay.classList.add('active');
    }

    showLoseMessage() {
        this.messageContent.className = 'message-content lose';
        const percentage = Math.round((this.floodedTiles.size / (this.boardSize * this.boardSize)) * 100);
        this.messageTitle.textContent = 'Game Over';
        this.messageText.textContent = `You used all ${this.maxMoves} moves. ${percentage}% of the board flooded.`;
        this.messageOverlay.classList.add('active');
    }
}

// Initialize game when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ColorFloodGame();
});
