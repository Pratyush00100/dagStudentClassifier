# Eightfold Candidate Data Transformer

Transforms messy, multi‑source candidate data into a single trustworthy, canonical profile with provenance and confidence.

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

Required packages: `phonenumbers`, `python-dateutil`, `jsonschema`, `requests`.

## Usage

### Default Output (Full Schema)

```bash
python cli.py \
  --ats sample_inputs/ats.json \
  --github-file sample_inputs/github.json \
  --linkedin-file sample_inputs/linkedin.json \
  --config configs/default.json \
  --out output/default.json
```

### Custom Config (Remapped Fields, Subset)

```bash
python cli.py \
  --ats sample_inputs/ats.json \
  --github-file sample_inputs/github.json \
  --linkedin-file sample_inputs/linkedin.json \
  --config configs/custom.json \
  --out output/custom.json
```

### Using Live GitHub API (Instead of Local File)

```bash
python cli.py --ats sample_inputs/ats.json --github octocat --config configs/default.json
```

## Output

- **output/default.json** – Full canonical profile with provenance and confidence.
- **output/custom.json** – Remapped profile (name, primary_email, phone, skills_list).

## Testing

Run the full test suite:

```bash
pytest tests/ -v
```

Includes unit tests for every node, integration tests for robustness, and a golden‑file regression test.

## Assumptions

- All inputs refer to the same person (single‑candidate pipeline).
- Email is the only merge key used.
- Source priority: ATS > LinkedIn > GitHub.
- Default country for phones/location is US when not inferable.
