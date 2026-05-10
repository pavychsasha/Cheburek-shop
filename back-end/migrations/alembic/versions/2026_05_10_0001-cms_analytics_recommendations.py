"""Add CMS analytics, tags, and order notes

Revision ID: cmsanalytics001
Revises: e9353578d4d0
Create Date: 2026-05-10 00:01:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "cmsanalytics001"
down_revision: Union[str, None] = "e9353578d4d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("Orders", sa.Column("customer_notes", sa.Text(), nullable=True))
    op.add_column("Orders", sa.Column("admin_notes", sa.Text(), nullable=True))

    op.create_table(
        "ProductTags",
        sa.Column("tag_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=False),
        sa.PrimaryKeyConstraint("tag_id"),
        sa.UniqueConstraint("name", name="uq_product_tag_name"),
    )
    op.create_index("ix_product_tag_name", "ProductTags", ["name"])

    op.create_table(
        "product_tag_association",
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("tag_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["Products.product_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["ProductTags.tag_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("product_id", "tag_id"),
    )

    op.create_table(
        "DashboardPreferences",
        sa.Column("preference_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("preferences", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("preference_id"),
        sa.UniqueConstraint("user_id", name="uq_dashboard_preference_user_id"),
    )

    op.create_table(
        "VisitorDailyStats",
        sa.Column("stat_id", sa.UUID(), nullable=False),
        sa.Column("visit_date", sa.Date(), nullable=False),
        sa.Column("visitor_hash", sa.String(length=64), nullable=False),
        sa.Column("page_views", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("stat_id"),
        sa.UniqueConstraint(
            "visit_date",
            "visitor_hash",
            name="uq_visitor_daily_hash",
        ),
    )
    op.create_index(
        "ix_visitor_daily_visit_date",
        "VisitorDailyStats",
        ["visit_date"],
    )

    op.create_table(
        "PageViewDailyStats",
        sa.Column("stat_id", sa.UUID(), nullable=False),
        sa.Column("visit_date", sa.Date(), nullable=False),
        sa.Column("path", sa.String(length=250), nullable=False),
        sa.Column("views", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("stat_id"),
        sa.UniqueConstraint(
            "visit_date",
            "path",
            name="uq_page_view_daily_path",
        ),
    )
    op.create_index(
        "ix_page_view_daily_visit_date",
        "PageViewDailyStats",
        ["visit_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_page_view_daily_visit_date", table_name="PageViewDailyStats")
    op.drop_table("PageViewDailyStats")
    op.drop_index("ix_visitor_daily_visit_date", table_name="VisitorDailyStats")
    op.drop_table("VisitorDailyStats")
    op.drop_table("DashboardPreferences")
    op.drop_table("product_tag_association")
    op.drop_index("ix_product_tag_name", table_name="ProductTags")
    op.drop_table("ProductTags")
    op.drop_column("Orders", "admin_notes")
    op.drop_column("Orders", "customer_notes")
