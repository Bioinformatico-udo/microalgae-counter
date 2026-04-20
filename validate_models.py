"""
Valida que los modelos YOLO sean correctos y se puedan cargar.
"""

import os
import torch
from pathlib import Path
from ultralytics import YOLO

# Permitir cargar modelos YOLO de forma segura
torch.serialization.add_safe_globals(['ultralytics.nn.tasks.DetectionModel'])

def validate_yolo_model(model_path):
    """
    Valida si un archivo .pt es un modelo YOLO válido.
    """
    try:
        if not os.path.exists(model_path):
            return False, 0, "Archivo no encontrado"
        
        size_bytes = os.path.getsize(model_path)
        size_mb = size_bytes / (1024 * 1024)
        
        # Verificar que no sea un placeholder de texto
        with open(model_path, 'rb') as f:
            first_bytes = f.read(10)
            if first_bytes.startswith(b'#'):
                return False, size_mb, "Archivo placeholder (contiene solo texto)"
        
        # Intentar cargar con torch usando weights_only=False para modelos YOLO
        try:
            checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
            return True, size_mb, "Modelo YOLO válido"
        except Exception as e:
            # Si falla, intentar cargar directamente con YOLO
            try:
                model = YOLO(model_path)
                return True, size_mb, "Modelo YOLO válido (cargado con ultralytics)"
            except:
                return False, size_mb, f"Error: {str(e)[:100]}"
            
    except Exception as e:
        return False, 0, f"Error: {str(e)[:100]}"

def main():
    print("="*60)
    print("Validación de Modelos YOLO")
    print("="*60)
    print()
    
    model_dirs = ['default', 'monoclonal', 'policlonal', 'refined']
    base_path = Path('models')
    
    valid_models = []
    invalid_models = []
    
    for model_dir in model_dirs:
        dir_path = base_path / model_dir
        if dir_path.exists():
            for pt_file in dir_path.glob('*.pt'):
                is_valid, size_mb, message = validate_yolo_model(str(pt_file))
                
                if is_valid:
                    valid_models.append((pt_file, size_mb))
                    print(f"✅ {pt_file.parent.name}/{pt_file.name}")
                    print(f"   Tamaño: {size_mb:.2f} MB - {message}")
                else:
                    invalid_models.append((pt_file, message))
                    print(f"❌ {pt_file.parent.name}/{pt_file.name}")
                    print(f"   {message}")
                print()
    
    print("="*60)
    print("RESUMEN")
    print("="*60)
    print(f"✅ Modelos válidos: {len(valid_models)}")
    for model, size in valid_models:
        print(f"   - {model.parent.name}/{model.name} ({size:.2f} MB)")
    
    if invalid_models:
        print(f"\n❌ Modelos inválidos: {len(invalid_models)}")
        for model, error in invalid_models:
            print(f"   - {model.parent.name}/{model.name}: {error}")
    
    print()

if __name__ == '__main__':
    main()