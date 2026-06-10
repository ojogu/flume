# Flume

> A dual-surface video processing platform — a REST API for developers and a chat-based bot for everyone else.

Flume abstracts the complexity of video processing behind two interfaces: a programmable **REST API** (FlumeAPI) and a natural-language **Telegram bot**. Both share a unified backend powered by FastAPI, Celery, FFmpeg, and a full OpenTelemetry observability stack.

---

## Documentation

The project's knowledge base lives in [`docs/`](./docs). It is a first-class part of the codebase.

| Path | Description |
|------|-------------|
| [`docs/architecture.md`](./docs/architecture.md) | High-level system design, tech stack, data flow, and design principles |
| [`docs/prd.md`](./docs/prd.md) | Product Requirements Document — goals, personas, features, API contract, bot flows |
| [`docs/tradeoffs.md`](./docs/tradeoffs.md) | Architecture Decision Log — 10 key tradeoffs with rationale |
| [`docs/design/`](./docs/design/) | Detailed subsystem designs: auth flows, observability pipeline, logging, API key hierarchy, video operation registry, frontend design system |
| [`docs/decisions/`](./docs/decisions/) | Architecture Decision Records (ADRs) for storage vendor, API key model, and workflow orchestration |
| [`docs/learn.md`](./docs/learn.md) | Concepts and patterns the project teaches |
| [`docs/docs-info.md`](./docs/docs-info.md) | Guide to writing and maintaining this documentation system |

---

## Features

- **Dual Authentication** — Google OAuth 2.0 and email magic links for the dashboard; API key auth (`X-API-Key`) for programmatic access
- **JWT with Refresh Rotation** — Short-lived access tokens, refresh token blacklisting via Redis, automatic client-side refresh
- **Async Job Queue** — Celery workers with dedicated `default` and `email` queues, RabbitMQ broker, retry logic, and Flower monitoring
- **Video Processing Pipeline** — 13 operations across three categories: transformative (trim, cut, compress, transcode, resize, watermark, subtitle, mute, convert-to-audio), combinatory (join), and terminal (extract-audio, thumbnail, gif)
- **Download Engine** — yt-dlp integration for downloading from social media links
- **FFmpeg Processor** — Subprocess-based FFmpeg operations with pipeline validation
- **Cloud Storage** — Cloudflare R2 (S3-compatible) with presigned URLs for private-by-default access
- **LLM Integration** — Google ADK, Gemini, LiteLLM, and Claude ready for natural-language bot commands and voice-note transcription (Whisper)
- **Email Service** — Jinja2-rendered transactional emails sent via Resend
- **Structured Logging** — structlog with three output pipelines: console (colorful dev), file (JSON), and OpenTelemetry bridge to Loki
- **Full Observability Stack** — OpenTelemetry auto-instrumentation → OTel Collector → Grafana (datasources pre-configured for Prometheus, Loki, Tempo) — all running in Docker Compose
- **Telegram Bot** — Full bot interface (via `python-telegram-bot`) with live demo; WhatsApp integration via Twilio planned
- **API Key Management** — Create, list, update, revoke, and scope API keys with SHA-256 hashing and `flm_` prefix for secret scanning

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌───────────────────┐
│   React SPA  │────▶│  FastAPI      │◀────│  Telegram Bot     │
│  (Vite/TS)   │     │  (Uvicorn)    │     │  (python-telegram)│
└─────────────┘     └──────┬───────┘     └───────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │PostgreSQL│ │  Redis   │ │RabbitMQ  │
        │(Aiven)   │ │ (Cache)  │ │(Broker)  │
        └──────────┘ └──────────┘ └────┬─────┘
                                       │
                              ┌────────▼────────┐
                              │  Celery Workers  │
                              │ (default, email)  │
                              └────────┬─────────┘
                                       │
                              ┌────────▼────────┐
                              │  FFmpeg / yt-dlp │
                              │  Cloudflare R2   │
                              └─────────────────┘

Observability (all services):
  FastAPI / Celery ──▶ OpenTelemetry SDK ──▶ OTel Collector ──▶ Grafana
                                                      ├──▶ Tempo (traces)
                                                      ├──▶ Loki (logs)
                                                      └──▶ Prometheus (metrics)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12, FastAPI, Uvicorn |
| **Async Workers** | Celery 5, RabbitMQ |
| **ORM / Database** | SQLAlchemy 2.0 (async), asyncpg, PostgreSQL (Aiven), Alembic |
| **Cache / Session** | Redis 7 |
| **Frontend** | React 19, TypeScript 5, Vite 6, Tailwind CSS 4 |
| **UI Components** | @base-ui/react, shadcn/ui, Framer Motion |
| **Auth** | Google OAuth 2.0, PyJWT, bcrypt, Fernet encryption |
| **Video** | FFmpeg (subprocess), yt-dlp |
| **AI / LLM** | Google ADK, Gemini, LiteLLM |
| **Email** | Resend, Jinja2 |
| **Messaging** | python-telegram-bot, Twilio |
| **Storage** | Cloudflare R2 (S3-compatible) |
| **Logging** | structlog |
| **Observability** | OpenTelemetry, Grafana, Loki, Tempo, Prometheus |
| **Orchestration** | Docker Compose |
| **Package Mgmt** | uv (Python), npm (JS) |
| **Linting** | Ruff (Python), ESLint (TS — planned) |

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12 (optional, for local backend dev)
- Node.js 20+ (optional, for local frontend dev)

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/ojogu/flume.git
   cd flume
   ```

2. **Configure environment variables**

   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your secrets:
   #   - DATABASE_URL (PostgreSQL async)
   #   - REDIS_URL
   #   - JWT_SECRET_KEY
   #   - ENCRYPTION_KEY (Fernet key)
   #   - CLIENT_ID / CLIENT_SECRET (Google OAuth)
   #   - RESEND_KEY (email)
   #   - TELEGRAM_KEY
   ```

3. **Start all services**

   ```bash
   docker compose up -d
   ```

   This launches: backend (port 5001), frontend (port 5174), Celery worker, Celery beat, Flower (port 5555), RabbitMQ, Redis, and the full observability stack — OTel Collector, Grafana (port 3001), Loki, Tempo, Prometheus.

4. **Run database migrations**

   ```bash
   ./migrate.sh "initial schema"
   ```

5. **Open the app**

   - Frontend: [http://localhost:5174](http://localhost:5174)
   - API health check: [http://localhost:5001/api/v1/root](http://localhost:5001/api/v1/root)
   - Grafana dashboards: [http://localhost:3001](http://localhost:3001) (anonymous access enabled)
   - Flower (Celery monitoring): [http://localhost:5555](http://localhost:5555)

---

## Project Structure

```
flume/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── main.py             # App entry point, lifespan, middleware, routers
│   │   ├── auth/               # JWT tokens, OAuth, magic link routes & service
│   │   ├── route/              # API route handlers (API keys)
│   │   ├── service/            # Business logic (user, api_key, google, downloader, processor, storage, llm, jobs)
│   │   ├── model/              # SQLAlchemy models (User, MagicLinkToken, ApiKey, Project)
│   │   ├── schema/             # Pydantic request/response schemas
│   │   ├── core/               # DI, email service, custom exceptions, templates
│   │   └── utils/              # Config, DB engine, Redis, telemetry, logging, crypto, responses, error handlers
│   ├── celery_app/             # Celery app, config, tasks (send_email)
│   ├── migrations/             # Alembic migrations
│   └── observability/          # OTel Collector, Prometheus, Loki, Tempo, Grafana configs
├── web/                        # React SPA frontend
│   └── src/
│       ├── pages/              # Landing, Login, Callback, Dashboard, Bot, Pricing, Docs
│       ├── components/         # Common, UI (shadcn), landing, bot, pricing sections
│       ├── stores/             # Zustand auth store
│       ├── lib/                # API client, design tokens, utilities
│       ├── hooks/              # useTheme
│       └── router/             # React Router routes
├── bot/                        # Telegram/WhatsApp bot (in progress)
├── docs/                       # Architecture docs, PRD, ADRs, design specs, tradeoffs
├── docker-compose.yml          # All services orchestration
├── deploy.sh                   # Deployment script (pull → build → restart)
└── migrate.sh                  # Alembic migration helper
```

---

## API Reference

All endpoints are prefixed with `/api/v1`.

### Health

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/root` | None | Health check |

### Authentication

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/auth/login` | None | Get Google OAuth authorization URL |
| GET | `/api/v1/auth/callback` | None | Google OAuth callback → issues JWT tokens |
| GET | `/api/v1/auth/magic-link` | None | Send magic link email |
| GET | `/api/v1/auth/magic-link/verify` | None | Verify magic link token → issues JWT tokens |
| GET | `/api/v1/auth/me` | Access Token | Get current user profile |
| POST | `/api/v1/auth/logout` | Refresh Token | Blacklist refresh token |
| POST | `/api/v1/auth/refresh-token` | Refresh Token | Issue new access + refresh tokens |

### API Keys

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/keys` | Access Token | Create a new API key |
| GET | `/api/v1/keys` | Access Token | List all API keys |
| GET | `/api/v1/keys/{key_id}` | Access Token | Get a specific API key |
| PATCH | `/api/v1/keys/{key_id}` | Access Token | Update API key name/expiry |
| DELETE | `/api/v1/keys/{key_id}` | Access Token | Revoke (soft-delete) an API key |

---

## Development

### Running the backend locally

```bash
cd backend
uv venv && source .venv/bin/activate
uv sync
uv run uvicorn src.main:app --reload --port 5000
```

### Running the frontend locally

```bash
cd web
npm install
npm run dev          # Vite dev server → http://localhost:5173
```

The Vite dev server proxies `/api` requests to `http://localhost:5000`.

### Database migrations

```bash
./migrate.sh "description of change"
```

### Linting

```bash
cd backend && uv run ruff check .
```

---

## Deployment

```bash
./deploy.sh
```

This pulls the latest code, builds the frontend, rebuilds the frontend Docker image, and restarts all containers. The backend runs with `--reload` and volume mounts for development.

---

## Observability

The observability stack is pre-configured and runs alongside the application:

| Service | URL | Purpose |
|---------|-----|---------|
| Grafana | `http://localhost:3001` | Dashboards with pre-configured Prometheus, Loki, and Tempo datasources |
| Flower | `http://localhost:5555` | Celery worker monitoring |
| Loki | — | Log aggregation from structlog → OTel Collector |
| Tempo | — | Distributed tracing (48h retention, service graphs, span metrics) |
| Prometheus | — | Metrics collection via OTel Collector remote write |

The OpenTelemetry SDK auto-instruments FastAPI, httpx, Celery, Redis, and SQLAlchemy. Logs, traces, and metrics are correlated via trace IDs, enabling click-through from log entries to trace spans in Grafana.

---

## Contributing

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

feat(auth): add Google OAuth callback handler
fix(worker): handle FFmpeg timeout gracefully
docs(api): document video operation registry
```

Lint with `ruff check` before committing. See [`agent.md`](./agent.md) for AI-assisted development conventions.

---

## License

MIT
