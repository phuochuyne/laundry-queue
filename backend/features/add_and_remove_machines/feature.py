import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from sqlalchemy import text
from functools import wraps

bp = Blueprint('capability_add_and_remove_machines_e6daa139', __name__)


def get_db():
    """Get database connection from Flask g object."""
    from flask import current_app
    if 'db' not in g:
        g.db = current_app.config['DATABASE_ENGINE']
    return g.db


def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'UNAUTHORIZED', 'message': 'Authentication required'}), 401
        
        # Store user info in g for downstream use
        # In a real implementation, validate token and extract user info
        g.user = {'authenticated': True}
        return f(*args, **kwargs)
    return decorated_function


def require_property_manager(f):
    """Decorator to require property manager permissions."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In a real implementation, check user role from token/session
        # For now, assume authenticated users have property manager role
        if not hasattr(g, 'user') or not g.user.get('authenticated'):
            return jsonify({'error': 'FORBIDDEN', 'message': 'User does not have property manager permissions'}), 403
        return f(*args, **kwargs)
    return decorated_function


def validate_uuid(uuid_string):
    """Validate UUID format."""
    try:
        uuid.UUID(uuid_string)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def generate_qr_code_payload():
    """Generate a unique QR code payload."""
    return f"machine_{uuid.uuid4().hex}"


@bp.route('/api/capability_add_and_remove_machines_e6daa139/machines', methods=['POST'])
@require_auth
@require_property_manager
def create_machine():
    """Creates a new machine record with machine number, type, and QR code payload."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'INVALID_INPUT', 'message': 'Machine number or type is invalid or missing'}), 400
        
        machine_number = data.get('machine_number')
        machine_type = data.get('machine_type')
        
        # Validate required fields
        if not machine_number or not machine_type:
            return jsonify({'error': 'INVALID_INPUT', 'message': 'Machine number or type is invalid or missing'}), 400
        
        # Validate machine_number length
        if not isinstance(machine_number, str) or len(machine_number) < 1 or len(machine_number) > 50:
            return jsonify({'error': 'INVALID_INPUT', 'message': 'Machine number or type is invalid or missing'}), 400
        
        # Validate machine_type enum
        if machine_type not in ['washer', 'dryer']:
            return jsonify({'error': 'INVALID_INPUT', 'message': 'Machine number or type is invalid or missing'}), 400
        
        # Generate unique ID and QR code payload
        machine_id = str(uuid.uuid4())
        qr_code_payload = generate_qr_code_payload()
        created_at = datetime.utcnow()
        
        # Insert into database
        db = get_db()
        with db.connect() as conn:
            query = text("""
                INSERT INTO f_e6daa139__machines 
                (id, machine_number, machine_type, qr_code_payload, created_at, deleted_at)
                VALUES (:id, :machine_number, :machine_type, :qr_code_payload, :created_at, NULL)
            """)
            conn.execute(query, {
                'id': machine_id,
                'machine_number': machine_number,
                'machine_type': machine_type,
                'qr_code_payload': qr_code_payload,
                'created_at': created_at
            })
            conn.commit()
        
        return jsonify({
            'id': machine_id,
            'machine_number': machine_number,
            'machine_type': machine_type,
            'qr_code_payload': qr_code_payload,
            'created_at': created_at.isoformat() + 'Z'
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'INTERNAL_ERROR', 'message': 'Failed to create machine record'}), 500


@bp.route('/api/capability_add_and_remove_machines_e6daa139/machines', methods=['GET'])
@require_auth
def list_machines():
    """Retrieves all active (non-deleted) machines."""
    try:
        db = get_db()
        with db.connect() as conn:
            query = text("""
                SELECT id, machine_number, machine_type, qr_code_payload, created_at
                FROM f_e6daa139__machines
                WHERE deleted_at IS NULL
                ORDER BY created_at DESC
            """)
            result = conn.execute(query)
            rows = result.fetchall()
        
        machines = []
        for row in rows:
            machines.append({
                'id': row[0],
                'machine_number': row[1],
                'machine_type': row[2],
                'qr_code_payload': row[3],
                'created_at': row[4].isoformat() + 'Z' if isinstance(row[4], datetime) else row[4]
            })
        
        return jsonify({'machines': machines}), 200
        
    except Exception as e:
        return jsonify({'error': 'INTERNAL_ERROR', 'message': 'Failed to retrieve machines'}), 500


@bp.route('/api/capability_add_and_remove_machines_e6daa139/machines/<machine_id>', methods=['DELETE'])
@require_auth
@require_property_manager
def delete_machine(machine_id):
    """Soft-deletes a machine by setting the deleted_at timestamp."""
    try:
        # Validate UUID format
        if not validate_uuid(machine_id):
            return jsonify({'error': 'INVALID_MACHINE_ID', 'message': 'Machine ID is not a valid UUID'}), 400
        
        db = get_db()
        with db.connect() as conn:
            # Check if machine exists and is not already deleted
            check_query = text("""
                SELECT id, deleted_at FROM f_e6daa139__machines
                WHERE id = :machine_id
            """)
            result = conn.execute(check_query, {'machine_id': machine_id})
            row = result.fetchone()
            
            if not row:
                return jsonify({'error': 'MACHINE_NOT_FOUND', 'message': 'Machine does not exist or is already deleted'}), 404
            
            if row[1] is not None:
                return jsonify({'error': 'MACHINE_NOT_FOUND', 'message': 'Machine does not exist or is already deleted'}), 404
            
            # Soft delete the machine
            deleted_at = datetime.utcnow()
            delete_query = text("""
                UPDATE f_e6daa139__machines
                SET deleted_at = :deleted_at
                WHERE id = :machine_id
            """)
            conn.execute(delete_query, {
                'deleted_at': deleted_at,
                'machine_id': machine_id
            })
            conn.commit()
        
        return jsonify({
            'success': True,
            'deleted_at': deleted_at.isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        if 'MACHINE_NOT_FOUND' in str(e) or 'INVALID_MACHINE_ID' in str(e):
            raise
        return jsonify({'error': 'INTERNAL_ERROR', 'message': 'Failed to delete machine'}), 500


@bp.route('/api/capability_add_and_remove_machines_e6daa139/machines/<machine_id>', methods=['GET'])
@require_auth
def get_machine(machine_id):
    """Retrieves a single machine record by ID."""
    try:
        # Validate UUID format
        if not validate_uuid(machine_id):
            return jsonify({'error': 'INVALID_MACHINE_ID', 'message': 'Machine ID is not a valid UUID'}), 400
        
        db = get_db()
        with db.connect() as conn:
            query = text("""
                SELECT id, machine_number, machine_type, qr_code_payload, created_at, deleted_at
                FROM f_e6daa139__machines
                WHERE id = :machine_id
            """)
            result = conn.execute(query, {'machine_id': machine_id})
            row = result.fetchone()
        
        if not row:
            return jsonify({'error': 'MACHINE_NOT_FOUND', 'message': 'Machine does not exist'}), 404
        
        response = {
            'id': row[0],
            'machine_number': row[1],
            'machine_type': row[2],
            'qr_code_payload': row[3],
            'created_at': row[4].isoformat() + 'Z' if isinstance(row[4], datetime) else row[4]
        }
        
        if row[5] is not None:
            response['deleted_at'] = row[5].isoformat() + 'Z' if isinstance(row[5], datetime) else row[5]
        
        return jsonify(response), 200
        
    except Exception as e:
        if 'MACHINE_NOT_FOUND' in str(e) or 'INVALID_MACHINE_ID' in str(e):
            raise
        return jsonify({'error': 'INTERNAL_ERROR', 'message': 'Failed to retrieve machine'}), 500
