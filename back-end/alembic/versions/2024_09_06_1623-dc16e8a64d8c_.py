"""empty message

Revision ID: dc16e8a64d8c
Revises: 8fa9ea5c6351
Create Date: 2024-09-06 16:23:59.121968

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dc16e8a64d8c"
down_revision: Union[str, None] = "8fa9ea5c6351"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
