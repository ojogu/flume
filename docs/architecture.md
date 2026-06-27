# Architecture

> High-level system design — the conceptual layers, module layout, API surface, and pipeline flow.

## What Flume Is

Flume is managed media processing infrastructure surfaced through two interfaces:

- **FlumeAPI** — a REST API for programmatic media processing
- **Flume** — a chat-based video editor on Telegram and WhatsApp

## Three-Layer Model

Flume's operations are classified along two independent axes:

| Layer | Audience | Purpose |
|-------|----------|---------|
| **Capability** | Developers | Product taxonomy — what Flume offers (Transform, Extract, Combine, etc.) |
| **Operation** | Developers + Consumers | Concrete executable operations (trim, resize, thumbnail, etc.) |
| **Execution** | Pipeline Engine | Validation semantics — how the engine processes artifacts |

See [three-layer-architecture.md](./design/three-layer-architecture.md) for the full model.

## Tech Stack

| Component | Technology |
|---|---|
| API Framework | FastAPI |
| Task Queue | Celery + Redis |
| Video Processing | FFmpeg |
| Social Downloads | yt-dlp |
| Storage | Cloudflare R2 (primary) / Amazon S3 (fallback) |
| Bots | python-telegram-bot, WhatsApp Business API |
| AI | LLM (intent parsing), Whisper (transcription) |

## Module Layout

```
backend/src/
├── route/          # FastAPI route handlers (job, upload, auth)
├── service/        # Business logic (jobs, upload, storage, validation, processor, etc.)
├── model/          # SQLAlchemy ORM models (job, upload, api key, user)
├── schema/         # Pydantic request/response schemas
├── core/           # App config, DI dependencies, exception base
├── utils/          # Registry, config, logging, DB, Redis, crypto, response helpers
├── auth/           # Authentication logic
└── main.py         # FastAPI application entry point
```

## API Surface

All endpoints are mounted under `/v1` and require an `X-API-Key` header.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/job` | Create a media processing job |
| GET | `/v1/job/{id}` | Get job status and result |
| POST | `/v1/uploads/presign` | Request a presigned upload URL |
| POST | `/v1/uploads/{id}/complete` | Confirm an upload landed in R2 |

## Pipeline Flow

```
Client → POST /v1/job
              ↓
        1. Intake (validation gates)
              ↓
        2. Dispatch (enqueue to Celery)
              ↓
        3. Execution Loop (Celery worker)
              ↓
        4. Completion (process outputs → mark done)
```

### 1. Intake

Five sequential validation gates in `src/service/validation.py`:

| Gate | Check |
|------|-------|
| Schema | Request body well-formed, source valid, pipeline non-empty |
| Registry | Every operation name exists in the registry |
| Params | Required params present, types match, bounds respected |
| Type compatibility | Each step's output type matches the next step's input type |
| Pipeline spec | Build enriched spec with category, capability, input/output types |

Jobs are persisted in `pending` status.

### 2. Dispatch

The job ID is published to Celery + Redis. The API response returns immediately with the job ID and status. All processing is asynchronous.

### 3. Execution Loop

The Celery worker reads the enriched pipeline spec from the job record. It walks steps by index — for each step it fetches the input artifact, dispatches FFmpeg processing, writes the output artifact to R2, and advances to the next step.

### 4. Completion

After the final operation finishes, the job's **outputs** (delivery targets) are processed — generate a presigned download link, upload to a client-specified URL, etc. Then the job is marked `complete`.

## Upload Flow

```
POST /v1/uploads/presign  →  PUT <presigned_url>  →  POST /v1/uploads/{id}/complete
```

1. Client requests a presigned PUT URL (declares filename, content-type, optional size hint)
2. Client uploads file bytes directly to Cloudflare R2 via the presigned URL
3. Client confirms the upload — the service verifies the object exists in R2 and transitions status from `pending` to `unattached`

Uploaded files can be referenced as `source.uri` in a job request.

## Operation Registry

Defined in `src/utils/registry.py`. A hardcoded catalog of 12 operations with:

- **Category** — execution semantics (transformative, combinatory, conversion)
- **Capability** — product taxonomy (transform, extract, combine, generate)
- **Input/output types** — artifact type compatibility
- **Param definitions** — validation rules per parameter

See [operation-registry.md](./design/operation-registry.md) for the full reference, [api-contract.md](./design/api-contract.md) for request/response schemas, and [workflow-orchestrator-pipeline.md](./design/workflow-orchestrator-pipeline.md) for orchestrator internals.

---

*See [tradeoffs.md](./tradeoffs.md) for architectural decisions and [three-layer-architecture.md](./design/three-layer-architecture.md) for the capability model.*
