"""Deterministic contract checks for End session button."""

from backend import create_app


def test_feature_routes_are_registered():
    app = create_app(testing=True)
    actual = {
        (rule.rule, method)
        for rule in app.url_map.iter_rules()
        for method in (rule.methods or set())
    }
    expected = (('/api/capability_end_session_button_342bee96/sessions/<session_id>/end', 'POST'),)
    assert all(route in actual for route in expected)


def test_protected_routes_reject_missing_authentication():
    client = create_app(testing=True).test_client()
    response = client.post('/api/capability_end_session_button_342bee96/sessions/test-id/end')
    assert response.status_code == 401
