from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config.database import get_db
from bson import ObjectId
from datetime import datetime

risks_bp = Blueprint('risks', __name__)

SEVERITY_SCORE = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}

def serialize(risk):
    return {
        'id': str(risk['_id']),
        'title': risk.get('title', ''),
        'description': risk.get('description', ''),
        'severity': risk.get('severity', 'Medium'),
        'likelihood': risk.get('likelihood', 1),
        'impact': risk.get('impact', ''),
        'mitigationPlan': risk.get('mitigationPlan', ''),
        'status': risk.get('status', 'Open'),
        'riskScore': risk.get('riskScore', 0),
        'createdAt': risk.get('createdAt', datetime.utcnow()).isoformat()
    }

def log_action(user_id, action, details=''):
    get_db().audit_logs.insert_one({
        'userId': ObjectId(user_id) if user_id else None,
        'action': action,
        'module': 'Risks',
        'details': details,
        'timestamp': datetime.utcnow()
    })

@risks_bp.route('/', methods=['GET'])
@jwt_required()
def get_all():
    db = get_db()
    risks = list(db.risks.find().sort('createdAt', -1))
    return jsonify([serialize(r) for r in risks])

@risks_bp.route('/', methods=['POST'])
@jwt_required()
def create():
    data = request.get_json()
    db = get_db()
    user_id = get_jwt_identity()

    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({'message': 'Risk title is required'}), 400

    severity   = data.get('severity', 'Medium')
    likelihood = int(data.get('likelihood', 1))
    risk_score = SEVERITY_SCORE.get(severity, 1) * likelihood

    doc = {
        'title': title,
        'description': data.get('description', ''),
        'severity': severity,
        'likelihood': likelihood,
        'impact': data.get('impact', ''),
        'mitigationPlan': data.get('mitigationPlan', ''),
        'status': data.get('status', 'Open'),
        'riskScore': risk_score,
        'createdBy': ObjectId(user_id),
        'createdAt': datetime.utcnow()
    }
    result = db.risks.insert_one(doc)
    doc['_id'] = result.inserted_id

    log_action(user_id, 'Risk identified', f'{title} (Score: {risk_score})')
    return jsonify(serialize(doc)), 201

@risks_bp.route('/<risk_id>', methods=['PUT'])
@jwt_required()
def update(risk_id):
    data = request.get_json()
    db = get_db()
    user_id = get_jwt_identity()

    update_fields = {}
    for field in ['title', 'description', 'severity', 'impact', 'mitigationPlan', 'status']:
        if field in data:
            update_fields[field] = data[field]
    if 'likelihood' in data:
        update_fields['likelihood'] = int(data['likelihood'])

    # Recalculate risk score if severity or likelihood changed
    existing = db.risks.find_one({'_id': ObjectId(risk_id)})
    if existing:
        new_severity   = update_fields.get('severity', existing.get('severity', 'Medium'))
        new_likelihood = update_fields.get('likelihood', existing.get('likelihood', 1))
        update_fields['riskScore'] = SEVERITY_SCORE.get(new_severity, 1) * new_likelihood

    db.risks.update_one({'_id': ObjectId(risk_id)}, {'$set': update_fields})
    risk = db.risks.find_one({'_id': ObjectId(risk_id)})
    if not risk:
        return jsonify({'message': 'Risk not found'}), 404

    log_action(user_id, 'Risk updated', f"{risk.get('title', '')} → {risk.get('status', '')}")
    return jsonify(serialize(risk))

@risks_bp.route('/<risk_id>', methods=['DELETE'])
@jwt_required()
def delete(risk_id):
    db = get_db()
    user_id = get_jwt_identity()

    risk = db.risks.find_one({'_id': ObjectId(risk_id)})
    if not risk:
        return jsonify({'message': 'Risk not found'}), 404

    db.risks.delete_one({'_id': ObjectId(risk_id)})
    log_action(user_id, 'Risk deleted', risk.get('title', ''))
    return jsonify({'message': 'Risk deleted successfully'})
