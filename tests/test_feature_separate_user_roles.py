"""Deterministic contract checks for Separate user roles."""

from backend import create_app


def test_feature_routes_are_registered():
    app = create_app(testing=True)
    actual = {
        (rule.rule, method)
        for rule in app.url_map.iter_rules()
        for method in (rule.methods or set())
    }
    expected = (('/api/capability_separate_user_roles_e876dcda/auth/signup/resident', 'POST'), ('/api/capability_separate_user_roles_e876dcda/auth/signup/admin', 'POST'), ('/api/capability_separate_user_roles_e876dcda/auth/me', 'GET'))
    assert all(route in actual for route in expected)


def test_protected_routes_reject_missing_authentication():
    client = create_app(testing=True).test_client()
    response = client.get('/api/capability_separate_user_roles_e876dcda/auth/me')
    assert response.status_code == 401
