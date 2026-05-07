# Flume — Learning Guide

## What You're Building

Flume is a video processing platform with two surfaces built on one shared backend:

- **FlumeAPI** — a REST API that lets developers submit video processing jobs programmatically
- **Flume** — a chat-based video editor running on Telegram and WhatsApp, powered by LLM

Users send a video link or file, describe what they want done, and get back a processed video — trimmed, compressed, joined, converted, or subtitled. Heavy work runs asynchronously in the background. Output is delivered in-chat for small files, via a web URL for large ones.

The system handles social video downloading (yt-dlp), media processing (FFmpeg), job queuing (Celery + RabbitMQ), cloud storage (Cloudflare R2/), and natural language intent parsing (LLM).

---

## What You'll Learn

### Asynchronous Processing & Job Queues
- How to design a job queue system where work is decoupled from the request that triggered it
- Celery task lifecycle: queuing, execution, retries, and failure handling
- Redis as a message broker — how it moves tasks between the API and workers
- Job state management: tracking `queued → processing → completed → failed`
- Webhook delivery on job completion

### Concurrency & Worker Scaling
- How worker concurrency works — running multiple tasks simultaneously on one machine
- Difference between I/O-bound and CPU-bound tasks, and why it matters for video processing
- Worker pool configuration and tuning
- Handling resource contention when multiple jobs run in parallel

### API Design & Auth
- RESTful API design principles — resource naming, HTTP methods, status codes
- API versioning (`/v1/`)
- API key authentication — generation, hashing, validation
- Rate limiting per key — token bucket or fixed window patterns
- Structured error responses with meaningful codes and messages
- Webhook design — signing payloads with HMAC-SHA256, delivery retries

### Media Processing Pipelines
- How FFmpeg works as a command-line tool and how to drive it from Python
- Building a pipeline of chained operations (trim → compress → watermark)
- Handling video metadata (duration, resolution, format, codec)
- Using yt-dlp to download video from social platforms and handling platform-specific changes
- Format transcoding and why codec choice matters for output size and compatibility
- Generating thumbnails, GIFs, and extracting audio tracks

### Cloud Storage & File Handling
- Integrating with object storage (Cloudflare R2 / Amazon S3) via the S3-compatible API
- Generating pre-signed URLs for secure, time-limited file access
- Managing file lifecycle — upload, retrieval, expiry, and deletion
- Handling large file transfers without loading everything into memory

### Bot Development
- Building a Telegram bot with webhook-based event handling
- WhatsApp Business API — message types, media handling, webhook verification
- Designing async bot interactions: acknowledge immediately, deliver result later
- Managing conversation state across multiple messages
- Voice note handling — receiving audio and passing it to a transcription service

### AI Integration
- Using LLM as an intent orchestrator — parsing ambiguous natural language into structured job parameters
- Designing prompts that extract reliable structured output (timestamps, operation types, parameters)
- Handling multi-turn context — "now do the same but shorter" refers to the previous job
- Integrating Whisper for audio transcription and feeding output into LLM
- Knowing when to ask a clarifying question vs. when to proceed with best-guess parameters

### Error Handling & Resilience
- Retry logic with exponential backoff for failed tasks
- Handling partial failures in chained operations
- Distinguishing recoverable errors (network timeout) from unrecoverable ones (invalid video format)
- Surfacing errors meaningfully — to API consumers via structured responses, to bot users via plain language

### Configuration & Secrets Management
- Separating config from code using environment variables
- Managing secrets (API keys, storage credentials, bot tokens) without hardcoding
- Environment-specific config (development vs. production)

### Code Organisation & Testability
- Structuring a monolith with clean internal boundaries — modules that could be extracted later if needed
- Writing code that is testable despite having external dependencies (FFmpeg, yt-dlp, Redis, S3)
- Mocking external services in tests
- Separation of concerns: routing, business logic, and I/O in distinct layers

---

## Why This Project Covers So Much

Most projects teach one or two of these concepts in isolation. Flume forces them to work together:

- The API teaches you request/response design and auth
- The job queue teaches you async processing and concurrency
- The media pipeline teaches you I/O-heavy work and external tool integration
- The bot teaches you event-driven architecture and stateful conversations
- LLM integration teaches you how to use AI as a functional component, not a gimmick
- Storage integration teaches you cloud infrastructure fundamentals

By the time Flume is built, you will have touched backend API design, distributed task processing, media engineering, cloud storage, bot development, and AI integration — all within one coherent system.