import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, g
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from functools import wraps
import os

bp = Blueprint('capability_notification_when_wash_nearly_finished_a72b87c1', __name__)

def get_db_connection():
    """Get database connection from SQLAlchemy engine."""
    database_url = os.environ.get('DATABASE_URL', 'mysql+pymysql://user:password@localhost/dbname')
    engine = create_engine(database_url, poolclass=NullPool)
    return engine.connect()

def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'unauthorized', 'message': 'Authentication required'}), 401
        
        # Extract user_id from token (simplified - in production use proper JWT validation)
        try:
            # Assuming Bearer token format: "Bearer <user_id>"
            token = auth_header.replace('Bearer ', '')
            g.user_id = token
        except:
            return jsonify({'error': 'unauthorized', 'message': 'Authentication required'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/api/capability_notification_when_wash_nearly_finished_a72b87c1/notifications/device-token', methods=['POST'])
@require_auth
def register_device_token():
    """Registers or updates a user's device token for push notifications."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'invalid_request', 'message': 'Request body is required'}), 400
    
    token = data.get('token')
    platform = data.get('platform')
    
    # Validate token
    if not token or not isinstance(token, str) or len(token) < 1 or len(token) > 1024:
        return jsonify({'error': 'invalid_token', 'message': 'Device token is invalid or empty'}), 400
    
    # Validate platform
    if platform not in ['ios', 'android']:
        return jsonify({'error': 'invalid_platform', 'message': 'Platform must be ios or android'}), 400
    
    user_id = g.user_id
    conn = get_db_connection()
    
    try:
        # Check if device token already exists for this user
        result = conn.execute(
            text("SELECT id, created_at FROM f_a72b87c1__device_tokens WHERE user_id = :user_id AND platform = :platform"),
            {"user_id": user_id, "platform": platform}
        )
        existing = result.fetchone()
        
        now = datetime.utcnow()
        
        if existing:
            # Update existing token
            device_id = existing[0]
            created_at = existing[1]
            conn.execute(
                text("UPDATE f_a72b87c1__device_tokens SET token = :token, updated_at = :updated_at WHERE id = :id"),
                {"token": token, "updated_at": now, "id": device_id}
            )
            conn.commit()
        else:
            # Insert new token
            device_id = str(uuid.uuid4())
            created_at = now
            conn.execute(
                text("""INSERT INTO f_a72b87c1__device_tokens 
                        (id, user_id, token, platform, created_at, updated_at) 
                        VALUES (:id, :user_id, :token, :platform, :created_at, :updated_at)"""),
                {
                    "id": device_id,
                    "user_id": user_id,
                    "token": token,
                    "platform": platform,
                    "created_at": now,
                    "updated_at": now
                }
            )
            conn.commit()
        
        return jsonify({
            'id': device_id,
            'user_id': user_id,
            'token': token,
            'platform': platform,
            'created_at': created_at.isoformat() + 'Z' if isinstance(created_at, datetime) else created_at,
            'updated_at': now.isoformat() + 'Z'
        }), 200
        
    finally:
        conn.close()

@bp.route('/api/capability_notification_when_wash_nearly_finished_a72b87c1/notifications/session/<session_id>', methods=['GET'])
@require_auth
def get_notification_by_session(session_id):
    """Retrieves notification details for a session to enable tapping notification to open app to active session."""
    user_id = g.user_id
    conn = get_db_connection()
    
    try:
        # Fetch notification for the session
        result = conn.execute(
            text("""SELECT id, session_id, user_id, machine_id, title, body, 
                           delivery_status, sent_at, created_at 
                    FROM f_a72b87c1__notifications 
                    WHERE session_id = :session_id"""),
            {"session_id": session_id}
        )
        notification = result.fetchone()
        
        if not notification:
            return jsonify({
                'error': 'notification_not_found',
                'message': 'No notification found for this session'
            }), 404
        
        # Check if user is authorized to view this notification
        if notification[2] != user_id:
            return jsonify({
                'error': 'forbidden',
                'message': 'Not authorized to view this notification'
            }), 403
        
        return jsonify({
            'id': notification[0],
            'session_id': notification[1],
            'user_id': notification[2],
            'machine_id': notification[3],
            'title': notification[4],
            'body': notification[5],
            'delivery_status': notification[6],
            'sent_at': notification[7].isoformat() + 'Z' if isinstance(notification[7], datetime) else notification[7],
            'created_at': notification[8].isoformat() + 'Z' if isinstance(notification[8], datetime) else notification[8]
        }), 200
        
    finally:
        conn.close()

def schedule_notification_check():
    """Background job that checks active sessions and sends notifications 5 minutes before completion.
    
    This function should be called by a background scheduler (e.g., Celery, APScheduler).
    It checks for active wash sessions and sends notifications to users 5 minutes before completion.
    """
    conn = get_db_connection()
    
    try:
        # This is a simplified implementation. In a real system, you would:
        # 1. Query active wash sessions from a sessions table
        # 2. Calculate which sessions will complete in ~5 minutes
        # 3. Check if notification already sent for that session
        # 4. Get user's device tokens
        # 5. Send push notification via FCM/APNs
        # 6. Record notification in database
        
        # Example logic (requires sessions table which is not in this feature):
        # Get sessions that will complete in approximately 5 minutes
        target_time = datetime.utcnow() + timedelta(minutes=5)
        time_window_start = datetime.utcnow() + timedelta(minutes=4, seconds=30)
        time_window_end = datetime.utcnow() + timedelta(minutes=5, seconds=30)
        
        # In a real implementation, you would query a sessions table here
        # For now, this is a placeholder that demonstrates the structure
        
        # Example: Find sessions ending soon that don't have notifications yet
        # sessions_query = text("""
        #     SELECT s.id, s.user_id, s.machine_id, s.end_time, m.name
        #     FROM sessions s
        #     LEFT JOIN f_a72b87c1__notifications n ON s.id = n.session_id
        #     LEFT JOIN machines m ON s.machine_id = m.id
        #     WHERE s.end_time BETWEEN :start AND :end
        #     AND s.status = 'active'
        #     AND n.id IS NULL
        # """)
        # sessions = conn.execute(sessions_query, {
        #     "start": time_window_start,
        #     "end": time_window_end
        # }).fetchall()
        
        # For each session, create notification and send push
        # for session in sessions:
        #     session_id, user_id, machine_id, end_time, machine_name = session
        #     
        #     # Get user's device tokens
        #     tokens_result = conn.execute(
        #         text("SELECT token, platform FROM f_a72b87c1__device_tokens WHERE user_id = :user_id"),
        #         {"user_id": user_id}
        #     )
        #     device_tokens = tokens_result.fetchall()
        #     
        #     if device_tokens:
        #         notification_id = str(uuid.uuid4())
        #         now = datetime.utcnow()
        #         title = "Wash Nearly Complete"
        #         body = f"Your wash on {machine_name} will be done in 5 minutes"
        #         
        #         # Insert notification record
        #         conn.execute(
        #             text("""INSERT INTO f_a72b87c1__notifications 
        #                     (id, session_id, user_id, machine_id, title, body, 
        #                      sent_at, delivery_status, created_at)
        #                     VALUES (:id, :session_id, :user_id, :machine_id, :title, 
        #                             :body, :sent_at, :delivery_status, :created_at)"""),
        #             {
        #                 "id": notification_id,
        #                 "session_id": session_id,
        #                 "user_id": user_id,
        #                 "machine_id": machine_id,
        #                 "title": title,
        #                 "body": body,
        #                 "sent_at": now,
        #                 "delivery_status": "pending",
        #                 "created_at": now
        #             }
        #         )
        #         
        #         # Send push notifications to all user devices
        #         for token, platform in device_tokens:
        #             send_push_notification(token, platform, title, body, {
        #                 "session_id": session_id,
        #                 "notification_id": notification_id
        #             })
        #         
        #         # Update status to sent
        #         conn.execute(
        #             text("UPDATE f_a72b87c1__notifications SET delivery_status = 'sent' WHERE id = :id"),
        #             {"id": notification_id}
        #         )
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def register_background_components(registry):
    """Register this feature's background job with the application."""
    registry.register(
        'capability_notification_when_wash_nearly_finished_a72b87c1.function.schedule_notification_check',
        schedule_notification_check,
    )

def update_notification_delivery_status(notification_id, status):
    """Updates the delivery status of a notification when push service confirms delivery or failure.
    
    Args:
        notification_id: UUID of the notification
        status: New delivery status ('pending', 'sent', 'delivered', 'failed')
    """
    conn = get_db_connection()
    
    try:
        # Validate status
        valid_statuses = ['pending', 'sent', 'delivered', 'failed']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}")
        
        # Update notification delivery status
        conn.execute(
            text("UPDATE f_a72b87c1__notifications SET delivery_status = :status WHERE id = :id"),
            {"status": status, "id": notification_id}
        )
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def send_push_notification(token, platform, title, body, data):
    """Helper function to send push notifications via FCM or APNs.
    
    This is a placeholder for the actual push notification implementation.
    In production, you would integrate with Firebase Cloud Messaging (FCM) for Android
    and Apple Push Notification service (APNs) for iOS.
    
    Args:
        token: Device token
        platform: 'ios' or 'android'
        title: Notification title
        body: Notification body
        data: Additional data payload (dict)
    """
    # Placeholder implementation
    # In production, use libraries like:
    # - firebase-admin for FCM
    # - apns2 for APNs
    pass
