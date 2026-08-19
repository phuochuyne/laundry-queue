"""Deterministic contract checks for Add and remove machines."""

from backend import create_app


def test_feature_routes_are_registered():
    app = create_app(testing=True)
    actual = {
        (rule.rule, method)
        for rule in app.url_map.iter_rules()
        for method in (rule.methods or set())
    }
    expected = (('/api/capability_add_and_remove_machines_e6daa139/machines', 'POST'), ('/api/capability_add_and_remove_machines_e6daa139/machines', 'GET'), ('/api/capability_add_and_remove_machines_e6daa139/machines/<machine_id>', 'DELETE'), ('/api/capability_add_and_remove_machines_e6daa139/machines/<machine_id>', 'GET'))
    assert all(route in actual for route in expected)


def test_protected_routes_reject_missing_authentication():
    client = create_app(testing=True).test_client()
    response = client.post('/api/capability_add_and_remove_machines_e6daa139/machines')
    assert response.status_code == 401
    response = client.get('/api/capability_add_and_remove_machines_e6daa139/machines')
    assert response.status_code == 401
    response = client.delete('/api/capability_add_and_remove_machines_e6daa139/machines/test-id')
    assert response.status_code == 401
    response = client.get('/api/capability_add_and_remove_machines_e6daa139/machines/test-id')
    assert response.status_code == 401
