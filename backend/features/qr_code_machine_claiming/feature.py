import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.core.auth import require_auth
from backend.core.db import get_engine

bp = Blueprint('capability_qr_code_machine_claiming_a1e10606', __name__)


@bp.route('/api/capability_qr_code_machine_claiming_a1e10606/machines/claim', methods=['POST'])
@require_auth
def claim_machine_by_qr():
    """
    Validates a scanned QR code value, identifies the corresponding machine,
    checks if the machine is already claimed, and creates a new active claim
    for the authenticated user if the machine is available.
    """
    try:
        # Get authenticated user ID
        user_id = g.identity['sub']
        
        # Validate request body
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'INVALID_REQUEST',
                'message': 'Request body is required'
            }), 400
        
        qr_code_value = data.get('qr_code_value')
        
        # Validate qr_code_value
        if not qr_code_value:
            return jsonify({
                'error': 'INVALID_REQUEST',
                'message': 'qr_code_value is required'
            }), 400
        
        if not isinstance(qr_code_value, str) or len(qr_code_value) < 1 or len(qr_code_value) > 255:
            return jsonify({
                'error': 'INVALID_REQUEST',
                'message': 'qr_code_value must be a string between 1 and 255 characters'
            }), 400
        
        # Look up the QR code in the machine_qr_codes table
        qr_lookup_query = text("""
            SELECT id, machine_id
            FROM f_a1e10606__machine_qr_codes
            WHERE qr_code_value = :qr_code_value
            LIMIT 1
        """)
        
        with get_engine().begin() as connection:
            qr_result = connection.execute(
                qr_lookup_query,
                {'qr_code_value': qr_code_value}
            ).fetchone()

            if not qr_result:
                return jsonify({
                    'error': 'INVALID_QR_CODE',
                    'message': 'The scanned QR code is not valid or does not match any machine'
                }), 400

            machine_id = qr_result.machine_id

            active_claim_query = text("""
                SELECT id
                FROM f_a1e10606__machine_claims
                WHERE machine_id = :machine_id AND status = 'active'
                LIMIT 1
            """)
            active_claim = connection.execute(
                active_claim_query,
                {'machine_id': machine_id}
            ).fetchone()

            if active_claim:
                return jsonify({
                    'error': 'MACHINE_ALREADY_IN_USE',
                    'message': 'This machine is already in use by another user'
                }), 409

            machine_name = f"Machine {machine_id[:8]}"
            claim_id = str(uuid.uuid4())
            claimed_at = datetime.utcnow()
            insert_claim_query = text("""
                INSERT INTO f_a1e10606__machine_claims
                (id, machine_id, user_id, claimed_at, status)
                VALUES (:id, :machine_id, :user_id, :claimed_at, :status)
            """)
            connection.execute(
                insert_claim_query,
                {
                    'id': claim_id,
                    'machine_id': machine_id,
                    'user_id': user_id,
                    'claimed_at': claimed_at,
                    'status': 'active'
                }
            )
        
        # Return success response
        return jsonify({
            'claim_id': claim_id,
            'machine_id': machine_id,
            'machine_name': machine_name,
            'claimed_at': claimed_at.isoformat() + 'Z'
        }), 200
        
    except SQLAlchemyError:
        return jsonify({
            'error': 'DATABASE_ERROR',
            'message': 'An error occurred while processing the claim'
        }), 500
    except Exception:
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred'
        }), 500
