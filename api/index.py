"""
Vercel Serverless Function Entry Point for MaScan Flask Application
"""

import sys
import os
import traceback
from flask import Flask, jsonify

# Get the directory paths
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, '../app')
src_dir = os.path.join(app_dir, 'src')

# Add directories to Python path
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Create fallback app first
fallback_app = Flask(__name__)

try:
    from flask_app import create_app
    app = create_app()
    
except Exception as e:
    # Log error for debugging
    error_msg = f"Failed to create Flask app: {str(e)}\n{traceback.format_exc()}"
    print(error_msg)
    
    # Use fallback app
    app = fallback_app
    
    @app.route('/')
    @app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
    def catch_all(path=''):
        return jsonify({
            'error': 'App initialization failed',
            'details': str(e),
            'full_error': error_msg,
            'required_setup': {
                'step_1': 'Go to Vercel dashboard → Project Settings → Environment Variables',
                'step_2': 'Add DATABASE_URL with your Supabase PostgreSQL connection string',
                'step_3': 'Add SECRET_KEY with a strong random key',
                'step_4': 'Redeploy the project',
                'docs': 'See DEPLOYMENT.md in your repository for details'
            }
        }), 500

# Add health check and debug endpoints (work even if blueprint loading failed)
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    from database import db
    db_status = 'connected' if hasattr(db, 'is_connected') and db.is_connected else 'disconnected'
    
    return jsonify({
        'status': 'alive',
        'database': db_status,
        'environment': os.getenv('FLASK_ENV', 'development'),
        'version': '1.0'
    }), 200

@app.route('/_debug', methods=['GET'])
def debug():
    """Debug endpoint showing app configuration."""
    from database import db
    
    db_connected = hasattr(db, 'is_connected') and db.is_connected
    
    return jsonify({
        'app_name': 'MaScan Attendance System',
        'environment': os.getenv('FLASK_ENV', 'development'),
        'database_connected': db_connected,
        'has_database_url': bool(os.getenv('DATABASE_URL')),
        'blueprints': list(app.blueprints.keys()),
        'routes_count': len([rule for rule in app.url_map.iter_rules()]),
        'static_folder': app.static_folder,
        'template_folder': app.template_folder
    }), 200
