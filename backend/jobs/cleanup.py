import threading
import time
from datetime import datetime

from sqlalchemy.orm import Session

from backend.core.config import get_settings
from backend.db.database import SessionLocal
from backend.db.models import SharedFile
from backend.services.file_service import delete_shared_file


def cleanup_expired_files(db: Session) -> int:
    now = datetime.utcnow()
    expired = db.query(SharedFile).filter(SharedFile.expires_at <= now).all()
    for shared in expired:
        delete_shared_file(shared)
        db.delete(shared)
    db.commit()
    return len(expired)


def run_cleanup_once() -> int:
    db = SessionLocal()
    try:
        return cleanup_expired_files(db)
    finally:
        db.close()


def start_cleanup_scheduler(stop_event: threading.Event) -> threading.Thread:
    settings = get_settings()

    def _worker():
        while not stop_event.is_set():
            run_cleanup_once()
            stop_event.wait(settings.cleanup_interval_minutes * 60)

    thread = threading.Thread(target=_worker, daemon=True, name="cleanup-scheduler")
    thread.start()
    return thread
