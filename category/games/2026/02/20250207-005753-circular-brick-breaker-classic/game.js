const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let centerX, centerY, radius;
let animationId;
let gameState = 'start'; // start, playing, gameOver, levelComplete

let score = 0;
let lives = 3;
let level = 1;
let combo = 0;
let lastBrickTime = 0;

const BRICK_ROWS = 5;
const BRICKS_PER_ROW = [8, 12, 16, 20, 24];
const BRICK_COLORS = ['#e91e63', '#9c27b0', '#3f51b5', '#2196f3', '#00bcd4'];
const BRICK_POINTS = [50, 40, 30, 20, 10];

let bricks = [];
let balls = [];
let paddle = { angle: 0 };
let particles = [];

const COMBO_TIMEOUT = 1500;

function resize() {
    const container = document.getElementById('game-container');
    const size = Math.min(container.offsetWidth, container.offsetHeight);
    canvas.width = size * window.devicePixelRatio;
    canvas.height = size * window.devicePixelRatio;
    canvas.style.width = size + 'px';
    canvas.style.height = size + 'px';
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    centerX = size / 2;
    centerY = size / 2;
    radius = size * 0.45;
}

function initBricks() {
    bricks = [];
    const brickThickness = (radius * 0.5) / BRICK_ROWS;

    for (let row = 0; row < BRICK_ROWS; row++) {
        const innerRadius = radius * 0.15 + row * brickThickness;
        const outerRadius = innerRadius + brickThickness - 2;
        const count = BRICKS_PER_ROW[row];
        const arcSize = (Math.PI * 2) / count;

        for (let i = 0; i < count; i++) {
            const startAngle = i * arcSize;
            const endAngle = startAngle + arcSize - 0.02;

            bricks.push({
                row,
                innerRadius,
                outerRadius,
                startAngle,
                endAngle,
                color: BRICK_COLORS[row],
                points: BRICK_POINTS[row],
                alive: true
            });
        }
    }
}

function createBall() {
    const angle = Math.random() * Math.PI * 2;
    const speed = 3 + level * 0.5;

    balls = [{
        x: centerX,
        y: centerY,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        radius: 6,
        active: true,
        trail: []
    }];
}

function createParticles(x, y, color, count = 15) {
    for (let i = 0; i < count; i++) {
        const angle = (Math.PI * 2 / count) * i + Math.random() * 0.5;
        const speed = 2 + Math.random() * 3;
        particles.push({
            x, y,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            radius: 2 + Math.random() * 3,
            color,
            life: 1
        });
    }
}

function updatePaddle(e) {
    if (gameState !== 'playing') return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    paddle.angle = Math.atan2(y, x);
}

function update() {
    if (gameState !== 'playing') return;

    // Update combo
    if (Date.now() - lastBrickTime > COMBO_TIMEOUT && combo > 0) {
        combo = 0;
        updateComboDisplay();
    }

    // Update balls
    balls.forEach(ball => {
        if (!ball.active) return;

        // Update trail
        ball.trail.push({ x: ball.x, y: ball.y });
        if (ball.trail.length > 10) ball.trail.shift();

        ball.x += ball.vx;
        ball.y += ball.vy;

        const distFromCenter = Math.hypot(ball.x - centerX, ball.y - centerY);
        const ballAngle = Math.atan2(ball.y - centerY, ball.x - centerX);

        // Check paddle collision (outer arc)
        const paddleInnerRadius = radius * 0.95;
        const paddleOuterRadius = radius * 0.98;
        const paddleArc = Math.PI * 0.3;

        if (distFromCenter >= paddleInnerRadius && distFromCenter <= paddleOuterRadius) {
            let angleDiff = ballAngle - paddle.angle;
            while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
            while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;

            if (Math.abs(angleDiff) < paddleArc / 2) {
                // Reflect ball toward center
                const normalAngle = ballAngle + Math.PI;
                const speed = Math.hypot(ball.vx, ball.vy);
                ball.vx = Math.cos(normalAngle) * speed;
                ball.vy = Math.sin(normalAngle) * speed;
                ball.x = centerX + Math.cos(ballAngle) * paddleInnerRadius;
                ball.y = centerY + Math.sin(ballAngle) * paddleInnerRadius;

                // Particle effect
                createParticles(ball.x, ball.y, '#4fc3f7', 8);
            }
        }

        // Check brick collision
        bricks.forEach(brick => {
            if (!brick.alive) return;

            if (distFromCenter >= brick.innerRadius && distFromCenter <= brick.outerRadius) {
                let brickAngle = ballAngle;
                while (brickAngle < brick.startAngle) brickAngle += Math.PI * 2;
                while (brickAngle > brick.endAngle + Math.PI * 2) brickAngle -= Math.PI * 2;

                if (brickAngle >= brick.startAngle && brickAngle <= brick.endAngle) {
                    brick.alive = false;

                    // Reflect
                    const normalAngle = distFromCenter < (brick.innerRadius + brick.outerRadius) / 2
                        ? ballAngle + Math.PI
                        : ballAngle;
                    const speed = Math.hypot(ball.vx, ball.vy) * 1.01;
                    ball.vx = Math.cos(normalAngle) * speed;
                    ball.vy = Math.sin(normalAngle) * speed;

                    // Score and combo
                    combo++;
                    lastBrickTime = Date.now();
                    const comboBonus = Math.min(combo, 10);
                    score += brick.points * comboBonus;
                    updateScoreDisplay();

                    createParticles(
                        centerX + Math.cos(ballAngle) * distFromCenter,
                        centerY + Math.sin(ballAngle) * distFromCenter,
                        brick.color
                    );
                }
            }
        });

        // Check if ball is out of bounds
        if (distFromCenter > radius + 20) {
            ball.active = false;
        }
    });

    // Check for game over
    const activeBalls = balls.filter(b => b.active);
    if (activeBalls.length === 0) {
        lives--;
        updateLivesDisplay();

        if (lives <= 0) {
            gameState = 'gameOver';
            document.getElementById('final-score').textContent = score;
            document.getElementById('game-over-screen').classList.remove('hidden');
        } else {
            createBall();
        }
    }

    // Update particles
    particles = particles.filter(p => {
        p.x += p.vx;
        p.y += p.vy;
        p.life -= 0.02;
        p.vx *= 0.98;
        p.vy *= 0.98;
        return p.life > 0;
    });

    // Check level complete
    if (bricks.every(b => !b.alive)) {
        gameState = 'levelComplete';
        document.getElementById('level-score').textContent = score;
        document.getElementById('level-complete-screen').classList.remove('hidden');
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw center circle
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius * 0.08, 0, Math.PI * 2);
    ctx.fillStyle = '#1a1a3a';
    ctx.fill();
    ctx.strokeStyle = '#4fc3f7';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Draw bricks
    bricks.forEach(brick => {
        if (!brick.alive) return;

        ctx.beginPath();
        ctx.arc(centerX, centerY, brick.outerRadius, brick.startAngle, brick.endAngle);
        ctx.arc(centerX, centerY, brick.innerRadius, brick.endAngle, brick.startAngle, true);
        ctx.closePath();
        ctx.fillStyle = brick.color;
        ctx.fill();
        ctx.strokeStyle = 'rgba(255,255,255,0.2)';
        ctx.lineWidth = 1;
        ctx.stroke();
    });

    // Draw particles
    particles.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius * p.life, 0, Math.PI * 2);
        ctx.fillStyle = p.color + Math.floor(p.life * 255).toString(16).padStart(2, '0');
        ctx.fill();
    });

    // Draw ball trail
    balls.forEach(ball => {
        ball.trail.forEach((pos, i) => {
            const alpha = i / ball.trail.length * 0.5;
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, ball.radius * (i / ball.trail.length), 0, Math.PI * 2);
            ctx.fillStyle = `rgba(79, 195, 247, ${alpha})`;
            ctx.fill();
        });
    });

    // Draw balls
    balls.forEach(ball => {
        if (!ball.active) return;

        ctx.beginPath();
        ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
        ctx.fillStyle = '#4fc3f7';
        ctx.fill();
        ctx.shadowColor = '#4fc3f7';
        ctx.shadowBlur = 15;
        ctx.fill();
        ctx.shadowBlur = 0;
    });

    // Draw paddle
    const paddleInnerRadius = radius * 0.95;
    const paddleOuterRadius = radius * 0.98;
    const paddleArc = Math.PI * 0.3;

    ctx.beginPath();
    ctx.arc(centerX, centerY, paddleOuterRadius, paddle.angle - paddleArc / 2, paddle.angle + paddleArc / 2);
    ctx.arc(centerX, centerY, paddleInnerRadius, paddle.angle + paddleArc / 2, paddle.angle - paddleArc / 2, true);
    ctx.closePath();
    ctx.fillStyle = '#4fc3f7';
    ctx.fill();
    ctx.shadowColor = '#4fc3f7';
    ctx.shadowBlur = 20;
    ctx.fill();
    ctx.shadowBlur = 0;
}

function gameLoop() {
    update();
    draw();
    animationId = requestAnimationFrame(gameLoop);
}

function updateScoreDisplay() {
    document.getElementById('score').textContent = score;
    updateComboDisplay();
}

function updateComboDisplay() {
    const comboEl = document.getElementById('combo');
    if (combo > 1) {
        comboEl.textContent = `${combo}x Combo!`;
        comboEl.classList.add('active');
    } else {
        comboEl.classList.remove('active');
    }
}

function updateLivesDisplay() {
    const livesEl = document.querySelectorAll('.life');
    livesEl.forEach((el, i) => {
        el.classList.toggle('lost', i >= lives);
    });
}

function startGame() {
    score = 0;
    lives = 3;
    level = 1;
    combo = 0;
    initBricks();
    createBall();
    updateScoreDisplay();
    updateLivesDisplay();
    document.getElementById('level-display').textContent = 'Level 1';
    document.getElementById('start-screen').classList.add('hidden');
    gameState = 'playing';
}

function nextLevel() {
    level++;
    combo = 0;
    initBricks();
    createBall();
    updateScoreDisplay();
    document.getElementById('level-display').textContent = `Level ${level}`;
    document.getElementById('level-complete-screen').classList.add('hidden');
    gameState = 'playing';
}

function restartGame() {
    startGame();
    document.getElementById('game-over-screen').classList.add('hidden');
}

// Event listeners
window.addEventListener('resize', resize);
canvas.addEventListener('mousemove', updatePaddle);
canvas.addEventListener('touchmove', (e) => {
    e.preventDefault();
    updatePaddle(e.touches[0]);
}, { passive: false });

document.getElementById('start-btn').addEventListener('click', startGame);
document.getElementById('restart-btn').addEventListener('click', restartGame);
document.getElementById('next-level-btn').addEventListener('click', nextLevel);

// Initialize
resize();
initBricks();
gameLoop();
