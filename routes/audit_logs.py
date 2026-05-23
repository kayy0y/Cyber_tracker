from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from config.database import get_db
from datetime import datetime

audit_logs_bp = Blueprint('audit_logs', __name__)

@audit_logs_bp.route('/', methods=['GET'])
@jwt_required()
def get_all():
    db = get_db()
    logs_cursor = db.audit_logs.find().sort('timestamp', -1).limit(200)
    logs = []
    for log in logs_cursor:
        user_name = 'System'
        if log.get('userId'):
            user = db.users.find_one({'_id': log['userId']}, {'name': 1, 'email': 1})
            if user:
                user_name = user.get('name', 'Unknown')
        logs.append({
            'action': log.get('action', ''),
            'module': log.get('module', ''),
            'details': log.get('details', ''),
            'userName': user_name,
            'timestamp': log.get('timestamp', datetime.utcnow()).isoformat()
        })
    return jsonify(logs)
