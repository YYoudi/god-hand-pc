"""Original game-free larger-texture diagnostic pack; not remaster artwork."""
from pathlib import Path
import argparse
import json
import hd_packs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(hd_packs.create_example(args.output), indent=2))
