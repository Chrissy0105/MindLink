from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from extensions import db, bcrypt
import os

# ------------------- Initialize App and Config -------------------
app = Flask(__name__, 
    static_folder='static',
    static_url_path=''
)
app.config.from_object(Config)

# ------------------- Initialize Extensions with app -------------------
db.init_app(app)
bcrypt.init_app(app)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})  # Configure CORS for API routes

# Create tables within app context
with app.app_context():
    db.create_all()

# ------------------- Register Blueprints -------------------
from auth_bp import auth_bp
from chat_bp import chat_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(chat_bp, url_prefix='/api/chat')

if __name__ == '__main__':
    app.run(debug=True)

# ------------------- Create DB Tables -------------------
with app.app_context():
    db.create_all()

# ------------------- Frontend Routes -------------------
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/login')
def login():
    return send_from_directory('static', 'login.html')

@app.route('/signup')
def signup():
    return send_from_directory('static', 'signup.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory('static', 'dashboard.html')

# Handle 404 errors by returning to index
@app.errorhandler(404)
def not_found(e):
    return send_from_directory('static', 'index.html')

# ------------------- Health Check -------------------
@app.route('/api/health', methods=['GET'])
def health_check():
    return {'status': 'ok'}, 200

# ------------------- Run the App -------------------
if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
