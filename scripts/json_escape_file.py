import sys
import json

if len(sys.argv) != 2:
    print("Missing argument\nUsage: python3 json_escape_file.py <PATH>", file=sys.stderr)
    exit(1)

try:
    with open(sys.argv[1]) as f:
        print(json.dumps(f.read()))
except Exception as e:
    print(f"Error while reading file: {e}", file=sys.stderr)
