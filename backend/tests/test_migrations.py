"""Alembic migration chain tests.

``upgrade head`` against a scratch SQLite database must produce the full
enterprise schema; ``downgrade base`` must cleanly reverse it.
"""
from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _make_config(db_url: str) -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    cfg.set_main_option("sqlalchemy.url", db_url)
    return cfg


def test_upgrade_head_creates_enterprise_schema(tmp_path):
    db_path = tmp_path / "migrations.db"
    cfg = _make_config(f"sqlite:///{db_path}")

    command.upgrade(cfg, "head")

    from sqlalchemy import create_engine

    engine = create_engine(f"sqlite:///{db_path}")
    inspector = inspect(engine)

    # New tables (spec §3)
    for table in ("organizations", "users", "agents", "agent_versions"):
        assert inspector.has_table(table), f"missing table {table}"

    # Altered tables
    call_cols = {c["name"] for c in inspector.get_columns("calls")}
    assert {"kind", "org_id", "agent_version_id"} <= call_cols
    campaign_cols = {c["name"] for c in inspector.get_columns("campaigns")}
    assert {"org_id", "agent_version_id"} <= campaign_cols
    contact_cols = {c["name"] for c in inspector.get_columns("contacts")}
    assert "org_id" in contact_cols

    transcript_cols = {c["name"] for c in inspector.get_columns("transcripts")}
    assert {
        "stt_final_ms",
        "llm_first_token_ms",
        "tts_first_audio_ms",
        "e2e_ms",
    } <= transcript_cols, "per-turn latency columns missing"

    version_cols = {c["name"] for c in inspector.get_columns("agent_versions")}
    assert {
        "system_prompt",
        "company_context",
        "question_flow",
        "extraction_schema",
        "disclosure_script",
        "escalation_rules",
        "voice_settings",
    } <= version_cols

    # alembic_version records the head revision
    rev_row = (
        engine.connect()
        .exec_driver_sql("SELECT version_num FROM alembic_version")
        .first()
    )
    assert rev_row is not None and rev_row[0]
    engine.dispose()


def test_downgrade_base_reverses_cleanly(tmp_path):
    db_path = tmp_path / "downgrade.db"
    cfg = _make_config(f"sqlite:///{db_path}")

    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")

    from sqlalchemy import create_engine

    engine = create_engine(f"sqlite:///{db_path}")
    inspector = inspect(engine)
    assert not inspector.has_table("organizations")
    assert not inspector.has_table("users")
    engine.dispose()
