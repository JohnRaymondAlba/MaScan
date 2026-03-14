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
fallback_errors = []

try:
    from flask_app import create_app
    app = create_app()
    
    # Add health check route
    @app.route('/health', methods=['GET'])
    def health():
        return {'status': 'ok', 'message': 'MaScan app is running on Vercel'}, 200
    
    # Add debug route to check app state
    @app.route('/_debug', methods=['GET'])
    def debug():
        return jsonify({
            'status': 'ok',
            'environment': os.getenv('FLASK_ENV', 'unknown'),
            'blueprints': list(app.blueprints.keys()),
            'routes': [str(rule) for rule in app.url_map.iter_rules()]
        }), 200
        
except Exception as e:
    # Log error for debugging
    error_msg = f"Failed to create Flask app: {str(e)}\n{traceback.format_exc()}"
    print(error_msg)
    fallback_errors.append(error_msg)
    
    # Use fallback app
    app = fallback_app
    
    @app.route('/')
    def root():
        return jsonify({
            'error': 'Failed to initialize MaScan app',
            'details': str(e),
            'initialization_errors': fallback_errors
        }), 500
    
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'error',
            'error': str(e),
            'full_traceback': error_msg
        }), 500
    
    @app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def catch_all(path):
        return jsonify({
            'error': 'App initialization failed',
            'requested_path': f'/{path}',
            'message': str(e)
        }), 500
