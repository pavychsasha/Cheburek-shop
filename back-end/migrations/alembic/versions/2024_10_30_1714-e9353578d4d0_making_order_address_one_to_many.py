"""Making order-address one to many

Revision ID: e9353578d4d0
Revises: 32be34b0cb1b
Create Date: 2024-10-30 17:14:14.062600

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import select, update, table, column, UUID
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e9353578d4d0"
down_revision: Union[str, None] = "32be34b0cb1b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Define the tables for query purposes
    orders_table = table("Orders", column("order_id", UUID), column("address_id", UUID))
    address_table = table(
        "Address", column("address_id", UUID), column("order_id", UUID)
    )

    # Step 1: Add address_id to Orders as nullable
    op.add_column("Orders", sa.Column("address_id", UUID, nullable=True))

    # Step 2: Transfer existing order_id from Address to Orders.address_id
    conn = op.get_bind()
    address_data = conn.execute(
        select(address_table.c.address_id, address_table.c.order_id)
    ).fetchall()

    for address_id, order_id in address_data:
        if order_id:
            conn.execute(
                update(orders_table)
                .where(orders_table.c.order_id == order_id)
                .values(address_id=address_id)
            )

    # Step 3: Set address_id to NOT NULL after data population
    op.alter_column("Orders", "address_id", nullable=False)

    # Step 4: Drop order_id from Address and its constraints
    op.drop_constraint("Address_order_id_key", "Address", type_="unique")
    op.drop_constraint("Address_order_id_fkey", "Address", type_="foreignkey")
    op.drop_column("Address", "order_id")

    # Step 5: Add constraints for Orders.address_id
    op.create_unique_constraint("uq_order_address_id", "Orders", ["address_id"])
    op.create_foreign_key(None, "Orders", "Address", ["address_id"], ["address_id"])


def downgrade() -> None:
    # Reverse the changes if needed
    op.drop_constraint(None, "Orders", type_="foreignkey")
    op.drop_constraint("uq_order_address_id", "Orders", type_="unique")
    op.drop_column("Orders", "address_id")
    op.add_column(
        "Address", sa.Column("order_id", sa.UUID(), autoincrement=False, nullable=False)
    )
    op.create_foreign_key(
        "Address_order_id_fkey",
        "Address",
        "Orders",
        ["order_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint("Address_order_id_key", "Address", ["order_id"])
