# LedgerLens

Turn scattered payment screenshots into a secure, organized financial ledger.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![JWT](https://img.shields.io/badge/Auth-JWT-000000?style=flat&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Render](https://img.shields.io/badge/Deploy-Render-46E3B7?style=flat&logo=render&logoColor=white)](https://render.com/)
[![Neon](https://img.shields.io/badge/Database-Neon-00E599?style=flat&logo=postgresql&logoColor=white)](https://neon.tech/)

## Overview

LedgerLens is a full-stack web application that lets a user upload a batch of unsorted payment screenshots — bank transfers, e-wallet notifications, QRIS payments, receipts — and automatically turns them into a structured, deduplicated, searchable transaction ledger, tied securely to their own account.

Built for a two-week hackathon by a solo developer. Designed to work end to end: authenticate, upload, review, export — not a single-purpose script.

## Table of Contents

- [Problem and Solution](#problem-and-solution)
- [Live Demo](#live-demo)
- [Technology Stack](#technology-stack)
- [Documentation](#documentation)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Roadmap](#roadmap)
- [Team](#team)
- [License](#license)

## Problem and Solution

Small business owners and individuals receive payment confirmations from multiple disconnected sources and typically save them as screenshots directly in their phone gallery, mixed in with unrelated photos. Reconciling these into a usable financial record means manually scrolling, reading, and re-entering each one.

LedgerLens removes that manual step. A user uploads a batch of photos as-is; the system classifies which images are payment proofs, extracts the transaction details, flags likely duplicates, and stores everything under the user's own account for later review and export.

Full problem framing and technical rationale are documented in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Live Demo

| | |
|---|---|
| Application | `<deployment URL to be added>` |
| Demo account | `<demo credentials to be added, if applicable>` |
| Video walkthrough | `<link to be added>` |

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Backend framework | FastAPI | REST API, request validation, routing |
| Language | Python 3.11+ | Application logic |
| Database | PostgreSQL (hosted on Neon) | Persistent, relational storage |
| ORM / Migrations | SQLAlchemy / SQLModel, Alembic | Data modeling and schema migrations |
| Authentication | JWT (access + refresh tokens) | Stateless, per-user session security |
| Password security | Passlib (bcrypt) | Password hashing |
| AI / Vision | Google Gemini (vision-capable) | Screenshot classification and data extraction |
| Structured output validation | Pydantic v2 | Schema-enforced AI output |
| Frontend templating | Jinja2 | Server-rendered HTML |
| Styling | Tailwind CSS | Accessible, high-contrast UI for non-technical users |
| Interactivity | HTMX | Partial page updates without a JavaScript framework |
| Image processing | Pillow, imagehash | Resizing, compression, perceptual duplicate detection |
| Fuzzy matching | RapidFuzz | Counterparty name similarity in deduplication |
| Reporting | openpyxl, fpdf2 | Excel and PDF export |
| Containerization | Docker | Consistent local and production environments |
| Hosting | Render (app), Neon (database) | Free-tier-friendly cloud deployment |

## Documentation

| Document | Contents |
|---|---|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Problem framing, pipeline stages, design decisions and trade-offs |
| [`docs/SCHEMA.md`](docs/SCHEMA.md) | Database schema, entity relationships, migration notes |
| [`docs/API.md`](docs/API.md) | REST API endpoint reference, request and response formats |
| [`docs/DESIGN.md`](docs/DESIGN.md) | UI/UX design principles, screen flow, accessibility considerations |

## Project Structure

```
ledgerlens/
├── app/
│   ├── main.py                    # Application entry point
│   ├── core/
│   │   ├── config.py                # Settings and environment variables
│   │   ├── security.py               # JWT issuance/verification, password hashing
│   │   └── database.py               # Database engine and session management
│   ├── models/                     # SQLAlchemy/SQLModel ORM models
│   │   ├── user.py
│   │   └── transaction.py
│   ├── schemas/                    # Pydantic request/response schemas
│   │   ├── user.py
│   │   └── transaction.py
│   ├── api/
│   │   ├── deps.py                   # Shared dependencies (get_current_user, etc.)
│   │   └── routes/
│   │       ├── auth.py                 # Register, login, token refresh
│   │       ├── transactions.py         # Upload, list, export
│   │       └── users.py
│   ├── services/                   # Business logic, independent of route handlers
│   │   ├── vision_service.py         # Classification and extraction
│   │   ├── dedup_service.py          # Deduplication logic
│   │   └── report_service.py         # Excel/PDF generation
│   ├── templates/                  # Jinja2 templates
│   └── utils/
│       └── image_processing.py       # Resize, compress
├── alembic/                        # Database migrations
├── tests/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── SCHEMA.md
│   ├── API.md
│   └── DESIGN.md
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
├── render.yaml
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11 or newer
- Docker (for local PostgreSQL) or an existing PostgreSQL instance
- An API key for a vision-capable language model (Google Gemini)

### Installation

```bash
git clone https://github.com/Xhyro-v/ledgerlens.git
cd ledgerlens
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Local Database

```bash
docker run --name ledgerlens-db \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=ledgerlens \
  -p 5432:5432 -d postgres:16
```

### Configuration

```bash
cp .env.example .env
```

Fill in the required values (see [Environment Variables](#environment-variables)).

### Run Migrations

```bash
alembic upgrade head
```

### Start the Application

```bash
uvicorn app.main:app --reload
```

The application will be available at `http://localhost:8000`.

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `JWT_SECRET` | Secret key used to sign JWT tokens | Yes |
| `JWT_ALGORITHM` | Signing algorithm (default `HS256`) | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | No |
| `GOOGLE_API_KEY` | API key for the vision model | Yes |
| `CONFIDENCE_THRESHOLD` | Minimum confidence before auto-confirming an extracted record | No |

`DATABASE_URL` points to a local PostgreSQL instance during development and to the hosted Neon instance in production. The application code reads this value from the environment in both cases; no code changes are required between environments.

## Deployment

The application is deployed as two independent, free-tier-friendly services:

- **Database:** [Neon](https://neon.tech) — serverless PostgreSQL, connection string generated on project creation.
- **Cloud File Storage** [Cloudinary](https://cloudinary.com) - File storage to storage jpeg or png files
- **Application:** [Render](https://render.com) — deployed from this repository, configured via `render.yaml`.

Deployment steps:

1. Create a Neon project and copy its connection string.
2. Create a Render web service linked to this repository.
3. Set `DATABASE_URL`, `JWT_SECRET`, and `GOOGLE_API_KEY` as environment variables in the Render dashboard.
4. Trigger a deploy. Render builds the Docker image and starts the service automatically on push.
5. Run `alembic upgrade head` against the production database before first use.

Full details in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Roadmap

- Automatic cloud-folder synchronization to remove the manual upload step.
- Multi-currency support.
- Category-level expense tagging.
- Password reset and email verification flows.

## Team

| Role | Name |
|---|---|
| Developer | `Naufal Azhar` |

## License

Developed for hackathon submission purposes. License terms to be determined.