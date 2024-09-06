import secrets
import time
from typing import Annotated, Any
import uuid

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status, Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials


router = APIRouter(tags=["Demo Auth"])

security = HTTPBasic()


@router.get("/basic-auth/")
def demo_basic_auth_credetials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    return {
        "message": "Hi",
        "username": credentials.username,
        "password": credentials.password,
    }


static_auth_token_to_username = {
    "fdgfdgggfdgdfgfdvgfgvdggvfdscvgffgvdvgfgdvfdvfgvdfgvdfgdvfgdse32ffg": "admin",
    "jojnhghngjfdgsdfadsrghjkloiuiuyjrfsdcvbjkhiuytrffrsehn": "john",
}

usernames_to_password = {
    "admin": "admin",
    "john": "password",
}


def get_auth_user_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authrnticate": "Basic"},
    )
    correct_password = usernames_to_password.get(credentials.username)
    if not correct_password:
        raise unauthed_exc

    if not secrets.compare_digest(
        credentials.password.encode("utf-8"),
        correct_password.encode("utf-8"),
    ):
        raise unauthed_exc
    return credentials.username


def get_username_by_static_auth_token(
    static_token: Annotated[
        str,
        Header(alias="x-static-auth-token"),
    ]
) -> str:
    if token := static_auth_token_to_username.get(static_token):
        return token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
    )


@router.get("/basic-auth-username/")
def demo_basic_auth_username(
    auth_username: Annotated[str, Depends(get_auth_user_username)]
):
    return {
        "message": f"Hi {auth_username}",
    }


@router.get("/some-http-header-auth/")
def demo_some_http_header(
    auth_username: Annotated[str, Depends(get_username_by_static_auth_token)],
):
    return {
        "message": f"Hi {auth_username}",
    }


COOOKIES: dict[str, dict[str, Any]] = {}
COOOKIE_SESSION_ID_KEY = "web-app-session-id"


def generate_session_id() -> str:
    return uuid.uuid4().hex


def get_session_data(
    session_id: Annotated[str, Cookie(alias=COOOKIE_SESSION_ID_KEY)],
) -> dict[str, Any]:
    if session_id not in COOOKIES:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not authenticated",
        )
    return COOOKIES[session_id]


@router.post("/login-cookie/")
def demo_basic_auth_login_set_cookie(
    response: Response,
    # auth_username: Annotated[str, Depends(get_auth_user_username)],
    auth_username: Annotated[str, Depends(get_username_by_static_auth_token)],
):
    session_id = generate_session_id()
    COOOKIES[session_id] = {"username": auth_username, "login_at": int(time.time())}
    response.set_cookie(COOOKIE_SESSION_ID_KEY, session_id)
    return {
        "result": "Ok",
    }


@router.get("/check-cookie/")
def demo_auth_check_cookie(
    user_session_data: Annotated[dict, Depends(get_session_data)]
):
    username = user_session_data["username"]
    return {
        "message": f"Hello, {username}",
        **user_session_data,
    }


@router.post("/logout-cookie/")
def demo_basic_auth_logout_cookie(
    response: Response,
    session_id: Annotated[str, Cookie(alias=COOOKIE_SESSION_ID_KEY)],
    user_session_data: Annotated[dict, Depends(get_session_data)],
):
    COOOKIES.pop(session_id)
    response.delete_cookie(COOOKIE_SESSION_ID_KEY)
    username = user_session_data["username"]
    return {
        "message": f"Bye, {username}!",
    }
