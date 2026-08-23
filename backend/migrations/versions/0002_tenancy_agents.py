"""Enterprise multi-tenancy + agents (spec §3 data-model delta).

New tables: organizations, users, agents, agent_versions (immutable),
knowledge_documents (reserved).
Altered tables: campaigns (+org_id, +agent_version_id; legacy domain_config_id
stays read-only), contacts (+org_id), calls (+kind phone|playground, +org_id,
+agent_version_id; campaign_id/contact_id become nullable for playground
rows), transcripts (+per-turn latency columns).

Revision ID: 0002_tenancy_agents
Revises: 0001_baseline
Create Date: 2026-08-23
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_tenancy_agents"
down_revision = "0001_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=200), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_organizations_slug"), "organizations", ["slug"])

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("org_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True
        ),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_org_id"), "users", ["org_id"])
    op.create_index(op.f("ix_users_email"), "users", ["email"])

    op.create_table(
        "agents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("org_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        # Logical FK to agent_versions.id — avoids circular DDL (see model docs).
        sa.Column("current_version_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agents_org_id"), "agents", ["org_id"])

    op.create_table(
        "agent_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("company_context", sa.JSON(), nullable=False),
        sa.Column("question_flow", sa.JSON(), nullable=False),
        sa.Column("extraction_schema", sa.JSON(), nullable=False),
        sa.Column("disclosure_script", sa.Text(), nullable=False),
        sa.Column("escalation_rules", sa.JSON(), nullable=False),
        sa.Column("voice_settings", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True
        ),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("agent_id", "version", name="uq_agent_version_number"),
    )
    op.create_index(op.f("ix_agent_versions_agent_id"), "agent_versions", ["agent_id"])

    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("org_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=500), nullable=False),
        sa.Column("mime", sa.String(length=200), nullable=True),
        sa.Column("storage_key", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_knowledge_documents_org_id"), "knowledge_documents", ["org_id"]
    )

    with op.batch_alter_table("campaigns") as batch:
        batch.add_column(sa.Column("org_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("agent_version_id", sa.Integer(), nullable=True))

    op.create_index(op.f("ix_campaigns_org_id"), "campaigns", ["org_id"])

    with op.batch_alter_table("contacts") as batch:
        batch.add_column(sa.Column("org_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_contacts_org_id"), "contacts", ["org_id"])

    with op.batch_alter_table("calls") as batch:
        batch.alter_column("campaign_id", existing_type=sa.Integer(), nullable=True)
        batch.alter_column("contact_id", existing_type=sa.Integer(), nullable=True)
        batch.add_column(
            sa.Column(
                "kind",
                sa.String(length=20),
                nullable=False,
                server_default="phone",
            )
        )
        batch.add_column(sa.Column("org_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("agent_version_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_calls_kind"), "calls", ["kind"])
    op.create_index(op.f("ix_calls_org_id"), "calls", ["org_id"])

    with op.batch_alter_table("transcripts") as batch:
        batch.add_column(sa.Column("stt_final_ms", sa.Float(), nullable=True))
        batch.add_column(sa.Column("llm_first_token_ms", sa.Float(), nullable=True))
        batch.add_column(sa.Column("tts_first_audio_ms", sa.Float(), nullable=True))
        batch.add_column(sa.Column("e2e_ms", sa.Float(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("transcripts") as batch:
        batch.drop_column("e2e_ms")
        batch.drop_column("tts_first_audio_ms")
        batch.drop_column("llm_first_token_ms")
        batch.drop_column("stt_final_ms")

    op.drop_index(op.f("ix_calls_org_id"), table_name="calls")
    op.drop_index(op.f("ix_calls_kind"), table_name="calls")
    with op.batch_alter_table("calls") as batch:
        batch.drop_column("agent_version_id")
        batch.drop_column("org_id")
        batch.drop_column("kind")

    op.drop_index(op.f("ix_contacts_org_id"), table_name="contacts")
    with op.batch_alter_table("contacts") as batch:
        batch.drop_column("org_id")

    op.drop_index(op.f("ix_campaigns_org_id"), table_name="campaigns")
    with op.batch_alter_table("campaigns") as batch:
        batch.drop_column("agent_version_id")
        batch.drop_column("org_id")

    op.drop_table("knowledge_documents")
    op.drop_table("agent_versions")
    op.drop_table("agents")
    op.drop_table("users")
    op.drop_table("organizations")
