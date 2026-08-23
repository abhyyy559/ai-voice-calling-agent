"""Seed-script tests: idempotent demo tenant bootstrap."""
from __future__ import annotations

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.auth import verify_password
from app.models import Agent, AgentVersion, Campaign, Contact, User
from scripts.seed_demo import seed_demo


def test_seed_demo_creates_org_agent_campaign_contacts(tmp_path):
    db_url = f"sqlite:///{tmp_path / 'demo.db'}"
    result = seed_demo(db_url)

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    with Session() as db:
        user = db.scalar(select(User).where(User.email == "demo@example.com"))
        assert user is not None, "demo user missing"
        assert verify_password("demo1234", user.password_hash)
        assert user.role == "owner"

        org = db.get(type(user).organization.property.mapper.class_, user.org_id)
        assert org.slug == result["org_slug"]

        agent = db.scalars(select(Agent)).first()
        assert agent is not None
        version = db.get(AgentVersion, agent.current_version_id)
        assert version is not None
        assert version.version == 1
        assert version.disclosure_script.lower().startswith(
            "hello"
        ), "disclosure script should come from absent-student.json"

        campaign = db.scalars(select(Campaign)).first()
        assert campaign is not None
        assert campaign.agent_version_id == version.id
        assert campaign.status == "draft"

        contacts = db.scalars(select(Contact)).all()
        assert len(contacts) == 5
    engine.dispose()


def test_seed_demo_is_idempotent(tmp_path):
    db_url = f"sqlite:///{tmp_path / 'demo.db'}"
    first = seed_demo(db_url)
    second = seed_demo(db_url)
    assert second["status"] == "already_seeded"
    assert first["status"] != "already_seeded"

    engine = create_engine(db_url)
    with sessionmaker(bind=engine)() as db:
        assert len(db.scalars(select(User)).all()) == 1, "must not duplicate users"
        assert len(db.scalars(select(Contact)).all()) == 5, "must not duplicate contacts"
