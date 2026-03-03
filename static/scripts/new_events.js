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

    // Recorremos la lista. Usamos 'index' para crear un ID único por ciudad
    eventos.forEach((evento, index) => {
        htmlTarjetas += `
        <div class="myBg myBorder p-3 mt-4">
            <h3 class="subtitle fs-4">${evento.city}</h3>
            <p class="title fs-5">${evento.title}</p>
            <p id="restante-${index}" class="title fs-6"></p>
        </div>
        `;
    });

    contenedor.innerHTML = htmlTarjetas; // Insertamos todo en el HTML
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