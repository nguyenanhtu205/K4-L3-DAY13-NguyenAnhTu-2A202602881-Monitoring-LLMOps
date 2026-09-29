from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.tracing import get_langfuse_client, tracing_enabled

EXPECTED = {
    "baseline": ("baseline", 1),
    "candidate": ("candidate", 2),
    "production-promoted": ("production", 2),
    "production-rollback": ("production", 1),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify prompt label/version evidence in Langfuse traces")
    parser.add_argument("--trace", action="append", required=True, help="stage=trace_id (repeat four times)")
    args = parser.parse_args()
    if not tracing_enabled():
        print("Langfuse tracing is disabled: configure personal project keys in .env first.")
        return 1

    client = get_langfuse_client()
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["stage", "trace_id", "correlation_id", "prompt_name", "prompt_label", "prompt_version", "model", "tokens_in", "tokens_out", "cost_usd"])
    all_valid = len(args.trace) == len(EXPECTED)
    for item in args.trace:
        stage, trace_id = item.split("=", 1)
        response = client.api.observations.get_many(
            trace_id=trace_id,
            fields="basic,metadata,model,usage,prompt",
            limit=20,
        )
        observations = response.data
        root = next((observation for observation in observations if observation.name == "lab-agent-run"), None)
        generation = next((observation for observation in observations if observation.type == "GENERATION"), None)
        metadata = root.metadata if root and isinstance(root.metadata, dict) else {}
        label, version = EXPECTED.get(stage, (None, None))
        valid = bool(
            stage in EXPECTED
            and root
            and generation
            and metadata.get("prompt_name") == "day13-chat"
            and metadata.get("prompt_label") == label
            and generation.prompt_version == version
            and generation.prompt_name == "day13-chat"
            and generation.model
            and generation.usage_details
            and generation.cost_details
        )
        all_valid = all_valid and valid
        writer.writerow([
            stage,
            trace_id,
            metadata.get("correlation_id", "missing"),
            metadata.get("prompt_name", "missing"),
            metadata.get("prompt_label", "missing"),
            generation.prompt_version if generation else "missing",
            generation.model if generation else "missing",
            generation.usage_details.get("input", "") if generation and generation.usage_details else "",
            generation.usage_details.get("output", "") if generation and generation.usage_details else "",
            generation.cost_details.get("total", "") if generation and generation.cost_details else "",
        ])

    path = ROOT / "submission" / "evidence" / "cp2-prompt-versioning.txt"
    path.write_text(output.getvalue(), encoding="utf-8")
    print(f"Prompt trace metadata valid: {all_valid}; summary: {path}")
    return 0 if all_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
