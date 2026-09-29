from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.agent import LabAgent
from app.tracing import get_langfuse_client, tracing_enabled


def main() -> int:
    parser = argparse.ArgumentParser(description="Create one prompt-version trace in the personal Langfuse project")
    parser.add_argument("--label", choices=("baseline", "candidate", "production"), required=True)
    args = parser.parse_args()
    if not tracing_enabled():
        print("Langfuse tracing is disabled: configure personal project keys in .env first.")
        return 1

    os.environ["LANGFUSE_PROMPT_LABEL"] = args.label
    correlation_id = f"req-{uuid.uuid4().hex[:8]}"
    result = LabAgent().run(
        user_id="cp2-demo-user",
        feature="qa",
        session_id="cp2-prompt-check",
        message="How do metrics, logs, and traces help investigate latency?",
        correlation_id=correlation_id,
    )
    get_langfuse_client().flush()
    print(
        f"label={args.label} trace_id={result.trace_id or 'unavailable'} "
        f"correlation_id={correlation_id} model=claude-sonnet-4-5 "
        f"tokens={result.tokens_in}/{result.tokens_out} cost_usd={result.cost_usd:.6f}"
    )
    return 0 if result.trace_id else 1


if __name__ == "__main__":
    raise SystemExit(main())
