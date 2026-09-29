from __future__ import annotations

import html
import json
import math
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "data" / "logs.jsonl"
CONFIG_PATH = ROOT / "config" / "dashboard.yaml"
OUTPUT_PATH = ROOT / "data" / "dashboard.html"


def percentile(values: list[float], percentile_value: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile_value / 100
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def load_records() -> list[dict[str, Any]]:
    if not LOG_PATH.exists():
        return []
    records = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
            record["_time"] = datetime.fromisoformat(record["ts"].replace("Z", "+00:00"))
            records.append(record)
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            continue
    return records


def svg_chart(
    values: list[float],
    *,
    unit: str,
    threshold: float | None = None,
    labels: list[str] | None = None,
) -> str:
    width, height = 760, 190
    left, right, top, bottom = 54, 14, 12, 34
    plot_width, plot_height = width - left - right, height - top - bottom
    if not values:
        return f'<div class="empty">No samples in the selected 60 minute window ({html.escape(unit)}).</div>'

    max_value = max([*values, threshold or 0, 1]) * 1.12
    points = []
    for index, value in enumerate(values):
        x = left + (plot_width * index / max(1, len(values) - 1))
        y = top + plot_height * (1 - value / max_value)
        points.append(f"{x:.1f},{y:.1f}")
    polyline = " ".join(points)
    grid = []
    for step in range(5):
        y = top + plot_height * step / 4
        value = max_value * (1 - step / 4)
        grid.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" class="gridline"/>'
            f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" class="axis">{value:.1f}</text>'
        )
    threshold_line = ""
    if threshold is not None:
        y = top + plot_height * (1 - min(threshold, max_value) / max_value)
        threshold_line = (
            f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" class="threshold"/>'
            f'<text x="{width-right-3}" y="{y-5:.1f}" text-anchor="end" class="threshold-label">limit {threshold:g}</text>'
        )
    x_labels = ""
    if labels:
        chosen = sorted({0, len(labels) // 2, len(labels) - 1})
        x_labels = "".join(
            f'<text x="{left + plot_width * index / max(1, len(labels)-1):.1f}" y="{height-8}" text-anchor="middle" class="axis">{html.escape(labels[index])}</text>'
            for index in chosen
        )
    return (
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(unit)} trend">'
        f'{"".join(grid)}{threshold_line}'
        f'<polyline points="{polyline}" class="series"/>'
        f'{x_labels}</svg>'
    )


def card(title: str, unit: str, summary: str, chart: str, threshold: str) -> str:
    return (
        '<section class="card">'
        f'<div class="card-head"><h2>{html.escape(title)}</h2><span>{html.escape(unit)}</span></div>'
        f'<div class="summary">{summary}</div>{chart}'
        f'<div class="limit">Threshold / SLO: {html.escape(threshold)}</div>'
        '</section>'
    )


def build_dashboard(now: datetime | None = None) -> str:
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))["dashboard"]
    now = now or datetime.now(timezone.utc)
    start = now - timedelta(minutes=config["time_range_minutes"])
    records = [record for record in load_records() if start <= record["_time"] <= now]
    requests = [record for record in records if record.get("event") == "request_received"]
    failures = [record for record in records if record.get("event") == "request_failed"]
    responses = [record for record in records if record.get("event") == "response_sent"]
    latency = [float(record["latency_ms"]) for record in responses if record.get("latency_ms") is not None]
    ttft = [float(record["ttft_ms"]) for record in responses if record.get("ttft_ms") is not None]

    latency_panel = config["panels"][0]
    threshold_latency = float(latency_panel["threshold"]["value"])
    latency_summary = (
        f'P50 <b>{percentile(latency, 50) or 0:.0f}</b> · '
        f'P95 <b>{percentile(latency, 95) or 0:.0f}</b> · '
        f'P99 <b>{percentile(latency, 99) or 0:.0f}</b> · '
        f'TTFT P95 <b>{percentile(ttft, 95) or 0:.0f}</b>'
    )
    cards = [card(
        latency_panel["title"], "ms", latency_summary,
        svg_chart(latency, unit="ms", threshold=threshold_latency), f'P95 ≤ {threshold_latency:g} ms',
    )]

    per_minute: Counter[str] = Counter(record["_time"].strftime("%H:%M") for record in requests)
    minute_labels = [(start + timedelta(minutes=index)).strftime("%H:%M") for index in range(60)]
    request_counts = [float(per_minute[label]) for label in minute_labels]
    total_requests = len(requests)
    rate = total_requests / max(1, config["time_range_minutes"])
    cards.append(card(
        config["panels"][1]["title"], "requests/minute",
        f'{total_requests} requests · <b>{rate:.2f}</b> average requests/minute',
        svg_chart(request_counts, unit="requests/minute", threshold=float(config["panels"][1]["threshold"]["value"]), labels=minute_labels),
        f'≥ {config["panels"][1]["threshold"]["value"]} requests/minute',
    ))

    failed_count = len(failures)
    error_rate = failed_count * 100 / total_requests if total_requests else 0.0
    tool_records = [record for record in records if record.get("tool_success") is not None]
    retrieval_success = sum(record.get("tool_success") is True for record in tool_records) * 100 / len(tool_records) if tool_records else 0.0
    error_types = Counter(str(record.get("error_type", "unknown")) for record in failures)
    error_summary = (
        f'Error rate <b>{error_rate:.1f}%</b> ({failed_count}/{total_requests}) · '
        f'Retrieval success <b>{retrieval_success:.1f}%</b><br>'
        f'Breakdown: {html.escape(", ".join(f"{key}={value}" for key, value in error_types.items()) or "no errors")}'
    )
    request_per_minute: Counter[str] = Counter(record["_time"].strftime("%H:%M") for record in requests)
    failures_per_minute: Counter[str] = Counter(record["_time"].strftime("%H:%M") for record in failures)
    errors_by_minute = [
        failures_per_minute[label] * 100 / request_per_minute[label]
        if request_per_minute[label]
        else 0.0
        for label in minute_labels
    ]
    cards.append(card(
        config["panels"][2]["title"], "%", error_summary,
        svg_chart(errors_by_minute, unit="error rate percent", threshold=float(config["panels"][2]["threshold"]["value"]), labels=minute_labels),
        f'error rate ≤ {config["panels"][2]["threshold"]["value"]}% · retrieval success ≥ 90%',
    ))

    cost_per_minute: defaultdict[str, float] = defaultdict(float)
    for record in responses:
        cost_per_minute[record["_time"].strftime("%H:%M")] += float(record.get("cost_usd", 0))
    costs = [cost_per_minute[label] for label in minute_labels]
    total_cost = sum(costs)
    cards.append(card(
        config["panels"][3]["title"], "USD", f'Total window cost <b>${total_cost:.6f}</b>',
        svg_chart(costs, unit="USD/minute"), f'total ≤ ${config["panels"][3]["threshold"]["value"]:g}',
    ))

    input_tokens = sum(int(record.get("tokens_in", 0)) for record in responses)
    output_tokens = sum(int(record.get("tokens_out", 0)) for record in responses)
    cards.append(card(
        config["panels"][4]["title"], "tokens", f'Input <b>{input_tokens:,}</b> · Output <b>{output_tokens:,}</b>',
        svg_chart([float(input_tokens), float(output_tokens)], unit="tokens", labels=["input", "output"]),
        f'total ≤ {config["panels"][4]["threshold"]["value"]:,} tokens',
    ))

    quality_values = [float(record["quality_score"]) for record in responses if record.get("quality_score") is not None]
    mean_quality = sum(quality_values) / len(quality_values) if quality_values else 0.0
    cards.append(card(
        config["panels"][5]["title"], "score (0–1)", f'Mean quality proxy <b>{mean_quality:.2f}</b>',
        svg_chart(quality_values, unit="score", threshold=float(config["panels"][5]["threshold"]["value"])),
        f'mean ≥ {config["panels"][5]["threshold"]["value"]:.2f}',
    ))

    range_text = f'{start.strftime("%Y-%m-%d %H:%M UTC")} – {now.strftime("%Y-%m-%d %H:%M UTC")}'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="{config["refresh_seconds"]}">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(config["title"])}</title>
<style>
:root {{ color-scheme: dark; font-family: Segoe UI, Arial, sans-serif; background:#0b1020; color:#e5e7eb; }}
body {{ margin:0; padding:28px; }} header {{ display:flex; justify-content:space-between; align-items:end; gap:18px; margin-bottom:22px; }}
h1 {{ font-size:24px; margin:0 0 6px; }} .range,.meta {{ color:#9ca3af; font-size:13px; }}
.layout {{ display:grid; grid-template-columns:repeat(2,minmax(360px,1fr)); gap:16px; }}
.card {{ background:#151c30; border:1px solid #29334b; border-radius:12px; padding:16px; min-width:0; }}
.card-head {{ display:flex; align-items:center; justify-content:space-between; gap:12px; }} h2 {{ font-size:16px; margin:0; }} .card-head span {{ color:#a5b4fc; font-size:12px; }}
.summary {{ min-height:42px; color:#aeb9ca; font-size:13px; line-height:1.7; margin-top:12px; }} .summary b {{ color:#fff; }}
svg {{ width:100%; height:auto; overflow:visible; }} .gridline {{ stroke:#29334b; stroke-width:1; }} .axis {{ fill:#8793a8; font-size:10px; }}
.series {{ fill:none; stroke:#8b9cff; stroke-width:3; stroke-linecap:round; stroke-linejoin:round; }}
.threshold {{ stroke:#f59e0b; stroke-width:1.5; stroke-dasharray:6 5; }} .threshold-label {{ fill:#fbbf24; font-size:10px; }}
.limit {{ color:#fbbf24; font-size:12px; border-top:1px solid #29334b; padding-top:10px; margin-top:5px; }} .empty {{ height:100px; display:grid; place-items:center; color:#8793a8; }}
@media(max-width:850px) {{ .layout {{ grid-template-columns:1fr; }} header {{ align-items:start; flex-direction:column; }} }}
</style></head><body><header><div><h1>{html.escape(config["title"])}</h1><div class="range">Time range: last {config["time_range_minutes"]} minutes · {html.escape(range_text)}</div></div><div class="meta">Auto refresh: {config["refresh_seconds"]}s · Source: data/logs.jsonl · {len(records)} records</div></header>
<main class="layout">{"".join(cards)}</main></body></html>'''


def main() -> None:
    parser = argparse.ArgumentParser(description="Local six-panel LLMOps dashboard")
    parser.add_argument("--serve", action="store_true", help="Serve a live-refreshing dashboard on localhost")
    parser.add_argument("--port", type=int, default=8050)
    args = parser.parse_args()
    if args.serve:
        from http.server import BaseHTTPRequestHandler, HTTPServer

        class DashboardHandler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                document = build_dashboard().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(document)))
                self.end_headers()
                self.wfile.write(document)

            def log_message(self, format: str, *args: Any) -> None:
                return

        print(f"Dashboard at http://127.0.0.1:{args.port} (refreshes from logs every 30 seconds)")
        HTTPServer(("127.0.0.1", args.port), DashboardHandler).serve_forever()
        return

    OUTPUT_PATH.write_text(build_dashboard(), encoding="utf-8")
    print(f"Dashboard written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
