# nodes/extract.py
import json

ATS_FIELD_MAP = {
    "candidate_name": "full_name",
    "email_address": "emails",      # will be wrapped in list
    "phone_number": "phones",
    "current_company": None,        # we'll use it for experience
    "title": "title_raw"            # auxiliary
}

def extract_ats(data):
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except:
            return empty_candidate("ats")
    cand = empty_candidate("ats")
    for src_field, canon_field in ATS_FIELD_MAP.items():
        if canon_field is None:
            continue
        val = data.get(src_field)
        if val is not None:
            if canon_field in ("emails", "phones", "links", "skills"):
                # these are lists; wrap scalar if needed
                if isinstance(val, list):
                    cand[canon_field] = val
                else:
                    cand[canon_field] = [val]
            else:
                cand[canon_field] = val
    # Handle company -> experience
    company = data.get("current_company")
    title = data.get("title")
    if company or title:
        cand["experience"] = [{
            "company": company or "",
            "title": title or "",
            "start": None,
            "end": None,
            "summary": ""
        }]
    return cand

def empty_candidate(source):
    return {
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
        "education": []
    }
import re
KNOWN_SKILLS = ["JavaScript", "Python", "React", "Node.js", "Java", "C++", "SQL"]

def extract_skills_from_text(text):
    found = []
    for skill in KNOWN_SKILLS:
        if re.search(rf'\b{re.escape(skill)}\b', text, re.IGNORECASE):
            found.append(skill)
    return found

import json

def extract_github(data):
    # Handle file content (string) -> parse JSON
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return empty_candidate("github")
    
    if not isinstance(data, dict):
        return empty_candidate("github")

    cand = empty_candidate("github")
    cand["full_name"] = data.get("name")
    email = data.get("email")
    if email:
        cand["emails"] = [email]
    cand["headline"] = data.get("bio")
    # links
    cand["links"] = {
        "github": data.get("html_url"),
        "blog": data.get("blog") if data.get("blog") else None
    }
    # location parsing (simple)
    location_str = data.get("location")
    if location_str:
        parts = [p.strip() for p in location_str.split(",")]
        cand["location"] = {
            "city": parts[0],
            "region": parts[1] if len(parts) > 1 else None,
            "country": "US"  # assume US for demo; could be smarter
        }
    # Skills from bio
    cand["skills"] = extract_skills_from_text(data.get("bio", ""))
    
    # (Optional) location parsing – uncomment if you like
    # location = data.get("location")
    # if location:
    #     parts = [p.strip() for p in location.split(",")]
    #     cand["location"] = {"city": parts[0], "region": parts[1] if len(parts)>1 else None, "country": None}
    
    return cand

def extract_all(ctx):
    extracted = []
    for source_key, source in ctx["raw_sources"].items():
        if source["data"] is None:
            empty = empty_candidate(source_key)
            empty["_error"] = "no data"
            extracted.append(empty)
            continue
        try:
            if source["type"] == "ats_json":
                cand = extract_ats(source["data"])
            elif source["type"] == "github_api":
                cand = extract_github(source["data"])
            elif source["type"] == "recruiter_notes":
                cand = extract_notes(source["data"])   # we'll skip for now, but you can add regex extraction
            else:
                cand = empty_candidate(source_key)
            extracted.append(cand)
        except Exception as e:
            ctx["errors"].append({"node": "extract", "source": source_key, "error": str(e)})
            extracted.append(empty_candidate(source_key))
    ctx["extracted"] = extracted
    return ctx