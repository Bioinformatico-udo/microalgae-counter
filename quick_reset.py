"""
Reset rápido de base de datos - Sin interacción
Ejecutar para limpiar todos los datos rápidamente
"""

from app import app, db

def quick_reset():
    print("🔄 Reseteando base de datos...")
    
    with app.app_context():
        # Obtener tablas existentes
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if tables:
            print(f"📋 Eliminando {len(tables)} tablas...")
            db.drop_all()
            print("✅ Tablas eliminadas")
        
        print("🏗️  Creando nuevas tablas...")
        db.create_all()
        
        # Verificar
        inspector = inspect(db.engine)
        new_tables = inspector.get_table_names()
        print(f"✅ Base de datos reseteada. {len(new_tables)} tablas creadas.")
        
        for table in sorted(new_tables):
            print(f"   - {table}")

if __name__ == '__main__':
    quick_reset()