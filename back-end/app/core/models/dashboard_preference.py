from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class DashboardPreference(Base):
    __tablename__ = "DashboardPreferences"

    preference_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    preferences: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
