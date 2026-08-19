"""
Flask Blueprint for Building Code or Email Join Feature
Implements resident building membership via building code or approved email
"""

from flask import Blueprint, request, jsonify, g
from functools import wraps
import uuid
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
import re

# Create Blueprint
bp = Blueprint('capability_building_code_or_email_join_85677965', __name__)


# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated (assumes user_id is set in g.user_id by middleware)
        if not hasattr(g, 'user_id') or g.user_id is None:
            return jsonify({
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Authentication required.'
                }
            }), 401
        return f(*args, **kwargs)
    return decorated_function


def get_db_connection():
    """Get database connection from Flask g object"""
    if not hasattr(g, 'db_connection'):
        raise RuntimeError("Database connection not available")
    return g.db_connection


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@bp.route('/api/capability_building_code_or_email_join_85677965/buildings/join/code', methods=['POST'])
@require_auth
def join_building_by_code():
    """
    Validates a building code and creates a membership record when the code is valid,
    granting the user access to that building's machines
    """
    try:
        data = request.get_json()
        
        # Validate request
        if not data or 'building_code' not in data:
            return jsonify({
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'building_code is required'
                }
            }), 400
        
        building_code = data['building_code']
        
        # Validate building_code length
        if not building_code or len(building_code) < 1 or len(building_code) > 50:
            return jsonify({
                'error': {
                    'code': 'INVALID_BUILDING_CODE',
                    'message': 'The building code you entered is not valid. Please check the code and try again.'
                }
            }), 400
        
        user_id = g.user_id
        conn = get_db_connection()
        
        # Find building by code
        query = text("""
            SELECT id, name, building_code
            FROM f_85677965__buildings
            WHERE building_code = :building_code
        """)
        result = conn.execute(query, {'building_code': building_code})
        building = result.fetchone()
        
        if not building:
            return jsonify({
                'error': {
                    'code': 'INVALID_BUILDING_CODE',
                    'message': 'The building code you entered is not valid. Please check the code and try again.'
                }
            }), 400
        
        building_id = building[0]
        building_name = building[1]
        
        # Check if user already has membership
        check_query = text("""
            SELECT id
            FROM f_85677965__user_building_memberships
            WHERE user_id = :user_id AND building_id = :building_id
        """)
        existing = conn.execute(check_query, {
            'user_id': user_id,
            'building_id': building_id
        }).fetchone()
        
        if existing:
            return jsonify({
                'error': {
                    'code': 'ALREADY_MEMBER',
                    'message': 'You are already a member of this building.'
                }
            }), 409
        
        # Create membership
        membership_id = str(uuid.uuid4())
        joined_at = datetime.utcnow()
        
        insert_query = text("""
            INSERT INTO f_85677965__user_building_memberships
            (id, user_id, building_id, join_method, joined_at)
            VALUES (:id, :user_id, :building_id, :join_method, :joined_at)
        """)
        
        conn.execute(insert_query, {
            'id': membership_id,
            'user_id': user_id,
            'building_id': building_id,
            'join_method': 'building_code',
            'joined_at': joined_at
        })
        conn.commit()
        
        return jsonify({
            'success': True,
            'building_id': building_id,
            'building_name': building_name,
            'membership_id': membership_id,
            'joined_at': joined_at.isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        if hasattr(conn, 'rollback'):
            conn.rollback()
        raise e


@bp.route('/api/capability_building_code_or_email_join_85677965/buildings/join/email', methods=['POST'])
@require_auth
def join_building_by_email():
    """
    Validates an email address against the approved email list and creates a membership record
    when the email is approved, granting the user access to the associated building
    """
    try:
        data = request.get_json()
        
        # Validate request
        if not data or 'email_address' not in data:
            return jsonify({
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'email_address is required'
                }
            }), 400
        
        email_address = data['email_address']
        
        # Validate email format and length
        if not email_address or len(email_address) < 3 or len(email_address) > 320:
            return jsonify({
                'error': {
                    'code': 'EMAIL_NOT_APPROVED',
                    'message': 'This email address is not approved for any building. Please contact your property manager or use a building code instead.'
                }
            }), 400
        
        if not validate_email(email_address):
            return jsonify({
                'error': {
                    'code': 'EMAIL_NOT_APPROVED',
                    'message': 'This email address is not approved for any building. Please contact your property manager or use a building code instead.'
                }
            }), 400
        
        user_id = g.user_id
        conn = get_db_connection()
        
        # Find approved email and associated building
        query = text("""
            SELECT ae.building_id, b.name, b.building_code
            FROM f_85677965__approved_emails ae
            JOIN f_85677965__buildings b ON ae.building_id = b.id
            WHERE ae.email_address = :email_address
        """)
        result = conn.execute(query, {'email_address': email_address})
        approved_email = result.fetchone()
        
        if not approved_email:
            return jsonify({
                'error': {
                    'code': 'EMAIL_NOT_APPROVED',
                    'message': 'This email address is not approved for any building. Please contact your property manager or use a building code instead.'
                }
            }), 400
        
        building_id = approved_email[0]
        building_name = approved_email[1]
        
        # Check if user already has membership
        check_query = text("""
            SELECT id
            FROM f_85677965__user_building_memberships
            WHERE user_id = :user_id AND building_id = :building_id
        """)
        existing = conn.execute(check_query, {
            'user_id': user_id,
            'building_id': building_id
        }).fetchone()
        
        if existing:
            return jsonify({
                'error': {
                    'code': 'ALREADY_MEMBER',
                    'message': 'You are already a member of this building.'
                }
            }), 409
        
        # Create membership
        membership_id = str(uuid.uuid4())
        joined_at = datetime.utcnow()
        
        insert_query = text("""
            INSERT INTO f_85677965__user_building_memberships
            (id, user_id, building_id, join_method, joined_at)
            VALUES (:id, :user_id, :building_id, :join_method, :joined_at)
        """)
        
        conn.execute(insert_query, {
            'id': membership_id,
            'user_id': user_id,
            'building_id': building_id,
            'join_method': 'approved_email',
            'joined_at': joined_at
        })
        conn.commit()
        
        return jsonify({
            'success': True,
            'building_id': building_id,
            'building_name': building_name,
            'membership_id': membership_id,
            'joined_at': joined_at.isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        if hasattr(conn, 'rollback'):
            conn.rollback()
        raise e


@bp.route('/api/capability_building_code_or_email_join_85677965/user/memberships', methods=['GET'])
@require_auth
def get_user_memberships():
    """
    Retrieves all building memberships for the authenticated user,
    allowing the system to determine which buildings the user has access to
    """
    try:
        user_id = g.user_id
        conn = get_db_connection()
        
        # Get all memberships for user
        query = text("""
            SELECT 
                m.id as membership_id,
                m.building_id,
                b.name as building_name,
                b.building_code,
                m.join_method,
                m.joined_at
            FROM f_85677965__user_building_memberships m
            JOIN f_85677965__buildings b ON m.building_id = b.id
            WHERE m.user_id = :user_id
            ORDER BY m.joined_at DESC
        """)
        
        result = conn.execute(query, {'user_id': user_id})
        rows = result.fetchall()
        
        memberships = []
        for row in rows:
            membership = {
                'membership_id': row[0],
                'building_id': row[1],
                'building_name': row[2],
                'building_code': row[3],
                'join_method': row[4],
                'joined_at': row[5].isoformat() + 'Z' if hasattr(row[5], 'isoformat') else row[5]
            }
            memberships.append(membership)
        
        return jsonify({
            'memberships': memberships
        }), 200
        
    except Exception as e:
        raise e
