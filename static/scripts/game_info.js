// Agregar este código al final de main.js o en un script separado

// Esperar a que el DOM y Bootstrap estén completamente cargados
document.addEventListener('DOMContentLoaded', function () {
    // Obtener el botón
    const gameInfoButton = document.querySelector('.game_info');

    if (gameInfoButton) {
        // Inicializar el popover con Bootstrap
        const popover = new bootstrap.Popover(gameInfoButton, {
            trigger: 'manual', // Control manual para mostrar/ocultar
            html: true,
            content: '¡Información y reglas del juego aquí!',
            placement: 'top'
        });

        // Mostrar el popover automáticamente después de un pequeño retraso
        setTimeout(function () {
            popover.show();

            // Ocultar automáticamente después de 5 segundos
            setTimeout(function () {
                popover.hide();
            }, 3000);
        }, 500);
    }
});