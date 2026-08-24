#!/usr/bin/env python3
"""OpenRouter companion CLI for Claude Code.

Subcommands:
  models      List free models (default) or all models (--all)
  leaderboard Heuristic-ranked leaderboard of free models
  status      Show details for one model ID
  usage       Show API key usage/limits (requires OPENROUTER_API_KEY)
  mark-tried  Mark a model as tried in local state (feeds reminders)
  tried       List tried/untried free models -> drives the session reminder
  monitor     Long-running watcher: logs catalog changes to logs/openrouter_monitor.jsonl

Notes:
  - The models catalog (https://openrouter.ai/api/v1/models) is PUBLIC, no key needed.
  - Usage/credits need OPENROUTER_API_KEY in the environment.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "https://openrouter.ai/api/v1"
REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = REPO_ROOT / ".claude" / "openrouter_state.json"
MONITOR_LOG = REPO_ROOT / "logs" / "openrouter_monitor.jsonl"

# Rough quality tiers used by `leaderboard` (heuristic, not official rankings).
# Points for the vendor behind the model — frontier labs first.
VENDOR_SCORE = {
    "deepseek": 90, "qwen": 85, "meta-llama": 80, "mistralai": 78,
    "google": 88, "openai": 95, "anthropic": 95, "moonshotai": 82,
    "z-ai": 80, "tngtech": 70, "nousresearch": 65, "cognitivecomputations": 60,
    "shisa-ai": 55, "rekaai": 60, "thudm": 62, "arliai": 58,
}


def _get(path: str, params: dict | None = None) -> dict:
    url = f"{BASE_URL}{path}"
    if params:
        from urllib.parse import urlencode

        url += "?" + urlencode(params)
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key:
        req.add_header("Authorization", f"Bearer {api_key}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def _is_free(model: dict) -> bool:
    p = model.get("pricing") or {}
    return float(p.get("prompt", "1")) == 0.0 and float(p.get("completion", "1")) == 0.0


def fetch_models() -> list[dict]:
    return _get("/models")["data"]


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"tried": {}}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def fmt_ctx(n) -> str:
    if not n:
        return "?"
    return f"{n // 1000}k"


def print_models(models: list[dict], sort_by_ctx: bool = True) -> None:
    rows = []
    for m in models:
        rows.append((
            m["id"],
            m.get("name", "").split(":")[-1].strip()[:44],
            fmt_ctx(m.get("context_length")),
            ",".join((m.get("supported_parameters") or [])[:6]),
        ))
    if sort_by_ctx:
        rows.sort(key=lambda r: r[0])
    w0 = max(len(r[0]) for r in rows) + 2
    print(f"{'MODEL ID'.ljust(w0)}{'NAME'.ljust(46)}{'CTX':>6}  PARAMS")
    for r in rows:
        print(f"{r[0].ljust(w0)}{r[1].ljust(46)}{r[2]:>6}  {r[3]}")


def cmd_models(args) -> None:
    models = fetch_models()
    free = [m for m in models if _is_free(m)]
    if args.all:
        print(f"All {len(models)} models ({len(free)} free):\n")
        print_models(sorted(models, key=lambda m: m["id"]))
    else:
        print(f"{len(free)} FREE models on OpenRouter right now:\n")
        print_models(free)


def cmd_leaderboard(args) -> None:
    """Heuristic ranking: vendor score + context length. Not an official metric."""
    models = [m for m in fetch_models() if _is_free(m)]

    def score(m: dict) -> tuple:
        vendor = m["id"].split("/")[0]
        v = VENDOR_SCORE.get(vendor, 50)
        ctx = m.get("context_length") or 0
        # Cap ctx credit at 200k so huge-context weak models don't dominate.
        return (v + min(ctx / 40000, 5), m["id"])

    ranked = sorted(models, key=score, reverse=True)
    state = load_state()
    tried = state.get("tried", {})
    print(
        "OpenRouter FREE-model leaderboard (heuristic: vendor tier + context window;\n"
        "not an official benchmark — verify on https://openrouter.ai/rankings)\n"
    )
    w = max(len(m["id"]) for m in ranked[: args.top]) + 2
    for i, m in enumerate(ranked[: args.top], 1):
        flag = " [tried]" if m["id"] in tried else ""
        modality = "img-in" if "image" in (m.get("architecture", {}) or {}).get("input_modalities", []) else ""
        extra = f" {modality}" if modality else ""
        print(f"{i:>2}. {m['id'].ljust(w)}{fmt_ctx(m.get('context_length')):>6} ctx{extra}{flag}")
    untried_top = [m["id"] for m in ranked[: args.top] if m["id"] not in tried]
    if untried_top:
        print("\nUntried in the top ranks: " + ", ".join(untried_top))


def cmd_status(args) -> None:
    matches = [m for m in fetch_models() if m["id"] == args.model_id]
    if not matches:
        close = [m["id"] for m in fetch_models() if args.model_id.lower() in m["id"].lower()]
        print(f"Not found: {args.model_id}", file=sys.stderr)
        if close:
            print("Did you mean:\n  " + "\n  ".join(close[:10]), file=sys.stderr)
        sys.exit(1)
    print(json.dumps(matches[0], indent=2))


def cmd_usage(args) -> None:
    if not os.environ.get("OPENROUTER_API_KEY"):
        print(
            "OPENROUTER_API_KEY is not set.\n"
            "Get a key at https://openrouter.ai/settings/keys and put it in your\n"
            "environment (or .env) to enable usage tracking.",
            file=sys.stderr,
        )
        sys.exit(1)
    info = _get("/auth/key")
    d = info.get("data", {})
    limit = d.get("limit")
    usage = d.get("usage", 0)
    remaining = (limit - usage) if isinstance(limit, (int, float)) else None
    print("API key usage:")
    print(f"  usage:     ${usage}")
    print(f"  limit:     {'$' + str(limit) if limit is not None else 'unlimited'}")
    if remaining is not None:
        print(f"  remaining: ${remaining:.2f}")
    print(f"  free-tier: {d.get('is_free_tier', '?')}")
    # Free-model daily allowance depends on lifetime credits ($10+ unlocks 1000/day).
    try:
        credits = _get("/credits")
        c = credits.get("data", {})
        print(f"  credits purchased: ${c.get('total_credits', 0)}")
        if float(c.get('total_credits', 0)) >= 10:
            print("  -> daily free-model cap: 1000 requests/day")
        else:
            print("  -> daily free-model cap: 50 requests/day "
                  "(top up $10 lifetime to unlock 1000/day)")
    except urllib.error.HTTPError:
        pass


def cmd_mark_tried(args) -> None:
    state = load_state()
    state.setdefault("tried", {})[args.model_id] = datetime.now(timezone.utc).isoformat()
    save_state(state)
    print(f"Marked tried: {args.model_id}")


def cmd_tried(args) -> None:
    state = load_state()
    tried = state.get("tried", {})
    free = [m["id"] for m in fetch_models() if _is_free(m)]
    untried = [mid for mid in free if mid not in tried]
    print(f"Free models: {len(free)} | tried: {len([t for t in tried if t in free])} | untried: {len(untried)}")
    if args.untried:
        for mid in untried:
            print(f"  - {mid}")


def cmd_monitor(args) -> None:
    """Long-running watcher: polls the catalog, logs additions/removals of
    free models and total counts. Ctrl+C to stop."""
    MONITOR_LOG.parent.mkdir(parents=True, exist_ok=True)

    def log(event: dict) -> None:
        event["ts"] = datetime.now(timezone.utc).isoformat()
        with MONITOR_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    log({"event": "monitor_start", "interval_s": args.interval})
    prev_free: set[str] | None = None
    while True:
        try:
            models = fetch_models()
            free_ids = {m["id"] for m in models if _is_free(m)}
            if prev_free is not None:
                added = sorted(free_ids - prev_free)
                removed = sorted(prev_free - free_ids)
                for mid in added:
                    log({"event": "free_model_added", "model": mid})
                    print(f"[+] NEW free model: {mid}", flush=True)
                for mid in removed:
                    log({"event": "free_model_removed", "model": mid})
                    print(f"[-] no longer free: {mid}", flush=True)
                if added or removed:
                    log({"event": "catalog_change",
                         "free_count": len(free_ids),
                         "added": added, "removed": removed})
                else:
                    log({"event": "poll_ok", "free_count": len(free_ids),
                         "total_count": len(models)})
            else:
                log({"event": "baseline", "free_count": len(free_ids),
                     "total_count": len(models)})
                print(f"Baseline: {len(models)} models, {len(free_ids)} free.", flush=True)
            prev_free = free_ids
        except Exception as exc:  # noqa: BLE001 — monitor must survive transient errors
            log({"event": "poll_error", "error": str(exc)[:200]})
            print(f"[!] poll error: {exc}", flush=True)
        time.sleep(args.interval)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("models", help="list free models (or --all)")
    p.add_argument("--all", action="store_true")
    p.set_defaults(func=cmd_models)

    p = sub.add_parser("leaderboard", help="ranked free models (heuristic)")
    p.add_argument("--top", type=int, default=15)
    p.set_defaults(func=cmd_leaderboard)

    p = sub.add_parser("status", help="details for one model ID")
    p.add_argument("model_id")
    p.set_defaults(func=cmd_status)

    sub.add_parser("usage", help="API-key usage & free-tier caps").set_defaults(func=cmd_usage)

    p = sub.add_parser("mark-tried", help="mark a model as tried")
    p.add_argument("model_id")
    p.set_defaults(func=cmd_mark_tried)

    p = sub.add_parser("tried", help="tried/untried summary")
    p.add_argument("--untried", action="store_true", help="list untried free models")
    p.set_defaults(func=cmd_tried)

    p = sub.add_parser("monitor", help="long-running catalog watcher")
    p.add_argument("--interval", type=int, default=900, help="seconds between polls (default 900)")
    p.set_defaults(func=cmd_monitor)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
