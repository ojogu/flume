# ADR 005 — Upload Flow Decision

**Status:** Accepted
**Date:** 2026-06-24
**Context:** How should users upload their media resources — directly to our object storage (R2) or via our server?

---

## Decision

Users upload directly to R2 via a presigned short-lived URL. The server generates the URL, the client uploads directly — the server never touches the bytes.

## Considered Options

- **Direct upload via presigned URL (chosen)** — Server generates a time-limited presigned URL, client uploads directly to R2
- **Backend relay** — Client uploads to server, server uploads to R2

## Tradeoffs

Direct upload scales well for video and audio — no bandwidth passes through our server. The tradeoff is implementation complexity: two endpoints instead of one, edge cases like network failure, retries, and multipart uploads.

## Consequences

### Positive
- No bandwidth load on our server; files go directly to R2
- Scales well for heavy media resources
- Faster uploads
- Our server becomes a middleman — auth gate, metadata generator, ingestion trigger

### Negative
- Increases the API surface (two endpoints vs. one)
- More edge cases to handle at the client layer

### Risks Mitigated
- Slow uploads caused by double-hop (client → server → R2)
- Server resource contention (memory, disk) during large file transfers

### Risks Accepted
- Added complexity of presigned URL generation and lifecycle management
- Client must handle retry and multipart logic

---

## Four Questions

| Question | Answer |
|---|---|
| What breaks if I get this wrong? | Users cannot upload media — the first step of the entire system breaks. No files in, no processing out. |
| What did I choose and what did I reject? | Chose direct upload via presigned URL. Rejected backend relay to avoid bandwidth bottlenecks. |
| How do I know it's working? | Files land in R2 successfully and are available for internal processing. |
| What assumptions am I making that could be wrong? | I don't know. |

---

*See [README](./readme.md) for the full documentation guide.*
