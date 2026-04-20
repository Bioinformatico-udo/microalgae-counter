# Contador de Microalgas

Aplicación web para conteo manual y automático de microalgas en imágenes de cultivos, con análisis estadístico de correlación.

## Características

- 📸 **Subida de imágenes** - Soporta múltiples formatos (PNG, JPG, TIFF)
- 👨‍🔬 **Conteo manual** - Interfaz intuitiva con temporizador para técnicos
- 🤖 **Conteo automático** - Basado en modelo YOLO11m pre-entrenado
- 📊 **Análisis estadístico** - Correlación de Pearson entre conteos manuales y automáticos
- 📈 **Visualización** - Gráficos interactivos y tablas de resultados
- 💾 **Historial persistente** - Almacenamiento en SQLite de todos los conteos
- 📱 **Responsive** - Funciona en dispositivos móviles, tablets y desktop

## Requisitos del Sistema

- Python 3.8+
- 8GB RAM mínimo (recomendado 16GB para YOLO)
- GPU recomendada para procesamiento rápido

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/microalgae-counter.git
cd microalgae-counter