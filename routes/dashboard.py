from flask import jsonify
from flask_jwt_extended import jwt_required
from config.database import get_db
from bson import ObjectId
from flask import Blueprint
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    db = get_db()

    total_frameworks  = db.frameworks.count_documents({})
    completed_tasks   = db.tasks.count_documents({'status': 'Completed'})
    pending_tasks     = db.tasks.count_documents({'status': 'Pending'})
    in_progress_tasks = db.tasks.count_documents({'status': 'In Progress'})
    open_risks        = db.risks.count_documents({'status': 'Open'})

    # Average compliance across all frameworks
    frameworks = list(db.frameworks.find({}, {'completionPercentage': 1}))
    avg_compliance = 0
    if frameworks:
        avg_compliance = round(sum(f.get('completionPercentage', 0) for f in frameworks) / len(frameworks))

    # Risk severity breakdown
    risks_by_severity_cursor = db.risks.aggregate([
        {'$group': {'_id': '$severity', 'count': {'$sum': 1}}}
    ])
    risks_by_severity = [{'name': r['_id'], 'value': r['count']} for r in risks_by_severity_cursor]

    # Tasks by status breakdown
    tasks_by_status_cursor = db.tasks.aggregate([
        {'$group': {'_id': '$status', 'count': {'$sum': 1}}}
    ])
    tasks_by_status = [{'name': t['_id'], 'value': t['count']} for t in tasks_by_status_cursor]

    # Recent activity logs (last 8)
    recent_logs_cursor = db.audit_logs.find().sort('timestamp', -1).limit(8)
    recent_logs = []
    for log in recent_logs_cursor:
        user_name = 'System'
        if log.get('userId'):
            user = db.users.find_one({'_id': log['userId']}, {'name': 1})
            if user:
                user_name = user['name']
        recent_logs.append({
            'action': log.get('action', ''),
            'module': log.get('module', ''),
            'details': log.get('details', ''),
            'userName': user_name,
            'timestamp': log.get('timestamp', datetime.utcnow()).isoformat()
        })

    return jsonify({
        'totalFrameworks': total_frameworks,
        'completedTasks': completed_tasks,
        'pendingTasks': pending_tasks,
        'inProgressTasks': in_progress_tasks,
        'openRisks': open_risks,
        'avgCompliance': avg_compliance,
        'risksBySeverity': risks_by_severity,
        'tasksByStatus': tasks_by_status,
        'recentLogs': recent_logs
    })
