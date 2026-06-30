# nodes/confidence.py

SOURCE_BASE_CONF = {
    "ats": 0.8,
    "github": 0.6,
    "notes": 0.4
}

def assign_confidence(ctx):
    if not ctx["merged"]:
        return ctx
    merged = ctx["merged"][0]
    # We need to compute confidence per field based on provenance
    # We'll group provenance by field
    field_prov = {}
    for p in merged.get("provenance", []):
        field = p["field"]
        if field not in field_prov:
            field_prov[field] = []
        field_prov[field].append(p["source"])

    conf = {}
    # Scalars
    for field in ["full_name", "headline", "years_experience", "location"]:
        if merged.get(field) is not None:
            # confidence from the highest priority source that provided it (already in provenance)
            # Actually we need to know the winning source; provenance for scalar contains only one entry
            prov_entries = field_prov.get(field, [])
            if prov_entries:
                # take the source of the winner (the first in provenance)
                src = prov_entries[0]
                conf[field] = SOURCE_BASE_CONF.get(src, 0.5)
                # agreement boost: if other sources also provided same value, we could check, but skip for simplicity
            else:
                conf[field] = 0.0
        else:
            conf[field] = 0.0

    # List fields: confidence = average of source base conf for each unique source that contributed items
    for field in ["emails", "phones", "skills", "experience", "education"]:
        if field in field_prov:
            sources = list(set(field_prov[field]))
            if sources:
                avg_conf = sum(SOURCE_BASE_CONF.get(s, 0.5) for s in sources) / len(sources)
                conf[field] = round(avg_conf, 2)
            else:
                conf[field] = 0.0
        else:
            conf[field] = 0.0

    # Overall confidence: average of all non-zero confidences? or all fields? We'll average all scalar + list confidences
    all_confs = [v for v in conf.values()]
    overall = sum(all_confs) / len(all_confs) if all_confs else 0.0
    merged["overall_confidence"] = round(overall, 2)
    merged["_confidence"] = conf   # internal storage, can be used by projection
    ctx["merged"][0] = merged
    ctx["canonical"] = merged      # the merged record IS the canonical record
    return ctx