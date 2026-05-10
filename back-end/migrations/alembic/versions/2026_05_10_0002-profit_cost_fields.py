"""Add product and order cost fields

Revision ID: profitcost0002
Revises: cmsanalytics001
Create Date: 2026-05-10 02:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "profitcost0002"
down_revision: Union[str, None] = "cmsanalytics001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "Products",
        sa.Column(
            "cost_price",
            sa.Float(),
            nullable=False,
            server_default="0",
        ),
    )
    op.create_check_constraint(
        "check_product_cost_price_non_negative",
        "Products",
        "cost_price >= 0",
    )

    op.add_column(
        "order_product_association",
        sa.Column(
            "cost_price",
            sa.Float(),
            nullable=False,
            server_default="0",
        ),
    )
    op.create_check_constraint(
        "check_order_product_cost_price_non_negative",
        "order_product_association",
        "cost_price >= 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "check_order_product_cost_price_non_negative",
        "order_product_association",
        type_="check",
    )
    op.drop_column("order_product_association", "cost_price")
    op.drop_constraint(
        "check_product_cost_price_non_negative",
        "Products",
        type_="check",
    )
    op.drop_column("Products", "cost_price")
