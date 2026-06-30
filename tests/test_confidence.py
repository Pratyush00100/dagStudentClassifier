import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nodes.confidence import assign_confidence


def make_merged(**kwargs):
    base = {
        "source": "merged",
        "full_name": "A",
        "headline": "B",
        "emails": ["e"],
        "phones": [],
        "location": None,
        "years_experience": 2,
        "skills": [{"name": "X"}],
        "experience": [{"company": "C"}],
        "education": [],
        "provenance": [
            {"field": "full_name", "source": "ats", "method": "source_priority"},
            {"field": "headline", "source": "github", "method": "source_priority"},
            {"field": "emails", "source": "ats", "method": "union"},
            {"field": "skills", "source": "github", "method": "union"}
        ]
    }
    base.update(kwargs)
    return base

def test_confidence_scalar_from_source():
    ctx = {"merged": [make_merged()], "config": {}}
    ctx = assign_confidence(ctx)
    conf = ctx["merged"][0]["_confidence"]
    assert conf["full_name"] == 0.8
    assert conf["headline"] == 0.6

def test_overall_confidence_average():
    ctx = {"merged": [make_merged()], "config": {}}
    ctx = assign_confidence(ctx)
    overall = ctx["merged"][0]["overall_confidence"]
    # Should be average of non-null fields; all fields present except maybe null ones
    assert 0 < overall <= 1.0

def test_null_field_confidence_zero():
    merged = make_merged(location=None)  # location is None, provenance not present
    ctx = {"merged": [merged], "config": {}}
    ctx = assign_confidence(ctx)
    assert ctx["merged"][0]["_confidence"]["location"] == 0.0