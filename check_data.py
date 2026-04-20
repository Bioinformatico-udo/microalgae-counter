"""
Script para diagnosticar qué datos hay en la base de datos
"""

from app import app, db
from app import Batch, BatchCountingSession, BatchImageCount, AutomaticBatchResult, AutomaticImageResult, Image

def check_data():
    with app.app_context():
        print("=" * 60)
        print("DIAGNÓSTICO DE BASE DE DATOS")
        print("=" * 60)
        
        # Verificar batches
        batches = Batch.query.all()
        print(f"\n📦 Batches: {len(batches)}")
        for batch in batches:
            print(f"   - ID: {batch.id}, Nombre: {batch.name}, Imágenes: {batch.total_images}")
            
            # Verificar imágenes del batch
            images = Image.query.filter_by(batch_id=batch.id).all()
            print(f"     Imágenes en batch: {len(images)}")
            for img in images:
                print(f"       - ID: {img.id}, Archivo: {img.filename}")
            
            # Verificar sesiones de conteo manual
            sessions = BatchCountingSession.query.filter_by(batch_id=batch.id).all()
            print(f"     Sesiones de conteo manual: {len(sessions)}")
            for session in sessions:
                print(f"       - Técnico: {session.technician_name}, Completada: {session.is_completed}")
                counts = BatchImageCount.query.filter_by(session_id=session.id).all()
                print(f"         Conteos manuales: {len(counts)}")
                for count in counts:
                    print(f"           - Imagen ID: {count.image_id}, Conteo: {count.manual_count}, Tiempo: {count.time_taken_seconds}")
            
            # Verificar resultados automáticos
            auto_results = AutomaticBatchResult.query.filter_by(batch_id=batch.id).all()
            print(f"     Resultados automáticos: {len(auto_results)}")
            for auto in auto_results:
                print(f"       - Modelo: {auto.model_used}, Procesado: {auto.processed_at}")
                img_results = AutomaticImageResult.query.filter_by(batch_result_id=auto.id).all()
                print(f"         Conteos automáticos: {len(img_results)}")
                for ir in img_results:
                    print(f"           - Imagen ID: {ir.image_id}, Conteo: {ir.count}")

if __name__ == '__main__':
    check_data()