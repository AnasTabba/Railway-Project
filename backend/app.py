import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import extensions and configuration
from config import config
from extensions import db, jwt

# Import blueprints
from routes.auth_routes import auth_bp
from routes.station_routes import station_bp
from routes.train_routes import train_bp
from routes.schedule_routes import schedule_bp
from routes.search_routes import search_bp
from routes.booking_routes import booking_bp
from routes.payment_routes import payment_bp
from routes.admin_routes import admin_bp

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(station_bp)
    app.register_blueprint(train_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(admin_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'Railway Management System API is running'}), 200
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=os.getenv('FLASK_ENV') == 'development', host='0.0.0.0', port=5000)
