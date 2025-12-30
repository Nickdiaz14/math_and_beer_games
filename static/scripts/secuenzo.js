let n;
let cells;
let cell_size;
let game_matrix;
let user_matrix;
let in_game = false;
let boards_solved = 0;
let timerInterval = null;
let validateTimeout = null;
let centisecondsElapsed = 300;

const timer = document.getElementById('timer');
const back = document.getElementById('back');
const s_boards = document.getElementById('s_boards');

document.addEventListener('DOMContentLoaded', function () {
    n = Number(document.body.dataset.n)
    game_matrix = Array.from({ length: n }, () => Array(n).fill(0));
    user_matrix = Array.from({ length: n }, () => Array(n).fill(0));
    back.addEventListener('click', () => {
        window.history.back();
    });

    window.addEventListener('pageshow', (e) => {
        if (e.persisted) {
            window.location.reload();
        }
    });
    cell_size = n === 5 ? 'z-5' : 'z-6';
    const matrix = document.getElementById('matrix');
    for (let i = 0; i < n; i++) {
        const mtr = document.createElement('tr')
        for (let j = 0; j < n; j++) {
            const mtd = document.createElement('td')
            mtd.classList.add('grey')
            mtd.classList.add(cell_size)
            mtd.id = `cell-${i}-${j}`;
            mtd.addEventListener('click', () => toggle_color(i, j, mtd))
            mtr.appendChild(mtd)
        }
        matrix.appendChild(mtr)
    }
    matrix.classList.add('matrix')
    cells = document.querySelectorAll('td');
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

    updateTimerDisplay();

    timerInterval = setInterval(() => {
        centisecondsElapsed--; // Incrementar tiempo
        if (centisecondsElapsed >= 0) {
            updateTimerDisplay();
        } else {
            stop_timer();
            if (!in_game) setTimeout(() => continueGame(), 200);
            if (in_game) sendRecord();
        }
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

    if (game_matrix[row][col] !== 0) {
        if (user_matrix[row][col] !== 1) {
            user_matrix[row][col] = 1
            td.classList.remove('grey');
            td.classList.remove('blue');
            td.classList.add('red');
        } else if (n === 5 && user_matrix[row][col] === 1) {
            user_matrix[row][col] = 2
            td.classList.remove('red');
            td.classList.add('blue');
        }
    } else {
        sendRecord();
    }

    if (validateTimeout) clearTimeout(validateTimeout);

    validateTimeout = setTimeout(() => valid_solution(), 200);
}

function getSpots(max, size) {
    const values = n === 5 ? 2 : 1;
    const spots = [];
    while (spots.length < size) {
        const a = Math.floor(Math.random() * max);
        const b = Math.floor(Math.random() * max);
        const c = Math.floor(Math.random() * values) + 1;
        const candidate = [a, b, c];

        // revisar que cumpla la distancia mínima con todos los anteriores
        let ok = true;
        for (const p of spots) {
            if (Math.abs(candidate[0] - p[0]) + Math.abs(candidate[1] - p[1]) < 1) {
                ok = false;
                break;
            }
        }

        if (ok) spots.push(candidate);
        // si no, intenta otro punto
    }
    return spots;
}

function startGame() {
    in_game = false;
    centisecondsElapsed = 300;
    const spots = getSpots(n, 3 + Math.floor(boards_solved / 2));
    game_matrix = Array.from({ length: n }, () => Array(n).fill(0));
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
            const cell = document.getElementById(`cell-${i}-${j}`);
            let color = spots.some(p => p[0] === i && p[1] === j && p[2] === 2) ? ['blue', 'blocked'] : spots.some(p => p[0] === i && p[1] === j && p[2] === 1) ? ['red', 'blocked'] : ['grey', 'locked'];
            for (let k = 0; k < color.length; k++) {
                cell.classList.add(color[k])
            }
        }
    }
    const red_cells = spots.filter(p => p[2] === 1)
    red_cells.forEach(([x, y]) => {
        game_matrix[x][y] = 1
    })
    if (n === 5) {
        const blue_cells = spots.filter(p => p[2] === 2)
        blue_cells.forEach(([x, y]) => {
            game_matrix[x][y] = 2
        })
    }
    start_timer();
}

function continueGame() {
    in_game = true;
    centisecondsElapsed = 800;
    cells.forEach(cell => {
        cell.className = `grey ${cell_size}`
    })
    start_timer();
}

function valid_solution() {
    if (user_matrix.flat().filter(v => v === 0).length !== game_matrix.flat().filter(v => v === 0).length) return
    let flag = true;
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
            if (user_matrix[i][j] !== game_matrix[i][j]) {
                flag = false;
            }
        }
    }

    if (flag) {
        game_matrix = Array.from({ length: n }, () => Array(n).fill(0));
        user_matrix = Array.from({ length: n }, () => Array(n).fill(0));
        boards_solved++;
        s_boards.textContent = `Tableros resueltos: ${boards_solved}`
        stop_timer();
        setTimeout(() => {
            cells.forEach(cell => cell.className = `grey ${cell_size}`)
            startGame()
        }, 600); // siguiente tablero
    }
}

function sendRecord() {
    let game = n === 6 ? `Unicolor` : 'Bicolor'
    fetch('/leaderboard/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            game: `T${game}`,
            record: boards_solved,
            userid: localStorage.getItem('userId')
        })
    })
        .then(response => response.json())
        .then(data => {
            window.location.href = `/leaderboard?game=T${game}&name=Secuenzo ${game}&better=${data.better}&type=3&record=${boards_solved}`
        })
}
