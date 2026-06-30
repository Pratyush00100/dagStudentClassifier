from nodes.normalize import normalize_phone
def test_e164():
    assert normalize_phone("555-1234") == "+15551234"
    assert normalize_phone("+1-555-1234") == "+15551234"
    assert normalize_phone("invalid") is None