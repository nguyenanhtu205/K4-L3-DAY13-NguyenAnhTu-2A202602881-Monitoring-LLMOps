from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.tracing import get_langfuse_client, tracing_enabled


def main() -> int:
    if not tracing_enabled():
        print("Langfuse tracing is disabled: configure personal project keys in .env first.")
        return 1

    summary_path = ROOT / "submission" / "evidence" / "cp2-generated-traces.csv"
    with summary_path.open(encoding="utf-8", newline="") as handle:
        traces = list(csv.DictReader(handle))
    client = get_langfuse_client()
    report = ["trace_id,correlation_id,root,retriever,generation,model,prompt,version,usage_cost,pii_capture"]
    all_valid = len(traces) >= 10
    for trace in traces:
        trace_id = trace["trace_id"]
        response = client.api.observations.get_many(
            trace_id=trace_id,
            limit=20,
            fields="basic,metadata,model,usage,prompt,io",
        )
        observations = response.data
        root = next((item for item in observations if item.name == "lab-agent-run"), None)
        retriever = next((item for item in observations if item.name == "document-retrieval"), None)
        generation = next((item for item in observations if item.name == "fake-llm-generation"), None)
        correlation_id = trace["correlation_id"]
        metadata = root.metadata if root and isinstance(root.metadata, dict) else {}
        child_correlation_matches = all(
            item is None or item.metadata.get("correlation_id") == correlation_id
            for item in (root, retriever, generation)
        )
        parentage_ok = bool(
            root
            and root.parent_observation_id is None
            and retriever
            and retriever.parent_observation_id == root.id
            and generation
            and generation.parent_observation_id == root.id
        )
        usage_cost_ok = bool(
            generation
            and generation.model
            and generation.prompt_name == "day13-chat"
            and generation.usage_details
            and generation.cost_details
        )
        any_io_capture = any(
            item and (item.input is not None or item.output is not None)
            for item in (root, retriever, generation)
        )
        context_ok = bool(
            root
            and re.fullmatch(r"[0-9a-f]{12}", root.user_id or "")
            and root.session_id
            and root.environment
            and metadata.get("feature")
            and metadata.get("model")
            and metadata.get("correlation_id") == correlation_id
        )
        prompt_ok = bool(
            metadata.get("prompt_source") == "langfuse"
            and metadata.get("prompt_name") == "day13-chat"
            and generation
            and metadata.get("prompt_version") == generation.prompt_version
        )
        valid = bool(
            parentage_ok
            and child_correlation_matches
            and context_ok
            and usage_cost_ok
            and prompt_ok
            and not any_io_capture
        )
        all_valid = all_valid and valid
        report.append(
            ",".join(
                [
                    trace_id,
                    correlation_id,
                    "yes" if root else "no",
                    "yes" if retriever else "no",
                    "yes" if generation else "no",
                    generation.model if generation and generation.model else "missing",
                    generation.prompt_name if generation and generation.prompt_name else "missing",
                    str(generation.prompt_version) if generation and generation.prompt_version is not None else "missing",
                    "yes" if usage_cost_ok else "no",
                    "yes" if any_io_capture else "no",
                ]
            )
        )

    report.append(f"verified={sum(1 for row in report[1:] if row.split(',')[2:5] == ['yes','yes','yes'])}/{len(traces)}")
    output_path = ROOT / "submission" / "evidence" / "cp2-trace-validation.txt"
    output_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Validated {len(traces)} trace summaries; all criteria pass: {all_valid}; output: {output_path}")
    return 0 if all_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
