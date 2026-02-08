class LunarLander {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');

        this.canvas.width = 700;
        this.canvas.height = 500;

        this.GRAVITY = 0.05;
        this.THRUST_POWER = 0.15;
        this.ROTATION_SPEED = 0.05;
        this.MAX_LANDING_SPEED = 2.0;
        this.FUEL_CONSUMPTION = 0.3;

        this.reset();

        this.keys = {};
        this.thrusting = false;
        this.gameOver = false;
        this.gameStarted = false;

        this.fuelBar = document.getElementById('fuelBar');
        this.speedDisplay = document.getElementById('speed');
        this.altitudeDisplay = document.getElementById('altitude');
        this.gameOverScreen = document.getElementById('gameOver');
        this.startScreen = document.getElementById('startScreen');
        this.resultTitle = document.getElementById('resultTitle');
        this.resultMessage = document.getElementById('resultMessage');
        this.resultScore = document.getElementById('resultScore');

        this.bindEvents();
        this.generateTerrain();
        this.render();
    }

    reset() {
        this.lander = {
            x: this.canvas.width / 2,
            y: 50,
            vx: (Math.random() - 0.5) * 2,
            vy: 0,
            angle: 0,
            fuel: 100
        };

        this.particles = [];
        this.gameOver = false;
        this.thrusting = false;
        this.generateTerrain();
        this.updateHUD();
    }

    bindEvents() {
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                this.thrusting = true;
            }
            this.keys[e.code] = true;
        });

        document.addEventListener('keyup', (e) => {
            if (e.code === 'Space') {
                this.thrusting = false;
            }
            this.keys[e.code] = false;
        });

        this.canvas.addEventListener('mousedown', () => this.thrusting = true);
        this.canvas.addEventListener('mouseup', () => this.thrusting = false);
        this.canvas.addEventListener('mouseleave', () => this.thrusting = false);

        this.canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.thrusting = true;
        });
        this.canvas.addEventListener('touchend', () => this.thrusting = false);

        document.getElementById('startBtn').addEventListener('click', () => {
            this.startScreen.classList.add('hidden');
            this.gameStarted = true;
            this.gameLoop();
        });

        document.getElementById('restartBtn').addEventListener('click', () => {
            this.gameOverScreen.classList.add('hidden');
            this.reset();
            this.gameStarted = true;
        });
    }

    generateTerrain() {
        this.terrain = [];
        this.padStart = Math.floor(this.canvas.width * 0.3 + Math.random() * this.canvas.width * 0.4);
        this.padWidth = 80;
        this.padEnd = this.padStart + this.padWidth;

        const segments = 70;
        const segmentWidth = this.canvas.width / segments;

        let y = this.canvas.height * 0.3;

        for (let i = 0; i <= segments; i++) {
            const x = i * segmentWidth;

            if (x >= this.padStart && x <= this.padEnd) {
                this.terrain.push({ x, y: this.canvas.height - 40, isPad: true });
            } else {
                y += (Math.random() - 0.5) * 30;
                y = Math.max(this.canvas.height * 0.2, Math.min(this.canvas.height * 0.5, y));
                this.terrain.push({ x, y: this.canvas.height - y, isPad: false });
            }
        }
    }

    update() {
        if (!this.gameStarted || this.gameOver) return;

        this.lander.vy += this.GRAVITY;

        if (this.thrusting && this.lander.fuel > 0) {
            const thrustX = Math.sin(this.lander.angle) * this.THRUST_POWER;
            const thrustY = -Math.cos(this.lander.angle) * this.THRUST_POWER;

            this.lander.vx += thrustX;
            this.lander.vy += thrustY;
            this.lander.fuel -= this.FUEL_CONSUMPTION;

            this.spawnParticles();
        }

        this.lander.x += this.lander.vx;
        this.lander.y += this.lander.vy;

        if (this.lander.x < 20) {
            this.lander.x = 20;
            this.lander.vx *= -0.5;
        }
        if (this.lander.x > this.canvas.width - 20) {
            this.lander.x = this.canvas.width - 20;
            this.lander.vx *= -0.5;
        }

        if (this.lander.y < 0) {
            this.lander.y = 0;
            this.lander.vy = 0;
        }

        this.checkCollision();
        this.updateParticles();
        this.updateHUD();
    }

    spawnParticles() {
        for (let i = 0; i < 3; i++) {
            const spread = (Math.random() - 0.5) * 0.5;
            this.particles.push({
                x: this.lander.x - Math.sin(this.lander.angle + spread) * 15,
                y: this.lander.y + Math.cos(this.lander.angle + spread) * 15,
                vx: -Math.sin(this.lander.angle + spread) * 3 + (Math.random() - 0.5),
                vy: Math.cos(this.lander.angle + spread) * 3 + (Math.random() - 0.5),
                life: 1,
                size: 3 + Math.random() * 3
            });
        }
    }

    updateParticles() {
        this.particles = this.particles.filter(p => {
            p.x += p.vx;
            p.y += p.vy;
            p.life -= 0.03;
            p.size *= 0.95;
            return p.life > 0;
        });
    }

    checkCollision() {
        for (let i = 0; i < this.terrain.length - 1; i++) {
            const t1 = this.terrain[i];
            const t2 = this.terrain[i + 1];

            if (this.lander.x >= t1.x && this.lander.x <= t2.x) {
                const terrainY = t1.y + (t2.y - t1.y) * (this.lander.x - t1.x) / (t2.x - t1.x);

                if (this.lander.y + 15 >= terrainY) {
                    if (t1.isPad && t2.isPad) {
                        const speed = Math.sqrt(this.lander.vx ** 2 + this.lander.vy ** 2);

                        if (speed <= this.MAX_LANDING_SPEED && Math.abs(this.lander.angle) < 0.3) {
                            this.endGame(true);
                        } else {
                            this.endGame(false, speed > this.MAX_LANDING_SPEED ? 'Too fast!' : 'Bad angle!');
                        }
                    } else {
                        this.endGame(false, 'Crashed into terrain!');
                    }
                    return;
                }
            }
        }
    }

    endGame(success, message = '') {
        this.gameOver = true;

        if (success) {
            const score = Math.floor(
                this.lander.fuel * 10 +
                (this.MAX_LANDING_SPEED - Math.abs(this.lander.vy)) * 100 +
                (1 - Math.abs(this.lander.angle)) * 50
            );
            this.resultTitle.textContent = 'Successful Landing!';
            this.resultTitle.style.color = '#4caf50';
            this.resultMessage.textContent = 'Nice piloting!';
            this.resultScore.textContent = `Score: ${score}`;
        } else {
            this.resultTitle.textContent = 'Game Over';
            this.resultTitle.style.color = '#f44336';
            this.resultMessage.textContent = message;
            this.resultScore.textContent = '';

            for (let i = 0; i < 50; i++) {
                this.particles.push({
                    x: this.lander.x,
                    y: this.lander.y,
                    vx: (Math.random() - 0.5) * 10,
                    vy: (Math.random() - 0.5) * 10,
                    life: 1,
                    size: 5 + Math.random() * 10,
                    color: Math.random() > 0.5 ? '#ff5722' : '#ffc107'
                });
            }
        }

        setTimeout(() => {
            this.gameOverScreen.classList.remove('hidden');
        }, 500);
    }

    updateHUD() {
        this.fuelBar.style.width = `${Math.max(0, this.lander.fuel)}%`;

        const speed = Math.sqrt(this.lander.vx ** 2 + this.lander.vy ** 2);
        this.speedDisplay.textContent = speed.toFixed(1);
        this.speedDisplay.style.color = speed > this.MAX_LANDING_SPEED ? '#ff5722' : '#4fc3f7';

        const altitude = Math.max(0, this.canvas.height - 40 - this.lander.y);
        this.altitudeDisplay.textContent = Math.floor(altitude);
    }

    render() {
        this.ctx.fillStyle = '#0a0a15';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        this.drawStars();
        this.drawTerrain();
        this.drawParticles();

        if (!this.gameOver || this.lander.fuel > 0) {
            this.drawLander();
        }

        if (this.thrusting && this.lander.fuel > 0 && !this.gameOver) {
            this.drawThrust();
        }
    }

    drawStars() {
        this.ctx.fillStyle = '#ffffff';
        for (let i = 0; i < 50; i++) {
            const x = (i * 137) % this.canvas.width;
            const y = (i * 251) % (this.canvas.height * 0.7);
            const size = (i % 3) * 0.5 + 0.5;
            this.ctx.globalAlpha = 0.3 + (i % 5) * 0.1;
            this.ctx.fillRect(x, y, size, size);
        }
        this.ctx.globalAlpha = 1;
    }

    drawTerrain() {
        this.ctx.beginPath();
        this.ctx.moveTo(0, this.canvas.height);
        this.ctx.lineTo(this.terrain[0].x, this.terrain[0].y);

        for (let i = 1; i < this.terrain.length; i++) {
            this.ctx.lineTo(this.terrain[i].x, this.terrain[i].y);
        }

        this.ctx.lineTo(this.canvas.width, this.canvas.height);
        this.ctx.closePath();

        this.ctx.fillStyle = '#4a4a5a';
        this.ctx.fill();

        this.ctx.strokeStyle = '#6a6a7a';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();

        this.ctx.fillStyle = '#4caf50';
        this.ctx.fillRect(this.padStart, this.canvas.height - 40, this.padWidth, 4);

        this.ctx.fillStyle = '#81c784';
        this.ctx.fillRect(this.padStart + 10, this.canvas.height - 42, this.padWidth - 20, 2);
    }

    drawParticles() {
        this.particles.forEach(p => {
            const alpha = p.life;
            if (p.color) {
                this.ctx.fillStyle = p.color;
            } else {
                const r = Math.floor(255 * p.life);
                const g = Math.floor(150 * p.life);
                this.ctx.fillStyle = `rgb(${r}, ${g}, 50)`;
            }
            this.ctx.globalAlpha = alpha;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            this.ctx.fill();
        });
        this.ctx.globalAlpha = 1;
    }

    drawLander() {
        this.ctx.save();
        this.ctx.translate(this.lander.x, this.lander.y);
        this.ctx.rotate(this.lander.angle);

        this.ctx.fillStyle = '#e0e0e0';
        this.ctx.strokeStyle = '#9e9e9e';
        this.ctx.lineWidth = 2;

        this.ctx.beginPath();
        this.ctx.moveTo(0, -15);
        this.ctx.lineTo(12, 10);
        this.ctx.lineTo(8, 15);
        this.ctx.lineTo(-8, 15);
        this.ctx.lineTo(-12, 10);
        this.ctx.closePath();
        this.ctx.fill();
        this.ctx.stroke();

        this.ctx.fillStyle = '#2196f3';
        this.ctx.beginPath();
        this.ctx.arc(0, 0, 5, 0, Math.PI * 2);
        this.ctx.fill();

        this.ctx.strokeStyle = '#ffc107';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.moveTo(-8, -5);
        this.ctx.lineTo(-15, -10);
        this.ctx.moveTo(8, -5);
        this.ctx.lineTo(15, -10);
        this.ctx.stroke();

        this.ctx.fillStyle = '#ff5722';
        this.ctx.fillRect(-3, -18, 6, 4);

        this.ctx.restore();
    }

    drawThrust() {
        this.ctx.save();
        this.ctx.translate(this.lander.x, this.lander.y);
        this.ctx.rotate(this.lander.angle);

        const gradient = this.ctx.createLinearGradient(0, 15, 0, 35);
        gradient.addColorStop(0, '#ff5722');
        gradient.addColorStop(0.5, '#ffc107');
        gradient.addColorStop(1, 'transparent');

        this.ctx.fillStyle = gradient;
        this.ctx.beginPath();
        this.ctx.moveTo(-5, 15);
        this.ctx.lineTo(5, 15);
        this.ctx.lineTo(0, 30 + Math.random() * 10);
        this.ctx.closePath();
        this.ctx.fill();

        this.ctx.restore();
    }

    gameLoop() {
        this.update();
        this.render();
        requestAnimationFrame(() => this.gameLoop());
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new LunarLander();
});
