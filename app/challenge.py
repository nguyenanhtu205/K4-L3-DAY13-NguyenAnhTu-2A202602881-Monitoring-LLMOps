from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .incidents import STATE


REQUIRED_QUERY_FIELDS = {"user_id", "session_id", "feature", "message"}
EXPECTED_COHORT = "K4"
EXPECTED_CHALLENGE_ID = "day13-k4-l3a-monitoring-llmops-v1"


@dataclass(frozen=True)
class ChallengeConfig:
    cohort: str
    challenge_id: str
    incident: str
    seed: int
    affected_feature: str
    latency_threshold_ms: int
    queries: tuple[dict[str, str], ...]


def _require_text(payload: dict[str, Any], field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} phải là chuỗi không rỗng")
    return value.strip()


def load_challenge(path: str | Path = "config/challenge.json") -> ChallengeConfig:
    challenge_path = Path(path)
    if not challenge_path.exists():
        raise FileNotFoundError(
            f"{challenge_path} chưa được Lab Coach release. "
            "Hãy tiếp tục phần practice và chờ thông báo."
        )

    try:
        payload = json.loads(challenge_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("challenge.json không phải JSON hợp lệ") from exc

    if not isinstance(payload, dict):
        raise ValueError("challenge.json phải chứa một JSON object")

    cohort = _require_text(payload, "cohort")
    if cohort != EXPECTED_COHORT:
        raise ValueError(f"challenge không dành cho cohort {EXPECTED_COHORT}: {cohort}")

    challenge_id = _require_text(payload, "challenge_id")
    if challenge_id != EXPECTED_CHALLENGE_ID:
        raise ValueError(
            f"challenge_id không khớp lớp K4-L3A: {challenge_id!r}; "
            f"mong đợi {EXPECTED_CHALLENGE_ID!r}"
        )

    incident = _require_text(payload, "incident")
    if incident not in STATE:
        raise ValueError(f"incident không hợp lệ: {incident}")

    seed = payload.get("seed")
    if not isinstance(seed, int):
        raise ValueError("seed phải là số nguyên")

    latency_threshold_ms = payload.get("latency_threshold_ms")
    if not isinstance(latency_threshold_ms, int) or latency_threshold_ms <= 0:
        raise ValueError("latency_threshold_ms phải là số nguyên dương")

    raw_queries = payload.get("queries")
    if not isinstance(raw_queries, list) or not raw_queries:
        raise ValueError("queries phải là danh sách không rỗng")

    queries: list[dict[str, str]] = []
    for index, query in enumerate(raw_queries):
        if not isinstance(query, dict) or not REQUIRED_QUERY_FIELDS.issubset(query):
            raise ValueError(f"queries[{index}] thiếu trường bắt buộc")
        normalized = {field: query[field] for field in REQUIRED_QUERY_FIELDS}
        if any(not isinstance(value, str) or not value.strip() for value in normalized.values()):
            raise ValueError(f"queries[{index}] phải chứa các chuỗi không rỗng")
        queries.append(normalized)

    affected_feature = _require_text(payload, "affected_feature")
    if any(query["feature"] != affected_feature for query in queries):
        raise ValueError("mọi query phải thuộc affected_feature của challenge")

    return ChallengeConfig(
        cohort=cohort,
        challenge_id=challenge_id,
        incident=incident,
        seed=seed,
        affected_feature=affected_feature,
        latency_threshold_ms=latency_threshold_ms,
        queries=tuple(queries),
    )


def resolve_incident(
    explicit_scenario: str | None,
    challenge_path: str | Path = "config/challenge.json",
) -> str:
    if explicit_scenario is not None:
        if explicit_scenario not in STATE:
            raise ValueError(f"incident không hợp lệ: {explicit_scenario}")
        return explicit_scenario
    return load_challenge(challenge_path).incident


def ordered_queries(challenge: ChallengeConfig) -> list[dict[str, str]]:
    queries = [dict(query) for query in challenge.queries]
    random.Random(challenge.seed).shuffle(queries)
    return queries
