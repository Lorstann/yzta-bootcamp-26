"""
backend/services/storage.py
Curriculum file persistence: local disk (default) or S3.
"""

from __future__ import annotations

import logging
import re
import uuid
from pathlib import Path

from backend.config import settings

logger = logging.getLogger(__name__)

_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


def _safe_filename(filename: str) -> str:
    base = Path(filename or "upload.bin").name
    cleaned = _SAFE_NAME.sub("_", base).strip("._") or "upload.bin"
    return cleaned[:180]


def save_file(
    tenant_id: uuid.UUID,
    filename: str,
    data: bytes,
) -> str:
    """
    Persist bytes and return a URI.
    - local → file://{local_storage_dir}/{tenant_id}/{uuid}_{name}
    - s3 → s3://{bucket}/{tenant_id}/{uuid}_{name}
    """
    safe = _safe_filename(filename)
    key = f"{tenant_id}/{uuid.uuid4().hex}_{safe}"

    if settings.storage_backend == "s3":
        return _save_s3(key, data, filename=safe)

    return _save_local(key, data)


def _save_local(key: str, data: bytes) -> str:
    root = Path(settings.local_storage_dir)
    path = root / key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    uri = f"file://{path.resolve().as_posix()}"
    logger.info(
        "File saved locally | path=%s bytes=%s",
        path,
        len(data),
    )
    return uri


def _save_s3(key: str, data: bytes, *, filename: str) -> str:
    bucket = (settings.s3_bucket or "").strip()
    if not bucket:
        raise ValueError("S3_BUCKET is required when STORAGE_BACKEND=s3")

    import boto3

    client = boto3.client(
        "s3",
        region_name=settings.s3_region or None,
        aws_access_key_id=settings.aws_access_key_id or None,
        aws_secret_access_key=settings.aws_secret_access_key or None,
    )
    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=data,
        ContentDisposition=f'attachment; filename="{filename}"',
    )
    uri = f"s3://{bucket}/{key}"
    logger.info("File saved to S3 | uri=%s bytes=%s", uri, len(data))
    return uri
