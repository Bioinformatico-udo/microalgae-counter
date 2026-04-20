"""
Script to create sample model metadata and placeholder files.
Run this to set up the model directory structure.
"""

import os
import json
from datetime import datetime

def create_sample_models():
    """Create sample model metadata and placeholder files"""
    
    # Model configurations
    models_config = {
        'default': {
            'yolo11m_default': {
                'version': '1.0',
                'accuracy': 0.85,
                'description': 'Modelo por defecto para todo tipo de microalgas',
                'training_date': datetime.now().isoformat()
            }
        },
        'monoclonal': {
            'yolo11m_monoclonal_v1': {
                'version': '1.0',
                'accuracy': 0.92,
                'description': 'Modelo especializado para cultivos monoclonales - Chlorella vulgaris',
                'training_date': datetime.now().isoformat()
            },
            'yolo11m_monoclonal_v2': {
                'version': '2.0',
                'accuracy': 0.94,
                'description': 'Modelo mejorado para monoclonales - incluye Scenedesmus',
                'training_date': datetime.now().isoformat()
            }
        },
        'policlonal': {
            'yolo11m_policlonal_v1': {
                'version': '1.0',
                'accuracy': 0.88,
                'description': 'Modelo para cultivos policlonales - múltiples especies',
                'training_date': datetime.now().isoformat()
            }
        },
        'refined': {
            'yolo11m_refined_v1': {
                'version': '1.0',
                'accuracy': 0.96,
                'description': 'Modelo refinado con datos de campo',
                'training_date': datetime.now().isoformat()
            }
        }
    }
    
    # Create directories and metadata files
    for model_type, models in models_config.items():
        model_dir = os.path.join('models', model_type)
        os.makedirs(model_dir, exist_ok=True)
        
        # Create metadata.json
        metadata_file = os.path.join(model_dir, 'metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(models, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created metadata for {model_type}")
        
        # Create placeholder .pt files
        for model_name in models.keys():
            model_path = os.path.join(model_dir, f"{model_name}.pt")
            with open(model_path, 'w') as f:
                f.write(f"# Placeholder for {model_name}\n")
                f.write("# Replace with actual trained model weights\n")
            print(f"   Created placeholder: {model_name}.pt")
    
    print("\n" + "="*50)
    print("✅ Sample model structure created!")
    print("="*50)
    print("\n📌 To use real models:")
    print("   1. Train your YOLO models")
    print("   2. Copy .pt files to corresponding directories:")
    print("      - models/default/     for default model")
    print("      - models/monoclonal/  for monoclonal models")
    print("      - models/policlonal/  for policlonal models")
    print("      - models/refined/     for refined models")
    print("   3. Update metadata.json with accuracy and descriptions")

if __name__ == '__main__':
    create_sample_models()