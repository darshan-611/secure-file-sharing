from datetime import datetime, timedelta
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.core.config import get_settings
from backend.core.security import generate_share_token, hash_password
from backend.db.models import SharedFile
from backend.services.crypto_service import decrypt_bytes, encrypt_bytes


def _safe_name(filename: str) -> str:
    name = Path(filename).name.strip().replace("\x00", "")
    return name or "file.bin"


def validate_upload(file: UploadFile, payload: bytes) -> None:
    settings = get_settings()
    if len(payload) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds {settings.max_file_size_mb}MB limit.",
        )
    if file.content_type not in settings.allowed_mime_type_set:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type is not allowed.",
        )


def save_upload(
    db: Session,
    file: UploadFile,
    payload: bytes,
    *,
    expiry_hours: int | None,
    one_time_download: bool,
    password: str | None,
) -> SharedFile:
    settings = get_settings()
    validate_upload(file, payload)

    ttl_hours = expiry_hours or settings.default_expiry_hours
    if ttl_hours < 1 or ttl_hours > settings.max_expiry_hours:
        raise HTTPException(status_code=400, detail="Invalid expiry_hours.")

    token = generate_share_token()
    encrypted_blob = encrypt_bytes(payload)
    encrypted_file_path = settings.storage_dir / f"{token}.bin"
    encrypted_file_path.write_bytes(encrypted_blob)

    shared = SharedFile(
        token=token,
        encrypted_path=str(encrypted_file_path),
        original_filename=_safe_name(file.filename or "file.bin"),
        mime_type=file.content_type or "application/octet-stream",
        size_bytes=len(payload),
        password_hash=hash_password(password) if password else None,
        expires_at=datetime.utcnow() + timedelta(hours=ttl_hours),
        one_time_download=one_time_download,
    )
    db.add(shared)
    db.commit()
    db.refresh(shared)
    return shared


def ensure_downloadable(shared: SharedFile) -> None:
    now = datetime.utcnow()
    if shared.expires_at <= now:
        raise HTTPException(status_code=410, detail="This link has expired.")
    if shared.one_time_download and shared.downloaded:
        raise HTTPException(status_code=410, detail="This one-time link is already used.")


def read_decrypted_file(shared: SharedFile) -> bytes:
    path = Path(shared.encrypted_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File content missing.")
    blob = path.read_bytes()
    return decrypt_bytes(blob)


def record_download(db: Session, shared: SharedFile, ip: str | None) -> None:
    stamp = datetime.utcnow().isoformat()
    shared.download_count += 1
    shared.downloaded = True
    line = f"{stamp} - {ip or 'unknown'}"
    shared.access_log = f"{shared.access_log}\n{line}".strip()
    db.add(shared)
    db.commit()


def delete_shared_file(shared: SharedFile) -> None:
    path = Path(shared.encrypted_path)
    if path.exists():
        path.unlink()
