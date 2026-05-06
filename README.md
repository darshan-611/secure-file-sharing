# Secure File Sharing

Secure file sharing app with a FastAPI backend and React frontend. Files are encrypted at rest with AES-GCM before being written to disk.

## Tech Stack

- Backend: FastAPI, SQLAlchemy, SQLite
- Frontend: React + Vite
- Crypto: `cryptography` AES-GCM
- Password hashing: `passlib` with bcrypt

## Project Structure

- `backend/` API, services, DB models, cleanup job
- `frontend/` React UI for upload/success/download flows
- `database/files/` encrypted file storage root
- `requirements.txt` backend dependencies
- `.env.example` environment variables template

## Backend Setup

1. Create and activate a virtual environment:
   - Windows PowerShell:
     - `python -m venv .venv`
     - `.venv\Scripts\Activate.ps1`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Copy env template and edit values:
   - `copy .env.example .env`
4. Run API:
   - `uvicorn backend.main:app --reload --port 8000`

API endpoints:

- `POST /api/upload`
- `POST /api/verify-password`
- `GET /api/download/{token}`
- `GET /api/files/{token}`

## Frontend Setup

1. Open frontend directory:
   - `cd frontend`
2. Install dependencies:
   - `npm install`
3. (Optional) set custom API base URL:
   - create `frontend/.env` with `VITE_API_BASE_URL=http://localhost:8000/api`
4. Run dev server:
   - `npm run dev`

## End-to-End Flow

1. Upload page accepts file drag/drop or picker.
2. Optional password, expiry, and one-time toggle are submitted.
3. Backend validates type/size, encrypts file with AES-GCM, and stores encrypted bytes in `database/files/`.
4. Metadata and policy flags are stored in SQLite.
5. Recipient opens share link and verifies password (if required).
6. Backend validates expiry/one-time constraints, decrypts server-side, and streams file.
7. Download count and access log are updated.

## Encryption Lifecycle (Plain Language)

- Raw uploaded file bytes are never stored directly.
- On upload, the server generates a random nonce and encrypts bytes using your app key (`ENCRYPTION_KEY_B64`) with AES-GCM.
- Only the encrypted blob (nonce + ciphertext + auth tag) is saved on disk.
- During download, the server reads the blob, decrypts in memory, then streams plaintext to the authorized requester.
- Expired files are periodically deleted from both disk and database by the cleanup scheduler.

## Security Notes

- Use a strong random 32-byte encryption key in production.
- Keep `.env` private and out of source control.
- This project includes in-memory rate limiting (single-process baseline).
- Run behind HTTPS and a production-ready reverse proxy for deployment.
