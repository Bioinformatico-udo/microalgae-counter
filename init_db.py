"""
Inicializa la base de datos con las tablas necesarias.
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def init_database():
    """Initialize database with all tables"""
    
    print("=" * 60)
    print("Inicializando Base de Datos")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar si la base de datos ya existe
            import os
            db_path = app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
            
            if db_path and os.path.exists(db_path):
                print(f"\n⚠️ Base de datos existente encontrada: {db_path}")
                respuesta = input("¿Desea eliminarla y crear una nueva? (s/n): ")
                if respuesta.lower() == 's':
                    print("Eliminando base de datos existente...")
                    db.drop_all()
                    print("✅ Base de datos eliminada")
                else:
                    print("Cancelando inicialización...")
                    return
            
            print("\nCreando nuevas tablas...")
            db.create_all()
            
            print("\n✅ Base de datos inicializada exitosamente!")
            
            # Mostrar tablas creadas
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("\n📊 Tablas creadas:")
            for table in sorted(tables):
                print(f"  - {table}")
            
            print(f"\n📁 Ubicación de la base de datos: {db_path if db_path else 'En memoria'}")
            
        except Exception as e:
            print(f"\n❌ Error al inicializar la base de datos: {e}")
            sys.exit(1)

if __name__ == '__main__':
    init_database()