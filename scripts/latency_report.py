"""Per-turn latency report vs NFR-1 targets.

Reads per-turn latency metrics (stt_final_ms / llm_first_token_ms /
tts_first_audio_ms / e2e_ms) out of the calls database and prints a
count/median/P95 table. NFR targets: median <=900ms, P95 <=1.5s
end-of-speech-to-agent-speech.

Exit codes:
    0  report produced (including "no data yet" / "table not ready")
    1  gate failed: >=10 e2e samples AND P95(e2e_ms) > 1500ms
    2  configuration/connection problem (no DATABASE_URL, driver missing,
       database unreachable)

Usage:
    python scripts/latency_report.py [--json] [--database-url URL]

Database resolution order: --database-url arg > DATABASE_URL env var >
backend Settings default. Credentials are never echoed.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

METRIC_COLUMNS: tuple[str, ...] = (
    "stt_final_ms",
    "llm_first_token_ms",
    "tts_first_audio_ms",
    "e2e_ms",
)
TABLE_CANDIDATES: tuple[str, ...] = ("transcript_turns", "turns", "transcripts")
TARGET_MEDIAN_MS: float = 900.0
TARGET_P95_MS: float = 1500.0
GATE_METRIC: str = "e2e_ms"
GATE_MIN_SAMPLES: int = 10


def percentile(values: list[float], pct: float) -> float:
    """Linear-interpolated percentile on an already-sorted list."""
    if not values:
        raise ValueError("percentile of empty list")
    if len(values) == 1:
        return values[0]
    rank = (len(values) - 1) * (pct / 100.0)
    lower = int(rank)
    upper = min(lower + 1, len(values) - 1)
    fraction = rank - lower
    return values[lower] + (values[upper] - values[lower]) * fraction


def mask_database_url(url: str) -> str:
    return re.sub(r"(//[^:/@]+):[^@]*@", r"\1:***@", url)


def resolve_database_url(explicit: Optional[str]) -> tuple[str, str]:
    """Return (database_url, source_description); never raises for missing env alone."""
    if explicit:
        return explicit, "--database-url argument"
    env_url = os.environ.get("DATABASE_URL", "").strip()
    if env_url:
        return env_url, "DATABASE_URL environment variable"
    try:
        from app.config import get_settings

        return get_settings().database_url, "backend Settings default"
    except Exception as exc:
        raise RuntimeError(
            f"no DATABASE_URL set and backend settings unavailable ({exc}); "
            "pass --database-url or export DATABASE_URL"
        ) from exc


def load_metric_values(database_url: str) -> tuple[dict[str, list[float]], str]:
    """Fetch metric columns from whichever turn table exists.

    Returns (values_by_metric, human-readable source note). Raises RuntimeError
    only when the database itself cannot be opened; a missing turn table or
    missing latency columns is a normal pre-migration state reported via note.
    """
    try:
        from sqlalchemy import create_engine, inspect, text
    except Exception as exc:
        raise RuntimeError(f"sqlalchemy not installed ({exc}); pip install sqlalchemy") from exc

    try:
        engine = create_engine(database_url)
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
    except Exception as exc:
        raise RuntimeError(f"cannot connect to database ({type(exc).__name__}: {exc})") from exc

    def columns_of(table: str) -> set[str]:
        return {col["name"] for col in inspector.get_columns(table)}

    chosen: Optional[tuple[str, list[str]]] = None
    for table in TABLE_CANDIDATES:
        if table not in tables:
            continue
        cols = columns_of(table)
        present = [m for m in METRIC_COLUMNS if m in cols]
        if present:
            chosen = (table, present)
            break
    if chosen is None:
        for table in sorted(tables):
            cols = columns_of(table)
            present = [m for m in METRIC_COLUMNS if m in cols]
            if len(present) >= 2:
                chosen = (table, present)
                break
    empty: dict[str, list[float]] = {m: [] for m in METRIC_COLUMNS}
    if chosen is None:
        note = (
            "turn-latency table not ready yet: looked for tables "
            f"{list(TABLE_CANDIDATES)} with any of {list(METRIC_COLUMNS)}; "
            f"tables found: {sorted(tables) or 'none'}. Run Lane A's migration first."
        )
        return empty, note

    table, present = chosen
    order_col = next(
        (c for c in ("turn_index", "id", "created_at") if c in columns_of(table)), None
    )
    select_cols = ", ".join(present + ([order_col] if order_col else []))
    statement = text(f"SELECT {select_cols} FROM {table}")

    with engine.connect() as conn:
        rows = conn.execute(statement).fetchall()

    values: dict[str, list[float]] = {m: [] for m in METRIC_COLUMNS}
    for row in rows:
        for offset, metric in enumerate(present):
            raw = row[offset]
            if isinstance(raw, bool):
                continue
            if isinstance(raw, (int, float)):
                values[metric].append(float(raw))

    note = f"source: table '{table}', columns {present}, rows scanned {len(rows)}"
    return values, note


def summarize(values: dict[str, list[float]]) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for metric, samples in values.items():
        ordered = sorted(samples)
        count = len(ordered)
        median = percentile(ordered, 50) if ordered else None
        p95 = percentile(ordered, 95) if ordered else None
        median_ok = median is not None and median <= TARGET_MEDIAN_MS
        p95_ok = p95 is not None and p95 <= TARGET_P95_MS
        summary[metric] = {
            "count": count,
            "median_ms": round(median, 1) if median is not None else None,
            "p95_ms": round(p95, 1) if p95 is not None else None,
            "target_median_ms": TARGET_MEDIAN_MS,
            "target_p95_ms": TARGET_P95_MS,
            "median_pass": median_ok,
            "p95_pass": p95_ok,
        }
    return summary


def render_table(summary: dict[str, dict[str, Any]], note: str) -> str:
    header = (
        f"{'metric':<20} {'count':>6} {'median(ms)':>12} {'p95(ms)':>10} "
        f"{'t-med':>7} {'t-p95':>7} {'status':>8}"
    )
    lines = ["Latency report (NFR-1: median <=900ms, P95 <=1500ms)", header, "-" * len(header)]
    for metric, stats in summary.items():
        if stats["count"] == 0:
            status = "NO DATA"
            median_s = p95_s = "-"
        else:
            median_s = f"{stats['median_ms']:.1f}"
            p95_s = f"{stats['p95_ms']:.1f}"
            status = "PASS" if stats["median_pass"] and stats["p95_pass"] else "FAIL"
        lines.append(
            f"{metric:<20} {stats['count']:>6} {median_s:>12} {p95_s:>10} "
            f"{TARGET_MEDIAN_MS:>7.0f} {TARGET_P95_MS:>7.0f} {status:>8}"
        )
    lines.append(note)
    e2e = summary[GATE_METRIC]
    if e2e["count"] < GATE_MIN_SAMPLES:
        lines.append(
            f"GATE: skipped ({e2e['count']} e2e samples < {GATE_MIN_SAMPLES}; "
            "exit code stays 0)"
        )
    elif e2e["p95_ms"] is not None and e2e["p95_ms"] > TARGET_P95_MS:
        lines.append(
            f"GATE: FAIL — e2e P95 {e2e['p95_ms']}ms exceeds {TARGET_P95_MS:.0f}ms "
            f"on {e2e['count']} samples (exit code 1)"
        )
    else:
        lines.append(
            f"GATE: PASS — e2e P95 {e2e['p95_ms']}ms within {TARGET_P95_MS:.0f}ms "
            f"on {e2e['count']} samples"
        )
    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Per-turn latency report vs NFR targets")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON instead of a table")
    parser.add_argument("--database-url", default=None, help="override DATABASE_URL")
    args = parser.parse_args(argv)

    try:
        database_url, url_source = resolve_database_url(args.database_url)
    except RuntimeError as exc:
        print(f"latency-report: {exc}", file=sys.stderr)
        return 2

    try:
        values, note = load_metric_values(database_url)
    except RuntimeError as exc:
        print(f"latency-report: {exc}", file=sys.stderr)
        return 2

    summary = summarize(values)
    e2e = summary[GATE_METRIC]
    gate_failed = e2e["count"] >= GATE_MIN_SAMPLES and (
        e2e["p95_ms"] is not None and e2e["p95_ms"] > TARGET_P95_MS
    )

    if args.json:
        payload = {
            "database": mask_database_url(database_url),
            "database_source": url_source,
            "note": note,
            "targets": {"median_ms": TARGET_MEDIAN_MS, "p95_ms": TARGET_P95_MS},
            "metrics": summary,
            "gate": {
                "metric": GATE_METRIC,
                "min_samples": GATE_MIN_SAMPLES,
                "samples": e2e["count"],
                "failed": gate_failed,
            },
        }
        print(json.dumps(payload, indent=2))
    else:
        print(render_table(summary, note))
    return 1 if gate_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
