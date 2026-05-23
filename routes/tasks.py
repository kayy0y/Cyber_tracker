from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from config.database import get_db
from bson import ObjectId
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)

def serialize(task):
    assigned = task.get('assignedTo')
    framework = task.get('frameworkId')
    return {
        'id': str(task['_id']),
        'title': task.get('title', ''),
        'description': task.get('description', ''),
        'assignedTo': {'id': str(assigned['_id']), 'name': assigned.get('name', ''), 'email': assigned.get('email', '')} if assigned and isinstance(assigned, dict) else None,
        'frameworkId': {'id': str(framework['_id']), 'frameworkName': framework.get('frameworkName', '')} if framework and isinstance(framework, dict) else None,
        'deadline': task['deadline'].isoformat() if task.get('deadline') else None,
        'priority': task.get('priority', 'Medium'),
        'status': task.get('status', 'Pending'),
        'createdAt': task.get('createdAt', datetime.utcnow()).isoformat()
    }

def log_action(user_id, action, details=''):
    get_db().audit_logs.insert_one({
        'userId': ObjectId(user_id) if user_id else None,
        'action': action,
        'module': 'Tasks',
        'details': details,
        'timestamp': datetime.utcnow()
    })

def enrich_task(task, db):
    """Replace ObjectId refs with actual documents"""
    if task.get('assignedTo') and isinstance(task['assignedTo'], ObjectId):
        user = db.users.find_one({'_id': task['assignedTo']}, {'password': 0})
        task['assignedTo'] = user
    if task.get('frameworkId') and isinstance(task['frameworkId'], ObjectId):
        fw = db.frameworks.find_one({'_id': task['frameworkId']})
        task['frameworkId'] = fw
    return task

@tasks_bp.route('/users/all', methods=['GET'])
@jwt_required()
def get_users():
    db = get_db()
    users = list(db.users.find({}, {'password': 0}))
    return jsonify([{'id': str(u['_id']), 'name': u['name'], 'email': u['email'], 'role': u['role']} for u in users])

@tasks_bp.route('/', methods=['GET'])
@jwt_required()
def get_all():
    db = get_db()
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role', 'user')

    query = {} if role == 'admin' else {'assignedTo': ObjectId(user_id)}
    tasks = list(db.tasks.find(query).sort('createdAt', -1))
    tasks = [enrich_task(t, db) for t in tasks]
    return jsonify([serialize(t) for t in tasks])

@tasks_bp.route('/', methods=['POST'])
@jwt_required()
def create():
    data = request.get_json()
    db = get_db()
    user_id = get_jwt_identity()

    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({'message': 'Task title is required'}), 400

    assigned_id = data.get('assignedTo')
    framework_id = data.get('frameworkId')
    deadline_str = data.get('deadline')

    doc = {
        'title': title,
        'description': data.get('description', ''),
        'assignedTo': ObjectId(assigned_id) if assigned_id else None,
        'frameworkId': ObjectId(framework_id) if framework_id else None,
        'deadline': datetime.fromisoformat(deadline_str) if deadline_str else None,
        'priority': data.get('priority', 'Medium'),
        'status': data.get('status', 'Pending'),
        'createdBy': ObjectId(user_id),
        'createdAt': datetime.utcnow()
    }
    result = db.tasks.insert_one(doc)
    doc['_id'] = result.inserted_id
    doc = enrich_task(doc, db)

    log_action(user_id, 'Task created', title)
    return jsonify(serialize(doc)), 201

@tasks_bp.route('/<task_id>', methods=['PUT'])
@jwt_required()
def update(task_id):
    data = request.get_json()
    db = get_db()
    user_id = get_jwt_identity()

    update_fields = {}
    if 'title' in data:       update_fields['title']       = data['title']
    if 'description' in data: update_fields['description'] = data['description']
    if 'priority' in data:    update_fields['priority']    = data['priority']
    if 'status' in data:      update_fields['status']      = data['status']
    if 'assignedTo' in data:
        update_fields['assignedTo'] = ObjectId(data['assignedTo']) if data['assignedTo'] else None
    if 'frameworkId' in data:
        update_fields['frameworkId'] = ObjectId(data['frameworkId']) if data['frameworkId'] else None
    if 'deadline' in data:
        update_fields['deadline'] = datetime.fromisoformat(data['deadline']) if data['deadline'] else None

    db.tasks.update_one({'_id': ObjectId(task_id)}, {'$set': update_fields})
    task = db.tasks.find_one({'_id': ObjectId(task_id)})
    if not task:
        return jsonify({'message': 'Task not found'}), 404

    task = enrich_task(task, db)
    log_action(user_id, 'Task updated', f"{task.get('title', '')} → {task.get('status', '')}")
    return jsonify(serialize(task))

@tasks_bp.route('/<task_id>', methods=['DELETE'])
@jwt_required()
def delete(task_id):
    db = get_db()
    user_id = get_jwt_identity()

    task = db.tasks.find_one({'_id': ObjectId(task_id)})
    if not task:
        return jsonify({'message': 'Task not found'}), 404

    db.tasks.delete_one({'_id': ObjectId(task_id)})
    log_action(user_id, 'Task deleted', task.get('title', ''))
    return jsonify({'message': 'Task deleted successfully'})
