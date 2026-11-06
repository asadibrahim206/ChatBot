"""create messages table

Revision ID: 0001
Revises:
Create Date: 2026-10-30
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "messages",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column("session_id", sa.Text, nullable=False),
        sa.Column("role", sa.Text, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("messages_session_idx", "messages", ["session_id", "id"])


def downgrade() -> None:
    op.drop_index("messages_session_idx", table_name="messages")
    op.drop_table("messages")