"""
Vercel Serverless Function Entry Point for MaScan Flask Application
"""

import sys
import os

# Get the directory paths
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, '../app')
src_dir = os.path.join(app_dir, 'src')

# Add directories to Python path
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

try:
    from flask_app import create_app
    app = create_app()
    
    # Add health check route if not already present
    @app.route('/health')
    def health():
        return {'status': 'ok', 'message': 'MaScan app is running on Vercel'}, 200
        
except Exception as e:
    # Log error for debugging
    import traceback
    error_msg = f"Failed to create Flask app: {str(e)}\n{traceback.format_exc()}"
    print(error_msg)
    
    # Create minimal app for debugging
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def root():
        return jsonify({'error': 'Failed to initialize app', 'details': str(e)}), 500
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'error', 'error': str(e)}), 500
