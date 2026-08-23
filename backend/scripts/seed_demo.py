"""Demo seed script — creates a demo tenant ready to explore the platform.

Usage (from backend/):  python scripts/seed_demo.py

Creates (idempotently):
- organization "Demo University" (slug demo-university)
- owner user demo@example.com / demo1234
- agent "Absent Student Follow-up" with v1 built from
  domain-configs/absent-student.json
- draft campaign pinning that version, with 5 sample contacts

The seed never places calls and contains no secrets.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import inspect, select  # noqa: E402

from app.auth import hash_password  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.database import init_db  # noqa: E402
from app.models import Agent, AgentVersion, Campaign, Contact, Organization, User  # noqa: E402
from domain_config_schema import validate_agent_version_payload  # noqa: E402

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demo1234"

SAMPLE_CONTACTS: list[dict[str, Any]] = [
    {
        "name": "Ravi Sharma",
        "phone": "+919000000001",
        "custom_fields": {"student_name": "Aarav Sharma", "class": "10-A"},
    },
    {
        "name": "Priya Patel",
        "phone": "+919000000002",
        "custom_fields": {"student_name": "Ishaan Patel", "class": "9-B"},
    },
    {
        "name": "Sunita Reddy",
        "phone": "+919000000003",
        "custom_fields": {"student_name": "Ananya Reddy", "class": "11-C"},
    },
    {
        "name": "Mohan Iyer",
        "phone": "+919000000004",
        "custom_fields": {"student_name": "Karthik Iyer", "class": "12-A"},
    },
    {
        "name": "Fatima Khan",
        "phone": "+919000000005",
        "custom_fields": {"student_name": "Zoya Khan", "class": "10-B"},
    },
]


def _alembic_upgrade_head(database_url: str) -> None:
    """Apply migrations programmatically when the schema is missing."""
    from alembic import command
    from alembic.config import Config

    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    cfg.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(cfg, "head")


def _load_absent_student_config() -> dict[str, Any]:
    path = PROJECT_ROOT / "domain-configs" / "absent-student.json"
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _version_payload_from_config(config: dict[str, Any]) -> dict[str, Any]:
    """Map the legacy domain-config file onto the AgentVersion payload shape."""
    return {
        "system_prompt": config["system_prompt"],
        "company_context": {"institution": "Demo University"},
        "question_flow": config["question_flow"],
        "extraction_schema": config["extraction_schema"],
        "disclosure_script": config["mandatory_disclosure"],
        "escalation_rules": config["escalation_rules"],
        "voice_settings": {"voice_id": "default", "speed": 1.0},
    }


def seed_demo(database_url: str | None = None) -> dict[str, Any]:
    """Create the demo tenant; returns a summary dict. Safe to run repeatedly."""
    settings = get_settings()
    if database_url:
        settings = settings.model_copy(update={"database_url": database_url})
    engine, session_factory = init_db(settings)

    inspector = inspect(engine)
    if not inspector.has_table("organizations"):
        _alembic_upgrade_head(settings.database_url)

    with session_factory() as db:
        existing = db.scalar(select(User).where(User.email == DEMO_EMAIL))
        if existing is not None:
            return {"status": "already_seeded", "email": DEMO_EMAIL}

        org = Organization(name="Demo University", slug="demo-university")
        db.add(org)
        db.flush()

        owner = User(
            org_id=org.id,
            email=DEMO_EMAIL,
            password_hash=hash_password(DEMO_PASSWORD),
            role="owner",
        )
        db.add(owner)
        db.flush()

        config = _load_absent_student_config()
        payload = _version_payload_from_config(config)
        validated = validate_agent_version_payload(payload)

        agent = Agent(
            org_id=org.id,
            name=config["display_name"] if "display_name" in config else config["name"],
            description="Seeded demo agent — absent student follow-up calls.",
            status="draft",
        )
        db.add(agent)
        db.flush()

        version = AgentVersion(
            agent_id=agent.id,
            version=1,
            system_prompt=validated.system_prompt,
            company_context=validated.company_context,
            question_flow=[step.model_dump() for step in validated.question_flow],
            extraction_schema={
                name: field.model_dump()
                for name, field in validated.extraction_schema.items()
            },
            disclosure_script=validated.disclosure_script,
            escalation_rules=[
                rule if isinstance(rule, str) else rule.model_dump()
                for rule in validated.escalation_rules
            ],
            voice_settings=validated.voice_settings,
            created_by=owner.id,
        )
        db.add(version)
        db.flush()
        agent.current_version_id = version.id

        campaign = Campaign(
            org_id=org.id,
            name="Absent Students - Demo Week",
            agent_version_id=version.id,
            status="draft",
        )
        db.add(campaign)
        db.flush()

        # Sample contacts are fictional numbers; consent=True lets the demo
        # explore the launch flow. No real calls can happen without telephony
        # credentials configured.
        for sample in SAMPLE_CONTACTS:
            db.add(
                Contact(
                    campaign_id=campaign.id,
                    org_id=org.id,
                    consent=True,
                    consent_source="seed",
                    **sample,
                )
            )

        db.commit()

        return {
            "status": "seeded",
            "org_slug": org.slug,
            "org_id": org.id,
            "user_id": owner.id,
            "agent_id": agent.id,
            "version_id": version.id,
            "campaign_id": campaign.id,
            "contacts": len(SAMPLE_CONTACTS),
        }


def main() -> None:
    result = seed_demo()
    if result["status"] == "already_seeded":
        print(f"Demo tenant already exists ({DEMO_EMAIL}) — nothing to do.")
        return
    print("Demo tenant seeded:")
    print(f"  login      : {DEMO_EMAIL} / {DEMO_PASSWORD}")
    print(f"  org_id     : {result['org_id']}")
    print(f"  agent_id   : {result['agent_id']} (version {result['version_id']})")
    print(f"  campaign_id: {result['campaign_id']}")
    print(f"  contacts   : {result['contacts']}")


if __name__ == "__main__":
    main()
