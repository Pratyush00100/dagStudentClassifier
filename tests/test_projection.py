import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nodes.projection import resolve_path, project
import json

def test_resolve_path_simple_key():
    obj = {"a": {"b": 1}}
    assert resolve_path(obj, "a.b") == 1

def test_resolve_path_array_index():
    obj = {"emails": ["a@b.com", "c@d.com"]}
    assert resolve_path(obj, "emails[0]") == "a@b.com"

def test_resolve_path_skills_name():
    obj = {"skills": [{"name": "Python"}, {"name": "Java"}]}
    assert resolve_path(obj, "skills[].name") == ["Python", "Java"]

def test_projection_default_config():
    config = {
        "fields": [
            {"path": "full_name", "type": "string", "required": True},
            {"path": "skills", "from": "skills[].name", "type": "string[]", "normalize": "canonical"}
        ],
        "include_confidence": False,
        "on_missing": "null"
    }
    canonical = {
        "full_name": "Jane",
        "skills": [{"name": "JavaScript"}, {"name": "React"}],
        "_confidence": {}
    }
    ctx = {"config": config, "canonical": canonical}
    ctx = project(ctx)
    assert ctx["output"] == {"full_name": "Jane", "skills": ["JavaScript", "React"]}

def test_projection_on_missing_omit():
    config = {
        "fields": [
            {"path": "missing_field", "type": "string", "required": False}
        ],
        "on_missing": "omit"
    }
    canonical = {}
    ctx = {"config": config, "canonical": canonical}
    ctx = project(ctx)
    assert "missing_field" not in ctx["output"]

def test_projection_on_missing_error():
    config = {
        "fields": [
            {"path": "must_exist", "type": "string", "required": True}
        ],
        "on_missing": "error"
    }
    canonical = {}
    ctx = {"config": config, "canonical": canonical}
    with pytest.raises(ValueError):
        project(ctx)