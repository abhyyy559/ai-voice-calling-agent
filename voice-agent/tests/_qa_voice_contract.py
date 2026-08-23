"""Shared helpers for Lane E voice-agent contract suites (Lane B runtime).

Lane B module paths may shift while lanes land concurrently, so symbol lookup
tries several candidate locations and reports every attempt on failure. The
``app`` package name collides between /backend and /voice-agent, so backend
entries are purged from ``sys.modules`` before importing Lane B code.
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
VOICE_AGENT_DIR: Path = PROJECT_ROOT / "voice-agent"
ABSENT_STUDENT_PATH: Path = PROJECT_ROOT / "domain-configs" / "absent-student.json"

for _p in (str(VOICE_AGENT_DIR), str(PROJECT_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def load_agent_config() -> dict[str, Any]:
    """Load absent-student.json with both disclosure key spellings populated."""
    with ABSENT_STUDENT_PATH.open(encoding="utf-8") as fh:
        config: dict[str, Any] = json.load(fh)
    disclosure = config.get("disclosure_script") or config.get("mandatory_disclosure") or ""
    config["mandatory_disclosure"] = disclosure
    config["disclosure_script"] = disclosure
    return config


def normalize(text: str) -> str:
    return " ".join(str(text).lower().split())


def _purge_backend_app_modules() -> None:
    for name in [n for n in list(sys.modules) if n == "app" or n.startswith("app.")]:
        del sys.modules[name]


def _prefer_voice_agent_app_package() -> None:
    """Ensure ``import app.*`` resolves to /voice-agent even when another lane
    put its own ``app`` package first on sys.path (both lanes ship one)."""
    if str(VOICE_AGENT_DIR) in sys.path:
        sys.path.remove(str(VOICE_AGENT_DIR))
    sys.path.insert(0, str(VOICE_AGENT_DIR))
    _purge_backend_app_modules()


def locate_symbols(
    attr_names: list[str],
    module_names: list[str],
) -> tuple[Optional[Any], str]:
    """First matching ``module.attr`` wins; otherwise return why every try failed."""
    failures: list[str] = []
    _prefer_voice_agent_app_package()
    for mod_name in module_names:
        try:
            mod = importlib.import_module(mod_name)
        except Exception as exc:
            failures.append(f"import {mod_name}: {type(exc).__name__}: {exc}")
            continue
        for attr in attr_names:
            obj = getattr(mod, attr, None)
            if obj is not None:
                return obj, ""
            failures.append(f"{mod_name}.{attr}: missing")
    return None, "; ".join(failures)


class FakeBackendClient:
    """Async in-memory stand-in for Lane B's BackendClient (frozen interface).

    Frozen methods (plan LANE B): get_agent_config(version_id),
    post_turns(call_id, turns), post_fields(...), post_complete(...).
    Capture lists are plain sync structures for assertions.
    """

    def __init__(self) -> None:
        self.configs: dict[Any, dict[str, Any]] = {}
        self.turns: list[tuple[Any, list[dict[str, Any]]]] = []
        self.fields: list[tuple[Any, list[dict[str, Any]]]] = []
        self.completions: list[dict[str, Any]] = []

    async def get_agent_config(self, version_id: Any) -> Optional[dict[str, Any]]:
        return self.configs.get(version_id)

    async def post_turns(self, call_id: Any, turns: list[dict[str, Any]]) -> bool:
        self.turns.append((call_id, [dict(t) for t in turns]))
        return True

    async def post_fields(self, call_id: Any, fields: Any) -> bool:
        rows = fields if isinstance(fields, list) else [fields]
        self.fields.append((call_id, [dict(f) for f in rows]))
        return True

    async def post_complete(
        self,
        call_id: Any,
        *args: Any,
        status: str = "completed",
        error: Optional[str] = None,
        summary: Optional[str] = None,
    ) -> bool:
        record = {
            "call_id": call_id,
            "status": status,
            "error": error,
            "summary": summary,
        }
        if args:
            record["args"] = args
        self.completions.append(record)
        return True
