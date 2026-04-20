"""
Verifica que los modelos YOLO copiados funcionan correctamente.
"""

import os
import torch
from ultralytics import YOLO
from pathlib import Path

def test_model(model_path, model_name):
    """
    Prueba un modelo YOLO para verificar que puede cargarse y usarse.
    
    Args:
        model_path (str): Ruta al archivo .pt
        model_name (str): Nombre descriptivo del modelo
    
    Returns:
        bool: True si el modelo funciona correctamente
    """
    print(f"\n{'='*60}")
    print(f"Probando: {model_name}")
    print(f"Archivo: {model_path}")
    print(f"{'='*60}")
    
    # Verificar que el archivo existe
    if not os.path.exists(model_path):
        print(f"❌ ERROR: Archivo no encontrado en {model_path}")
        return False
    
    # Verificar tamaño del archivo
    size_bytes = os.path.getsize(model_path)
    size_mb = size_bytes / (1024 * 1024)
    print(f"📦 Tamaño: {size_mb:.2f} MB")
    
    if size_mb < 1:
        print(f"⚠️ ADVERTENCIA: El archivo es muy pequeño ({size_mb:.2f} MB)")
        print("   Un modelo YOLO válido debería tener al menos varios MB")
    
    # Verificar que no es un placeholder de texto
    with open(model_path, 'rb') as f:
        first_bytes = f.read(20)
        if first_bytes.startswith(b'#'):
            print(f"❌ ERROR: El archivo es un placeholder de texto")
            print(f"   Contenido: {first_bytes[:50]}")
            return False
        else:
            print(f"✅ Formato binario válido")
    
    # Intentar cargar con torch
    try:
        checkpoint = torch.load(model_path, map_location='cpu')
        print(f"✅ Checkpoint cargado correctamente")
        
        # Verificar estructura
        if 'model' in checkpoint:
            print(f"✅ Contiene 'model' - formato YOLO")
        elif 'model_state_dict' in checkpoint:
            print(f"✅ Contiene 'model_state_dict' - checkpoint de entrenamiento")
        else:
            keys = list(checkpoint.keys())[:3]
            print(f"⚠️ Estructura del checkpoint: {keys}")
        
    except Exception as e:
        print(f"❌ Error cargando checkpoint: {e}")
        return False
    
    # Intentar cargar con YOLO
    try:
        print(f"🔄 Cargando modelo con ultralytics YOLO...")
        model = YOLO(model_path)
        print(f"✅ Modelo cargado exitosamente con YOLO")
        
        # Información del modelo
        if hasattr(model, 'model'):
            if hasattr(model.model, 'model'):
                print(f"📊 Tipo de modelo: {type(model.model.model).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cargando con YOLO: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("VALIDACIÓN DE MODELOS YOLO")
    print("="*60)
    
    # Definir los modelos a probar (rutas actualizadas con tus nombres)
    models_to_test = [
        {
            'path': "models/default/yolo11m_default.pt",
            'name': "Modelo por defecto (Default)"
        },
        {
            'path': "models/monoclonal/yolo11m_monoclonal_v1.pt",
            'name': "Modelo Monoclonal v1"
        },
        {
            'path': "models/refined/yolo11m_refined_v1.pt",
            'name': "Modelo Refinado v1"
        },
        {
            'path': "models/monoclonal/best.pt",
            'name': "Modelo best (si existe)"
        }
    ]
    
    results = {}
    
    for model_config in models_to_test:
        model_path = model_config['path']
        if os.path.exists(model_path):
            success = test_model(model_path, model_config['name'])
            results[model_config['name']] = success
        else:
            print(f"\n⚠️ Modelo no encontrado: {model_config['name']}")
            print(f"   Buscado en: {model_path}")
            results[model_config['name']] = False
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    
    working_models = []
    failed_models = []
    
    for name, success in results.items():
        if success:
            working_models.append(name)
            print(f"✅ {name}: FUNCIONA")
        else:
            failed_models.append(name)
            print(f"❌ {name}: NO FUNCIONA")
    
    print(f"\n📊 Total modelos funcionando: {len(working_models)}/{len(results)}")
    
    if working_models:
        print("\n🎉 Modelos que funcionan correctamente:")
        for model in working_models:
            print(f"   - {model}")
    
    if failed_models:
        print("\n⚠️ Modelos con problemas:")
        for model in failed_models:
            print(f"   - {model}")
        print("\n💡 Posibles soluciones:")
        print("   1. Verifica que los archivos .pt sean los pesos reales del entrenamiento")
        print("   2. Asegúrate de haber copiado los archivos correctamente")
        print("   3. Los archivos deben tener varios MB de tamaño")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    main()