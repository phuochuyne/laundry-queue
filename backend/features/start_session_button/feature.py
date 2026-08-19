"""
Flask Blueprint module for Start Session Button capability.
Implements session management for washing machine usage tracking.
"""

from flask import Blueprint, request, jsonify, g
from functools import wraps
import uuid
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import os

bp = Blueprint('capability_start_session_button_271c7167', __name__, url_prefix='/api/capability_start_session_button_271c7167')


def get_db_connection():
    """Get database connection from Flask g object or create new one."""
    if 'db_engine' not in g:
        database_url = os.environ.get('DATABASE_URL', 'mysql+pymysql://user:password@localhost/dbname')
        g.db_engine = create_engine(database_url, poolclass=NullPool)
    return g.db_engine.connect()


def require_auth(f):
    """Decorator to require authentication for endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'code': 'UNAUTHORIZED',
                'message': 'Authentication required'
            }), 401
        
        # Extract user_id from Bearer token or custom header
        # In production, validate JWT token here
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            # Try to extract from Authorization header
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
                # In production: decode JWT and extract user_id
                # For now, assume token IS the user_id for simplicity
                user_id = token
        
        if not user_id:
            return jsonify({
                'code': 'UNAUTHORIZED',
                'message': 'Authentication required'
            }), 401
        
        try:
            # Validate UUID format
            uuid.UUID(user_id)
            g.user_id = user_id
        except (ValueError, AttributeError):
            return jsonify({
                'code': 'UNAUTHORIZED',
                'message': 'Invalid authentication credentials'
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function


def validate_uuid(value, field_name):
    """Validate UUID format."""
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


@bp.route('/sessions', methods=['POST'])
@require_auth
def start_session():
    """
    Creates a new session record when user taps Start Session button.
    Changes machine status to In Use and enables countdown timer display.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'code': 'INVALID_REQUEST',
                'message': 'Invalid machine_id format or duration_minutes value'
            }), 400
        
        machine_id = data.get('machine_id')
        duration_minutes = data.get('duration_minutes')
        
        # Validate required fields
        if not machine_id or not duration_minutes:
            return jsonify({
                'code': 'INVALID_REQUEST',
                'message': 'Invalid machine_id format or duration_minutes value'
            }), 400
        
        # Validate machine_id UUID format
        if not validate_uuid(machine_id, 'machine_id'):
            return jsonify({
                'code': 'INVALID_REQUEST',
                'message': 'Invalid machine_id format or duration_minutes value'
            }), 400
        
        # Validate duration_minutes
        if not isinstance(duration_minutes, int) or duration_minutes < 1:
            return jsonify({
                'code': 'INVALID_REQUEST',
                'message': 'Invalid machine_id format or duration_minutes value'
            }), 400
        
        user_id = g.user_id
        
        conn = get_db_connection()
        
        try:
            # Check if machine already has an active session
            check_query = text("""
                SELECT session_id FROM f_271c7167__sessions
                WHERE machine_id = :machine_id AND status = 'in_use'
                LIMIT 1
            """)
            result = conn.execute(check_query, {'machine_id': machine_id})
            existing_session = result.fetchone()
            
            if existing_session:
                return jsonify({
                    'code': 'MACHINE_IN_USE',
                    'message': 'Machine already has an active session'
                }), 409
            
            # Create new session
            session_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            insert_query = text("""
                INSERT INTO f_271c7167__sessions
                (session_id, machine_id, user_id, started_at, duration_minutes, status, created_at, updated_at)
                VALUES
                (:session_id, :machine_id, :user_id, :started_at, :duration_minutes, :status, :created_at, :updated_at)
            """)
            
            conn.execute(insert_query, {
                'session_id': session_id,
                'machine_id': machine_id,
                'user_id': user_id,
                'started_at': now,
                'duration_minutes': duration_minutes,
                'status': 'in_use',
                'created_at': now,
                'updated_at': now
            })
            conn.commit()
            
            return jsonify({
                'session_id': session_id,
                'machine_id': machine_id,
                'user_id': user_id,
                'started_at': now.isoformat() + 'Z',
                'duration_minutes': duration_minutes,
                'status': 'in_use',
                'created_at': now.isoformat() + 'Z',
                'updated_at': now.isoformat() + 'Z'
            }), 201
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': 'Failed to create session'
        }), 500


@bp.route('/sessions/<session_id>', methods=['GET'])
@require_auth
def get_session(session_id):
    """
    Retrieves session details including started_at and duration_minutes
    to support countdown timer calculation on client.
    """
    try:
        # Validate session_id UUID format
        if not validate_uuid(session_id, 'session_id'):
            return jsonify({
                'code': 'SESSION_NOT_FOUND',
                'message': 'Session with specified ID does not exist'
            }), 404
        
        conn = get_db_connection()
        
        try:
            query = text("""
                SELECT session_id, machine_id, user_id, started_at, duration_minutes, 
                       status, created_at, updated_at
                FROM f_271c7167__sessions
                WHERE session_id = :session_id
                LIMIT 1
            """)
            
            result = conn.execute(query, {'session_id': session_id})
            row = result.fetchone()
            
            if not row:
                return jsonify({
                    'code': 'SESSION_NOT_FOUND',
                    'message': 'Session with specified ID does not exist'
                }), 404
            
            return jsonify({
                'session_id': row[0],
                'machine_id': row[1],
                'user_id': row[2],
                'started_at': row[3].isoformat() + 'Z' if row[3] else None,
                'duration_minutes': row[4],
                'status': row[5],
                'created_at': row[6].isoformat() + 'Z' if row[6] else None,
                'updated_at': row[7].isoformat() + 'Z' if row[7] else None
            }), 200
            
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': 'Failed to retrieve session'
        }), 500


@bp.route('/machines/<machine_id>/active-session', methods=['GET'])
@require_auth
def get_machine_active_session(machine_id):
    """
    Retrieves the active session for a specific machine to determine
    if machine is In Use and display countdown timer to all users.
    """
    try:
        # Validate machine_id UUID format
        if not validate_uuid(machine_id, 'machine_id'):
            return jsonify({
                'code': 'MACHINE_NOT_FOUND',
                'message': 'Machine with specified ID does not exist'
            }), 404
        
        conn = get_db_connection()
        
        try:
            query = text("""
                SELECT session_id, user_id, started_at, duration_minutes, status
                FROM f_271c7167__sessions
                WHERE machine_id = :machine_id AND status = 'in_use'
                ORDER BY started_at DESC
                LIMIT 1
            """)
            
            result = conn.execute(query, {'machine_id': machine_id})
            row = result.fetchone()
            
            if not row:
                return jsonify({
                    'has_active_session': False,
                    'session': None
                }), 200
            
            return jsonify({
                'has_active_session': True,
                'session': {
                    'session_id': row[0],
                    'user_id': row[1],
                    'started_at': row[2].isoformat() + 'Z' if row[2] else None,
                    'duration_minutes': row[3],
                    'status': row[4]
                }
            }), 200
            
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': 'Failed to retrieve machine active session'
        }), 500


@bp.teardown_app_request
def teardown_db(exception=None):
    """Close database connection at end of request."""
    db_engine = g.pop('db_engine', None)
    if db_engine is not None:
        db_engine.dispose()
