"""
End Session Button Feature Module

This module implements the end session functionality for laundry machines.
Users can tap the End Session button after removing laundry to make the machine available.
"""

from flask import Blueprint, request, jsonify, g
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from functools import wraps
import uuid

# Create Blueprint
bp = Blueprint('capability_end_session_button_342bee96', __name__, url_prefix='/api/capability_end_session_button_342bee96')


def get_db():
    """Get database connection from Flask g object"""
    from flask import current_app
    if 'db' not in g:
        g.db = current_app.config['DATABASE_ENGINE']
    return g.db


def require_auth(f):
    """Authentication decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for authentication token/user in request
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'error_code': 'UNAUTHORIZED',
                'message': 'Authentication required'
            }), 401
        
        # Extract user_id from token (simplified - in production use proper JWT validation)
        try:
            # Expecting format: "Bearer <user_id>" or just "<user_id>"
            token = auth_header.replace('Bearer ', '')
            # Validate UUID format
            user_id = str(uuid.UUID(token))
            g.user_id = user_id
        except (ValueError, AttributeError):
            return jsonify({
                'error_code': 'UNAUTHORIZED',
                'message': 'Authentication required'
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function


def validate_uuid(uuid_string):
    """Validate UUID format"""
    try:
        uuid.UUID(uuid_string)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


@bp.route('/sessions/<session_id>/end', methods=['POST'])
@require_auth
def end_session(session_id):
    """
    End an active laundry session.
    
    This endpoint marks a session as complete, records the end time, stops the timer,
    and updates the machine status from in_use to available.
    
    Args:
        session_id: UUID of the session to end (from URL path)
    
    Returns:
        JSON response with updated session and machine data
    """
    # Validate session_id format
    if not validate_uuid(session_id):
        return jsonify({
            'error_code': 'SESSION_NOT_FOUND',
            'message': 'Session not found'
        }), 404
    
    db = get_db()
    
    try:
        with db.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Fetch the session
                session_query = text("""
                    SELECT id, machine_id, user_id, started_at, ended_at, status
                    FROM f_342bee96__laundry_sessions
                    WHERE id = :session_id
                    FOR UPDATE
                """)
                
                session_result = conn.execute(session_query, {'session_id': session_id}).fetchone()
                
                if not session_result:
                    trans.rollback()
                    return jsonify({
                        'error_code': 'SESSION_NOT_FOUND',
                        'message': 'Session not found'
                    }), 404
                
                # Check if user owns this session
                if session_result[2] != g.user_id:  # user_id is at index 2
                    trans.rollback()
                    return jsonify({
                        'error_code': 'FORBIDDEN',
                        'message': 'User does not own this session'
                    }), 403
                
                # Check if session is already ended
                if session_result[5] == 'completed':  # status is at index 5
                    trans.rollback()
                    return jsonify({
                        'error_code': 'SESSION_ALREADY_ENDED',
                        'message': 'Session has already been ended'
                    }), 409
                
                machine_id = session_result[1]
                started_at = session_result[3]
                
                # Update session to completed
                ended_at = datetime.utcnow()
                update_session_query = text("""
                    UPDATE f_342bee96__laundry_sessions
                    SET status = 'completed', ended_at = :ended_at
                    WHERE id = :session_id
                """)
                
                conn.execute(update_session_query, {
                    'session_id': session_id,
                    'ended_at': ended_at
                })
                
                # Update machine status to available
                updated_at = datetime.utcnow()
                update_machine_query = text("""
                    UPDATE f_342bee96__machines
                    SET status = 'available', updated_at = :updated_at
                    WHERE id = :machine_id
                """)
                
                conn.execute(update_machine_query, {
                    'machine_id': machine_id,
                    'updated_at': updated_at
                })
                
                # Fetch updated machine data
                machine_query = text("""
                    SELECT id, status, updated_at
                    FROM f_342bee96__machines
                    WHERE id = :machine_id
                """)
                
                machine_result = conn.execute(machine_query, {'machine_id': machine_id}).fetchone()
                
                # Commit transaction
                trans.commit()
                
                # Format response
                response = {
                    'session': {
                        'id': session_id,
                        'user_id': g.user_id,
                        'machine_id': machine_id,
                        'started_at': started_at.isoformat() + 'Z' if started_at else None,
                        'ended_at': ended_at.isoformat() + 'Z',
                        'status': 'completed'
                    },
                    'machine': {
                        'id': machine_result[0],
                        'status': machine_result[1],
                        'updated_at': machine_result[2].isoformat() + 'Z' if machine_result[2] else updated_at.isoformat() + 'Z'
                    }
                }
                
                return jsonify(response), 200
                
            except Exception as e:
                trans.rollback()
                raise e
                
    except SQLAlchemyError as e:
        return jsonify({
            'error_code': 'INTERNAL_ERROR',
            'message': 'Failed to end session'
        }), 500
    except Exception as e:
        return jsonify({
            'error_code': 'INTERNAL_ERROR',
            'message': 'Failed to end session'
        }), 500


def register_blueprint(app):
    """Register this blueprint with the Flask app"""
    app.register_blueprint(bp)
