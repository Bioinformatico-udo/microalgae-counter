"""
Script para resetear completamente la base de datos.
Elimina todas las tablas y las vuelve a crear desde cero.
"""

import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def reset_database():
    """Reset all database tables"""
    from app import app, db
    
    with app.app_context():
        print("=" * 60)
        print("🔄 RESETEANDO BASE DE DATOS")
        print("=" * 60)
        
        # Obtener lista de tablas antes de eliminar
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if existing_tables:
            print(f"\n📋 Tablas existentes: {', '.join(existing_tables)}")
            print(f"   Total: {len(existing_tables)} tablas")
            
            print("\n🗑️  Eliminando todas las tablas...")
            db.drop_all()
            print("✅ Tablas eliminadas exitosamente")
        else:
            print("\n📋 No hay tablas existentes")
        
        print("\n🏗️  Creando nuevas tablas...")
        db.create_all()
        
        # Verificar tablas creadas
        inspector = inspect(db.engine)
        new_tables = inspector.get_table_names()
        
        print(f"\n✅ Base de datos reseteada exitosamente!")
        print(f"\n📊 Tablas creadas ({len(new_tables)}):")
        for table in sorted(new_tables):
            print(f"   - {table}")
        
        print("\n" + "=" * 60)
        print("✅ RESET COMPLETADO")
        print("=" * 60)


def delete_database_file():
    """Elimina el archivo de base de datos físicamente"""
    db_path = os.path.abspath('database/counts.db')
    if os.path.exists(db_path):
        # Obtener tamaño del archivo antes de eliminar
        size_bytes = os.path.getsize(db_path)
        size_mb = size_bytes / (1024 * 1024)
        os.remove(db_path)
        print(f"🗑️  Archivo de base de datos eliminado: {db_path}")
        print(f"   Tamaño: {size_mb:.2f} MB")
        return True
    else:
        print(f"ℹ️  No se encontró archivo de base de datos en: {db_path}")
        return False


def full_reset():
    """Reset completo: elimina archivo y recrea desde cero"""
    print("\n" + "=" * 60)
    print("⚠️  RESET COMPLETO DE BASE DE DATOS")
    print("=" * 60)
    print("\nEsta operación ELIMINARÁ TODOS LOS DATOS:")
    print("  - Imágenes subidas (solo referencias, no los archivos físicos)")
    print("  - Sets creados")
    print("  - Conteos manuales")
    print("  - Conteos automáticos")
    print("  - Sesiones de técnicos")
    print("  - Resultados de correlación")
    
    confirm = input("\n¿Está seguro? (escribe 'SI' para confirmar): ")
    
    if confirm == 'SI':
        print("\n🔄 Ejecutando reset completo...")
        
        # Primero eliminar el archivo de base de datos
        delete_database_file()
        
        # Luego recrear desde app
        from app import app, db
        with app.app_context():
            db.create_all()
            print("✅ Base de datos recreada desde cero")
        
        # Verificar tablas
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\n📊 Tablas creadas ({len(tables)}):")
        for table in sorted(tables):
            print(f"   - {table}")
        
        print("\n✅ Reset completo finalizado!")
    else:
        print("\n❌ Reset cancelado")


def quick_reset():
    """Reset rápido sin eliminar el archivo"""
    from app import app, db
    
    with app.app_context():
        print("\n🔄 Ejecutando reset rápido...")
        
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
        
        print("✅ Reset rápido completado!")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("RESETEADOR DE BASE DE DATOS")
    print("=" * 60)
    print("\nOpciones:")
    print("  1. Reset rápido (recrea tablas vacías)")
    print("  2. Reset completo (elimina archivo y recrea)")
    print("  3. Salir")
    
    option = input("\nSeleccione una opción (1, 2 o 3): ").strip()
    
    if option == '1':
        quick_reset()
    elif option == '2':
        full_reset()
    else:
        print("\nSaliendo...")