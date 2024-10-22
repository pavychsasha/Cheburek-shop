"""empty message

Revision ID: 5a0022b9e219
Revises: 25a2b70b62ea, 9879961c061f
Create Date: 2024-10-06 20:52:52.609382

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5a0022b9e219"
down_revision: Union[str, None] = ("25a2b70b62ea", "9879961c061f")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
