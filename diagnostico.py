"""
Script para diagnosticar problemas en la visualización de resultados
"""

from app import app, db
from app import Image, Batch, BatchCountingSession, BatchImageCount, AutomaticBatchResult, AutomaticImageResult

def diagnosticar():
    with app.app_context():
        print("=" * 60)
        print("DIAGNÓSTICO DE RESULTADOS")
        print("=" * 60)
        
        # 1. Verificar batches
        batches = Batch.query.all()
        print(f"\n📦 Batches encontrados: {len(batches)}")
        for batch in batches:
            print(f"   - ID: {batch.id}, Nombre: {batch.name}, Tipo: {getattr(batch, 'culture_type', 'monoclonal')}")
        
        # 2. Verificar imágenes en batches
        print(f"\n🖼️ Verificando imágenes...")
        for batch in batches:
            images = Image.query.filter_by(batch_id=batch.id).all()
            print(f"   Batch {batch.id}: {len(images)} imágenes")
        
        # 3. Verificar conteos manuales
        print(f"\n📝 Verificando conteos manuales...")
        sessions = BatchCountingSession.query.all()
        print(f"   Sesiones de conteo: {len(sessions)}")
        for session in sessions:
            counts = BatchImageCount.query.filter_by(session_id=session.id).all()
            print(f"   - Sesión {session.id} (Técnico: {session.technician_name}): {len(counts)} conteos")
            if counts:
                print(f"     Primer conteo: Imagen {counts[0].image_id} = {counts[0].manual_count}")
        
        # 4. Verificar conteos automáticos
        print(f"\n🤖 Verificando conteos automáticos...")
        auto_results = AutomaticBatchResult.query.all()
        print(f"   Resultados automáticos: {len(auto_results)}")
        for ar in auto_results:
            img_results = AutomaticImageResult.query.filter_by(batch_result_id=ar.id).all()
            print(f"   - Batch {ar.batch_id}: {len(img_results)} conteos automáticos")
            if img_results:
                print(f"     Primer conteo: Imagen {img_results[0].image_id} = {img_results[0].count}")
        
        # 5. Verificar endpoint de auto-results
        print(f"\n🔍 Verificando endpoint /api/batch/auto-results/4...")
        from routes.api_routes import get_batch_auto_results
        with app.test_request_context():
            # Simular petición
            result = get_batch_auto_results(4)
            print(f"   Respuesta: {result[0].json if hasattr(result[0], 'json') else 'No JSON'}")
        
        print("\n" + "=" * 60)
        print("DIAGNÓSTICO COMPLETADO")
        print("=" * 60)

if __name__ == '__main__':
    diagnosticar()