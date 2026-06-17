# WebDissect

A website reconnaissance tool: DNS records, SSL/TLS certificate inspection,
technology fingerprinting and HTTP endpoint mapping (from uploaded HAR files).

- Backend-Code: `backend/` (FastAPI, SQLAlchemy, SQLite)
- Frontend-Code: `frontend/` (Angular 21)

Projektdokumentation: [projektmanagement/README.md](projektmanagement/README.md)

## Quick start (Docker Compose)

```bash
docker compose up --build
```

Then open <http://localhost:8080>. nginx serves the Angular build and proxies
`/api` to the backend container.

Configuration lives in `.env` (JWT secret, Resend API key, DB filename). With a
placeholder `RESEND_KEY`, OTP codes are **not emailed** — they are written to the
backend container logs (`docker compose logs backend-server`) so the login flow
stays usable locally.

## Local development

Backend (Python 3.12+):

```bash
cd backend/server
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
DB_DIR=./db ENV=development python -m app   # serves on :6767
```

Frontend (Node):

```bash
cd frontend
npm install
npm start   # ng serve on :4200, proxies /api -> :6767 via proxy.conf.json
```

## API

Base path: `/api`. Every response uses the envelope
`{ "data": <T>, "message": <string>, "isSuccess": <bool> }`.

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| POST | `/auth/register` | – | Send an OTP to a `@htlstp.at` email |
| POST | `/auth/code/submit` | – | Submit OTP, returns a JWT token |
| POST | `/auth/login` | – | Email + password login, returns a JWT |
| GET | `/auth/me` | ✓ | Current user |
| PATCH | `/auth/me` | ✓ | Set / change password |
| GET | `/projects` | ✓ | List the user's projects |
| POST | `/projects` | ✓ | Create a project (`name`, `domain`) |
| GET | `/projects/{id}` | ✓ | Project + DNS / certs / tech / endpoints |
| PATCH | `/projects/{id}` | ✓ | Update name / domain |
| POST | `/projects/{id}/upload` | ✓ | Upload a HAR file (≤ 10 MB) |
| POST | `/projects/{id}/analysis/start` | ✓ | Run the analysis |

Interactive OpenAPI docs are available at `/docs` on the backend.
