# Flume — Product Requirements Document

**Version:** 1.0  
**Last Updated:** May 2026  
**Products:** FlumeAPI (B2B API) · Flume (B2C Chat Interface)  
**Platform:** flume.ojogulabs.xyz

---

## 1. Overview

Flume provides managed media processing infrastructure built on a single shared backend. It exposes the same core infrastructure through two distinct interfaces:

- **FlumeAPI** — a developer-facing REST API that eliminates media infrastructure overhead
- **Flume** — a consumer-facing chat assistant for natural language video editing, running on Telegram and WhatsApp

The core insight driving both products: media processing is technically complex but the demand for it is simple. Developers don't want to manage FFmpeg pipelines. Users don't want to install editing software. Flume abstracts the complexity for both audiences.

---

## 2. Goals

- Build a production-grade asynchronous media processing pipeline
- Expose that pipeline as a clean, well-documented REST API (FlumeAPI)
- Layer a natural language interface on top for consumer use (Flume)
- Deliver processed output in-chat for small files; via web URL for large files
- Establish a web presence that serves a functional role in the output delivery flow

---

## 3. Non-Goals (Current Version)

- Desktop or mobile native apps
- Real-time (synchronous) media processing
- Video hosting or streaming (output is stored temporarily, not hosted permanently)
- Social media publishing integrations
- Multi-language support (English only at launch)

---

## 4. Users

### FlumeAPI Users
- Backend developers building media features into their products
- Startups that need media processing without managing infrastructure
- Automation tools and content pipelines
- Platforms that serve user-generated content

### Flume Users
- Casual users who want to download or clip social media videos
- Content creators repurposing video for different platforms
- Social media managers handling high volumes of clips
- Users in mobile-first markets where messaging apps are the primary interface

---

## 5. Architecture

Flume uses a **monolith with clean internal boundaries**. One deployable unit, with code organized into discrete modules — not microservices. This captures good architectural discipline without operational overhead.

**Stack:**
- Language: Python
- API Framework: FastAPI
- Task Queue: Celery + Redis
- Video Processing: FFmpeg
- Social Download: yt-dlp
- Storage: Cloudflare R2 (primary) / Amazon S3 (fallback)
- Bot Frameworks: python-telegram-bot, WhatsApp Business API

**High-Level Flow:**

```
Flume / External API Clients
            ↓
        FastAPI (API Layer)
            ↓
        Celery + Redis (Job Queue)
            ↓
     Workers (Download → Process → Store)
            ↓
     Cloudflare R2 / S3 (Storage)
            ↓
     Output URL → Chat or Web
```

**Internal Modules:**
- `api/` — route handlers, auth, rate limiting
- `jobs/` — Celery tasks, job state management
- `downloader/` — yt-dlp wrapper, platform handling
- `processor/` — FFmpeg operations
- `storage/` — R2/S3 abstraction
- `bot/` — Telegram and WhatsApp handlers
- `ai/` — Claude integration, Whisper transcription

---

## 6. FlumeAPI — Developer API

### 6.1 Authentication

| Feature | Description |
|---|---|
| API Key Auth | Every request requires a valid `X-API-Key` header |
| Key Generation | Keys generated on registration, stored hashed |
| Key Revocation | Users can revoke and regenerate keys via dashboard |
| Scoped Keys | Future: read-only vs. full-access keys |

### 6.2 Video Ingestion

**Endpoint:** `POST /v1/jobs`

Accepts two input types:

**Remote URL (link-based)**
```json
{
  "input": {
    "type": "url",
    "url": "https://www.instagram.com/reel/..."
  },
  "operations": [...]
}
```

**Direct File Upload**
```json
{
  "input": {
    "type": "upload",
    "file_key": "uploads/uuid.mp4"
  },
  "operations": [...]
}
```

**Supported Platforms (URL input):**
- YouTube
- Instagram (Reels, Posts)
- TikTok
- X (Twitter)
- Facebook (public videos)

### 6.3 Video Processing Operations

All operations are expressed as a list in the job request. They execute in order.

| Operation | Parameters | Description |
|---|---|---|
| `trim` | `start`, `end` (timestamps) | Clip a segment from the video |
| `cut` | `segments` (array of ranges) | Remove specific segments |
| `join` | `clips` (array of file keys or URLs) | Concatenate multiple videos |
| `compress` | `quality` (low/medium/high) | Reduce file size |
| `transcode` | `format` (mp4, webm, mov) | Convert to target format |
| `resize` | `width`, `height` or `preset` | Resize dimensions |
| `watermark` | `image_url`, `position` | Overlay a watermark image |
| `thumbnail` | `timestamp` | Extract a still frame |
| `gif` | `start`, `end`, `fps` | Convert segment to GIF |
| `subtitle` | `file_url` or `auto: true` | Burn in subtitles |
| `mute` | — | Strip audio track |
| `extract_audio` | `format` (mp3, aac) | Export audio only |

**Example job request:**
```json
{
  "input": {
    "type": "url",
    "url": "https://www.youtube.com/watch?v=..."
  },
  "operations": [
    { "type": "trim", "start": "00:01:00", "end": "00:02:30" },
    { "type": "compress", "quality": "medium" },
    { "type": "watermark", "image_url": "https://...", "position": "bottom-right" }
  ],
  "webhook_url": "https://yourapp.com/webhooks/flume"
}
```

### 6.4 Async Job System

All processing is asynchronous. No synchronous processing endpoints exist.

**Job Lifecycle:**

```
queued → processing → completed
                    → failed
```

**Job Response (on creation):**
```json
{
  "job_id": "job_abc123",
  "status": "queued",
  "created_at": "2026-05-04T10:00:00Z"
}
```

**Polling endpoint:** `GET /v1/jobs/{job_id}`

```json
{
  "job_id": "job_abc123",
  "status": "completed",
  "output": {
    "url": "https://flume.ojogulabs.xyz/output/job_abc123.mp4",
    "size_bytes": 4200000,
    "expires_at": "2026-05-11T10:00:00Z"
  }
}
```

**Webhooks:**
- On job completion or failure, POST to `webhook_url` if provided
- Payload includes job ID, status, output URL, and error details if failed
- Signed with HMAC-SHA256 for verification

### 6.5 Output Handling

- Processed files stored on Cloudflare R2
- Output URLs are public but non-guessable (UUID-based paths)
- Files expire after 7 days (configurable per tier)
- Large files (>50MB) are not delivered inline — URL only

### 6.6 Developer Infrastructure

| Feature | Detail |
|---|---|
| Rate Limiting | Per API key, configurable by tier |
| Usage Tracking | Request count, processing minutes, storage used |
| Job History | `GET /v1/jobs` — list all jobs with filters |
| Error Codes | Structured error responses with codes and messages |
| Versioning | API versioned at `/v1/` |
| SDK | Python SDK (first), Node.js SDK (later) |

### 6.7 API Tiers (Planned)

| Tier | Jobs/month | Max file size | Storage | Price |
|---|---|---|---|---|
| Free | 50 | 100MB | 7-day expiry | $0 |
| Starter | 500 | 500MB | 30-day expiry | TBD |
| Pro | Unlimited | 2GB | 90-day expiry | TBD |

---

## 7. Flume — Consumer Chat Interface

### 7.1 Platforms

| Platform | Input Support | Output Support | Notes |
|---|---|---|---|
| Telegram | Links + file uploads | In-chat (≤50MB) + web URL | Full feature support |
| WhatsApp | Links (primarily) | In-chat (≤16MB) + web URL | File type/size constraints apply |

Voice notes are supported on both platforms. Audio is transcribed via Whisper and treated as a natural language editing command.

### 7.2 Core User Flows

**Flow 1: Download**
1. User sends a social media link
2. Bot acknowledges and queues download
3. Bot returns video in-chat (if small) or web URL (if large)

**Flow 2: Edit**
1. User sends a link or file + editing instruction
2. Bot parses instruction via Claude
3. Bot returns processed output

**Flow 3: Multi-step editing**
1. User sends a link
2. Bot downloads and confirms
3. User sends follow-up instructions ("now trim from 1:00 to 2:00")
4. Bot applies edit to the cached file
5. User continues or requests delivery

**Flow 4: Voice command**
1. User sends a voice note describing the edit
2. Bot transcribes via Whisper
3. Proceeds as a text instruction

### 7.3 Supported Commands (Natural Language)

Users do not need to learn syntax. Claude parses intent from plain language.

| User says | Operation triggered |
|---|---|
| "Download this" | Download from URL |
| "Cut from 1:00 to 2:30" | Trim |
| "Remove the first 30 seconds" | Trim |
| "Join these two clips" | Join |
| "Make it smaller" | Compress |
| "Convert to GIF" | GIF conversion |
| "Add subtitles" | Auto-subtitle via Whisper |
| "Make it vertical" | Resize to 9:16 |
| "Extract the audio" | Audio extraction |
| "Add my watermark" | Watermark (if image on file) |
| "Give me a thumbnail" | Thumbnail extraction |

### 7.4 Output Delivery Logic

| Output size | Telegram | WhatsApp |
|---|---|---|
| ≤ 50MB | Delivered in-chat | Delivered in-chat (if compatible format) |
| > 50MB | Web URL | Web URL |
| Unsupported format | Converted + in-chat | Web URL |

Web URLs point to the user's output page on `flume.ojogulabs.xyz`.

### 7.5 Claude Integration

Claude serves as the **intent orchestrator**, not a simple command parser.

Responsibilities:
- Parse ambiguous natural language into structured job parameters
- Handle multi-turn context ("now do the same but louder" refers to the previous clip)
- Ask clarifying questions when intent is genuinely ambiguous
- Surface errors in human-readable language ("The timestamp you gave is beyond the video length")
- Decide which operations to chain based on a single instruction

Claude is not used for video processing itself — only for understanding and orchestrating.

### 7.6 Bot Features

| Feature | Description |
|---|---|
| Async acknowledgment | Bot confirms receipt immediately, processes in background |
| Job status updates | Bot messages user when job completes or fails |
| Clip history | Users can retrieve recent outputs with `/history` |
| Shareable links | All outputs get a public web URL |
| Watermark (free tier) | Flume watermark applied to free-tier outputs |
| Group chat support | Bot works in group chats (Telegram) |
| `/help` command | Lists supported operations and examples |
| `/cancel` command | Cancels a queued job |

### 7.7 WhatsApp-Specific Constraints

- File uploads limited by WhatsApp to specific types and sizes (video, audio, image — varies by client)
- Primary input model for WhatsApp is link-based
- Output files must be delivered as compatible types (MP4 for video, MP3 for audio)
- Large outputs always delivered as web URL, not in-chat attachment

---

## 8. Web Presence

The web interface at `flume.ojogulabs.xyz` serves a **functional role** in the product, not just marketing.

### 8.1 Output Delivery Page

- Each processed job gets a unique public URL
- Page shows: video preview, file details, download button
- Expires in line with job storage policy
- Branded Flume page — reinforces product identity at point of delivery

### 8.2 Landing Page

- Product overview for FlumeAPI and Flume
- API documentation link
- Pricing tiers
- "Start building" CTA → API key registration

### 8.3 Developer Dashboard (Planned)

- API key management
- Job history and status
- Usage metrics (requests, processing minutes, storage)
- Webhook configuration

---

## 9. AI Features

### 9.1 Included in Core

| Feature | Mechanism |
|---|---|
| Natural language parsing | Claude (Flume) |
| Voice command support | Whisper transcription → Claude parsing |
| Human-readable errors | Claude generates error messages |

### 9.2 Optional / Advanced

| Feature | Mechanism | Priority |
|---|---|---|
| Auto subtitle generation | Whisper | High |
| Highlight detection | Claude + frame analysis | Medium |
| Video summarization | Claude + transcript | Medium |
| Auto short-form clip generation | Claude + highlight detection | Low |

---

## 10. Deliverables

### Phase 1 — Core Pipeline (MVP)

- [ ] FastAPI server with job creation and status endpoints
- [ ] API key authentication
- [ ] Celery + Redis job queue
- [ ] yt-dlp downloader module
- [ ] FFmpeg processing module (trim, compress, transcode)
- [ ] Cloudflare R2 storage integration
- [ ] Webhook delivery on job completion
- [ ] Job history endpoint
- [ ] Basic rate limiting

### Phase 2 — Flume (Telegram)

- [ ] Telegram bot setup and webhook handler
- [ ] Claude integration for intent parsing
- [ ] Link-based download flow
- [ ] Natural language editing flow
- [ ] In-chat delivery for small files
- [ ] Web URL delivery for large files
- [ ] Job status messaging
- [ ] `/history`, `/help`, `/cancel` commands

### Phase 3 — Flume (WhatsApp)

- [ ] WhatsApp Business API integration
- [ ] Voice note transcription via Whisper
- [ ] WhatsApp-specific output format handling
- [ ] Web URL fallback for large/incompatible outputs

### Phase 4 — Web & Dashboard

- [ ] Output delivery page (per-job public URL)
- [ ] Landing page
- [ ] Developer dashboard (API keys, usage, job history)
- [ ] Webhook configuration UI

### Phase 5 — Advanced Features

- [ ] Auto subtitle generation
- [ ] Highlight detection
- [ ] Video summarization
- [ ] Auto short-form clip generation
- [ ] Python SDK
- [ ] Billing and tier enforcement

---

## 11. Success Metrics

| Metric | Target |
|---|---|
| Job completion rate | > 95% |
| Average job processing time (trim/compress) | < 60 seconds |
| Bot response acknowledgment time | < 3 seconds |
| API uptime | > 99% |
| Output delivery success rate | > 98% |

---

## 12. Open Questions

- Permanent storage vs. expiring outputs — should paid tiers get permanent storage or just longer expiry?
- Abuse prevention — how do we handle users spamming large download jobs on free tier?
- WhatsApp Business API access — requires Meta approval; what's the fallback during review?
- Custom domain — `flume.ojogulabs.xyz` works for build phase; standalone domain before B2B push?

---

*Flume is a real product. Decisions are made with production users and scale in mind.*