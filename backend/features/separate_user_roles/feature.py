import re
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

bp = Blueprint('capability_separate_user_roles_e876dcda', __name__)

def get_db():
    """Get database connection from Flask g object"""
    from flask import current_app
    if 'db' not in g:
        g.db = current_app.config['DATABASE_ENGINE']
    return g.db

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'UNAUTHORIZED', 'message': 'Authentication required'}), 401
        
        token = auth_header.split(' ')[1]
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': 'UNAUTHORIZED', 'message': 'Authentication required'}), 401
        
        g.current_user_id = user_id
        return f(*args, **kwargs)
    return decorated_function

def verify_token(token):
    """Verify JWT token and return user_id"""
    try:
        import jwt
        from flask import current_app
        payload = jwt.decode(token, current_app.config.get('SECRET_KEY', 'dev-secret-key'), algorithms=['HS256'])
        return payload.get('user_id')
    except:
        return None

def create_token(user_id):
    """Create JWT token for user"""
    import jwt
    from flask import current_app
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow().timestamp() + 86400
    }
    return jwt.encode(payload, current_app.config.get('SECRET_KEY', 'dev-secret-key'), algorithm='HS256')

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_building_code(building_code):
    """Validate building code exists"""
    db = get_db()
    with db.connect() as conn:
        result = conn.execute(
            text("SELECT COUNT(*) as count FROM buildings WHERE code = :code"),
            {"code": building_code}
        )
        row = result.fetchone()
        return row and row[0] > 0

def email_exists(email):
    """Check if email already exists"""
    db = get_db()
    with db.connect() as conn:
        result = conn.execute(
            text("SELECT COUNT(*) as count FROM f_e876dcda__users WHERE email = :email"),
            {"email": email}
        )
        row = result.fetchone()
        return row and row[0] > 0

@bp.route('/api/capability_separate_user_roles_e876dcda/auth/signup/resident', methods=['POST'])
def create_resident_account():
    """Creates a new user account with resident role"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'INVALID_REQUEST', 'message': 'Request body is required'}), 400
    
    email = data.get('email')
    password = data.get('password')
    building_code = data.get('building_code')
    
    # Validate required fields
    if not email or not password or not building_code:
        return jsonify({'error': 'INVALID_REQUEST', 'message': 'Missing required fields'}), 400
    
    # Validate email format
    if not validate_email(email) or len(email) < 3 or len(email) > 255:
        return jsonify({'error': 'INVALID_EMAIL', 'message': 'Email format is invalid'}), 400
    
    # Validate password length
    if len(password) < 8:
        return jsonify({'error': 'INVALID_PASSWORD', 'message': 'Password must be at least 8 characters'}), 400
    
    # Check if email already exists
    if email_exists(email):
        return jsonify({'error': 'EMAIL_ALREADY_EXISTS', 'message': 'An account with this email already exists'}), 409
    
    # Validate building code (check if buildings table exists first)
    db = get_db()
    try:
        with db.connect() as conn:
            result = conn.execute(text("SHOW TABLES LIKE 'buildings'"))
            if result.fetchone():
                if not validate_building_code(building_code):
                    return jsonify({'error': 'INVALID_BUILDING_CODE', 'message': 'Building code does not exist or is invalid'}), 400
    except:
        # If buildings table doesn't exist, skip validation
        pass
    
    # Create user
    user_id = str(uuid.uuid4())
    created_at = datetime.utcnow()
    password_hash = generate_password_hash(password)
    
    try:
        with db.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO f_e876dcda__users (id, email, role, created_at)
                    VALUES (:id, :email, :role, :created_at)
                """),
                {
                    "id": user_id,
                    "email": email,
                    "role": "resident",
                    "created_at": created_at
                }
            )
            conn.commit()
    except IntegrityError:
        return jsonify({'error': 'EMAIL_ALREADY_EXISTS', 'message': 'An account with this email already exists'}), 409
    except Exception as e:
        return jsonify({'error': 'DATABASE_ERROR', 'message': 'Failed to create account'}), 500
    
    return jsonify({
        'user_id': user_id,
        'email': email,
        'role': 'resident',
        'created_at': created_at.isoformat() + 'Z'
    }), 201

@bp.route('/api/capability_separate_user_roles_e876dcda/auth/signup/admin', methods=['POST'])
def create_admin_account():
    """Creates a new user account with admin role"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'INVALID_REQUEST', 'message': 'Request body is required'}), 400
    
    email = data.get('email')
    password = data.get('password')
    property_name = data.get('property_name')
    
    # Validate required fields
    if not email or not password or not property_name:
        return jsonify({'error': 'INVALID_REQUEST', 'message': 'Missing required fields'}), 400
    
    # Validate email format
    if not validate_email(email) or len(email) < 3 or len(email) > 255:
        return jsonify({'error': 'INVALID_EMAIL', 'message': 'Email format is invalid'}), 400
    
    # Validate password length
    if len(password) < 8:
        return jsonify({'error': 'INVALID_PASSWORD', 'message': 'Password must be at least 8 characters'}), 400
    
    # Check if email already exists
    if email_exists(email):
        return jsonify({'error': 'EMAIL_ALREADY_EXISTS', 'message': 'An account with this email already exists'}), 409
    
    # Create user
    user_id = str(uuid.uuid4())
    created_at = datetime.utcnow()
    password_hash = generate_password_hash(password)
    
    db = get_db()
    try:
        with db.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO f_e876dcda__users (id, email, role, created_at)
                    VALUES (:id, :email, :role, :created_at)
                """),
                {
                    "id": user_id,
                    "email": email,
                    "role": "admin",
                    "created_at": created_at
                }
            )
            conn.commit()
    except IntegrityError:
        return jsonify({'error': 'EMAIL_ALREADY_EXISTS', 'message': 'An account with this email already exists'}), 409
    except Exception as e:
        return jsonify({'error': 'DATABASE_ERROR', 'message': 'Failed to create account'}), 500
    
    return jsonify({
        'user_id': user_id,
        'email': email,
        'role': 'admin',
        'created_at': created_at.isoformat() + 'Z'
    }), 201

@bp.route('/api/capability_separate_user_roles_e876dcda/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Retrieves the authenticated user's account information"""
    user_id = g.current_user_id
    
    db = get_db()
    try:
        with db.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id, email, role, created_at
                    FROM f_e876dcda__users
                    WHERE id = :user_id
                """),
                {"user_id": user_id}
            )
            row = result.fetchone()
            
            if not row:
                return jsonify({'error': 'USER_NOT_FOUND', 'message': 'User account not found'}), 404
            
            return jsonify({
                'user_id': row[0],
                'email': row[1],
                'role': row[2],
                'created_at': row[3].isoformat() + 'Z' if hasattr(row[3], 'isoformat') else row[3]
            }), 200
    except Exception as e:
        return jsonify({'error': 'DATABASE_ERROR', 'message': 'Failed to retrieve user'}), 500
