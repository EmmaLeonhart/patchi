"""Submit Patchi's paper to clawRxiv (POST /api/posts).

clawRxiv is an academic archive for AI-agent-authored papers. Submission is
authenticated and **publishes immediately and publicly**, so this script does
nothing without an explicit API key and a --confirm flag.

Two ways to get a key:
  1. Use an existing key:  export CLAWRXIV_API_KEY=oc_xxx
  2. Self-register an agent identity (prints a one-time key):
       python scripts/submit_clawrxiv.py --register "patchi-agent"

Then submit:
  python scripts/submit_clawrxiv.py --confirm --authors "Pygmalion,Emma Leonhart"

Title + abstract are parsed from PAPER.md (H1 = title; the text under
"## Abstract" = abstract); the full PAPER.md is the content.
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "PAPER.md"
BASE = "https://clawrxiv.io/api"


def _post(path: str, body: dict, key: str | None = None) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if key:
        req.add_header("Authorization", f"Bearer {key}")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def parse_paper(md: str):
    title = re.search(r"^#\s+(.+)$", md, re.M).group(1).strip()
    m = re.search(r"##\s+Abstract\s*\n(.+?)\n##\s", md, re.S)
    abstract = re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
    return title, abstract


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--register", metavar="CLAW_NAME",
                    help="register a new agent identity and print the one-time api_key")
    ap.add_argument("--confirm", action="store_true",
                    help="actually publish (without it, this is a dry run)")
    ap.add_argument("--authors", default="Pygmalion",
                    help="comma-separated human_names (default: Pygmalion)")
    args = ap.parse_args()

    if args.register:
        resp = _post("/auth/register", {"claw_name": args.register})
        print("Save this one-time API key:")
        print(json.dumps(resp, indent=2))
        return 0

    md = PAPER.read_text(encoding="utf-8")
    title, abstract = parse_paper(md)
    payload = {
        "title": title,
        "abstract": abstract,
        "content": md,
        "human_names": [a.strip() for a in args.authors.split(",") if a.strip()],
        "tags": ["cognition", "distributional-semantics", "neuro-symbolic",
                 "vector-symbolic-architectures", "negative-result"],
    }

    print(f"title   : {title}")
    print(f"abstract: {abstract[:200]}...")
    print(f"authors : {payload['human_names']}")
    print(f"content : {len(md)} chars from PAPER.md")

    if not args.confirm:
        print("\nDRY RUN — re-run with --confirm (and CLAWRXIV_API_KEY set) to publish.")
        return 0

    key = os.environ.get("CLAWRXIV_API_KEY")
    if not key:
        print("\nERROR: set CLAWRXIV_API_KEY (or use --register first).", file=sys.stderr)
        return 1
    resp = _post("/posts", payload, key=key)
    print("\nPUBLISHED:")
    print(json.dumps(resp, indent=2))
    pid = resp.get("paper_id")
    if pid:
        print(f"https://www.clawrxiv.io/abs/{pid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
