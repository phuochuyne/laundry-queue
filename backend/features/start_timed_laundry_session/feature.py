"""
Flask Blueprint for timed laundry session management.
Provides endpoints to start, retrieve, and end laundry sessions with timer functionality.
"""

from flask import Blueprint, request, jsonify, g
from datetime import datetime, timezone
from functools import wraps
import uuid
import sqlalchemy
from sqlalchemy import text

# Create Blueprint
bp = Blueprint('capability_start_timed_laundry_session_f115b2e6', __name__)


# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated (assumes user_id is set in g.user_id by middleware)
        if not hasattr(g, 'user_id') or g.user_id is None:
            return jsonify({
                'error': 'UNAUTHORIZED',
                'message': 'Authentication required'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


def get_db():
    """Get database connection from Flask g object."""
    if not hasattr(g, 'db_connection'):
        raise RuntimeError("Database connection not available")
    return g.db_connection


def calculate_remaining_minutes(started_at, duration_minutes):
    """Calculate remaining minutes for an active session."""
    if isinstance(started_at, str):
        started_at = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
    
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    elapsed_minutes = (now - started_at).total_seconds() / 60
    remaining = int(duration_minutes - elapsed_minutes)
    return max(0, remaining)


def format_session_response(session, include_remaining=False, include_ended_at=False):
    """Format session data for API response."""
    response = {
        'id': session['id'],
        'user_id': session['user_id'],
        'machine_id': session['machine_id'],
        'started_at': session['started_at'].isoformat() if isinstance(session['started_at'], datetime) else session['started_at'],
        'duration_minutes': session['duration_minutes'],
        'status': session['status'],
        'created_at': session['created_at'].isoformat() if isinstance(session['created_at'], datetime) else session['created_at'],
        'updated_at': session['updated_at'].isoformat() if isinstance(session['updated_at'], datetime) else session['updated_at']
    }
    
    if include_remaining:
        if session['status'] == 'active':
            response['remaining_minutes'] = calculate_remaining_minutes(
                session['started_at'], 
                session['duration_minutes']
            )
        else:
            response['remaining_minutes'] = None
    
    if include_ended_at:
        if session.get('ended_at'):
            response['ended_at'] = session['ended_at'].isoformat() if isinstance(session['ended_at'], datetime) else session['ended_at']
        else:
            response['ended_at'] = None
    
    return response


@bp.route('/api/capability_start_timed_laundry_session_f115b2e6/sessions', methods=['POST'])
@require_auth
def start_session():
    """Creates a new timed laundry session for a user on a claimed machine."""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'INVALID_REQUEST',
            'message': 'Request body is required'
        }), 400
    
    machine_id = data.get('machine_id')
    duration_minutes = data.get('duration_minutes')
    
    # Validate required fields
    if not machine_id:
        return jsonify({
            'error': 'INVALID_REQUEST',
            'message': 'machine_id is required'
        }), 400
    
    if duration_minutes is None:
        return jsonify({
            'error': 'INVALID_REQUEST',
            'message': 'duration_minutes is required'
        }), 400
    
    # Validate duration
    if not isinstance(duration_minutes, int) or duration_minutes < 1:
        return jsonify({
            'error': 'INVALID_DURATION',
            'message': 'Duration must be at least 1 minute'
        }), 400
    
    db = get_db()
    
    try:
        # Check if machine exists (assuming there's a machines table or we just proceed)
        # For this implementation, we'll check if machine_id is a valid UUID format
        try:
            uuid.UUID(machine_id)
        except ValueError:
            return jsonify({
                'error': 'MACHINE_NOT_FOUND',
                'message': 'Machine does not exist'
            }), 404
        
        # Check if machine already has an active session
        check_query = text("""
            SELECT id FROM f_f115b2e6__laundry_sessions
            WHERE machine_id = :machine_id AND status = 'active'
        """)
        result = db.execute(check_query, {'machine_id': machine_id})
        existing_session = result.fetchone()
        
        if existing_session:
            return jsonify({
                'error': 'MACHINE_IN_USE',
                'message': 'Machine already has an active session'
            }), 409
        
        # Create new session
        session_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        insert_query = text("""
            INSERT INTO f_f115b2e6__laundry_sessions
            (id, user_id, machine_id, started_at, duration_minutes, status, created_at, updated_at)
            VALUES (:id, :user_id, :machine_id, :started_at, :duration_minutes, :status, :created_at, :updated_at)
        """)
        
        db.execute(insert_query, {
            'id': session_id,
            'user_id': g.user_id,
            'machine_id': machine_id,
            'started_at': now,
            'duration_minutes': duration_minutes,
            'status': 'active',
            'created_at': now,
            'updated_at': now
        })
        db.commit()
        
        # Fetch the created session
        select_query = text("""
            SELECT id, user_id, machine_id, started_at, duration_minutes, status, created_at, updated_at
            FROM f_f115b2e6__laundry_sessions
            WHERE id = :id
        """)
        result = db.execute(select_query, {'id': session_id})
        session = result.fetchone()
        
        session_dict = dict(session._mapping)
        return jsonify(format_session_response(session_dict)), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': 'An error occurred while creating the session'
        }), 500


@bp.route('/api/capability_start_timed_laundry_session_f115b2e6/sessions/<session_id>', methods=['GET'])
@require_auth
def get_session(session_id):
    """Retrieves a specific laundry session by ID to display timer and remaining time."""
    db = get_db()
    
    try:
        query = text("""
            SELECT id, user_id, machine_id, started_at, duration_minutes, ended_at, status, created_at, updated_at
            FROM f_f115b2e6__laundry_sessions
            WHERE id = :id
        """)
        result = db.execute(query, {'id': session_id})
        session = result.fetchone()
        
        if not session:
            return jsonify({
                'error': 'SESSION_NOT_FOUND',
                'message': 'Session does not exist'
            }), 404
        
        session_dict = dict(session._mapping)
        return jsonify(format_session_response(session_dict, include_remaining=True, include_ended_at=True)), 200
        
    except Exception as e:
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': 'An error occurred while retrieving the session'
        }), 500


@bp.route('/api/capability_start_timed_laundry_session_f115b2e6/machines/<machine_id>/active-session', methods=['GET'])
@require_auth
def get_active_session_by_machine(machine_id):
    """Retrieves the active session for a specific machine to display timer and check machine availability."""
    db = get_db()
    
    try:
        query = text("""
            SELECT id, user_id, machine_id, started_at, duration_minutes, status, created_at, updated_at
            FROM f_f115b2e6__laundry_sessions
            WHERE machine_id = :machine_id AND status = 'active'
        """)
        result = db.execute(query, {'machine_id': machine_id})
        session = result.fetchone()
        
        if not session:
            return jsonify({
                'error': 'NO_ACTIVE_SESSION',
                'message': 'No active session found for this machine'
            }), 404
        
        session_dict = dict(session._mapping)
        return jsonify(format_session_response(session_dict, include_remaining=True)), 200
        
    except Exception as e:
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': 'An error occurred while retrieving the active session'
        }), 500


@bp.route('/api/capability_start_timed_laundry_session_f115b2e6/sessions/my-active', methods=['GET'])
@require_auth
def get_user_active_session():
    """Retrieves the authenticated user's active session to display their current timer."""
    db = get_db()
    
    try:
        query = text("""
            SELECT id, user_id, machine_id, started_at, duration_minutes, status, created_at, updated_at
            FROM f_f115b2e6__laundry_sessions
            WHERE user_id = :user_id AND status = 'active'
        """)
        result = db.execute(query, {'user_id': g.user_id})
        session = result.fetchone()
        
        if not session:
            return jsonify({
                'error': 'NO_ACTIVE_SESSION',
                'message': 'User has no active session'
            }), 404
        
        session_dict = dict(session._mapping)
        return jsonify(format_session_response(session_dict, include_remaining=True)), 200
        
    except Exception as e:
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': 'An error occurred while retrieving the active session'
        }), 500


@bp.route('/api/capability_start_timed_laundry_session_f115b2e6/sessions/<session_id>/end', methods=['POST'])
@require_auth
def end_session(session_id):
    """Marks a laundry session as completed when the user ends it, freeing the machine."""
    db = get_db()
    
    try:
        # Fetch the session
        select_query = text("""
            SELECT id, user_id, machine_id, started_at, duration_minutes, ended_at, status, created_at, updated_at
            FROM f_f115b2e6__laundry_sessions
            WHERE id = :id
        """)
        result = db.execute(select_query, {'id': session_id})
        session = result.fetchone()
        
        if not session:
            return jsonify({
                'error': 'SESSION_NOT_FOUND',
                'message': 'Session does not exist'
            }), 404
        
        session_dict = dict(session._mapping)
        
        # Check if user owns the session
        if session_dict['user_id'] != g.user_id:
            return jsonify({
                'error': 'FORBIDDEN',
                'message': 'User can only end their own session'
            }), 403
        
        # Check if session is already completed
        if session_dict['status'] == 'completed':
            return jsonify({
                'error': 'SESSION_ALREADY_ENDED',
                'message': 'Session has already been completed'
            }), 409
        
        # End the session
        now = datetime.now(timezone.utc)
        update_query = text("""
            UPDATE f_f115b2e6__laundry_sessions
            SET status = 'completed', ended_at = :ended_at, updated_at = :updated_at
            WHERE id = :id
        """)
        
        db.execute(update_query, {
            'id': session_id,
            'ended_at': now,
            'updated_at': now
        })
        db.commit()
        
        # Fetch updated session
        result = db.execute(select_query, {'id': session_id})
        updated_session = result.fetchone()
        updated_session_dict = dict(updated_session._mapping)
        
        response = {
            'id': updated_session_dict['id'],
            'user_id': updated_session_dict['user_id'],
            'machine_id': updated_session_dict['machine_id'],
            'started_at': updated_session_dict['started_at'].isoformat() if isinstance(updated_session_dict['started_at'], datetime) else updated_session_dict['started_at'],
            'duration_minutes': updated_session_dict['duration_minutes'],
            'ended_at': updated_session_dict['ended_at'].isoformat() if isinstance(updated_session_dict['ended_at'], datetime) else updated_session_dict['ended_at'],
            'status': updated_session_dict['status'],
            'updated_at': updated_session_dict['updated_at'].isoformat() if isinstance(updated_session_dict['updated_at'], datetime) else updated_session_dict['updated_at']
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': 'An error occurred while ending the session'
        }), 500
