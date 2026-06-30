import re
import phonenumbers

def normalize_phone(phone_str, default_country="US"):
    try:
        phone_num = phonenumbers.parse(phone_str, default_country)
        if phonenumbers.is_valid_number(phone_num):
            return phonenumbers.format_number(phone_num, phonenumbers.PhoneNumberFormat.E164)
    except:
        pass
    return None  # drop invalid

def normalize_email(email):
    email = email.strip().lower()
    if re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return email
    return None

def normalize_date(date_str):
    # For simplicity, expect YYYY-MM or YYYY; parse with dateutil optionally
    from dateutil import parser
    try:
        dt = parser.parse(date_str)
        return dt.strftime("%Y-%m")
    except:
        return None

def normalize_candidate(candidate):
    # phones
    valid_phones = []
    for p in candidate.get("phones", []):
        norm = normalize_phone(p)
        if norm:
            valid_phones.append(norm)
    candidate["phones"] = valid_phones

    # emails
    valid_emails = []
    for e in candidate.get("emails", []):
        norm = normalize_email(e)
        if norm:
            valid_emails.append(norm)
    candidate["emails"] = valid_emails

    # dates in experience (if any)
    for exp in candidate.get("experience", []):
        if exp.get("start"):
            exp["start"] = normalize_date(exp["start"])
        if exp.get("end"):
            exp["end"] = normalize_date(exp["end"])

    # canonical skills: a tiny mapping table
    SKILL_MAP = {
        "js": "JavaScript",
        "javascript": "JavaScript",
        "reactjs": "React",
        "react": "React",
        "nodejs": "Node.js",
        "node": "Node.js",
    }
    norm_skills = []
    for skill in candidate.get("skills", []):
        # skill may be a string or an object {name, ...} depending on extraction
        if isinstance(skill, str):
            name = skill.strip().lower()
            canon = SKILL_MAP.get(name, skill.strip())
            norm_skills.append({
                "name": SKILL_MAP.get(name, skill.strip()),
                "confidence": None,           # will be filled later by confidence node
                "sources": [candidate["source"]]
            })
        else:
            # already object
            name = skill["name"].strip().lower()
            skill["name"] = SKILL_MAP.get(name, skill["name"].strip())
            norm_skills.append(skill)
    candidate["skills"] = norm_skills
    return candidate

def normalize_all(ctx):
    normalized = []
    for cand in ctx["extracted"]:
        try:
            norm = normalize_candidate(cand)
            normalized.append(norm)
        except Exception as e:
            ctx["errors"].append({"node": "normalize", "source": cand.get("source"), "error": str(e)})
            normalized.append(cand)  # keep original
    ctx["normalized"] = normalized
    return ctx