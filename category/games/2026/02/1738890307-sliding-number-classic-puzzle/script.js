class PuzzleGame {
    constructor() {
        this.size = 4;
        this.tiles = [];
        this.emptyIndex = 15;
        this.moveCount = 0;
        this.seconds = 0;
        this.timerInterval = null;
        this.gameStarted = false;

        this.puzzleElement = document.getElementById('puzzle');
        this.moveCountElement = document.getElementById('moveCount');
        this.timerElement = document.getElementById('timer');
        this.resetBtn = document.getElementById('resetBtn');
        this.successMessage = document.getElementById('successMessage');
        this.finalMovesElement = document.getElementById('finalMoves');
        this.finalTimeElement = document.getElementById('finalTime');

        this.resetBtn.addEventListener('click', () => this.resetGame());
        this.resetGame();
    }

    resetGame() {
        this.moveCount = 0;
        this.seconds = 0;
        this.gameStarted = false;
        this.stopTimer();
        this.updateMoveCount();
        this.updateTimer();
        this.hideSuccess();
        this.initializeTiles();
        this.shuffle();
        this.render();
    }

    initializeTiles() {
        this.tiles = [];
        for (let i = 1; i < this.size * this.size; i++) {
            this.tiles.push(i);
        }
        this.tiles.push(0);
        this.emptyIndex = this.size * this.size - 1;
    }

    shuffle() {
        for (let i = 0; i < 200; i++) {
            const neighbors = this.getNeighbors(this.emptyIndex);
            const randomNeighbor = neighbors[Math.floor(Math.random() * neighbors.length)];
            this.swap(randomNeighbor, this.emptyIndex);
        }
    }

    getNeighbors(index) {
        const neighbors = [];
        const row = Math.floor(index / this.size);
        const col = index % this.size;

        if (row > 0) neighbors.push(index - this.size);
        if (row < this.size - 1) neighbors.push(index + this.size);
        if (col > 0) neighbors.push(index - 1);
        if (col < this.size - 1) neighbors.push(index + 1);

        return neighbors;
    }

    swap(i, j) {
        [this.tiles[i], this.tiles[j]] = [this.tiles[j], this.tiles[i]];
        this.emptyIndex = this.tiles[i] === 0 ? i : j;
    }

    handleClick(index) {
        if (this.isAdjacent(index, this.emptyIndex)) {
            if (!this.gameStarted) {
                this.gameStarted = true;
                this.startTimer();
            }

            this.swap(index, this.emptyIndex);
            this.moveCount++;
            this.updateMoveCount();
            this.render();

            if (this.checkWin()) {
                this.stopTimer();
                this.showSuccess();
            }
        }
    }

    isAdjacent(i, j) {
        const rowI = Math.floor(i / this.size);
        const colI = i % this.size;
        const rowJ = Math.floor(j / this.size);
        const colJ = j % this.size;

        return (Math.abs(rowI - rowJ) + Math.abs(colI - colJ)) === 1;
    }

    checkWin() {
        for (let i = 0; i < this.size * this.size - 1; i++) {
            if (this.tiles[i] !== i + 1) return false;
        }
        return this.tiles[this.size * this.size - 1] === 0;
    }

    render() {
        this.puzzleElement.innerHTML = '';
        this.tiles.forEach((tile, index) => {
            const tileElement = document.createElement('div');
            tileElement.className = tile === 0 ? 'tile empty' : 'tile';
            tileElement.textContent = tile === 0 ? '' : tile;

            if (tile !== 0) {
                tileElement.addEventListener('click', () => this.handleClick(index));
            }

            this.puzzleElement.appendChild(tileElement);
        });
    }

    startTimer() {
        this.timerInterval = setInterval(() => {
            this.seconds++;
            this.updateTimer();
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    updateTimer() {
        const minutes = Math.floor(this.seconds / 60).toString().padStart(2, '0');
        const secs = (this.seconds % 60).toString().padStart(2, '0');
        this.timerElement.textContent = `${minutes}:${secs}`;
    }

    updateMoveCount() {
        this.moveCountElement.textContent = this.moveCount;
    }

    showSuccess() {
        this.finalMovesElement.textContent = this.moveCount;
        this.finalTimeElement.textContent = this.timerElement.textContent;
        this.successMessage.classList.remove('hidden');
    }

    hideSuccess() {
        this.successMessage.classList.add('hidden');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new PuzzleGame();
});
