# Flume — Architecture Decisions & Tradeoffs

A running record of every significant decision made during the design of Flume, including what was considered, what was chosen, and why.

---

## 1. Architecture: Monolith vs. Microservices

**Decision: Monolith with clean internal boundaries**

**Considered:**
- Microservices — each service (downloader, processor, storage, bot) deployed and scaled independently
- Monolith — one deployable unit with code organized into discrete internal modules

**Tradeoffs:**
- Microservices offer independent scaling and deployment but introduce significant operational overhead: multiple services to deploy, orchestrate, monitor, and debug. For a project at this stage, that overhead slows everything down without meaningful benefit.
- A monolith with clean internal boundaries captures the architectural discipline — the downloader, processor, storage, and bot modules are separate and well-defined — without the infrastructure tax. Services can be extracted later if scale demands it.

**Why monolith:** Ship faster, learn the right abstractions, avoid premature operational complexity. This is how most real systems actually start.

---

## 2. Message Broker: RabbitMQ vs. Redis-as-Broker

**Decision: RabbitMQ as broker, Redis as caching layer**

**Considered:**
- Redis as both broker and cache (simpler, one less service)
- RabbitMQ as broker + Redis as dedicated cache (cleaner separation of concerns)

**Tradeoffs:**
- Redis-as-broker works and is simpler to set up, but Redis is a cache — using it as a message broker conflates two different responsibilities.
- RabbitMQ is purpose-built for message queuing. It gives you exchanges, routing keys, acknowledgment patterns, and dead-letter queues — concepts worth learning properly.
- Separating broker and cache means Redis does one thing well: job state, session data, rate limit counters.

**Why RabbitMQ + Redis:** Better learning value, cleaner architecture, and more representative of how production systems are built.

---

## 3. User Identity: Platform-Native vs. Unified Account

**Decision: Platform-native identities first, optional linking via web account**

**Considered:**

**Option A — Email as anchor:**
Web account is created first. Telegram/WhatsApp are linked to it via a verification flow. Clean and standard, but adds friction upfront — bot users have to sign up before getting any value.

**Option B — Phone number as anchor:**
Phone number is the universal key across WhatsApp, Telegram, and web. Natural fit for WhatsApp, but Telegram doesn't always expose phone numbers. Phone numbers also change. Requires SMS infrastructure.

**Option C — Optonal Linking:**
Each platform creates its own identity. Users get value immediately. Linking is optional and prompted after a completed task.

**Decision:** Option C, with Option A as the linking mechanism.

Platform-native identities on first use — no signup required. After a task is completed, users are prompted with a CTA to link their account to a web profile. Linking uses a short-lived token flow in both directions (bot → web, web → bot).

**Why:** User experience is the priority. Friction before value kills adoption. Most bot users won't link, and that's acceptable — the ones who care about cross-platform history will.

---

## 4. Account Linking Flow

**Decision: Token-based linking in both directions**

**Bot → Web (primary flow):**
After a completed task, the bot sends a CTA with a link containing a short-lived, single-use token tied to the platform identity. User clicks, lands on web, confirms email, accounts are linked.

**Web → Bot (reverse flow):**
User on the web clicks "Link Telegram" or "Link WhatsApp." Web generates a short-lived code. User sends the code to the bot. Bot confirms, accounts are linked.

**Both flows are supported** because users can discover Flume from either direction.

**Settings page on web shows:**
- Telegram — linked / not linked + link/unlink action
- WhatsApp — linked / not linked + link/unlink action
- One web account can be linked to both Telegram and WhatsApp simultaneously

**Constraints:**
- A platform identity can only be linked to one web account
- Tokens are short-lived and single-use to prevent abuse

---

## 5. Data Ownership: Job History Across Platforms

**Decision: Each platform owns its own jobs. Linking is done via a shared user_id foreign key.**

**Considered:**
- Migrating jobs to a central owner upon account linking — reassigning job records from platform identity to web account at link time
- Keeping jobs platform-native, connected via a foreign key to a central users table

**Why no migration:** Migration adds complexity without benefit. Every job already knows where it came from. Audit is straightforward — the platform origin is always clear. Cross-platform history is just a query across platform tables filtered by `user_id`.

**Data model:**
- `users` table — central web accounts, the linking anchor
- `telegram_users`, `whatsapp_users` tables — platform identities, each with a nullable `user_id` FK to `users`
- Jobs belong to their platform table. After linking, the platform identity has a `user_id`, so cross-platform queries are simple joins.

---

## 6. Output Delivery

**Decision: In-chat for small files, web URL for large files**

**Telegram:**
- Supports links and direct file uploads as input
- Output delivered in-chat for files under ~50MB
- Output delivered as a web URL for larger files

**WhatsApp:**
- Primarily link-based input due to platform file type and size constraints
- Output delivered in-chat for small, compatible files
- Output delivered as a web URL for large or incompatible files

**Web URL delivery:** Processed files are stored on Cloudflare R2. Each job gets a unique public URL on `flume.ojogulabs.xyz`. This page serves a functional role in the product — not just marketing. It's where large outputs live.

---

## 7. Event Sourcing

**Decision: Apply selectively to the job lifecycle only**

**Considered:**
- Full event sourcing across the entire system
- No event sourcing
- Selective event sourcing for the job lifecycle

**Why selective:** Full event sourcing adds significant complexity. The payoff — audit trails, temporal queries, replayable history — is most valuable where state transitions matter. The job lifecycle (`JobCreated → JobQueued → JobStarted → JobCompleted / JobFailed`) is a natural fit. The rest of the system doesn't need it.

---

## 8. API Authentication

**Decision: API key authentication for FlumeAPI**

Developers pass an API key in the request header (`X-API-Key`). Keys are generated on registration, stored hashed, and can be revoked and regenerated. Rate limiting is enforced per key.

Bot users (Telegram/WhatsApp) are identified by their platform identity — no API key required. The bot authenticates internally on their behalf.

---

## 9. Sub-product Naming

**Decision: FlumeAPI (B2B) + Flume (B2C)**

Earlier names MediaFlow and MediaBot were replaced. Sub-product names should feel like they belong to the Flume brand.

- **FlumeAPI** — the developer-facing REST API
- **Flume** — the consumer chat interface on Telegram and WhatsApp ("Flume on Telegram", "Flume on WhatsApp")

---

## Open Questions

- Permanent storage vs. expiring outputs — should paid tiers get permanent storage or longer expiry?
- Abuse prevention on the free tier — rate limiting strategy for heavy download jobs
- WhatsApp Business API access requires Meta approval — what's the fallback during review?
- Standalone domain before a serious B2B push — `flume.ojogulabs.xyz` works for now