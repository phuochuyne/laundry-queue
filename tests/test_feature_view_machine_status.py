"""Deterministic contract checks for View machine status."""

from backend import create_app


def test_feature_routes_are_registered():
    app = create_app(testing=True)
    actual = {
        (rule.rule, method)
        for rule in app.url_map.iter_rules()
        for method in (rule.methods or set())
    }
    expected = (('/api/capability_view_machine_status_589af8dc/buildings/<building_id>/machines', 'GET'), ('/api/capability_view_machine_status_589af8dc/machines/<machine_id>/status', 'PATCH'), ('/api/capability_view_machine_status_589af8dc/machines/<machine_id>', 'GET'))
    assert all(route in actual for route in expected)


def test_protected_routes_reject_missing_authentication():
    client = create_app(testing=True).test_client()
    response = client.get('/api/capability_view_machine_status_589af8dc/buildings/test-id/machines')
    assert response.status_code == 401
    response = client.patch('/api/capability_view_machine_status_589af8dc/machines/test-id/status')
    assert response.status_code == 401
    response = client.get('/api/capability_view_machine_status_589af8dc/machines/test-id')
    assert response.status_code == 401
