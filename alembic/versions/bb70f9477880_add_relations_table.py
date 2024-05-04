"""add relations table

Revision ID: bb70f9477880
Revises: 485d4ebf1727
Create Date: 2024-04-24 23:55:41.302510

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bb70f9477880"
down_revision: Union[str, None] = "485d4ebf1727"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
table_name = "relations"


def upgrade():
    op.create_table(
        table_name,
        sa.Column("component_id_1", sa.Integer, sa.ForeignKey('components.id'), primary_key=True),
        sa.Column("component_id_2", sa.Integer, sa.ForeignKey('components.id'), primary_key=True),
    )

    op.create_index('idx_component_id_1', table_name, ['component_id_1'])
    op.create_index('idx_component_id_2', table_name, ['component_id_2'])


def downgrade():
    op.drop_index('idx_component_id_1', table_name)
    op.drop_index('idx_component_id_2', table_name)
    op.drop_table(table_name)
