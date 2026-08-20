"""Server-owned entry point for the assembled Zorentia application."""

import re
from pathlib import Path

from flask import abort, app, send_file, render_template
from backend import create_app as create_backend_app

PROJECT_ROOT = Path(__file__).resolve().parent
SCREEN_ROUTES = {'/buildings/{building_id}/machines': 'frontend/features/view_machine_status/machine_list.html', '/machines/{machine_id}': 'frontend/features/view_machine_status/machine_detail.html', '/signup': 'frontend/features/separate_user_roles/role_selection.html', '/signup/resident': 'frontend/features/separate_user_roles/resident_signup.html', '/signup/manager': 'frontend/features/separate_user_roles/manager_signup.html', '/login': 'frontend/features/separate_user_roles/login.html', '/admin/machines': 'frontend/features/add_and_remove_machines/machine_list.html', '/admin/machines/add': 'frontend/features/add_and_remove_machines/add_machine.html', '/admin/machines/{machine_id}': 'frontend/features/add_and_remove_machines/machine_detail.html', '/join': 'frontend/features/building_code_or_email_join/join_method_selection.html', '/join/code': 'frontend/features/building_code_or_email_join/join_by_building_code.html', '/join/email': 'frontend/features/building_code_or_email_join/join_by_email.html', '/join/success': 'frontend/features/building_code_or_email_join/membership_confirmation.html', '/memberships': 'frontend/features/building_code_or_email_join/my_memberships.html', '/scan-machine': 'frontend/features/qr_code_machine_claiming/qr_code_scanner.html', '/claim-confirmation': 'frontend/features/qr_code_machine_claiming/claim_confirmation.html', '/claim-error': 'frontend/features/qr_code_machine_claiming/claim_error.html', '/start-session': 'frontend/features/start_timed_laundry_session/start_session.html', '/active-session': 'frontend/features/start_timed_laundry_session/active_session.html', '/machine/:machine_id/start-session': 'frontend/features/start_session_button/start_session_confirmation.html', '/session/:session_id': 'frontend/features/start_session_button/active_session.html', '/notifications/settings': 'frontend/features/notification_when_wash_nearly_finished/notification_settings.html', '/notifications/push': 'frontend/features/notification_when_wash_nearly_finished/push_notification.html', '/session/{session_id}': 'frontend/features/notification_when_wash_nearly_finished/active_session_view.html', '/session/active': 'frontend/features/end_session_button/active_session.html', '/session/ended': 'frontend/features/end_session_button/session_ended_confirmation.html'}


def _flask_route(route):
    return re.sub(
        r"\{([A-Za-z_][A-Za-z0-9_]*)\}",
        lambda match: "<" + match.group(1) + ">",
        route,
    )


def _project_file(relative_path):
    target = (PROJECT_ROOT / relative_path).resolve()
    if target != PROJECT_ROOT and PROJECT_ROOT not in target.parents:
        raise RuntimeError("frontend_route_path_invalid")
    return target


def create_app(testing=False):
    app = create_backend_app(testing=testing)

    @app.get("/static/css/app.css")
    def frontend_css():
        return send_file(
            _project_file("frontend/static/css/app.css"),
            mimetype="text/css",
        )

    @app.get("/__frontend_assets/<path:relative_path>")
    def frontend_asset(relative_path):
        normalized = str(relative_path or "").replace("\\", "/")
        if not normalized.startswith("frontend/features/") or not normalized.endswith(".js"):
            abort(404)
        return send_file(
            _project_file(normalized),
            mimetype="text/javascript",
        )

    for index, (route, relative_path) in enumerate(SCREEN_ROUTES.items()):
        target = _project_file(relative_path)

        def serve_screen(_target=target, **_route_parameters):
            return send_file(_target, mimetype="text/html")

        app.add_url_rule(
            _flask_route(route),
            endpoint="frontend_screen_" + str(index),
            view_func=serve_screen,
            methods=["GET"],
        )
    @app.get('/')
    def serve_custom_home():
        return send_file(_project_file("templates/index.html"), mimetype="text/html")
    return app
