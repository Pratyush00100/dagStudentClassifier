# nodes/classify.py

def classify_sources(ctx):
    # We rely on the source key naming convention or file content
    for key, data in ctx["raw_sources"].items():
        if data is None:
            ctx["raw_sources"][key] = {"type": "unknown", "data": None}
        elif key == "ats":
            ctx["raw_sources"][key] = {"type": "ats_json", "data": data}
        elif key == "github":
            ctx["raw_sources"][key] = {"type": "github_api", "data": data}
        elif key == "notes":
            ctx["raw_sources"][key] = {"type": "recruiter_notes", "data": data}
        else:
            # default to unstructured text
            ctx["raw_sources"][key] = {"type": "text", "data": data}
    return ctx