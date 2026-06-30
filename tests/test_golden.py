import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pipeline import run_pipeline

def test_golden_default():
    # Load expected
    with open("tests/golden_default.json") as f:
        expected = json.load(f)
    config = json.load(open("configs/default.json"))
    sources = {
        "ats": "sample_inputs/ats.json",
        "github": "sample_inputs/github.json",
        "linkedin": "sample_inputs/linkedin.json"
    }
    output, errors = run_pipeline(sources, config)
    # Remove any dynamic field like candidate_id if you want to ignore? We'll keep it
    assert output == expected, f"Output differs. Got: {output}"

