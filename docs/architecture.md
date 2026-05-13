# Architecture

> High-level system design — why Flume is built the way it is.

## Overview

Flume is a video processing platform with two surfaces built on one shared backend:

- **FlumeAPI** — a REST API for programmatic video processing
- **Flume** — a chat-based video editor on Telegram and WhatsApp

The core insight: video processing is technically complex, but the demand for it is simple. Flume abstracts that complexity for both audiences.

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python, JavaScript (React)|
| API Framework | FastAPI |
| Task Queue | Celery + Redis |
| Video Processing | FFmpeg |
| Social Downloads | yt-dlp |
| Storage | Cloudflare R2 (primary) / Amazon S3 (fallback) |
| Bots | python-telegram-bot, WhatsApp Business API |
| AI | LLM (intent), Whisper (transcription) |

## High-Level Flow

```
Client (Flume / FlumeAPI)
        ↓
    FastAPI
        ↓
    Celery + Redis
        ↓
  Workers (Download → Process → Store)
        ↓
    Cloudflare R2 / S3
        ↓
  Output → Chat or Web
```

## Internal Modules

> Physical locations: `backend/` → `src/backend/`, `bot/` → `src/bot/`, `web/` → `src/web/`

```
flume/
├── backend/           # FastAPI application
│   ├── api/          # route handlers, auth, rate limiting
│   ├── jobs/         # Celery tasks, job state management
│   ├── processor/    # FFmpeg operations
│   ├── storage/      # R2/S3 abstraction
│   ├── downloader/   # yt-dlp wrapper, platform handling
│   └── ai/           # Claude + Whisper integration
├── bot/              # Telegram and WhatsApp handlers
└── web/              # React frontend (flume.ojogulabs.xyz)
```

## Key Design Decisions

See [tradeoffs.md](./tradeoffs.md) for a full record of every architectural decision made, including what was considered, what was chosen, and why.

## Principles

- **Monolith with clean boundaries** — one deployable unit, but modules are well-separated. Services can be extracted later if scale demands it.
- **Async by default** — all video processing runs in the background via Celery. No synchronous endpoints.
- **Intent over configuration** — the bot layer uses AI to parse natural language into structured operations. Users don't learn syntax.
- **Output via web URL** — large files are not delivered inline. They live on `flume.ojogulabs.xyz` with a functional role in the product.

---

*Architecture changes should be documented in [tradeoffs.md](./tradeoffs.md).*