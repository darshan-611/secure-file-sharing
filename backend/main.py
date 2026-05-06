import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router as api_router
from backend.core.config import get_settings
from backend.db.database import Base, engine
from backend.jobs.cleanup import run_cleanup_once, start_cleanup_scheduler

# 1. ಸೆಟ್ಟಿಂಗ್ಸ್ ಲೋಡ್ ಮಾಡುವುದು 
settings = get_settings()

stop_event = threading.Event()
cleanup_thread = None

@asynccontextmanager
async def lifespan(_: FastAPI):
    global cleanup_thread
    # ಡೇಟಾಬೇಸ್ ಟೇಬಲ್ಸ್ ಕ್ರಿಯೇಟ್ ಮಾಡುವುದು [cite: 2]
    Base.metadata.create_all(bind=engine)
    run_cleanup_once()
    cleanup_thread = start_cleanup_scheduler(stop_event)
    try:
        yield
    finally:
        stop_event.set()
        if cleanup_thread:
            cleanup_thread.join(timeout=1)

app = FastAPI(title=settings.app_name, lifespan=lifespan)

# 2. CORS ಕಾನ್ಫಿಗರೇಶನ್ ಸರಿಪಡಿಸುವುದು
# ಇಲ್ಲಿ localhost ಮತ್ತು 127.0.0.1 ಎರಡನ್ನೂ ಸೇರಿಸುವುದು ಮುಖ್ಯ
origins = [
    str(settings.frontend_url).rstrip("/"), # .env ನಿಂದ ಬರುವ URL 
    "http://localhost:5173", 
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # ಅಥವಾ ಟೆಸ್ಟಿಂಗ್‌ಗಾಗಿ ["*"] ಬಳಸಿ
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. API ರೂಟ್ಸ್ ಸೇರಿಸುವುದು [cite: 2]
app.include_router(api_router, prefix=settings.api_prefix)

@app.get("/health")
def health():
    return {"ok": True}
