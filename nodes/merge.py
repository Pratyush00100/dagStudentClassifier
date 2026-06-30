import hashlib

def merge_candidates(ctx):
    candidates = ctx["normalized"]
    if not candidates:
        ctx["merged"] = []
        return ctx
    priority_order = ctx["config"].get("source_priority", ["ats", "github"])
    # Sort candidates by priority
    def source_rank(cand):
        try:
            return priority_order.index(cand["source"])
        except ValueError:
            return len(priority_order)  # unknown source last
    sorted_cands = sorted(candidates, key=source_rank)

    merged = {
        "source": "merged",
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
        "provenance": []  # will collect provenance entries
    }

    # For provenance tracking
    def add_provenance(field, source, method):
        merged["provenance"].append({"field": field, "source": source, "method": method})

    print("merge_candidates normalized count:", len(candidates), "sources:", [cand.get("source") for cand in candidates])
    # Scalars: take first non‑null from sorted candidates
    for field in ["full_name", "headline", "years_experience"]:
        for cand in sorted_cands:
            val = cand.get(field)
            if val is not None:
                merged[field] = val
                add_provenance(field, cand["source"], "source_priority")
                break

    # Location (dict, treat as scalar)
    for cand in sorted_cands:
        val = cand.get("location")
        if val is not None:
            merged["location"] = val
            add_provenance("location", cand["source"], "source_priority")
            break

    # Lists: union
    seen_emails = set()
    seen_phones = set()
    seen_skills = set()
    seen_experience = set()  # (company, title) tuple
    seen_education = set()

    for cand in sorted_cands:
        for email in cand.get("emails", []):
            if email not in seen_emails:
                merged["emails"].append(email)
                seen_emails.add(email)
                add_provenance("emails", cand["source"], "union")
        for phone in cand.get("phones", []):
            if phone not in seen_phones:
                merged["phones"].append(phone)
                seen_phones.add(phone)
                add_provenance("phones", cand["source"], "union")
        # skills: assume list of strings or objects; we'll convert to string for dedup
        for skill in cand.get("skills", []):
            key = skill if isinstance(skill, str) else skill["name"].lower()
            if key not in seen_skills:
                merged["skills"].append(skill)
                seen_skills.add(key)
                add_provenance("skills", cand["source"], "union")
        for exp in cand.get("experience", []):
            key = (exp.get("company",""), exp.get("title",""))
            if key not in seen_experience:
                merged["experience"].append(exp)
                seen_experience.add(key)
                add_provenance("experience", cand["source"], "union")
        for edu in cand.get("education", []):
            key = (edu.get("institution",""), edu.get("degree",""), edu.get("field",""))
            if key not in seen_education:
                merged["education"].append(edu)
                seen_education.add(key)
                add_provenance("education", cand["source"], "union")

    # Links: merge dict
    for cand in sorted_cands:
        links = cand.get("links", {})
        if isinstance(links, dict):
            for k, v in links.items():
                if v and k not in merged["links"]:
                    merged["links"][k] = v
                    add_provenance(f"links.{k}", cand["source"], "union")

    if merged["emails"]:
        primary_email = merged["emails"][0]
        merged["candidate_id"] = hashlib.md5(primary_email.encode()).hexdigest()[:8]
    else:
        merged["candidate_id"] = "unknown-candidate"

    print("merged headline:", merged["headline"])
    ctx["merged"] = [merged]
    return ctx