"""add components table

Revision ID: 485d4ebf1727
Revises:
Create Date: 2024-04-24 23:47:31.885322

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "485d4ebf1727"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
table_name = "components"


def upgrade():
    op.create_table(
        table_name,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("type", sa.String, nullable=False),
        sa.Column("component_nomn", sa.String, nullable=False),
        sa.Column("component_gent", sa.String, nullable=False),
        sa.Column("component_datv", sa.String, nullable=False),
        sa.Column("component_accs", sa.String, nullable=False),
        sa.Column("component_ablt", sa.String, nullable=False),
        sa.Column("component_loct", sa.String, nullable=False),
        sa.Column("gender", sa.String, nullable=False),
        sa.Column("popularity", sa.Integer, nullable=False),
    )


def downgrade():
    op.drop_table(table_name)
