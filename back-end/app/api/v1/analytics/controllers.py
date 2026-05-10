from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.models import sql_db_helper
from app.core.services.visitor_analytics import record_visit

router = APIRouter(tags=["Analytics"])

VISITOR_COOKIE_NAME = "cheburek_visitor_id"


class VisitTrackRequest(BaseModel):
    path: str = Field(default="/", max_length=250)


@router.post("/visit", status_code=status.HTTP_204_NO_CONTENT)
async def track_visit(
    payload: VisitTrackRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(sql_db_helper.session_dependency),
) -> None:
    visitor_id = request.cookies.get(VISITOR_COOKIE_NAME)
    if not visitor_id:
        visitor_id = uuid4().hex
        response.set_cookie(
            VISITOR_COOKIE_NAME,
            visitor_id,
            max_age=60 * 60 * 24 * 365,
            httponly=True,
            samesite="lax",
            secure=settings.cookie_transport_settings.cookie_secure,
        )

    await record_visit(session=session, visitor_id=visitor_id, path=payload.path)
