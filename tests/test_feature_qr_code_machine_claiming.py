"""Deterministic contract checks for QR code machine claiming."""

from backend import create_app


def test_feature_routes_are_registered():
    app = create_app(testing=True)
    actual = {
        (rule.rule, method)
        for rule in app.url_map.iter_rules()
        for method in (rule.methods or set())
    }
    expected = (('/api/capability_qr_code_machine_claiming_a1e10606/machines/claim', 'POST'),)
    assert all(route in actual for route in expected)


def test_protected_routes_reject_missing_authentication():
    client = create_app(testing=True).test_client()
    response = client.post('/api/capability_qr_code_machine_claiming_a1e10606/machines/claim')
    assert response.status_code == 401
