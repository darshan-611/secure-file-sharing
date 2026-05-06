import base64
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "Secure File Sharing"
    api_prefix: str = "/api"
    frontend_url: str = "http://localhost:5173"
    database_url: str = f"sqlite:///{BASE_DIR / 'database' / 'secure_files.db'}"
    storage_dir: Path = BASE_DIR / "database" / "files"

    max_file_size_mb: int = 25
    allowed_mime_types: str = "image/png,image/jpeg,application/pdf,text/plain"
    default_expiry_hours: int = 24
    max_expiry_hours: int = 168

    cleanup_interval_minutes: int = 10
    rate_limit_window_seconds: int = 60
    rate_limit_max_attempts: int = 20

    # AES-256 key encoded as url-safe base64; example generated in .env.example
    encryption_key_b64: str = Field(
        default="MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def allowed_mime_type_set(self) -> set[str]:
        return {item.strip() for item in self.allowed_mime_types.split(",") if item.strip()}

    @property
    def encryption_key(self) -> bytes:
        key = base64.urlsafe_b64decode(self.encryption_key_b64.encode("utf-8"))
        if len(key) not in {16, 24, 32}:
            raise ValueError("ENCRYPTION_KEY_B64 must decode to 16/24/32 bytes.")
        return key


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    return settings
