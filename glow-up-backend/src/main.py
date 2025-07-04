from flask import Flask, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.auth import auth_bp
from src.routes.user import user_bp
from src.routes.ai_plans import ai_plans_bp
from src.routes.progress import progress_bp
import os

def create_app():
    app = Flask(__name__)
    
    # Configuración
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///glow_up.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configurar CORS
    CORS(app, origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
    
    # Inicializar base de datos
    db.init_app(app)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(ai_plans_bp, url_prefix='/api')
    app.register_blueprint(progress_bp, url_prefix='/api')
    
    # Crear tablas
    with app.app_context():
        db.create_all()
    
    # Ruta de salud
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Glow-Up AI Backend está funcionando correctamente'
        }), 200
    
    # Manejo de errores
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint no encontrado'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Error interno del servidor'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

