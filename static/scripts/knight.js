let n = 8;
let solved = false;
let timerInterval = null;
let validateTimeout = null;
let centisecondsElapsed = 0;
let game_matrix = Array.from({ length: n }, () => Array(n).fill(0));

const timer = document.getElementById('timer');
const title = document.getElementById('title');
const back = document.getElementById('back');

document.addEventListener('DOMContentLoaded', function () {
    back.addEventListener('click', () => window.location.href = `\menu_games?userid=${localStorage.getItem('userId')}`)
    const matrix = document.getElementById('matrix');
    for (let i = 0; i < n; i++) {
        const mtr = document.createElement('tr')
        for (let j = 0; j < n; j++) {
            const mtd = document.createElement('td')
            mtd.classList.add('grey')
            mtd.classList.add('z-8')
            mtd.id = `cell-${i}-${j}`;
            mtd.addEventListener('click', () => toggle_color(i, j, mtd))
            mtr.appendChild(mtd)
        }
        matrix.appendChild(mtr)
    }
    matrix.classList.add('matrix')
    startGame();
})

function updateTimerDisplay() {
    const minutes = Math.floor(centisecondsElapsed / 6000).toString().padStart(2, '0');
    const seconds = Math.floor((centisecondsElapsed % 6000) / 100).toString().padStart(2, '0');
    const milliseconds = (centisecondsElapsed % 100).toString().padStart(2, '0');
    timer.textContent = `${minutes}:${seconds}.${milliseconds}`;
}

function start_timer() {
    if (timerInterval !== null) return;

    centisecondsElapsed = 0;
    updateTimerDisplay();

    timerInterval = setInterval(() => {
        centisecondsElapsed++; // Incrementar tiempo
        updateTimerDisplay();
    }, 10); // Actualizar cada 10 ms (centésima de segundo)
}

function stop_timer() {
    if (timerInterval !== null) {
        clearInterval(timerInterval);  // ← Detiene el cronómetro
        timerInterval = null;          // ← Limpia el ID para poder reiniciarlo
    }
}

function click_animation(td, time) {
    td.classList.add('clicked');
    setTimeout(() => {
        td.classList.remove('clicked');
    }, time); // igual al tiempo de la transición
}

function toggle_color(row, col, td) {
    click_animation(td, 110);

    const current_horse = document.querySelector('.horse')
    current_horse.classList.remove('horse')

    const new_horse = document.getElementById(`cell-${row}-${col}`)
    new_horse.classList.add('horse')
    if (game_matrix[row][col] === 1) {
        game_matrix[row][col] = 0;
        const color = (row + col) % 2 === 0 ? 'white' : 'black';
        new_horse.classList.remove('red')
        new_horse.classList.add(color)
    }

    updateValidSpots(row, col);

    if (validateTimeout) clearTimeout(validateTimeout);

    validateTimeout = setTimeout(() => valid_solution(), 200);
}

function updateValidSpots(i, j) {
    const cells = document.querySelectorAll('td');
    cells.forEach(cell => cell.classList.add('locked'));

    // Todos los movimientos de caballo
    const valid = [
        [i + 2, j + 1],
        [i + 2, j - 1],
        [i - 2, j + 1],
        [i - 2, j - 1],
        [i + 1, j + 2],
        [i + 1, j - 2],
        [i - 1, j + 2],
        [i - 1, j - 2],
    ];

    // Desbloquea solo las celdas válidas dentro del tablero
    valid.forEach(([x, y]) => {
        if (x >= 0 && x < n && y >= 0 && y < n) {
            const cell = document.getElementById(`cell-${x}-${y}`);
            cell.classList.remove('locked');
        }
    });
}

function getSpots(max) {
    const spots = [];
    const size = 6;
    let count = 0;
    while (spots.length < size) {
        count++;
        const a = Math.floor(Math.random() * max);
        const b = Math.floor(Math.random() * max);
        const candidate = [a, b, 0];

        // revisar que cumpla la distancia mínima con todos los anteriores
        let ok = true;
        for (const p of spots) {
            if (Math.abs(candidate[0] - p[0]) + Math.abs(candidate[1] - p[1]) < 3) {
                ok = false;
                break;
            }
        }

        if (ok) spots.push(candidate);
        if (count >= 400) return null;
        // si no, intenta otro punto
    }

    const knight = Math.floor(Math.random() * size);
    spots[knight][2] = 1;
    return spots;
}

function startGame() {
    let spots = null;
    while (spots === null) {
        spots = getSpots(8);
    }
    const horseSpot = spots.find(p => p[2] === 1);
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
            const cell = document.getElementById(`cell-${i}-${j}`);
            let color = spots.some(p => p[0] === i && p[1] === j) ? 'red' : (i + j) % 2 === 0 ? 'white' : 'black';
            if ((horseSpot[0] === i) && (horseSpot[1] === j)) {
                cell.classList.add('horse')
                color = (i + j) % 2 === 0 ? 'white' : 'black';
                updateValidSpots(i, j);
            }

            if (color == 'red') {
                game_matrix[i][j] = 1;
            }
            cell.classList.add(color)
            cell.classList.remove('grey')
        }
    }
    start_timer();
}

function valid_solution() {
    if (game_matrix.some(row => row.includes(1))) return;
    const cells = document.querySelectorAll('td');
    cells.forEach(cell => cell.classList.add('locked'));
    stop_timer();
}