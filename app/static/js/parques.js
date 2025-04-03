document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos DOM
    const applyFiltersBtn = document.getElementById('apply-filters');
    const resetFiltersBtn = document.getElementById('reset-filters');
    const regionFilter = document.getElementById('region-filter');
    const typeFilter = document.getElementById('type-filter');
    const yearFilter = document.getElementById('year-filter');
    const parquesContainer = document.getElementById('parques-container');
    const parqueCards = document.querySelectorAll('.parque-card');
    const noResultsMessage = document.getElementById('no-results');
    
    // Detectar la página actual
    const isCorredoresPage = window.location.pathname.includes('Corredores');
    
    // Configurar las opciones de tipo según la página
    if (isCorredoresPage && typeFilter) {
        // Limpiar opciones existentes
        typeFilter.innerHTML = '';
        
        // Añadir opciones para corredores
        const options = [
            { value: 'todos', text: 'Todos los tipos' },
            { value: 'corredor-verde', text: 'Corredor Verde' },
            { value: 'corredor-urbano', text: 'Corredor Urbano' },
            { value: 'plaza-corredor', text: 'Plaza-Corredor' }
        ];
        
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.value;
            optionElement.textContent = option.text;
            typeFilter.appendChild(optionElement);
        });
        
        // Actualizar la etiqueta del filtro
        const typeFilterLabel = typeFilter.previousElementSibling;
        if (typeFilterLabel && typeFilterLabel.classList.contains('form-label')) {
            typeFilterLabel.textContent = 'Tipo de Corredor';
        }
    }
    
    // Función para aplicar filtros
    function applyFilters() {
        const selectedRegion = regionFilter.value;
        const selectedType = typeFilter.value;
        const selectedYear = yearFilter.value;
        
        let visibleCount = 0;
        
        // Recorrer todas las tarjetas y aplicar filtros
        parqueCards.forEach(card => {
            const cardRegion = card.getAttribute('data-region');
            const cardType = card.getAttribute('data-type');
            const cardYear = card.getAttribute('data-year');
            
            // Verificar si la tarjeta cumple con todos los filtros seleccionados
            const matchRegion = selectedRegion === 'todos' || cardRegion === selectedRegion;
            const matchType = selectedType === 'todos' || cardType === selectedType;
            const matchYear = selectedYear === 'todos' || cardYear === selectedYear;
            
            // Mostrar u ocultar la tarjeta según los filtros
            if (matchRegion && matchType && matchYear) {
                card.classList.remove('d-none');
                visibleCount++;
            } else {
                card.classList.add('d-none');
            }
        });
        
        // Mostrar mensaje si no hay resultados
        if (visibleCount === 0) {
            noResultsMessage.classList.remove('d-none');
        } else {
            noResultsMessage.classList.add('d-none');
        }
        
        // Animación para mostrar los resultados filtrados
        parquesContainer.style.opacity = '0';
        setTimeout(() => {
            parquesContainer.style.transition = 'opacity 0.5s ease';
            parquesContainer.style.opacity = '1';
        }, 100);
    }
    
    // Función para restablecer filtros
    function resetFilters() {
        regionFilter.value = 'todos';
        typeFilter.value = 'todos';
        yearFilter.value = 'todos';
        
        // Mostrar todas las tarjetas
        parqueCards.forEach(card => {
            card.classList.remove('d-none');
        });
        
        // Ocultar mensaje de no resultados
        noResultsMessage.classList.add('d-none');
        
        // Animación para mostrar todos los elementos
        parquesContainer.style.opacity = '0';
        setTimeout(() => {
            parquesContainer.style.transition = 'opacity 0.5s ease';
            parquesContainer.style.opacity = '1';
        }, 100);
    }
    
    // Event listeners
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', applyFilters);
    }
    
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', resetFilters);
    }
    
    // Inicializar la página con todos los elementos visibles
    resetFilters();
    
    // Animación de entrada para las tarjetas al cargar la página
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

    // Corregir la navegación de los botones
    const parquesRadio = document.getElementById('btnradio1');
    const corredoresRadio = document.getElementById('btnradio2');
    
    // Usar click en lugar de change para los radios
    if (corredoresRadio) {
        corredoresRadio.addEventListener('click', function() {
            console.log('Botón corredores clickeado');
            window.location.href = '/ejemplosCorredores';
        });
    }
    
    if (parquesRadio) {
        parquesRadio.addEventListener('click', function() {
            console.log('Botón parques clickeado');
            window.location.href = '/ejemplosParques';
        });
    }
});