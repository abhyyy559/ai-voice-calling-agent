"""Seed-script tests: clean beta tenant bootstrap + sample-data purge."""
from __future__ import annotations

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app.auth import verify_password
from app.models import Agent, AgentVersion, Campaign, Contact, User
from scripts.seed_demo import purge_sample_data, seed_demo


def test_seed_demo_creates_clean_beta_tenant(tmp_path):
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

        # Beta policy: no campaigns, no contacts — testers bring their own data.
        assert "campaign_id" not in result
        assert db.scalar(select(func.count()).select_from(Campaign)) == 0
        assert db.scalar(select(func.count()).select_from(Contact)) == 0
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
        assert len(db.scalars(select(Contact)).all()) == 0, "seed must not add contacts"


def test_purge_sample_data_removes_campaigns_contacts_calls(tmp_path):
    db_url = f"sqlite:///{tmp_path / 'demo.db'}"
    seed_result = seed_demo(db_url)

    # Simulate leftover demo junk: a campaign with contacts and a call.
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    with Session() as db:
        campaign = Campaign(
            org_id=seed_result["org_id"],
            name="Absent Students - Demo Week",
            agent_version_id=seed_result["version_id"],
            status="draft",
        )
        db.add(campaign)
        db.flush()
        db.add(
            Contact(
                campaign_id=campaign.id,
                org_id=seed_result["org_id"],
                name="Ravi Sharma",
                phone="+919000000001",
                consent=True,
                consent_source="test",
            )
        )
        from app.models import Call, Transcript

        call = Call(
            campaign_id=campaign.id,
            org_id=seed_result["org_id"],
            status="completed",
            duration_seconds=42.0,
        )
        db.add(call)
        db.flush()
        db.add(Transcript(call_id=call.id, turn_index=0, speaker="agent", text="hello"))
        other_org_call = Call(org_id=seed_result["org_id"] + 999, status="completed")
        db.add(other_org_call)
        db.commit()

    result = purge_sample_data(db_url)
    assert result["status"] == "purged"
    assert result["campaigns"] == 1
    assert result["contacts"] == 1
    assert result["calls"] == 1

    with Session() as db:
        from app.models import Call, Transcript

        assert db.scalar(select(func.count()).select_from(Campaign)) == 0
        assert db.scalar(select(func.count()).select_from(Contact)) == 0
        remaining = db.scalars(select(Call)).all()
        assert len(remaining) == 1
        assert remaining[0].org_id != seed_result["org_id"], "foreign-org call must survive"
        assert db.scalar(select(func.count()).select_from(Transcript)) == 0
        # Agents and users are preserved by design.
        assert db.scalar(select(func.count()).select_from(Agent)) == 1
        assert db.scalar(select(func.count()).select_from(User)) == 1
    engine.dispose()


def test_purge_without_demo_tenant_is_a_noop(tmp_path):
    db_url = f"sqlite:///{tmp_path / 'empty.db'}"
    assert purge_sample_data(db_url) == {"status": "no_demo_tenant", "email": "demo@example.com"}
