import ChartDataLabels from 'chartjs-plugin-datalabels';
Chart.register(ChartDataLabels);

document.addEventListener("DOMContentLoaded", function() {

    // ================================
    // 1. VARIABLES DE DATOS
    // ================================

    const nombresFases = [
        {% for fase in fases %}
            "{{ fase.nombre_fase }}"{% if not loop.last %},{% endif %}
        {% endfor %}
    ];

    const porcentajeIndicador = [
        {% for fase in fases %}
            {{ fase.porcentaje_indicador }}{% if not loop.last %},{% endif %}
        {% endfor %}
    ];

    const areasVerdes = [
        {% for fase in fases %}
            {{ fase.area_verde }}{% if not loop.last %},{% endif %}
        {% endfor %}
    ];

    const areasTotal = [
        {% for fase in fases %}
            {{ fase.area_total }}{% if not loop.last %},{% endif %}
        {% endfor %}
    ];

    const viabilidad = [
        {% for fase in fases %}
            "{{ fase.viabilidad }}"{% if not loop.last %},{% endif %}
        {% endfor %}
    ];

    // ================================
    // 2. CÁLCULO DE VIABILIDADES
    // ================================

    const conteoViable = viabilidad.filter(v => v.includes("Viable ✅")).length,
          conteoMediano = viabilidad.filter(v => v.includes("Medianamente viable ⚠️")).length,
          conteoNoViable = viabilidad.filter(v => v.includes("No viable ❌")).length;

    // ================================
    // 3. GRÁFICO DE BARRAS (Indicador)
    // ================================

    new Chart(document.getElementById('graficoIndicador'), {
        type: 'bar',
        data: {
            labels: nombresFases,
            datasets: [{
                label: 'Porcentaje de Indicador',
                data: porcentajeIndicador,
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                datalabels: {
                    display: true,
                    anchor: 'end',
                    align: 'top',
                    formatter: (value) => `${value}%`
                }
            },
            scales: {
                y: { beginAtZero: true, max: 100 }
            }
        }
    });

    // ================================
    // 4. GRÁFICO DONUT (Viabilidad)
    // ================================

    new Chart(document.getElementById('graficoPie'), {
        type: 'doughnut',
        data: {
            labels: ['Viable', 'Medianamente viable', 'No viable'],
            datasets: [{
                data: [conteoViable, conteoMediano, conteoNoViable],
                backgroundColor: [
                    'rgba(75, 192, 75, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(255, 99, 132, 0.7)'
                ]
            }]
        }
    });

    // ================================
    // 5. GRÁFICO DE BARRAS APILADAS (Área Verde vs Total)
    // ================================
    new Chart(document.getElementById('graficoArea'), {
        type: 'bar',
        data: {
            labels: nombresFases,
            datasets: [
                { label: 'Área Verde (m²)', data: areasVerdes, backgroundColor: 'rgba(75, 192, 75, 0.6)' },
                { label: 'Área Total (m²)', data: areasTotal, backgroundColor: 'rgba(54, 162, 235, 0.6)' }
            ]
        },
        options: { 
            responsive: true, 
            scales: { x: { stacked: true }, y: { stacked: true } }
        }
    });

    // 6. Gráfico de Radar (Sostenibilidad)
    new Chart(document.getElementById('graficoRadar'), {
        type: 'radar',
        data: {
            labels: nombresFases,
            datasets: [{
                label: 'Indicador de Sostenibilidad',
                data: porcentajeIndicador,
                backgroundColor: 'rgba(153, 102, 255, 0.6)',
                borderColor: 'rgba(153, 102, 255, 1)'
            }]
        }
    });

    // 7. Gráfico de Dispersión (Área Verde vs Indicador)
    new Chart(document.getElementById('graficoDispersion'), {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Área Verde vs. Indicador',
                data: nombresFases.map((_, i) => ({ x: areasVerdes[i], y: porcentajeIndicador[i] })),
                backgroundColor: 'rgba(255, 99, 132, 0.7)'
            }]
        },
        options: {
            scales: {
                x: { title: { display: true, text: 'Área Verde (m²)' } },
                y: { title: { display: true, text: 'Porcentaje de Indicador (%)' } }
            }
        }
    });
    // 8. Gráfico de Líneas (Evolución del Indicador a lo Largo de las Fases)
    new Chart(document.getElementById('graficoLineas'), {
        type: 'line',
        data: {
            labels: nombresFases,
            datasets: [{
                label: 'Evolución del Indicador (%)',
                data: porcentajeIndicador,
                borderColor: 'rgba(255, 159, 64, 1)',
                backgroundColor: 'rgba(255, 159, 64, 0.2)',
                borderWidth: 2,
                tension: 0.3, // Suaviza la línea
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, max: 100 }
            }
        }
    });
});