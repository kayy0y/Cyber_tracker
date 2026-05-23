from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from config.database import get_db
from bson import ObjectId
from datetime import datetime

frameworks_bp = Blueprint('frameworks', __name__)

def serialize(fw):
    return {
        'id': str(fw['_id']),
        'frameworkName': fw.get('frameworkName', ''),
        'description': fw.get('description', ''),
        'status': fw.get('status', 'Pending'),
        'completionPercentage': fw.get('completionPercentage', 0),
        'createdAt': fw.get('createdAt', datetime.utcnow()).isoformat()
    }

def log_action(user_id, action, details=''):
    get_db().audit_logs.insert_one({
        'userId': ObjectId(user_id) if user_id else None,
        'action': action,
        'module': 'Frameworks',
        'details': details,
        'timestamp': datetime.utcnow()
    })

@frameworks_bp.route('/', methods=['GET'])
@jwt_required()
def get_all():
    db = get_db()
    frameworks = list(db.frameworks.find().sort('createdAt', -1))
    return jsonify([serialize(f) for f in frameworks])

@frameworks_bp.route('/<fw_id>', methods=['GET'])
@jwt_required()
def get_one(fw_id):
    db = get_db()
    fw = db.frameworks.find_one({'_id': ObjectId(fw_id)})
    if not fw:
        return jsonify({'message': 'Framework not found'}), 404
    return jsonify(serialize(fw))

@frameworks_bp.route('/', methods=['POST'])
@jwt_required()
def create():
    data = request.get_json()
    db = get_db()
    user_id = get_jwt_identity()

    name = (data.get('frameworkName') or '').strip()
    if not name:
        return jsonify({'message': 'Framework name is required'}), 400

    doc = {
        'frameworkName': name,
        'description': data.get('description', ''),
        'status': data.get('status', 'Pending'),
        'completionPercentage': int(data.get('completionPercentage', 0)),
        'createdBy': ObjectId(user_id),
        'createdAt': datetime.utcnow()
    }
    result = db.frameworks.insert_one(doc)
    doc['_id'] = result.inserted_id

    log_action(user_id, 'Compliance framework created', name)
    return jsonify(serialize(doc)), 201

@frameworks_bp.route('/<fw_id>', methods=['PUT'])
@jwt_required()
def update(fw_id):
    data = request.get_json()
    db = get_db()
    user_id = get_jwt_identity()

    update_fields = {}
    if 'frameworkName' in data: update_fields['frameworkName'] = data['frameworkName']
    if 'description' in data:   update_fields['description']   = data['description']
    if 'status' in data:        update_fields['status']        = data['status']
    if 'completionPercentage' in data:
        update_fields['completionPercentage'] = int(data['completionPercentage'])

    db.frameworks.update_one({'_id': ObjectId(fw_id)}, {'$set': update_fields})
    fw = db.frameworks.find_one({'_id': ObjectId(fw_id)})
    if not fw:
        return jsonify({'message': 'Framework not found'}), 404

    log_action(user_id, 'Compliance framework updated', fw.get('frameworkName', ''))
    return jsonify(serialize(fw))

@frameworks_bp.route('/<fw_id>', methods=['DELETE'])
@jwt_required()
def delete(fw_id):
    db = get_db()
    user_id = get_jwt_identity()

    fw = db.frameworks.find_one({'_id': ObjectId(fw_id)})
    if not fw:
        return jsonify({'message': 'Framework not found'}), 404

    db.frameworks.delete_one({'_id': ObjectId(fw_id)})
    log_action(user_id, 'Compliance framework deleted', fw.get('frameworkName', ''))
    return jsonify({'message': 'Framework deleted successfully'})
