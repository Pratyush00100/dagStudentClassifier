# nodes/load.py
import os
import json
import requests

def load_sources(ctx, source_args):
    # source_args is a dict like {"ats": "sample_inputs/ats.json", "github": "https://github.com/octocat"}
    for key, path_or_url in source_args.items():
        try:
            if path_or_url.startswith("http"):
                resp = requests.get(path_or_url, timeout=10)
                resp.raise_for_status()
                ctx["raw_sources"][key] = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text
            else:
                if os.path.exists(path_or_url):
                    with open(path_or_url, "r", encoding="utf-8") as f:
                        # assume JSON for ATS, plain text for notes; we'll classify later
                        raw = f.read()
                        ctx["raw_sources"][key] = raw
                else:
                    raise FileNotFoundError(f"File {path_or_url} not found")
        except Exception as e:
            ctx["raw_sources"][key] = None
            ctx["errors"].append({"node": "load", "source": key, "error": str(e)})
    return ctx