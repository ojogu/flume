# ADR 004 — Internal vs Public API Separation

**Status:** Accepted  
**Date:** 2026-06-15  
**Context:** API documentation is a core part of any backend system. But this presents the challenge of having internal routes/services surfaced to the public. We want a clear separation between our internal APIs (what our frontend calls) and our public API (for our 3rd party consumers), not just in documentation but also URL structure.

---

## Decision

Enforce a three-router pattern — three separate `APIRouter` instances:

- **`internal_api`** — holds all routes for our internal APIs, under the `/v1/internal` prefix
- **`public_api`** — holds all routes for our public API, under the `/v1/public` prefix
- **`main`** — the head FastAPI app that includes both routers

## Considered Options

- **Three-router pattern (chosen)** — Each API surface gets its own router. Only the public router is exported as an OpenAPI spec. Our frontend reads that spec without needing filtering or rule-based logic — no internal spec exists to leak through.

- **Single app instance with tag-based filtering at export time** — One router for everything, tags distinguish internal vs public, filter at spec-export time. Less upfront structure but relies on discipline in tagging and export logic.

## Tradeoffs

**Why three-router pattern:**
- Clear separation of concerns — only public APIs are exported as OpenAPI spec
- Our frontend reads the public spec without worrying about filtering or rule-based logic, since internal routes were never in the spec to begin with

**What was accepted:**
- Managing three router instances, including routing the right routes to the right instance without mixing them up

## Consequences

### Positive
- Structural isolation
- Per-instance docs
- Granular control of each instance
- Proper URL distinction (`/v1/internal` vs `/v1/public`)

### Negative
- Managing three router instances

### Risks Mitigated
- Internal API surfaces will not leak into public specs

### Risks Accepted
- Confusion around which routes belong in which router instance

---

## Four Questions

| Question | Answer |
|---|---|
| What breaks if I get this wrong? | Internal routes exposed to the public — a significant security risk |
| What did I choose and what did I reject? | Chose the three-router pattern; rejected a single instance with tag-based filtering at export time |
| How do I know it's working? | Review the generated API spec and confirm only public routes are accounted for |
| What assumptions am I making that could be wrong? | That internal routes won't accidentally be added to the public router — human error in route placement is the biggest risk |
