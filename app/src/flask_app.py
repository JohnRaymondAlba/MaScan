"""Main Flask application for MaScan Attendance System."""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_session import Session
import os
from dotenv import load_dotenv

# Only import constants if not in production
try:
    from config.constants import *
except Exception as e:
    print(f"Warning: Could not load constants: {e}")

# Load environment variables
load_dotenv()

def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mascan-attendance-secret-key-2024')
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file upload
    
    # Determine environment and configure sessions accordingly
    env = os.getenv('FLASK_ENV', 'development')
    redis_url = os.getenv('REDIS_URL')
    
    if env == 'production' and redis_url:
        # Use Redis for production (Vercel)
        try:
            import redis
            app.config['SESSION_TYPE'] = 'redis'
            app.config['SESSION_REDIS'] = redis.from_url(redis_url)
        except ImportError:
            # Fallback to filesystem if redis not available
            app.config['SESSION_TYPE'] = 'filesystem'
    else:
        # Use filesystem for local development
        app.config['SESSION_TYPE'] = 'filesystem'
    
    # Enable CORS
    CORS(app)
    
    # Initialize Flask-Session
    try:
        Session(app)
    except Exception as e:
        print(f"Warning: Could not initialize sessions: {e}")
    
    # Add basic health check routes first (work without database)
    @app.route('/', methods=['GET'])
    def home():
        return jsonify({
            'status': 'ok',
            'app': 'MaScan Attendance System',
            'version': '1.0'
        }), 200
    
    @app.route('/health', methods=['GET'])
    def health_check():
        from database import db
        db_connected = hasattr(db, 'is_connected') and db.is_connected
        
        return jsonify({
            'status': 'ok' if db_connected else 'partial',
            'database': 'connected' if db_connected else 'disconnected',
            'app': 'MaScan Attendance System'
        }), 200 if db_connected else 503
    
    # Import database to check connection status
    from database import db
    db_connected = hasattr(db, 'is_connected') and db.is_connected
    
    # Register blueprints only if database is connected
    if db_connected:
        try:
            from routes.auth_routes import auth_bp
            from routes.dashboard_routes import dashboard_bp
            from routes.event_routes import event_bp
            from routes.attendance_routes import attendance_bp
            from routes.user_routes import user_bp
            from routes.api_routes import api_bp
            from routes.qr_management_routes import qr_mgmt_bp
            
            app.register_blueprint(auth_bp)
            app.register_blueprint(dashboard_bp)
            app.register_blueprint(event_bp)
            app.register_blueprint(attendance_bp)
            app.register_blueprint(user_bp)
            app.register_blueprint(api_bp, url_prefix='/api')
            app.register_blueprint(qr_mgmt_bp)
            
            print("All blueprints registered successfully")
        except Exception as e:
            print(f"Warning: Could not load some blueprints: {e}")
            import traceback
            print(traceback.format_exc())
    else:
        print("WARNING: Database not connected - blueprints not loaded")
        print("DATABASE_URL environment variable may not be set")
        print("Visit /setup-help for configuration instructions")
        
        @app.route('/setup-help', methods=['GET'])
        def setup_help():
            return jsonify({
                'error': 'Database not configured',
                'steps': [
                    'Go to Vercel project dashboard',
                    'Navigate to Settings → Environment Variables',
                    'Add DATABASE_URL with your Supabase connection string',
                    'Redeploy the project'
                ],
                'docs': 'Check DEPLOYMENT.md and SUPABASE_SETUP.md in the repository'
            }), 503
    
    # Add global error handlers
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error', 'message': str(error)}), 500
    
    @app.errorhandler(404)
    def not_found_handler(error):
        return jsonify({'error': 'Route not found', 'message': str(error)}), 404
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
