import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nodes.extract import extract_ats, extract_github, extract_linkedin, empty_candidate

def test_extract_ats_all_fields():
    data = {
        "candidate_name": "Jane Smith",
        "email_address": "jane@example.com",
        "phone_number": "555-1234",
        "current_company": "TechCorp",
        "title": "Engineer"
    }
    cand = extract_ats(data)
    assert cand["full_name"] == "Jane Smith"
    assert cand["emails"] == ["jane@example.com"]
    assert cand["phones"] == ["555-1234"]
    assert len(cand["experience"]) == 1
    assert cand["experience"][0]["company"] == "TechCorp"

def test_extract_ats_missing_fields():
    data = {}
    cand = extract_ats(data)
    assert cand["full_name"] is None
    assert cand["emails"] == []

def test_extract_github_from_dict():
    data = {
        "name": "Octocat",
        "bio": "Hello world",
        "email": "octo@github.com",
        "html_url": "http://github.com/octo",
        "blog": "http://blog.octo",
        "location": "San Francisco"
    }
    cand = extract_github(data)
    assert cand["full_name"] == "Octocat"
    assert cand["headline"] == "Hello world"
    assert cand["emails"] == ["octo@github.com"]
    assert cand["links"]["github"] == "http://github.com/octo"
    assert cand["location"]["city"] == "San Francisco"

def test_extract_github_from_string():
    import json
    data = json.dumps({"name": "Test", "bio": ""})
    cand = extract_github(data)
    assert cand["full_name"] == "Test"

def test_extract_github_invalid_json():
    cand = extract_github("not json")
    assert cand["source"] == "github"
    assert cand["full_name"] is None  # empty candidate

def test_extract_linkedin():
    data = {
        "full_name": "Jane",
        "headline": "Dev",
        "email": "jane@linkedin.com",
        "location": "NY, USA",
        "experience": [{"company": "X", "title": "Dev", "start": "2020-01", "end": None}],
        "education": [{"institution": "MIT", "degree": "BS", "field": "CS", "end_year": 2020}],
        "skills": ["Python", "Java"]
    }
    cand = extract_linkedin(data)
    assert cand["full_name"] == "Jane"
    assert len(cand["skills"]) == 2
    assert cand["skills"][0]["name"] == "Python"
    assert cand["skills"][0]["sources"] == ["linkedin"]