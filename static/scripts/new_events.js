// Tus variables y animaciones iniciales
const new_events_part = document.getElementById('new_events');
const events_list = document.getElementById('events_list');

if (new_events_part) {
    setTimeout(() => {
        new_events_part.classList.add('pop_up')
        setTimeout(() => {
            new_events_part.classList.remove('pop_up')
        }, 1000);
    }, 200);

    new_events_part.addEventListener('click', () => {
        events_list.classList.toggle('no_show')
        events_list.classList.toggle('displayColumn')
    });
}

// Lógica principal al cargar la página
document.addEventListener('DOMContentLoaded', function () {
    const eventosString = document.body.dataset.proxima;

    if (eventosString) {
        try {
            const eventos = JSON.parse(eventosString);
            construirTarjetas(eventos); // Paso 1: Dibuja el HTML
            iniciarCuentasAtras(eventos); // Paso 2: Arranca los relojes
        } catch (error) {
            console.error("Error al procesar los eventos:", error);
        }
    }
});

// Función para inyectar el HTML dinámicamente
function construirTarjetas(eventos) {
    const contenedor = document.getElementById('contenedor-dinamico');
    if (!contenedor) return;

    let htmlTarjetas = '';

    eventos.forEach((evento, index) => {
        htmlTarjetas += `
        <div class="upcoming-card myBg myBorder rounded-4 shadow-sm p-3 mt-3">
            <p class="subtitle fs-5 mb-1">${evento.city}</p>
            <p class="title fs-5 mb-2">${evento.title}</p>
            <div class="upcoming-countdown">
                <i class="fa-solid fa-clock me-1" style="color:var(--accent-beer)"></i>
                <span id="restante-${index}" class="upcoming-time">--d --h --m --s</span>
            </div>
        </div>
        `;
    });

    contenedor.innerHTML = htmlTarjetas;
}

// Función para actualizar los números
function iniciarCuentasAtras(eventos) {
    setInterval(() => {
        const ahora = new Date().getTime();

        eventos.forEach((evento, index) => {
            const fechaObjetivo = new Date(evento.date).getTime();
            const distancia = fechaObjetivo - ahora;

            // Cálculos
            const dias = Math.floor(distancia / (1000 * 60 * 60 * 24));
            const horas = Math.floor((distancia % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutos = Math.floor((distancia % (1000 * 60 * 60)) / (1000 * 60));
            const segundos = Math.floor((distancia % (1000 * 60)) / 1000);

            // Actualizamos los elementos exactos de esta ciudad
            const restante = document.getElementById(`restante-${index}`);
            restante.innerText = `${String(dias).padStart(2, '0')}d ${String(horas).padStart(2, '0')}h ${String(minutos).padStart(2, '0')}m ${String(segundos).padStart(2, '0')}s`
        });
    }, 1000);
}