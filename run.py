"""
Quick start script for Microalgae Counter
"""

import os
import sys

def setup_directories():
    """Create necessary directories"""
    dirs = ['uploads', 'database', 'static/images/results', 'models', 'static/css', 'static/js']
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✅ Created directory: {dir_name}")

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import flask_sqlalchemy
        print("✅ Flask dependencies OK")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install flask flask-sqlalchemy flask-cors")
        return False
    
    try:
        import numpy
        import cv2
        print("✅ Image processing dependencies OK")
    except ImportError as e:
        print(f"⚠️ Optional dependency missing: {e}")
        print("Some features may be limited")
    
    return True

def main():
    """Main setup function"""
    print("=" * 50)
    print("Microalgae Counter - Setup")
    print("=" * 50)
    
    # Create directories
    setup_directories()
    
    # Check dependencies
    if not check_dependencies():
        print("\n⚠️ Please install missing dependencies and try again")
        return
    
    # Create .env file if not exists
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write("""FLASK_ENV=development
SECRET_KEY=dev-secret-key-12345
YOLO_MODEL_PATH=models/yolo11m_microalgae.pt
""")
        print("✅ Created .env file")
    
    print("\n" + "=" * 50)
    print("Setup complete! Starting application...")
    print("=" * 50)
    print("\n💡 Note: The YOLO model is not installed yet.")
    print("   Automatic counting will use demonstration mode.")
    print("   To enable real AI counting, train a YOLO model and place it at:")
    print("   models/yolo11m_microalgae.pt\n")
    
    # Run the application
    from app import create_app
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()