import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nodes.validate import build_schema, validate
from jsonschema import ValidationError

def test_schema_generation():
    config = {
        "fields": [
            {"path": "name", "type": "string", "required": True},
            {"path": "emails", "type": "string[]", "required": False}
        ]
    }
    schema = build_schema(config)
    assert schema["type"] == "object"
    assert "name" in schema["required"]
    assert schema["properties"]["name"]["type"] == "string"
    # For non-required array, type should be ["array", "null"]
    assert schema["properties"]["emails"]["type"] == ["array", "null"]

def test_validate_correct_output():
    config = {
        "fields": [{"path": "name", "type": "string", "required": True}]
    }
    output = {"name": "Jane"}
    # No exception
    validate(instance=output, schema=build_schema(config))

def test_validate_missing_required_raises():
    config = {
        "fields": [{"path": "name", "type": "string", "required": True}]
    }
    output = {}
    with pytest.raises(ValidationError):
        validate(instance=output, schema=build_schema(config))