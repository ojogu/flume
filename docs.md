# Docs Rollout Log

Tracking the `docs-site` restructure — what was removed, why, where the
content went, and what is deliberately deferred.

## Why

The docs at `docs-site/content/docs/` drifted out of sync with the product.
They described SDKs that don't exist, endpoints that were never built,
statuses that were renamed, and placeholder pages with no content. This log
records every decision so the rollout stays auditable.

## Rule

Any factual claim in the docs (URL, endpoint, header, field, param, error
code, status, event) is copied from the backend source, not written from
memory. Sources are cited per page in the entries below.

---

## Phase 1 — Structure + reader-facing pages

### Kept / rewritten

- `docs/index.mdx` — rewritten from a broken-link marketing page into a
  plain overview with real links.
- `docs/get-started/quickstart.mdx` — rewritten. Removed fake SDK tabs
  (`@flume/node`, `flume-python`, `flume-go` — no SDKs exist), fake sandbox
  key `fl_test_`, and the fake `/v1/auth/verify` endpoint. Now curl-only
  against the real API.
- `docs/get-started/authentication.mdx` — rewritten. Removed the marketing
  prose and the fake `/v1/auth/verify` call; now documents the real
  `X-API-Key` header, `flm_` prefix, SHA-256-at-rest, and the real
  `GET /v1/utils/verify-key` endpoint.
- `docs/get-started/concepts.mdx` — rewritten. Folds in the good orphan
  content from `core-concepts.mdx` with corrected facts:
  - Job status `complete` → `succeeded` (real: `pending`, `processing`,
    `succeeded`, `partial_success`, `failed`, `dead`).
  - The pipeline is optional — an empty pipeline is a valid download-only
    job (schema `pipeline: list = Field(default_factory=list)`, no minimum).
  - Removed the "max 10 pipeline steps" claim — no such limit exists in the
    schema or validation.
  - Added the missing `meme` operation (registry has 13, not 12).

### Nav (`docs/meta.json`)

- Pruned dead entries: `guides`, `recipes`, `operations`, `sdks`,
  `deployment`, `examples` (all stub or dead-end pages, removed in Phase 5).
- Ordered for the final structure; `operations`, `common-tasks`, and
  `errors` are added back in the phases that create them.

### Deferred

- Remotion video guides (per-operation/per-recipe videos) — parked.
  `flume-marketing-video/` (untracked Remotion project) is unchanged.
- SDKs, sandbox keys, rate limits, versioning, pagination docs — not
  documented until they exist.

---

## Phase 2 — API reference: core (index, jobs, uploads)

**Completed:**
- `api-reference/index.mdx` — base URL, X-API-Key, envelope `{status,message,data,role}`, HTTP codes, pagination, error codes
- `api-reference/jobs.mdx` — POST/GET /job, GET /job/{id}, GET /job/{id}/download, statuses, enriched pipeline_steps, timecode normalization note
- `api-reference/uploads.mdx` — presign + complete flow, UploadResponse fields, upload lifecycle (pending→unattached→attached), cleanup warning, own-R2 alternative
- `api-reference/meta.json` — trimmed to index, jobs, uploads

**Build:** `next build` passes (57 pages, no errors).

## Phase 3 — API reference: webhooks + utils, operations

**Completed:**
- `api-reference/webhooks.mdx` — all 7 webhook endpoints, event catalog (7 events; note: `job.cancelled`, `job.retried`, `ping` are in the EventType enum but missing from the static catalog served by `/utils/events`)
- `api-reference/utils.mdx` — `/utils/platforms`, `/utils/events`, `/utils/verify-key`
- `operations.mdx` (root) — all 13 ops with exact registry params, timecode format note, meme Gate-2 code bug callout
- `meta.json` — added `operations` to top-level nav; added `webhooks`, `utils` to api-reference nav

**Build:** `next build` passes (60 pages, no errors).

## Phase 4 — Common tasks, errors, architecture

**Completed:**
- `errors.mdx` — error envelope, HTTP codes, error_code catalog (20 codes from exception.py), validation gate catalog (Gates 1–5 + 1.5 join check), common scenarios table
- `common-tasks.mdx` — 3 worked examples: trim+compress, extract audio, thumbnail (complete curl + response + poll + download flow)
- `architecture/index.mdx` — "How Flume works": submission → validate → dispatch → orchestrator → download → pipeline → delivery → cleanup
- `meta.json` — added `common-tasks`, `errors` before `architecture`

**Build:** `next build` passes (62 pages, no errors).

## Phase 5 — Fold-in cleanup, deletions, build

**Completed:**

**Build script:**
- `package.json` `build` changed from `npm run validate-spec && npm run generate-api && next build` to `next build`
- `scripts/generate-docs.ts` deleted (would have wiped hand-written api-reference/)

**Webhooks fixes:**
- `webhooks/event-catalog.mdx` — added `job.retried` event; fixed payload example to use `succeeded` instead of `completed`
- `webhooks/subscriptions.mdx` — all paths prefixed with `/v1`
- `webhooks/delivery.mdx` — path prefixed with `/v1`
- `webhooks/index.mdx` — path prefixed with `/v1`
- `api-reference/webhooks.mdx` — fixed signature header from `Flume-Signature` to `X-Signature-256`

**Deletions:**
- `guides/` — all stale stub pages (analyze, combine, extract, generate, transform, their subdirs, meta.json)
- `recipes/` — index.mdx (dead)
- `examples/` — index.mdx (dead)
- `deployment/` — index.mdx (dead)
- `sdks/` — go.mdx, javascript.mdx, python.mdx, meta.json (SDKs don't exist)
- `operations/` — entire directory with all old stub sub-pages (replaced by new `operations.mdx`)
- `authentication/` — api-keys.mdx, index.mdx, meta.json, rotating-keys.mdx (superseded by `get-started/authentication.mdx`)
- `api-reference/health/` — generated page from stale openapi.json
- `api-reference/errors.mdx`, `api-reference/operations.mdx`, `api-reference/pipelines.mdx`, `api-reference/rate-limits.mdx` — generated placeholders
- `architecture/jobs.mdx`, `architecture/lifecycle.mdx`, `architecture/operation-registry.mdx`, `architecture/pipeline-execution.mdx`, `architecture/storage.mdx`, `architecture/webhooks.mdx`, `architecture/yt-dlp.mdx`, `architecture/meta.json` — all replaced by single `architecture/index.mdx`
- Orphan stubs at root: `getting-started.mdx`, `core-concepts.mdx`, `pagination.mdx`, `versioning.mdx`, `operations-reference.mdx`, `rate-limits.mdx`
- Empty `changelog/` dir removed (file `changelog.mdx` kept)
- `scripts/generate-docs.ts` deleted

**Duplicate title fix:**
- Removed body `# H1` from `quickstart`, `concepts`, `authentication`, `api-reference/index`, `architecture/index`, `changelog` — the frontmatter `title` is rendered by `<DocsTitle>` so the title showed twice
- `index.mdx` — `title: Home` → `title: Flume`; removed body `# Flume`
- Deleted orphan `get-started/uploads.mdx` (marketing page, unlinked since Phase 1)

**Hyperlink + stale-content pass:**
- Added `platforms.mdx` — dynamic "Supported Platforms" page (yt-dlp-driven, managed via dashboard); linked from nav and from `api-reference/utils.mdx`
- "dashboard" now links to `https://flume.ojogulabs.xyz/dashboard` in `authentication.mdx` (x2) and `quickstart.mdx`
- Plain-text references became links: "Operations reference", "Errors reference", "upload API" (concepts + jobs), `GET /v1/utils/events` (webhooks), index "Transform/Combine/Convert/Extend" → `/docs/operations`, "five validation gates" + "webhook subscribers" (architecture)
- Removed stale callouts: operations Gate-2 "code bug" (fixed), api-reference/webhooks "not yet in the static catalog" (fixed)
- Event count 7 → 10 in `api-reference/webhooks.mdx` (table now lists all 10) and `api-reference/utils.mdx`
- `quickstart.mdx` `[Operations]` link retargeted from `/docs/api-reference` → `/docs/operations`
- `/v1` prefix restored on test-endpoint paths in `webhooks/testing.mdx` and `webhooks/event-catalog.mdx`
- Fixed fake host/key in `webhooks/testing.mdx` (`api.flume.example.com`/`your-api-key` → real host + `flm_` placeholder)
- `changelog.mdx` — 12 → 13 operations; removed fake "Sandbox and Live API key modes"; rewrote platform claim to note yt-dlp/dashboard-driven list

**Build:** `next build` passes (24 pages).

**Diagram → image swap:**
- Converted the two user-supplied diagrams (JPEG-in-PNG payload) to true PNGs via ffmpeg at `docs-site/public/images/architecture.png` and `docs-site/public/images/webhook.png`; removed the mislabeled originals from `docs-site/` root
- Replaced the ASCII "High-level flow" diagram (`architecture/index.mdx`) and "How It Works" diagram (`webhooks/index.mdx`) with `![...](/images/...)` references
- Images are imported by the fumadocs remark-image plugin → bundled to hashed `/docs/_next/static/media/...` URLs
- Required `images.unoptimized: true` in `next.config.mjs`: the default `next/image` optimizer endpoint (`/_next/image`) is not under the `/docs` prefix, so nginx (`location /docs`) would not reach it. With optimization off, `<img src>` points directly at `/docs/_next/static/media/...` (same path pattern as the JS/CSS chunks, verified served)
- **Build:** `next build` passes (24 pages); built HTML confirmed to reference the bundled images

**Deploy note:** images are bundled at build time — rebuild + restart the docs container (`docker compose build docs && docker compose up -d docs`) to pick up the new diagrams.

**Future-proof copy pass:**
- Removed hardcoded operation counts — `operations.mdx` ("13 operations", category counts) and `concepts.mdx` ("There are 13 operations") now describe a growing catalog; the `Count` column in the categories table was replaced with the operations list per category
- `changelog.mdx` keeps the exact "13 core operations" for v1.0.0 (historical record); its platform line now says platforms are tested and curated
- `platforms.mdx` reframed from "dynamic / changes as yt-dlp updates" to **curated and admin-tested** (each platform validated before enablement, capabilities + limitations registered, active-only exposure) — matches the backend admin-CRUD implementation
- `api-reference/utils.mdx` updated to match ("added after validation rather than mirrored automatically")

---

## Deferred items

These features exist in the product but are not yet documented. They are
deferred until they are ready.

| Item | Reason deferred |
|------|----------------|
| SDKs (`@flume/node`, `flume-python`, `flume-go`) | No SDKs exist yet |
| Sandbox/test keys (`fl_test_...`) | No sandbox environment — `fl_test_` is fake; only `flm_` live keys |
| Rate limits | Not yet implemented |
| Pagination docs | Pagination exists in `GET /v1/job` (page/per_page) but not yet documented separately |
| API versioning | Not yet implemented |
| Remotion video guides (per-op, per-recipe) | `flume-marketing-video/` Remotion project exists (untracked); videos are a future content project |
| Per-operation deep-dive guides | Covered by `operations.mdx` + `common-tasks.mdx` for now |
| Per-recipe examples | Covered by `common-tasks.mdx` for now |
| `mute` operation docs | Documented in `operations.mdx` but has no params — confirm if that's correct |

## Code bugs found during docs verification

| Location | Bug | Effect | Status |
|----------|-----|-------|--------|
| `backend/src/service/validation.py` Gate 2 | Error message omits `meme` from valid ops | Misleading error when `meme` submitted | **Fixed** — `meme` added to list |
| `backend/src/service/util.py` `EVENT_CATALOG` | Missing `job.cancelled`, `job.retried`, `ping` events | Events can be subscribed to but don't appear in `GET /utils/events` | **Fixed** — 3 events added |
| `backend/src/public/route/utils.py` `verify_api_key` docstring | Says "does NOT update last_used_at" but it actually does | Stale docstring | **Fixed** — docstring updated |

---

## Contact & support rollout

**Backend — contact form API (live on port 5001):**
- Fixed the email task-name bug: `src/core/email_service.py` enqueued `"celery_app.task.send_email_task"`, but the Celery task is registered as `"jobs.email.send"` (no `celery_app/task.py` exists) → magic-link emails silently failed to enqueue. Now `"jobs.email.send"`.
- New `SUPPORT_TO_EMAIL=nkangprecious26@gmail.com` in `backend/.env` + `support_to_email` in `src/utils/config.py`.
- New `POST /v1/support/contact` (public, no auth) in `src/public/route/support.py` — body `{name, email, subject, message}` (`src/public/schema/support.py`, validation via Pydantic `EmailStr`); renders `src/core/templates/contact_submission.html` via `send_contact_email()` and enqueues the Celery email task.
- Verified: imports clean in backend container, endpoint returns success envelope, worker received task, task `SUCCESS`, Resend returned a send receipt.
- **Note:** backend runs with `--reload` + bind mount, so the new route is already live.

**Contact channels unified:**
- Email → `support@ojogulabs.xyz` everywhere: `docs/layout.tsx` (mailto replaced by `/docs/support` link), `web/.../PricingHero.tsx` (was `hello@flume.dev`), `web/.../ErrorPage.tsx` + `NotFoundPage.tsx` (were `support@flume.ai`)
- WhatsApp dummy `wa.me/000000000` → `https://wa.me/2349065011334` in Footer, landing HeroSection, bot HeroSection, bot CTASection (x2), bot PlatformsSection; removed all `DUMMY LINK` comments
- Footer GitHub `#github` → `https://github.com/ojogu/flume`
- Fixed broken docs nav link "Start processing" → `https://flume.ojogulabs.xyz/signup` (no such route) → `/login`

**Dashboard:**
- New `web/src/pages/dashboard/SupportPage.tsx` — contact form posting to `/v1/support/contact` + email/WhatsApp fallbacks; route `/dashboard/support` added; Support nav item (desktop + mobile)
- "Contact support" links added to DashboardErrorPage, DashboardNotFoundPage, JobErrorCallout

**Docs:**
- New client `ContactForm` component (`docs-site/src/components/common/ContactForm.tsx`) registered in the MDX renderer (`app/docs/[[...slug]]/page.tsx`)
- New `content/docs/support.mdx` (form + email/WhatsApp/GitHub fallbacks), added to `meta.json`; docs nav Support → `/docs/support`
- **Build:** docs `next build` now **25 pages**; web `npm run build` passes
- **Deploy note:** rebuild + restart docs container and web container to pick up the new support page, nav links, and unified contact links

---

## Pricing block

Subscription pricing and payment/feature limits are **not decided yet** — pricing is temporarily blocked.

**Single switch:** `web/src/lib/pricing.ts` — `PRICING_BLOCKED = true`. Flip to `false` to unblock.

While blocked:
- Navbar (desktop + mobile) and Footer Pricing links fire a toast ("Subscription pricing and payments are coming soon.") instead of navigating
- `/pricing` route renders `PricingBlockedPage` (`PricingComingSoon` banner) instead of `PricingPage`
- Landing `PricingSection` renders the `PricingComingSoon` banner instead of the placeholder tiers

**Unblock steps:** set `PRICING_BLOCKED = false` in `web/src/lib/pricing.ts`, then rebuild + restart the web container. Existing pricing components (`PricingHero`, `ComparisonTable`, `PricingFAQ`, tier data) are untouched and just get rendered again.

**Deploy note:** rebuild + restart web container to ship the block.
