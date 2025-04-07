"""
WSGI entry point for the Trip Planning Assistant application
"""
from app_factory import create_app

# Create the application
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
