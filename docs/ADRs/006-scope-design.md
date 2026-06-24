# ADR 006 — Scope Design for Public API

**Status:** Accepted  
**Date:** 2026-06-17  
**Context:** Users have different needs — one might just need to trim and join, another might need compression and storage. Scopes give developers granular control of what they can and cannot do. The goals are to enforce least-privilege access (security posture), create pricing tiers that map cleanly to capability sets, audit what a key was used for, and revoke granular access without killing an entire integration.

---

## Decision

No scopes for now.

## Considered Options

- **Implement and integrate scopes** — Build a full scope system for different operations from the start.
- **Keep it lean** — All operations are open to all API keys; no scope enforcement.

## Tradeoffs

**Why no scopes was chosen:**

For an MVP and at our scale, scopes are over-engineering. A scope system is a trust boundary and a monetization tool. It makes more sense when we have a handful of user needs with distinct capability requirements. For now, an API with all functionalities exposed is sufficient.

**What was accepted:**

- A strong reduction in monetization strategy / pricing tiers based on scopes — we need to find other means to place value on.
- API keys that are exploited must be revoked entirely — revoking a key without scopes kills the entire integration.

## Consequences

### Positive
- Reduce overall engineering overhead of managing scopes.

### Negative
- Weakens monetization strategy / pricing tier differentiation.
- Key exploitation requires full key revocation, killing the entire integration rather than just the abused scope.

### Risks Mitigated
- We stay lean, avoiding complexity of handling scopes from the auth layer to docs. We can iterate and build faster.

### Risks Accepted
- Key revocation could disrupt developer experience — generating a new key rather than just removing the compromised scope.

---

## Four Questions

| Question | Answer |
|---|---|
| What breaks if I get this wrong? | Great impact on monetization strategy and developer experience. |
| What did I choose and what did I reject? | Chose no scopes for now until we have a handful of developers and can iterate towards scoped APIs. |
| How do I know it's working? | An API key gives unrestricted access to all functionalities — simplicity is the metric. |
| What assumptions am I making that could be wrong? | That scopes are over-engineering for an MVP. We might hit a large userbase sooner than expected, and retrofitting scopes carries cost. |
