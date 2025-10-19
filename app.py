from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db, bcrypt
from auth_bp import auth_bp
from chat_bp import chat_bp

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)

# Configure CORS properly
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5000", "http://127.0.0.1:5000"])

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(chat_bp, url_prefix='/api/chat')

@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'ok', 'message': 'MindLink API is running'}, 200

# Serve static files for frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    try:
        return app.send_static_file('index.html')
    except:
        return {'error': 'Frontend not found'}, 404

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    print("🚀 Starting MindLink server on http://localhost:5000")
    print("📊 API endpoints available at:")
    print("   - POST http://localhost:5000/api/auth/signup")
    print("   - POST http://localhost:5000/api/auth/login")
    print("   - POST http://localhost:5000/api/chat/message")
    print("   - GET  http://localhost:5000/api/chat/history")
    app.run(host='0.0.0.0', port=5000, debug=True)