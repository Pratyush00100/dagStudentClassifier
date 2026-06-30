import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nodes.normalize import normalize_phone, normalize_email, normalize_date, normalize_location

def test_phone_e164_us_default():
    assert normalize_phone("415-555-0132") == "+14155550132"

def test_phone_e164_plus_prefix():
    assert normalize_phone("+14155550132") == "+14155550132"

def test_phone_invalid_returns_none():
    assert normalize_phone("abc") is None
    assert normalize_phone("") is None

def test_email_lowercase_and_valid():
    assert normalize_email("John@Example.com") == "john@example.com"
    assert normalize_email("  jane@test.org ") == "jane@test.org"

def test_email_invalid_returns_none():
    assert normalize_email("notanemail") is None
    assert normalize_email("@.com") is None

def test_date_parsing():
    assert normalize_date("2020-01") == "2020-01"
    assert normalize_date("2020/01/15") == "2020-01"
    assert normalize_date("Jan 2020") == "2020-01"

def test_date_invalid_returns_none():
    assert normalize_date("garbage") is None

def test_location_default_country():
    from nodes.normalize import normalize_location
    loc = {"city": "San Francisco", "region": "CA", "country": None}
    norm = normalize_location(loc)
    assert norm["city"] == "San Francisco"
    assert norm["region"] == "CA"
    assert norm["country"] == "US"  # default for CA region

def test_location_preserves_country():
    loc = {"city": "London", "region": None, "country": "GB"}
    norm = normalize_location(loc)
    assert norm["country"] == "GB"