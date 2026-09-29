from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.prompt_management import DEFAULT_PROMPT_TEMPLATE
from app.tracing import get_langfuse_client, tracing_enabled

PROMPT_V2 = (
    DEFAULT_PROMPT_TEMPLATE
    + "\nAnswer concisely; use short bullets when they make the answer clearer."
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage Day 13 prompt labels in your Langfuse project")
    parser.add_argument("action", choices=("status", "bootstrap", "promote-v2", "rollback-v1"))
    parser.add_argument("--name", default=os.getenv("LANGFUSE_PROMPT_NAME", "day13-chat"))
    args = parser.parse_args()

    if not tracing_enabled():
        print("Langfuse tracing is disabled: configure personal project keys in .env first.")
        return 1

    client = get_langfuse_client()
    try:
        if args.action == "status":
            prompt = client.get_prompt(
                args.name,
                label="production",
                type="text",
                fallback=DEFAULT_PROMPT_TEMPLATE,
                fetch_timeout_seconds=5,
                max_retries=0,
            )
            if getattr(prompt, "is_fallback", False):
                print(f"Prompt {args.name!r} could not be resolved as managed production.")
            else:
                print(f"Managed prompt {args.name!r}: production version {prompt.version}.")
            return 0

        if args.action == "bootstrap":
            current = client.get_prompt(
                args.name,
                label="production",
                type="text",
                fallback=DEFAULT_PROMPT_TEMPLATE,
                fetch_timeout_seconds=5,
                max_retries=0,
            )
            if not getattr(current, "is_fallback", False):
                print(f"Prompt {args.name!r} already has a managed production label; leaving it untouched.")
                return 2
            version_one = client.create_prompt(
                name=args.name,
                type="text",
                prompt=DEFAULT_PROMPT_TEMPLATE,
                labels=["baseline", "production"],
                commit_message="CP2 baseline prompt v1",
            )
            version_two = client.create_prompt(
                name=args.name,
                type="text",
                prompt=PROMPT_V2,
                labels=["candidate"],
                commit_message="CP2 candidate prompt v2",
            )
            print(f"Created {args.name!r}: baseline/production v{version_one.version}; candidate v{version_two.version}.")
            return 0

        if args.action == "promote-v2":
            client.update_prompt(name=args.name, version=2, new_labels=["candidate", "production"])
            print(f"Moved production to {args.name!r} v2; candidate remains on v2.")
            return 0

        client.update_prompt(name=args.name, version=1, new_labels=["baseline", "production"])
        print(f"Rolled production back to {args.name!r} v1; baseline remains on v1.")
        return 0
    except Exception as exc:
        print(f"Langfuse prompt operation failed ({type(exc).__name__}); no credentials were printed.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
