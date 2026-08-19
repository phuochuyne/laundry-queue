"""Deterministic contract checks for Building code or email join."""

from backend import create_app


def test_feature_routes_are_registered():
    app = create_app(testing=True)
    actual = {
        (rule.rule, method)
        for rule in app.url_map.iter_rules()
        for method in (rule.methods or set())
    }
    expected = (('/api/capability_building_code_or_email_join_85677965/buildings/join/code', 'POST'), ('/api/capability_building_code_or_email_join_85677965/buildings/join/email', 'POST'), ('/api/capability_building_code_or_email_join_85677965/user/memberships', 'GET'))
    assert all(route in actual for route in expected)


def test_protected_routes_reject_missing_authentication():
    client = create_app(testing=True).test_client()
    response = client.post('/api/capability_building_code_or_email_join_85677965/buildings/join/code')
    assert response.status_code == 401
    response = client.post('/api/capability_building_code_or_email_join_85677965/buildings/join/email')
    assert response.status_code == 401
    response = client.get('/api/capability_building_code_or_email_join_85677965/user/memberships')
    assert response.status_code == 401
