from __future__ import annotations

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
    if not tracing_enabled():
        print("Langfuse tracing is disabled: configure personal project keys in .env first.")
        return 1

    agent = LabAgent()
    results = []
    for index in range(1, 11):
        correlation_id = f"req-{uuid.uuid4().hex[:8]}"
        result = agent.run(
            user_id=f"cp2-user-{index:02d}",
            feature="qa",
            session_id=f"cp2-session-{index:02d}",
            message="How do metrics, logs, and traces help investigate latency?",
            correlation_id=correlation_id,
        )
        results.append((index, result.trace_id, correlation_id, result.tokens_in, result.tokens_out, result.cost_usd))

    get_langfuse_client().flush()
    output = ["index,trace_id,correlation_id,tokens_in,tokens_out,cost_usd"]
    output.extend(
        f"{index},{trace_id or ''},{correlation_id},{tokens_in},{tokens_out},{cost_usd:.6f}"
        for index, trace_id, correlation_id, tokens_in, tokens_out, cost_usd in results
    )
    evidence_path = ROOT / "submission" / "evidence" / "cp2-generated-traces.csv"
    evidence_path.write_text("\n".join(output) + "\n", encoding="utf-8")
    print(f"Generated {len(results)} traces; summary: {evidence_path}")
    return 0 if all(trace_id for _, trace_id, *_ in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
