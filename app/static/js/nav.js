document.addEventListener('DOMContentLoaded', function() {
    // Referencias a los módulos
    const introductionModule = document.getElementById('introductionModule');
    
    // Referencias a los botones de navegación
    const navToIntroduction = document.getElementById('navToIntroduction');
    
    // Evento para el botón de navegación
    navToIntroduction.addEventListener('click', function(e) {
        e.preventDefault(); // Prevenir comportamiento predeterminado
        
        // Desplazarse suavemente hasta el módulo de introducción
        introductionModule.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    });
});