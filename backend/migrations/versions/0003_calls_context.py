"""P0-2 personalization: calls.context carries packed contact fields.

``calls.context`` is a JSON bag holding the per-call runtime context the
backend packs into LiveKit room/token metadata, currently
``{"contact": {<custom_fields>}}`` so the voice agent can personalize its
opening ("calling about Aarav... may I speak with Suresh?").

Revision ID: 0003_calls_context
Revises: 0002_tenancy_agents
Create Date: 2026-08-25
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0003_calls_context"
down_revision = "0002_tenancy_agents"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("calls") as batch:
        batch.add_column(sa.Column("context", sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("calls") as batch:
        batch.drop_column("context")
