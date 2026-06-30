import argparse
import json
from pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ats", help="Path to ATS JSON file")
    parser.add_argument("--github", help="GitHub username or URL")
    parser.add_argument("--config", default="configs/default.json", help="Config file path")
    parser.add_argument("--out", default="output/result.json", help="Output file")
    args = parser.parse_args()

    # Load config
    with open(args.config, "r") as f:
        config = json.load(f)

    # Build source args
    source_args = {}
    if args.ats:
        source_args["ats"] = args.ats
    if args.github:
        # construct full API URL
        username = args.github.strip().split("/")[-1]
        source_args["github"] = f"https://api.github.com/users/{username}"

    output, errors = run_pipeline(source_args, config)

    # Save output
    with open(args.out, "w") as f:
        json.dump(output, f, indent=2)

    # Print to console
    print(json.dumps(output, indent=2))
    if errors:
        print("\nWarnings/Errors:", json.dumps(errors, indent=2))

if __name__ == "__main__":
    main()