"""Deterministic contract checks for Notification when wash nearly finished."""

from backend import create_app


def test_feature_routes_are_registered():
    app = create_app(testing=True)
    actual = {
        (rule.rule, method)
        for rule in app.url_map.iter_rules()
        for method in (rule.methods or set())
    }
    expected = (('/api/capability_notification_when_wash_nearly_finished_a72b87c1/notifications/device-token', 'POST'), ('/api/capability_notification_when_wash_nearly_finished_a72b87c1/notifications/session/<session_id>', 'GET'))
    assert all(route in actual for route in expected)


def test_protected_routes_reject_missing_authentication():
    client = create_app(testing=True).test_client()
    response = client.post('/api/capability_notification_when_wash_nearly_finished_a72b87c1/notifications/device-token')
    assert response.status_code == 401
    response = client.get('/api/capability_notification_when_wash_nearly_finished_a72b87c1/notifications/session/test-id')
    assert response.status_code == 401
