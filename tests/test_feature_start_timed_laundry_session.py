"""Deterministic contract checks for Start timed laundry session."""

from backend import create_app


def test_feature_routes_are_registered():
    app = create_app(testing=True)
    actual = {
        (rule.rule, method)
        for rule in app.url_map.iter_rules()
        for method in (rule.methods or set())
    }
    expected = (('/api/capability_start_timed_laundry_session_f115b2e6/sessions', 'POST'), ('/api/capability_start_timed_laundry_session_f115b2e6/sessions/<session_id>', 'GET'), ('/api/capability_start_timed_laundry_session_f115b2e6/machines/<machine_id>/active-session', 'GET'), ('/api/capability_start_timed_laundry_session_f115b2e6/sessions/my-active', 'GET'), ('/api/capability_start_timed_laundry_session_f115b2e6/sessions/<session_id>/end', 'POST'))
    assert all(route in actual for route in expected)


def test_protected_routes_reject_missing_authentication():
    client = create_app(testing=True).test_client()
    response = client.post('/api/capability_start_timed_laundry_session_f115b2e6/sessions')
    assert response.status_code == 401
    response = client.get('/api/capability_start_timed_laundry_session_f115b2e6/sessions/test-id')
    assert response.status_code == 401
    response = client.get('/api/capability_start_timed_laundry_session_f115b2e6/machines/test-id/active-session')
    assert response.status_code == 401
    response = client.get('/api/capability_start_timed_laundry_session_f115b2e6/sessions/my-active')
    assert response.status_code == 401
    response = client.post('/api/capability_start_timed_laundry_session_f115b2e6/sessions/test-id/end')
    assert response.status_code == 401
