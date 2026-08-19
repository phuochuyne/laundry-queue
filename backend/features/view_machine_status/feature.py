import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from sqlalchemy import text
from functools import wraps

bp = Blueprint('capability_view_machine_status_589af8dc', __name__)


def get_db():
    """Get database connection from Flask g object."""
    from flask import current_app
    if 'db' not in g:
        g.db = current_app.config['DATABASE_ENGINE']
    return g.db


def require_auth(f):
    """Decorator to require authentication for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'UNAUTHORIZED', 'message': 'Authentication required'}), 401
        
        # Store user info in g for use in route handlers if needed
        g.user_authenticated = True
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/api/capability_view_machine_status_589af8dc/buildings/<building_id>/machines', methods=['GET'])
@require_auth
def list_machines_by_building(building_id):
    """Retrieves all machines for a specific building with their current status."""
    try:
        # Validate UUID format
        uuid.UUID(building_id)
    except (ValueError, AttributeError):
        return jsonify({'error': 'BUILDING_NOT_FOUND', 'message': 'Building does not exist'}), 404
    
    db = get_db()
    
    # Check if building exists
    building_query = text("""
        SELECT id, name 
        FROM f_589af8dc__buildings 
        WHERE id = :building_id
    """)
    
    with db.connect() as conn:
        building_result = conn.execute(building_query, {'building_id': building_id}).fetchone()
        
        if not building_result:
            return jsonify({'error': 'BUILDING_NOT_FOUND', 'message': 'Building does not exist'}), 404
        
        # Get all machines for the building
        machines_query = text("""
            SELECT id, machine_number, status, updated_at
            FROM f_589af8dc__machines
            WHERE building_id = :building_id
            ORDER BY machine_number
        """)
        
        machines_result = conn.execute(machines_query, {'building_id': building_id}).fetchall()
        
        building_data = {
            'id': building_result[0],
            'name': building_result[1]
        }
        
        machines_data = []
        for machine in machines_result:
            machines_data.append({
                'id': machine[0],
                'machine_number': machine[1],
                'status': machine[2],
                'updated_at': machine[3].isoformat() if isinstance(machine[3], datetime) else machine[3]
            })
        
        return jsonify({
            'building': building_data,
            'machines': machines_data
        }), 200


@bp.route('/api/capability_view_machine_status_589af8dc/machines/<machine_id>/status', methods=['PATCH'])
@require_auth
def update_machine_status(machine_id):
    """Updates the status field of a machine."""
    try:
        # Validate UUID format
        uuid.UUID(machine_id)
    except (ValueError, AttributeError):
        return jsonify({'error': 'MACHINE_NOT_FOUND', 'message': 'Machine does not exist'}), 404
    
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({'error': 'INVALID_STATUS', 'message': 'Status must be Available, In Use, or Finished'}), 400
    
    status = data['status']
    valid_statuses = ['Available', 'In Use', 'Finished']
    
    if status not in valid_statuses:
        return jsonify({'error': 'INVALID_STATUS', 'message': 'Status must be Available, In Use, or Finished'}), 400
    
    db = get_db()
    
    # Check if machine exists
    check_query = text("""
        SELECT id, machine_number, status
        FROM f_589af8dc__machines
        WHERE id = :machine_id
    """)
    
    with db.connect() as conn:
        machine_result = conn.execute(check_query, {'machine_id': machine_id}).fetchone()
        
        if not machine_result:
            return jsonify({'error': 'MACHINE_NOT_FOUND', 'message': 'Machine does not exist'}), 404
        
        # Update machine status
        update_query = text("""
            UPDATE f_589af8dc__machines
            SET status = :status, updated_at = :updated_at
            WHERE id = :machine_id
        """)
        
        updated_at = datetime.utcnow()
        conn.execute(update_query, {
            'status': status,
            'updated_at': updated_at,
            'machine_id': machine_id
        })
        conn.commit()
        
        # Fetch updated machine
        fetch_query = text("""
            SELECT id, machine_number, status, updated_at
            FROM f_589af8dc__machines
            WHERE id = :machine_id
        """)
        
        updated_machine = conn.execute(fetch_query, {'machine_id': machine_id}).fetchone()
        
        machine_data = {
            'id': updated_machine[0],
            'machine_number': updated_machine[1],
            'status': updated_machine[2],
            'updated_at': updated_machine[3].isoformat() if isinstance(updated_machine[3], datetime) else updated_machine[3]
        }
        
        return jsonify({'machine': machine_data}), 200


@bp.route('/api/capability_view_machine_status_589af8dc/machines/<machine_id>', methods=['GET'])
@require_auth
def get_machine_status(machine_id):
    """Retrieves the current status and details of a single machine."""
    try:
        # Validate UUID format
        uuid.UUID(machine_id)
    except (ValueError, AttributeError):
        return jsonify({'error': 'MACHINE_NOT_FOUND', 'message': 'Machine does not exist'}), 404
    
    db = get_db()
    
    query = text("""
        SELECT id, building_id, machine_number, status, updated_at
        FROM f_589af8dc__machines
        WHERE id = :machine_id
    """)
    
    with db.connect() as conn:
        machine_result = conn.execute(query, {'machine_id': machine_id}).fetchone()
        
        if not machine_result:
            return jsonify({'error': 'MACHINE_NOT_FOUND', 'message': 'Machine does not exist'}), 404
        
        machine_data = {
            'id': machine_result[0],
            'building_id': machine_result[1],
            'machine_number': machine_result[2],
            'status': machine_result[3],
            'updated_at': machine_result[4].isoformat() if isinstance(machine_result[4], datetime) else machine_result[4]
        }
        
        return jsonify({'machine': machine_data}), 200
