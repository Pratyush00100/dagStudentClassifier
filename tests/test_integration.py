from pipeline import run_pipeline
import json
import os
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_full_pipeline_default_output():
    config = json.load(open("configs/default.json"))
    sources = {
        "ats": "sample_inputs/ats.json",
        "github": "sample_inputs/github.json",
        "linkedin": "sample_inputs/linkedin.json"
    }
    output, errors = run_pipeline(sources, config)
    assert "candidate_id" in output
    assert "full_name" in output
    assert "provenance" in output
    assert output["overall_confidence"] > 0
    # no errors except possibly validation warnings? We'll ensure they are empty
    # (validation errors already fixed)
    assert len(errors) == 0

def test_missing_source_continues():
    config = json.load(open("configs/default.json"))
    sources = {
        "ats": "nonexistent.json",
        "github": "sample_inputs/github.json"
    }
    output, errors = run_pipeline(sources, config)
    # Should still get an output (with whatever data from github)
    assert output is not None
    # errors should contain the load error
    assert any(e["node"] == "load" for e in errors)

def test_malformed_json_source():
    # Create a temporary malformed file
    with open("temp_bad.json", "w") as f:
        f.write("not json")
    config = json.load(open("configs/default.json"))
    sources = {"ats": "temp_bad.json", "github": "sample_inputs/github.json"}
    output, errors = run_pipeline(sources, config)
    os.remove("temp_bad.json")
    # Pipeline should not crash; output must exist
    assert output is not None
    # Graceful degradation: the malformed source just contributes nothing
    
def test_deterministic():
    config = json.load(open("configs/default.json"))
    sources = {
        "ats": "sample_inputs/ats.json",
        "github": "sample_inputs/github.json"
    }
    output1, _ = run_pipeline(sources, config)
    output2, _ = run_pipeline(sources, config)
    assert output1 == output2