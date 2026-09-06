"""Validate every preset in domain-configs/presets against AgentVersionPayload."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from domain_config_schema import AgentVersionPayload  # noqa: E402

presets_dir = ROOT / "domain-configs" / "presets"
ok = True
for p in sorted(presets_dir.glob("*.json")):
    data = json.loads(p.read_text(encoding="utf-8"))
    try:
        AgentVersionPayload(**data["version_payload"])
        print(f"OK   {p.name:<32} {data['name']}")
    except Exception as exc:  # noqa: BLE001
        ok = False
        print(f"FAIL {p.name}: {exc}")
sys.exit(0 if ok else 1)
