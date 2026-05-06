import hmac
import json
import secrets
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode
from collections import defaultdict, deque
from hashlib import sha256

from passlib.context import CryptContext

from backend.core.config import get_settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_rate_state: dict[str, deque[float]] = defaultdict(deque)


def generate_share_token() -> str:
    return secrets.token_urlsafe(24)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def _sign(data: bytes) -> str:
    key = get_settings().encryption_key
    return hmac.new(key, data, sha256).hexdigest()


def create_download_grant(token: str, ttl_seconds: int = 300) -> str:
    payload = {"token": token, "exp": int(time.time()) + ttl_seconds}
    payload_raw = json.dumps(payload).encode("utf-8")
    payload_part = urlsafe_b64encode(payload_raw).decode("utf-8")
    sig_part = _sign(payload_raw)
    return f"{payload_part}.{sig_part}"


def verify_download_grant(grant: str, token: str) -> bool:
    if not grant or "." not in grant:
        return False
    payload_part, sig_part = grant.split(".", 1)
    try:
        payload_raw = urlsafe_b64decode(payload_part.encode("utf-8"))
        expected_sig = _sign(payload_raw)
        if not hmac.compare_digest(expected_sig, sig_part):
            return False
        payload = json.loads(payload_raw.decode("utf-8"))
    except Exception:
        return False
    return payload.get("token") == token and int(payload.get("exp", 0)) >= int(time.time())


def enforce_rate_limit(key: str) -> bool:
    settings = get_settings()
    now = time.time()
    window_start = now - settings.rate_limit_window_seconds
    bucket = _rate_state[key]

    while bucket and bucket[0] < window_start:
        bucket.popleft()

    if len(bucket) >= settings.rate_limit_max_attempts:
        return False

    bucket.append(now)
    return True
