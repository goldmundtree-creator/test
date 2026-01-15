const canvas = document.getElementById('game-canvas');
const ctx = canvas.getContext('2d');
const nextCanvas = document.getElementById('next-canvas');
const nextCtx = nextCanvas.getContext('2d');

const ROWS = 20;
const COLS = 10;
const BLOCK_SIZE = 30;

const COLORS = [
    null,
    '#FF0D72', // I
    '#0DC2FF', // J
    '#0DFF72', // L
    '#F538FF', // O
    '#FF8E0D', // S
    '#FFE138', // T
    '#3877FF'  // Z
];

const SHAPES = [
    [],
    [[1, 1, 1, 1]], // I
    [[2, 0, 0], [2, 2, 2]], // J
    [[0, 0, 3], [3, 3, 3]], // L
    [[4, 4], [4, 4]], // O
    [[0, 5, 5], [5, 5, 0]], // S
    [[0, 6, 0], [6, 6, 6]], // T
    [[7, 7, 0], [0, 7, 7]]  // Z
];

let board = [];
let score = 0;
let level = 1;
let lines = 0;
let currentPiece = null;
let nextPiece = null;
let gameOver = false;
let isPaused = false;
let dropCounter = 0;
let dropInterval = 1000;
let lastTime = 0;

function createBoard() {
    board = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
}

function drawBlock(ctx, x, y, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 2;
    ctx.strokeRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.fillRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE / 2, BLOCK_SIZE / 2);
}

function drawBoard() {
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    for (let row = 0; row < ROWS; row++) {
        for (let col = 0; col < COLS; col++) {
            if (board[row][col]) {
                drawBlock(ctx, col, row, COLORS[board[row][col]]);
            }
        }
    }
}

function drawPiece(piece, offsetX = 0, offsetY = 0, context = ctx) {
    piece.shape.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value) {
                drawBlock(context, piece.x + x + offsetX, piece.y + y + offsetY, COLORS[value]);
            }
        });
    });
}

function drawNextPiece() {
    nextCtx.fillStyle = '#f0f0f0';
    nextCtx.fillRect(0, 0, nextCanvas.width, nextCanvas.height);

    if (nextPiece) {
        const offsetX = (4 - nextPiece.shape[0].length) / 2;
        const offsetY = (4 - nextPiece.shape.length) / 2;

        nextPiece.shape.forEach((row, y) => {
            row.forEach((value, x) => {
                if (value) {
                    drawBlock(nextCtx, x + offsetX, y + offsetY, COLORS[value]);
                }
            });
        });
    }
}

function createPiece() {
    const type = Math.floor(Math.random() * 7) + 1;
    return {
        shape: SHAPES[type].map(row => [...row]),
        x: Math.floor(COLS / 2) - Math.floor(SHAPES[type][0].length / 2),
        y: 0,
        type: type
    };
}

function collision(piece, offsetX = 0, offsetY = 0) {
    for (let y = 0; y < piece.shape.length; y++) {
        for (let x = 0; x < piece.shape[y].length; x++) {
            if (piece.shape[y][x]) {
                const newX = piece.x + x + offsetX;
                const newY = piece.y + y + offsetY;

                if (newX < 0 || newX >= COLS || newY >= ROWS) {
                    return true;
                }

                if (newY >= 0 && board[newY][newX]) {
                    return true;
                }
            }
        }
    }
    return false;
}

function merge() {
    currentPiece.shape.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value) {
                const boardY = currentPiece.y + y;
                const boardX = currentPiece.x + x;
                if (boardY >= 0) {
                    board[boardY][boardX] = value;
                }
            }
        });
    });
}

function rotate(piece) {
    const rotated = piece.shape[0].map((_, i) =>
        piece.shape.map(row => row[i]).reverse()
    );

    const previousShape = piece.shape;
    piece.shape = rotated;

    let offset = 0;
    while (collision(piece, offset)) {
        offset = offset > 0 ? -(offset + 1) : -offset + 1;
        if (Math.abs(offset) > piece.shape[0].length) {
            piece.shape = previousShape;
            return;
        }
    }

    piece.x += offset;
}

function clearLines() {
    let linesCleared = 0;

    outer: for (let row = ROWS - 1; row >= 0; row--) {
        for (let col = 0; col < COLS; col++) {
            if (!board[row][col]) {
                continue outer;
            }
        }

        board.splice(row, 1);
        board.unshift(Array(COLS).fill(0));
        linesCleared++;
        row++;
    }

    if (linesCleared > 0) {
        lines += linesCleared;
        score += [0, 100, 300, 500, 800][linesCleared] * level;
        level = Math.floor(lines / 10) + 1;
        dropInterval = Math.max(100, 1000 - (level - 1) * 100);
        updateScore();
    }
}

function moveDown() {
    if (!collision(currentPiece, 0, 1)) {
        currentPiece.y++;
    } else {
        merge();
        clearLines();
        currentPiece = nextPiece;
        nextPiece = createPiece();
        drawNextPiece();

        if (collision(currentPiece)) {
            endGame();
        }
    }
}

function moveLeft() {
    if (!collision(currentPiece, -1, 0)) {
        currentPiece.x--;
    }
}

function moveRight() {
    if (!collision(currentPiece, 1, 0)) {
        currentPiece.x++;
    }
}

function hardDrop() {
    while (!collision(currentPiece, 0, 1)) {
        currentPiece.y++;
        score += 2;
    }
    updateScore();
    moveDown();
}

function updateScore() {
    document.getElementById('score').textContent = score;
    document.getElementById('level').textContent = level;
    document.getElementById('lines').textContent = lines;
}

function endGame() {
    gameOver = true;
    document.getElementById('final-score').textContent = score;
    document.getElementById('game-over').classList.remove('hidden');
}

function restartGame() {
    createBoard();
    score = 0;
    level = 1;
    lines = 0;
    dropInterval = 1000;
    gameOver = false;
    isPaused = false;
    currentPiece = createPiece();
    nextPiece = createPiece();
    updateScore();
    drawNextPiece();
    document.getElementById('game-over').classList.add('hidden');
    lastTime = 0;
    requestAnimationFrame(update);
}

function update(time = 0) {
    if (gameOver) return;

    if (!isPaused) {
        const deltaTime = time - lastTime;
        lastTime = time;

        dropCounter += deltaTime;

        if (dropCounter > dropInterval) {
            moveDown();
            dropCounter = 0;
        }

        drawBoard();
        drawPiece(currentPiece);
    }

    requestAnimationFrame(update);
}

document.addEventListener('keydown', (e) => {
    if (gameOver || isPaused) {
        if (e.key === 'p' || e.key === 'P') {
            isPaused = !isPaused;
        }
        return;
    }

    switch (e.key) {
        case 'ArrowLeft':
            moveLeft();
            break;
        case 'ArrowRight':
            moveRight();
            break;
        case 'ArrowDown':
            moveDown();
            dropCounter = 0;
            break;
        case 'ArrowUp':
            rotate(currentPiece);
            break;
        case ' ':
            e.preventDefault();
            hardDrop();
            dropCounter = 0;
            break;
        case 'p':
        case 'P':
            isPaused = !isPaused;
            break;
    }

    drawBoard();
    drawPiece(currentPiece);
});

document.getElementById('restart-btn').addEventListener('click', restartGame);

createBoard();
currentPiece = createPiece();
nextPiece = createPiece();
updateScore();
drawNextPiece();
requestAnimationFrame(update);
