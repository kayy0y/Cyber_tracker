from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from config.database import get_db
from bson import ObjectId
from datetime import datetime
import bcrypt

auth_bp = Blueprint('auth', __name__)

def serialize_user(user):
    return {
        'id': str(user['_id']),
        'name': user['name'],
        'email': user['email'],
        'role': user['role']
    }

def log_action(user_id, action, module, details=''):
    db = get_db()
    db.audit_logs.insert_one({
        'userId': user_id,
        'action': action,
        'module': module,
        'details': details,
        'timestamp': datetime.utcnow()
    })

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    db = get_db()

    name     = (data.get('name') or '').strip()
    email    = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    role     = data.get('role', 'user')

    if not name or not email or not password:
        return jsonify({'message': 'Name, email and password are required'}), 400

    if len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters'}), 400

    if db.users.find_one({'email': email}):
        return jsonify({'message': 'An account with this email already exists'}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user_doc = {
        'name': name,
        'email': email,
        'password': hashed,
        'role': role if role in ['admin', 'user'] else 'user',
        'createdAt': datetime.utcnow()
    }

    result = db.users.insert_one(user_doc)
    user_doc['_id'] = result.inserted_id

    log_action(result.inserted_id, 'User registered', 'Auth', f'New account: {email}')

    token = create_access_token(
        identity=str(result.inserted_id),
        additional_claims={'role': user_doc['role']}
    )
    return jsonify({'token': token, 'user': serialize_user(user_doc)}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    db = get_db()

    email    = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = db.users.find_one({'email': email})
    if not user:
        return jsonify({'message': 'Invalid email or password'}), 400

    if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({'message': 'Invalid email or password'}), 400

    log_action(user['_id'], 'User logged in', 'Auth', f'{email} signed in')

    token = create_access_token(
        identity=str(user['_id']),
        additional_claims={'role': user['role']}
    )
    return jsonify({'token': token, 'user': serialize_user(user)})


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    db = get_db()
    user = db.users.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify(serialize_user(user))
