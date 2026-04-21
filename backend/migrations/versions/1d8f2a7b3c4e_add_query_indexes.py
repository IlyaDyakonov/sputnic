"""add query indexes

Revision ID: 1d8f2a7b3c4e
Revises: 0d6439d2e79f
Create Date: 2026-04-21 11:20:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1d8f2a7b3c4e"
down_revision: Union[str, Sequence[str], None] = "0d6439d2e79f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Indexes for hot list queries and relation filtering.
    op.create_index("ix_files_created_at", "files", ["created_at"], unique=False)
    op.create_index("ix_alerts_created_at", "alerts", ["created_at"], unique=False)
    op.create_index("ix_alerts_file_id", "alerts", ["file_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_alerts_file_id", table_name="alerts")
    op.drop_index("ix_alerts_created_at", table_name="alerts")
    op.drop_index("ix_files_created_at", table_name="files")
