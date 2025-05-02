document.addEventListener('DOMContentLoaded', function () {
    // ========== 1. DETECTAR EL PROCESO DESDE LA URL ==========
    const currentUrl = window.location.pathname;
    let currentProceso = '';

    if (currentUrl.includes('/diagnostico/')) {
        currentProceso = currentUrl.split('/diagnostico/')[1];
    } else if (currentUrl.includes('/resultado/')) {
        currentProceso = currentUrl.split('/resultado/')[1];
    } else {
        currentProceso = currentUrl.replace(/^\//, '');
    }

    console.log("Proceso detectado:", currentProceso);

    // ========== 2. BOTONES DE NAVEGACIÓN ==========
    const navToTabla = document.getElementById('navToTabla');
    const navToDiagnostico = document.getElementById('navToDiagnostico');
    const navToResultados = document.getElementById('navToResultados');

    if (navToTabla) {
        navToTabla.addEventListener('click', () => {
            window.location.href = '/' + currentProceso;
        });
    }

    if (navToDiagnostico) {
        navToDiagnostico.addEventListener('click', () => {
            window.location.href = '/diagnostico/' + currentProceso;
        });
    }

    if (navToResultados) {
        navToResultados.addEventListener('click', () => {
            window.location.href = '/resultado/' + currentProceso;
        });
    }

    // ========== 3. CAMBIO DE TÍTULO DE TABLA ==========
    const aplicarTituloBtn = document.getElementById('aplicarTitulo');
    const tituloInput = document.getElementById('tablaTitulo');
    const tituloTabla = document.querySelector('.title-table');

    const proceso = document.getElementById('proceso-container')?.dataset.proceso;
    const storageKeyTitulo = `tituloTabla_${proceso}`;

    console.log("Proceso actual:", proceso);

    // Mostrar título guardado si existe
    const tituloGuardado = localStorage.getItem(storageKeyTitulo);
    if (tituloGuardado && tituloTabla) {
        tituloTabla.textContent = tituloGuardado;
    }

    aplicarTituloBtn?.addEventListener('click', function (e) {
        e.preventDefault();

        const nuevoTitulo = tituloInput.value.trim();
        const tituloFinal = nuevoTitulo || "Registro de Datos - Línea de Investigación";

        if (tituloTabla) {
            tituloTabla.textContent = tituloFinal;
        }

        localStorage.setItem(storageKeyTitulo, tituloFinal);

        // Cerrar el modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('crearTitulo'));
        modal?.hide();
    });

    // ========== 4. SUBIR Y MOSTRAR IMAGEN PERSONALIZADA ==========
    const storageKeyImg = `imagenProceso_${proceso}`;
    const imagenInput = document.getElementById('imagenInput');
    const imagenElemento = document.getElementById('fullSizeImage');

    // Mostrar imagen guardada
    const imagenGuardada = localStorage.getItem(storageKeyImg);
    if (imagenGuardada && imagenElemento) {
        imagenElemento.src = imagenGuardada;
    }

    // Cargar nueva imagen
    imagenInput?.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function (event) {
            const base64Image = event.target.result;
            if (imagenElemento) {
                imagenElemento.src = base64Image;
            }
            localStorage.setItem(storageKeyImg, base64Image);
        };
        reader.readAsDataURL(file);
    });

    // DEBUG extra
    console.log("URL de redirección:", '/diagnostico/' + currentProceso);
});
