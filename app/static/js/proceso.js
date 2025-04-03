document.addEventListener('DOMContentLoaded', function() {
    // Obtener el proceso actual (ajusta este regex según tu estructura de URL)
    const currentUrl = window.location.pathname;
    let currentProceso = '';
    
    // Detectar el proceso desde la URL
    if (currentUrl.includes('/diagnostico/')) {
        currentProceso = currentUrl.split('/diagnostico/')[1];
    } else if (currentUrl.includes('/resultado/')) {
        currentProceso = currentUrl.split('/resultado/')[1];
    } else {
        // Para la página principal
        currentProceso = currentUrl.replace(/^\//, ''); // Eliminar la barra inicial
    }
    
    console.log("Proceso detectado:", currentProceso); // Depuración
    
    // Referencias a los botones de navegación
    const navToTabla = document.getElementById('navToTabla');
    const navToDiagnostico = document.getElementById('navToDiagnostico');
    const navToResultados = document.getElementById('navToResultados');
    
    // Eventos para los botones de navegación
    if (navToTabla) {
        navToTabla.addEventListener('click', function() {
            window.location.href = '/' + currentProceso;
        });
    }
    
    if (navToDiagnostico) {
        navToDiagnostico.addEventListener('click', function() {
            window.location.href = '/diagnostico/' + currentProceso;
        });
    }
    
    if (navToResultados) {
        navToResultados.addEventListener('click', function() {
            window.location.href = '/resultado/' + currentProceso;
        });
    }

    console.log("URL de redirección:", '/diagnostico/' + currentProceso);
});