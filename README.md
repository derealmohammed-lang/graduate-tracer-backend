# Graduate Tracer — FastAPI Backend

REST API for the Graduate Tracer app: authentication, graduate profiles,
employment/education/certification/business records, surveys, notifications,
and admin/super-admin management — backed by PostgreSQL via SQLAlchemy.

## Stack

- **FastAPI** + **Uvicorn**
- **PostgreSQL** via **SQLAlchemy 2.0** (sync) + **psycopg2**
- **Alembic** for migrations
- **JWT** (python-jose) + **bcrypt** (passlib) for auth
- **reportlab** / **openpyxl** for PDF / Excel report export

## 1. Prerequisites

- Python 3.11+
- A running PostgreSQL server (local, Docker, or hosted)

## 2. Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env: set DATABASE_URL to your PostgreSQL connection string and
# SECRET_KEY to a long random string.
```

Create the database (adjust to your Postgres setup):

```bash
createdb graduate_tracer
```

## 3. Run migrations

The first migration hasn't been generated yet (it depends on your DB being
reachable, which the sandbox that produced this code didn't have). Generate
and apply it once your `.env` points at a real database:

```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

From then on, after any model change:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

## 4. Seed starter data

Creates a super administrator account plus starter departments/programs:

```bash
python seed.py
```

This prints the super admin's email/password to the console — **change
that password** (or delete/recreate the account) before using this beyond
local development.

## 5. Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

- API root: http://localhost:8000
- Interactive docs (Swagger UI): http://localhost:8000/docs
- Alternative docs (ReDoc): http://localhost:8000/redoc

## 6. Flutter app

The Flutter app (`graduate_tracer_app.zip`) is now connected to this API — see
its README for the `--dart-define=API_BASE_URL=...` setup. No manual wiring
needed; just run this backend and point the app at it.

## Endpoints added while connecting the Flutter app

A few gaps surfaced once the app actually needed real data; these were added
on top of the original endpoint set:

- `GET /programs`, `GET /departments` — **unauthenticated**, used by the
  registration form so a new graduate can pick their program before they
  have an account.
- `GET /admin/employment`, `/admin/education`, `/admin/certifications`,
  `/admin/businesses` — cross-graduate list views (each row includes
  `graduate_name`/`admission_number`) for the admin management screens.
- `GET /admin/graduates/{id}/employment`, `.../education`,
  `.../certifications`, `.../businesses` — single-graduate record views for
  the admin Graduate Details screen.
- `GET /graduates/me` now returns a computed `program`, `department`,
  `graduation_year`, `employment_status`, `current_position`, and
  `profile_completion` instead of just the raw graduate row.
- `GET /surveys` now includes `has_responded` per survey.
- `GET /admin/audit-logs` now includes a resolved `user_name`.

## What's stubbed / left as TODO

- **Employment trend analytics** (`GET /analytics/employment-trend`) needs a
  time-series snapshot table (e.g. a scheduled job recording the employment
  breakdown monthly); it currently returns an empty placeholder.
- **File uploads** (profile photos, certificate attachments) — the `files`
  table and `FileRecord` model exist, but there's no upload endpoint yet.
  Add one using FastAPI's `UploadFile`, store to disk/S3, and record the
  URL in a `files` row.
- **Email delivery** for password reset — `create_password_reset_token`
  returns the raw token instead of emailing it. Wire up an email provider
  (SES, SendGrid, etc.) and send the token via a reset link instead.
- **Audit logging** — the `AuditLog` model and admin-facing endpoint exist,
  but nothing writes to it yet. Add a small helper (or SQLAlchemy event
  listener) that inserts a row whenever an admin creates/updates/deletes a
  record, and call it from the relevant routers.
- **Push notifications** (Firebase Cloud Messaging) — the in-app
  notification system (`notifications` / `user_notifications` tables) is
  fully wired; FCM push delivery on top of it is not implemented.
- **Refresh-token rotation / revocation** — refresh tokens are stateless
  JWTs today. For production, consider a denylist table keyed by a `jti`
  claim so tokens can be revoked (e.g. on logout or password change).

## Project structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app + router registration
│   ├── core/
│   │   ├── config.py           # Settings from environment variables
│   │   ├── security.py         # Password hashing, JWT create/verify
│   │   └── database.py         # SQLAlchemy engine/session/Base
│   ├── models/                 # SQLAlchemy ORM models (one file per domain)
│   ├── schemas/                # Pydantic request/response schemas
│   ├── api/                    # FastAPI routers (one file per domain)
│   ├── services/               # Business logic used by routers
│   └── utils/
├── alembic/                    # Migrations
├── seed.py                     # Starter data script
├── requirements.txt
└── .env.example
```
