import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nodes.merge import merge_candidates

def make_cand(source, **kwargs):
    base = {
        "source": source,
        "full_name": None,
        "emails": [],
        "phones": [],
        "location": None,
        "links": {},
        "headline": None,
        "years_experience": None,
        "skills": [],
        "experience": [],
        "education": [],
        "provenance": []
    }
    base.update(kwargs)
    return base

def test_scalar_priority():
    config = {"source_priority": ["ats", "github"]}
    ctx = {
        "config": config,
        "normalized": [
            make_cand("github", full_name="GitHub Name"),
            make_cand("ats", full_name="ATS Name")
        ]
    }
    ctx = merge_candidates(ctx)
    merged = ctx["merged"][0]
    assert merged["full_name"] == "ATS Name"
    prov = [p for p in merged["provenance"] if p["field"] == "full_name"]
    assert prov[0]["source"] == "ats"
    assert prov[0]["method"] == "source_priority"

def test_union_emails():
    config = {"source_priority": ["ats", "github"]}
    ctx = {
        "config": config,
        "normalized": [
            make_cand("github", emails=["a@b.com"]),
            make_cand("ats", emails=["b@c.com"])
        ]
    }
    ctx = merge_candidates(ctx)
    merged = ctx["merged"][0]
    assert set(merged["emails"]) == {"a@b.com", "b@c.com"}

def test_skills_dedup_by_name():
    config = {"source_priority": ["ats", "github"]}
    ctx = {
        "config": config,
        "normalized": [
            make_cand("github", skills=[{"name": "Python", "confidence": None, "sources": ["github"]}]),
            make_cand("linkedin", skills=[{"name": "Python", "confidence": None, "sources": ["linkedin"]}])
        ]
    }
    ctx = merge_candidates(ctx)
    merged = ctx["merged"][0]
    assert len(merged["skills"]) == 1
    # The skill may be from first source (github) or union; we trust dedup