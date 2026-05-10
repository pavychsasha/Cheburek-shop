from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.dashboard_preference import DashboardPreference
from app.core.schemas.admin import DashboardPreferences, DashboardWidgetPreference


DEFAULT_DASHBOARD_WIDGETS = [
    DashboardWidgetPreference(id="metrics", position=0),
    DashboardWidgetPreference(id="revenue", chart_type="line", position=1),
    DashboardWidgetPreference(id="profit", chart_type="area", position=2),
    DashboardWidgetPreference(id="orders", chart_type="bar", position=3),
    DashboardWidgetPreference(id="visitors", chart_type="area", position=4),
    DashboardWidgetPreference(id="status", chart_type="pie", position=5),
    DashboardWidgetPreference(id="top-products", position=6),
    DashboardWidgetPreference(id="low-stock", position=7),
    DashboardWidgetPreference(id="recent-orders", position=8),
]


def default_dashboard_preferences() -> DashboardPreferences:
    return DashboardPreferences(
        widgets=[
            widget.model_copy()
            for widget in DEFAULT_DASHBOARD_WIDGETS
        ]
    )


async def get_dashboard_preferences(
    session: AsyncSession,
    user_id: uuid.UUID,
) -> DashboardPreferences:
    result = await session.execute(
        select(DashboardPreference).where(DashboardPreference.user_id == user_id)
    )
    preference = result.scalar_one_or_none()
    if preference is None:
        return default_dashboard_preferences()

    return DashboardPreferences.model_validate(preference.preferences)


async def update_dashboard_preferences(
    session: AsyncSession,
    user_id: uuid.UUID,
    update: DashboardPreferences,
) -> DashboardPreferences:
    normalized = DashboardPreferences(
        widgets=sorted(update.widgets, key=lambda widget: widget.position)
    )
    result = await session.execute(
        select(DashboardPreference).where(DashboardPreference.user_id == user_id)
    )
    preference = result.scalar_one_or_none()
    if preference is None:
        preference = DashboardPreference(
            user_id=user_id,
            preferences=normalized.model_dump(mode="json"),
        )
    else:
        preference.preferences = normalized.model_dump(mode="json")

    session.add(preference)
    await session.commit()
    return normalized
