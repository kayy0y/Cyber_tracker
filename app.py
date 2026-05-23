from flask import Flask, render_template, send_from_directory
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'fallback-dev-secret-change-in-production')

jwt = JWTManager(app)

# ── API Blueprints ──────────────────────────────────────────────
from routes.auth        import auth_bp
from routes.frameworks  import frameworks_bp
from routes.tasks       import tasks_bp
from routes.risks       import risks_bp
from routes.dashboard   import dashboard_bp
from routes.audit_logs  import audit_logs_bp

app.register_blueprint(auth_bp,       url_prefix='/api/auth')
app.register_blueprint(frameworks_bp, url_prefix='/api/frameworks')
app.register_blueprint(tasks_bp,      url_prefix='/api/tasks')
app.register_blueprint(risks_bp,      url_prefix='/api/risks')
app.register_blueprint(dashboard_bp,  url_prefix='/api/dashboard')
app.register_blueprint(audit_logs_bp, url_prefix='/api/auditlogs')

# ── Frontend Page Routes ────────────────────────────────────────
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/frameworks')
def frameworks_page():
    return render_template('frameworks.html')

@app.route('/tasks')
def tasks_page():
    return render_template('tasks.html')

@app.route('/risks')
def risks_page():
    return render_template('risks.html')

@app.route('/audit-logs')
def audit_logs_page():
    return render_template('audit_logs.html')

# ── Health check for Render ─────────────────────────────────────
@app.route('/health')
def health():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
