/**
 * Main JavaScript for Microalgae Counter Application
 * Handles counting timers, API calls, and UI interactions
 */

// Global variables
let currentTimer = null;
let startTime = null;
let currentImageId = null;

// Timer functions
function startTimer() {
    if (currentTimer) clearInterval(currentTimer);
    startTime = Date.now();
    currentTimer = setInterval(updateTimer, 100);
}

function updateTimer() {
    const elapsed = (Date.now() - startTime) / 1000;
    const minutes = Math.floor(elapsed / 60);
    const seconds = (elapsed % 60).toFixed(1);
    const timerDisplay = document.getElementById('timer');
    if (timerDisplay) {
        timerDisplay.textContent = `${minutes}:${seconds.toString().padStart(4, '0')}`;
    }
}

function stopTimer() {
    if (currentTimer) {
        clearInterval(currentTimer);
        currentTimer = null;
        const elapsed = (Date.now() - startTime) / 1000;
        return elapsed;
    }
    return 0;
}

// Image upload functions
async function uploadImage(file) {
    showLoading();
    const formData = new FormData();
    formData.append('image', file);
    
    try {
        const response = await fetch('/api/upload-image', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            currentImageId = data.image_id;
            showAlert('Imagen subida exitosamente', 'success');
            return data;
        } else {
            showAlert('Error al subir imagen: ' + data.error, 'danger');
            return null;
        }
    } catch (error) {
        hideLoading();
        showAlert('Error de conexión: ' + error.message, 'danger');
        return null;
    }
}

// Manual count submission
async function submitManualCount(technicianName, count) {
    if (!currentImageId) {
        showAlert('Primero sube una imagen', 'warning');
        return false;
    }
    
    const timeTaken = stopTimer();
    
    const data = {
        technician_name: technicianName,
        image_id: currentImageId,
        count: parseInt(count),
        time_taken: timeTaken
    };
    
    showLoading();
    
    try {
        const response = await fetch('/api/manual-count', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        hideLoading();
        
        if (result.success) {
            showAlert('Conteo guardado exitosamente', 'success');
            return true;
        } else {
            showAlert('Error: ' + result.error, 'danger');
            return false;
        }
    } catch (error) {
        hideLoading();
        showAlert('Error de conexión: ' + error.message, 'danger');
        return false;
    }
}

// Automatic count request
async function getAutomaticCount(imageId) {
    showLoading();
    
    try {
        const response = await fetch(`/api/auto-count/${imageId}`);
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            return data;
        } else {
            showAlert('Error en conteo automático: ' + data.error, 'danger');
            return null;
        }
    } catch (error) {
        hideLoading();
        showAlert('Error de conexión: ' + error.message, 'danger');
        return null;
    }
}

// Correlation analysis
async function analyzeCorrelation(imageIds) {
    showLoading();
    
    try {
        const response = await fetch('/api/analyze-correlation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image_ids: imageIds })
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            displayCorrelationResults(data);
            return data;
        } else {
            showAlert('Error en análisis: ' + data.error, 'danger');
            return null;
        }
    } catch (error) {
        hideLoading();
        showAlert('Error de conexión: ' + error.message, 'danger');
        return null;
    }
}

// Display correlation results
function displayCorrelationResults(data) {
    const resultsDiv = document.getElementById('correlation-results');
    if (!resultsDiv) return;
    
    const corr = data.correlation;
    
    resultsDiv.innerHTML = `
        <div class="alert alert-info">
            <h4>Resultados del Análisis Estadístico</h4>
            <p><strong>Coeficiente de Correlación de Pearson:</strong> ${corr.correlation}</p>
            <p><strong>Valor p:</strong> ${corr.p_value}</p>
            <p><strong>Interpretación:</strong> ${corr.interpretation}</p>
            <p><strong>Significancia:</strong> ${corr.significant ? 'Sí (p < 0.05)' : 'No (p ≥ 0.05)'}</p>
        </div>
        <div class="text-center">
            <img src="${data.plot_url}?t=${Date.now()}" class="correlation-plot img-fluid" alt="Gráfico de correlación">
        </div>
        <div class="counts-grid mt-4">
            <div class="count-card">
                <h5>Conteos Manuales</h5>
                <p>Promedio: ${(data.manual_counts.reduce((a,b) => a+b,0)/data.manual_counts.length).toFixed(2)}</p>
                <p>Valores: ${data.manual_counts.join(', ')}</p>
            </div>
            <div class="count-card">
                <h5>Conteos Automáticos</h5>
                <p>Promedio: ${(data.auto_counts.reduce((a,b) => a+b,0)/data.auto_counts.length).toFixed(2)}</p>
                <p>Valores: ${data.auto_counts.join(', ')}</p>
            </div>
        </div>
    `;
}

// Helper functions
function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.add('active');
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.remove('active');
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Initialize page-specific functionality
document.addEventListener('DOMContentLoaded', function() {
    // Manual count page initialization
    if (document.getElementById('manual-count-form')) {
        initializeManualCountPage();
    }
    
    // Results page initialization
    if (document.getElementById('analyze-button')) {
        initializeResultsPage();
    }
});

function initializeManualCountPage() {
    const startButton = document.getElementById('start-counting');
    const submitButton = document.getElementById('submit-count');
    
    if (startButton) {
        startButton.addEventListener('click', startTimer);
    }
    
    if (submitButton) {
        submitButton.addEventListener('click', () => {
            const technician = document.getElementById('technician-name').value;
            const count = document.getElementById('count-value').value;
            
            if (!technician || !count) {
                showAlert('Por favor complete todos los campos', 'warning');
                return;
            }
            
            submitManualCount(technician, count);
        });
    }
}

function initializeResultsPage() {
    const analyzeButton = document.getElementById('analyze-button');
    if (analyzeButton) {
        analyzeButton.addEventListener('click', () => {
            const imageIds = getSelectedImageIds();
            if (imageIds.length > 0) {
                analyzeCorrelation(imageIds);
            } else {
                showAlert('Seleccione al menos una imagen para analizar', 'warning');
            }
        });
    }
}

function getSelectedImageIds() {
    const checkboxes = document.querySelectorAll('.image-selector:checked');
    return Array.from(checkboxes).map(cb => parseInt(cb.value));
}

// Export functions for use in templates
window.uploadImage = uploadImage;
window.submitManualCount = submitManualCount;
window.getAutomaticCount = getAutomaticCount;
window.analyzeCorrelation = analyzeCorrelation;
window.startTimer = startTimer;