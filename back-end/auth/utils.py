from datetime import datetime, timedelta, timezone
import uuid
import jwt
import bcrypt

from core.config import settings


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
):

    to_encode = payload.copy()
    now = datetime.now(tz=timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
        jti=str(uuid.uuid4()),  # ToDo: add blacklist logic
    )

    encoded = jwt.encode(
        payload=to_encode,
        key=private_key,
        algorithm=algorithm,
    )

    return encoded


def decode_jwt(
    token,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
):
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decoded


def hash_password(
    password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(password=pwd_bytes, salt=salt)


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    pwd_bytes: bytes = password.encode()
    return bcrypt.checkpw(password=pwd_bytes, hashed_password=hashed_password)
