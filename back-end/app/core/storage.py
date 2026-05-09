from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import PurePosixPath
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from minio import Minio
from minio.error import S3Error

from app.core.config import settings

ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/svg+xml": ".svg",
}


@dataclass(frozen=True)
class StoredObject:
    object_name: str
    url: str
    content_type: str
    size: int


def get_minio_client() -> Minio:
    return Minio(
        endpoint=settings.media.endpoint,
        access_key=settings.media.access_key,
        secret_key=settings.media.secret_key,
        secure=settings.media.secure,
    )


def public_media_url(object_name: str) -> str:
    base_url = settings.media.public_base_url.rstrip("/")
    safe_name = str(PurePosixPath(object_name))
    return f"{base_url}/{safe_name}"


async def ensure_media_bucket() -> None:
    client = get_minio_client()

    def ensure_bucket() -> None:
        if not client.bucket_exists(settings.media.bucket):
            client.make_bucket(settings.media.bucket)

    await run_in_threadpool(ensure_bucket)


async def check_media_storage() -> None:
    client = get_minio_client()
    exists = await run_in_threadpool(client.bucket_exists, settings.media.bucket)
    if not exists:
        raise RuntimeError("Configured media bucket does not exist.")


def _validate_object_name(object_name: str) -> str:
    normalized = str(PurePosixPath(object_name))
    if normalized.startswith("../") or normalized == ".":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid media object path.",
        )
    return normalized


async def upload_product_image(file: UploadFile) -> StoredObject:
    content_type = file.content_type or "application/octet-stream"
    extension = ALLOWED_IMAGE_MIME_TYPES.get(content_type)
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, WebP, GIF, and SVG images are supported.",
        )

    max_bytes = settings.media.max_image_upload_bytes
    payload = await file.read(max_bytes + 1)
    if len(payload) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                "Image is too large. "
                f"Maximum size is {settings.media.max_image_upload_mb} MB."
            ),
        )
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file is empty.",
        )

    object_name = f"products/{uuid4().hex}{extension}"
    return await put_media_object(
        object_name=object_name,
        payload=payload,
        content_type=content_type,
    )


async def put_media_object(
    *,
    object_name: str,
    payload: bytes,
    content_type: str,
) -> StoredObject:
    normalized_name = _validate_object_name(object_name)
    client = get_minio_client()
    await ensure_media_bucket()

    await run_in_threadpool(
        client.put_object,
        settings.media.bucket,
        normalized_name,
        BytesIO(payload),
        len(payload),
        content_type=content_type,
    )
    return StoredObject(
        object_name=normalized_name,
        url=public_media_url(normalized_name),
        content_type=content_type,
        size=len(payload),
    )


async def get_media_object(object_name: str):
    normalized_name = _validate_object_name(object_name)
    client = get_minio_client()

    def fetch_object():
        try:
            response = client.get_object(settings.media.bucket, normalized_name)
            try:
                data = response.read()
                content_type = response.headers.get(
                    "content-type", "application/octet-stream"
                )
            finally:
                response.close()
                response.release_conn()
            return data, content_type
        except S3Error as exc:
            if exc.code in {"NoSuchKey", "NoSuchBucket"}:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Media object was not found.",
                ) from exc
            raise

    return await run_in_threadpool(fetch_object)
