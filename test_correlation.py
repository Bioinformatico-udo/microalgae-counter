"""
Script para probar la correlación directamente desde Python
"""

from app import app, db
from app import Batch, BatchCountingSession, BatchImageCount, AutomaticBatchResult, AutomaticImageResult, Image
from scipy import stats
import numpy as np

def test_correlation():
    with app.app_context():
        batch_id = 4
        print("=" * 60)
        print(f"ANALIZANDO CORRELACIÓN PARA BATCH ID: {batch_id}")
        print("=" * 60)
        
        # Obtener resultados automáticos
        batch_result = AutomaticBatchResult.query.filter_by(batch_id=batch_id)\
            .order_by(AutomaticBatchResult.processed_at.desc()).first()
        
        if not batch_result:
            print("❌ No hay resultados automáticos para este batch")
            return
        
        print(f"\n✅ Resultados automáticos encontrados:")
        print(f"   Modelo: {batch_result.model_used}")
        print(f"   Procesado: {batch_result.processed_at}")
        
        # Obtener conteos automáticos
        auto_counts = {}
        for r in batch_result.image_results:
            auto_counts[r.image_id] = r.count
        print(f"   Conteos automáticos: {len(auto_counts)}")
        
        # Obtener sesiones manuales
        sessions = BatchCountingSession.query.filter_by(batch_id=batch_id, is_completed=True).all()
        print(f"\n✅ Sesiones manuales: {len(sessions)}")
        
        if len(sessions) == 0:
            print("❌ No hay sesiones manuales completadas")
            return
        
        # Para cada sesión, calcular correlación
        all_manual_counts = []
        all_auto_counts = []
        
        for session in sessions:
            counts = BatchImageCount.query.filter_by(session_id=session.id).all()
            print(f"\n   Técnico: {session.technician_name}")
            print(f"   Conteos manuales: {len(counts)}")
            
            manual_vals = []
            auto_vals = []
            
            for count in counts:
                if count.image_id in auto_counts:
                    manual_vals.append(count.manual_count)
                    auto_vals.append(auto_counts[count.image_id])
                    all_manual_counts.append(count.manual_count)
                    all_auto_counts.append(auto_counts[count.image_id])
            
            print(f"   Pares coincidentes: {len(manual_vals)}")
            
            if len(manual_vals) >= 2:
                corr, p_val = stats.pearsonr(manual_vals, auto_vals)
                print(f"   Correlación: r={corr:.4f}, p={p_val:.6f}")
            else:
                print(f"   ❌ Insuficientes datos para correlación")
        
        # Correlación global
        print(f"\n{'='*60}")
        print(f"DATOS GLOBALES")
        print(f"{'='*60}")
        print(f"Total pares manual-auto: {len(all_manual_counts)}")
        
        if len(all_manual_counts) >= 2:
            print(f"\nPrimeros 10 pares:")
            for i in range(min(10, len(all_manual_counts))):
                print(f"   Imagen {i+1}: Manual={all_manual_counts[i]}, Auto={all_auto_counts[i]}")
            
            corr, p_val = stats.pearsonr(all_manual_counts, all_auto_counts)
            print(f"\n📊 CORRELACIÓN GLOBAL:")
            print(f"   Coeficiente de Pearson (r): {corr:.4f}")
            print(f"   Valor p: {p_val:.6f}")
            print(f"   Muestras: {len(all_manual_counts)}")
            
            if corr >= 0.7:
                print(f"   Interpretación: Correlación FUERTE")
            elif corr >= 0.4:
                print(f"   Interpretación: Correlación MODERADA")
            else:
                print(f"   Interpretación: Correlación DÉBIL")
                
            if p_val < 0.05:
                print(f"   Significancia: Estadísticamente significativo (p < 0.05)")
            else:
                print(f"   Significancia: No estadísticamente significativo (p ≥ 0.05)")
        else:
            print(f"❌ No hay suficientes datos para correlación global")
            print(f"   Se necesitan al menos 2 pares manual-auto")

if __name__ == '__main__':
    test_correlation()