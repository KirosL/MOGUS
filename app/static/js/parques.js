document.addEventListener('DOMContentLoaded', function () {
    // ==== Referencias a elementos DOM ====
    const applyFiltersBtn = document.getElementById('apply-filters');
    const resetFiltersBtn = document.getElementById('reset-filters');
    const regionFilter = document.getElementById('region-filter');
    const typeFilter = document.getElementById('type-filter');
    const yearFilter = document.getElementById('year-filter');
    const parquesContainer = document.getElementById('parques-container');
    const parqueCards = document.querySelectorAll('.parque-card');
    const noResultsMessage = document.getElementById('no-results');

    // ==== Detectar la página actual ====
    const isCorredoresPage = window.location.pathname.includes('Corredores');

    // ==== Configurar opciones del filtro de tipo si es la página de corredores ====
    if (isCorredoresPage && typeFilter) {
        typeFilter.innerHTML = ''; // Limpiar opciones existentes

        const options = [
            { value: 'todos', text: 'Todos los tipos' },
            { value: 'corredor-verde', text: 'Corredor Verde' },
            { value: 'corredor-urbano', text: 'Corredor Urbano' },
            { value: 'plaza-corredor', text: 'Plaza-Corredor' }
        ];

        options.forEach(opt => {
            const optionElement = document.createElement('option');
            optionElement.value = opt.value;
            optionElement.textContent = opt.text;
            typeFilter.appendChild(optionElement);
        });

        // Cambiar el texto de la etiqueta
        const typeFilterLabel = typeFilter.previousElementSibling;
        if (typeFilterLabel && typeFilterLabel.classList.contains('form-label')) {
            typeFilterLabel.textContent = 'Tipo de Corredor';
        }
    }

    // ==== Función para aplicar los filtros ====
    function applyFilters() {
        const selectedRegion = regionFilter.value;
        const selectedType = typeFilter.value;
        const selectedYear = yearFilter.value;
        let visibleCount = 0;

        parqueCards.forEach(card => {
            const cardRegion = card.getAttribute('data-region');
            const cardType = card.getAttribute('data-type');
            const cardYear = card.getAttribute('data-year');

            const matchRegion = selectedRegion === 'todos' || cardRegion === selectedRegion;
            const matchType = selectedType === 'todos' || cardType === selectedType;
            const matchYear = selectedYear === 'todos' || cardYear === selectedYear;

            if (matchRegion && matchType && matchYear) {
                card.classList.remove('d-none');
                visibleCount++;
            } else {
                card.classList.add('d-none');
            }
        });

        // Mostrar/ocultar mensaje si no hay resultados
        noResultsMessage.classList.toggle('d-none', visibleCount > 0);

        // Efecto de animación
        parquesContainer.style.opacity = '0';
        setTimeout(() => {
            parquesContainer.style.transition = 'opacity 0.5s ease';
            parquesContainer.style.opacity = '1';
        }, 100);
    }

    // ==== Función para resetear los filtros ====
    function resetFilters() {
        regionFilter.value = 'todos';
        typeFilter.value = 'todos';
        yearFilter.value = 'todos';

        parqueCards.forEach(card => {
            card.classList.remove('d-none');
        });

        noResultsMessage.classList.add('d-none');

        parquesContainer.style.opacity = '0';
        setTimeout(() => {
            parquesContainer.style.transition = 'opacity 0.5s ease';
            parquesContainer.style.opacity = '1';
        }, 100);
    }

    // ==== Eventos de botones ====
    if (applyFiltersBtn) applyFiltersBtn.addEventListener('click', applyFilters);
    if (resetFiltersBtn) resetFiltersBtn.addEventListener('click', resetFilters);

    // ==== Inicialización al cargar ====
    resetFilters();

    // ==== Animación de entrada para tarjetas ====
    parqueCards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 50);
        }, index * 100);
    });

    // ==== Navegación entre vistas (radio buttons) ====
    const parquesRadio = document.getElementById('btnradio1');
    const corredoresRadio = document.getElementById('btnradio2');

    if (corredoresRadio) {
        corredoresRadio.addEventListener('click', () => {
            console.log('Botón corredores clickeado');
            window.location.href = '/ejemplosCorredores';
        });
    }

    if (parquesRadio) {
        parquesRadio.addEventListener('click', () => {
            console.log('Botón parques clickeado');
            window.location.href = '/ejemplosParques';
        });
    }
});
