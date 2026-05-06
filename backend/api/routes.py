from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.core.config import get_settings
from backend.core.security import (
    create_download_grant,
    enforce_rate_limit,
    verify_download_grant,
    verify_password,
)
from backend.db.database import get_db
from backend.db.models import SharedFile
from backend.services.file_service import (
    ensure_downloadable,
    read_decrypted_file,
    record_download,
    save_upload,
)

router = APIRouter()


@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    password: str | None = Form(default=None),
    expiry_hours: int | None = Form(default=None),
    one_time_download: bool = Form(default=False),
    db: Session = Depends(get_db),
):
    rate_key = f"upload:{request.client.host if request.client else 'unknown'}"

    if not enforce_rate_limit(rate_key):
        raise HTTPException(status_code=429, detail="Too many upload attempts.")

    payload = await file.read()

    shared = save_upload(
        db,
        file,
        payload,
        expiry_hours=expiry_hours,
        one_time_download=one_time_download,
        password=password,
    )

    settings = get_settings()

    # Correct frontend share link
    link = f"{settings.frontend_url}/share/{shared.token}"

    return {
        "token": shared.token,
        "link": link,
        "filename": shared.original_filename,
        "expires_at": shared.expires_at,
        "requires_password": bool(shared.password_hash),
        "one_time_download": shared.one_time_download,
    }


@router.post("/verify-password")
def verify_file_password(
    request: Request,
    token: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    rate_key = f"verify:{token}:{request.client.host if request.client else 'unknown'}"

    if not enforce_rate_limit(rate_key):
        raise HTTPException(status_code=429, detail="Too many verify attempts.")

    shared = db.query(SharedFile).filter(SharedFile.token == token).first()

    if not shared:
        raise HTTPException(status_code=404, detail="Invalid token.")

    ensure_downloadable(shared)

    if not shared.password_hash:
        return {
            "authorized": True,
            "grant": create_download_grant(token),
        }

    if not verify_password(password, shared.password_hash):
        raise HTTPException(status_code=401, detail="Invalid password.")

    return {
        "authorized": True,
        "grant": create_download_grant(token),
    }


@router.get("/download/{token}")
def download_file(
    token: str,
    request: Request,
    grant: str | None = None,
    db: Session = Depends(get_db),
):
    rate_key = f"download:{token}:{request.client.host if request.client else 'unknown'}"

    if not enforce_rate_limit(rate_key):
        raise HTTPException(status_code=429, detail="Too many download attempts.")

    shared = db.query(SharedFile).filter(SharedFile.token == token).first()

    if not shared:
        raise HTTPException(status_code=404, detail="Invalid token.")

    ensure_downloadable(shared)

    if shared.password_hash and not verify_download_grant(grant or "", token):
        raise HTTPException(status_code=401, detail="Password verification required.")

    content = read_decrypted_file(shared)

    record_download(
        db,
        shared,
        request.client.host if request.client else None,
    )

    headers = {
        "Content-Disposition": f'attachment; filename="{shared.original_filename}"',
        "Content-Length": str(len(content)),
    }

    return StreamingResponse(
        BytesIO(content),
        media_type=shared.mime_type,
        headers=headers,
    )


@router.get("/files/{token}")
def file_status(
    token: str,
    db: Session = Depends(get_db),
):
    shared = db.query(SharedFile).filter(SharedFile.token == token).first()

    if not shared:
        raise HTTPException(status_code=404, detail="Invalid token.")

    is_expired = shared.expires_at <= datetime.utcnow()

    return {
        "token": shared.token,
        "filename": shared.original_filename,
        "expires_at": shared.expires_at,
        "requires_password": bool(shared.password_hash),
        "one_time_download": shared.one_time_download,
        "downloaded": shared.downloaded,
        "is_expired": is_expired,
    }