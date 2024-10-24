import uuid

from fastapi import Request


async def session_id(request: Request) -> uuid.UUID:
    session_uuid: uuid.UUID | str | None = request.session.get("session_id")

    # If no session_id exists, create one
    if not session_uuid:
        session_uuid = uuid.uuid4()
        request.session["session_id"] = str(
            session_uuid
        )  # uuid is not json serializable

    if isinstance(session_uuid, str):
        session_uuid = uuid.UUID(session_uuid)
    return session_uuid


async def current_language(request: Request) -> str:
    if not request.session.get("language"):
        request.session["language"] = "en"
        return request.session["language"]

    return request.session["language"]
