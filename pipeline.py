# pipeline.py
import copy
from nodes import load, classify, extract, normalize, merge, confidence, projection, validate

def create_context(config):
    return {
        "config": config,
        "raw_sources": {},      # {source_key: {"type": ..., "data": ...}}
        "extracted": [],        # list of raw candidate dicts
        "normalized": [],       # list of normalized candidate dicts
        "merged": [],           # list with one merged candidate
        "canonical": {},        # final canonical record
        "output": {},           # after projection
        "errors": []            # non‑fatal errors
    }

def run_pipeline(source_args, config):
    ctx = create_context(config)

    # Node 1
    ctx = load.load_sources(ctx, source_args)

    # Node 2
    ctx = classify.classify_sources(ctx)

    # Node 3
    ctx = extract.extract_all(ctx)

    # Node 4
    ctx = normalize.normalize_all(ctx)

    # Node 5
    ctx = merge.merge_candidates(ctx)

    # Node 6
    ctx = confidence.assign_confidence(ctx)

    # Node 7 – build canonical record (already done inside merge/confidence)
    # We'll move it to its own step later if needed.

    # Node 8
    ctx = projection.project(ctx)

    # Node 9
    ctx = validate.validate_output(ctx)

    return ctx["output"], ctx["errors"]