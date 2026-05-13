# ADR 001 — Choosing a Storage Vendor for Flume

**Status:** Accepted  
**Date:** 2026-05-07  
**Context:** Storage is a key component of Flume, considering we are a video processing platform, and choosing the best storage vendor is critical for our system.

---

## Decision

I came to a conclusion to use Cloudflare R2 as our storage vendor.

## Considered Options

- **Amazon S3** — AWS object storage, market leader, egress fees apply
- **Cloudflare R2** — Zero egress fees, generous free tier, S3-compatible
- **Byteship** — A new storage infrastrcture. It has a tight free model (5gb of storage, and no private url) which does not give us the flexiblity we need. 
Without private URLs, any user with the storage link can access any file — unacceptable for a platform where user A must not access user B's content. 

## Tradeoffs

**Why R2 was chosen:**

- **Egress cost** — AWS charges you for every GB that leaves their storage. So if 1000 users each download a 100MB processed video: that's 100GB of egress. AWS charges roughly $0.09 per GB — that's $9 just for delivery, on top of storage costs. The more users, the more this compounds. Cloudflare doesn't charge for egress. Those same 1000 users downloading 100MB each — $0 in egress fees. You only pay for storage itself.
- **Generous free tier** — Juxtaposed to other vendors, R2 provides more than a generous free tier for testing/launch. 10 GB storage, 1 million Class A operations (writes), and free egress — with no time limit, unlike S3's 12-month free tier or byteship 5gb storage for it's free tier
- **Buckets are private by default** — Cloudflare r2 storage are privates, which is exactly what we need for flume. Each user should have it's designated storage, which interfering with another. Compared to Byteship which doesn't offer private url in it's free tier
- **Presigned URLs** — for both upload and download — time-limited, with the expiry embedded in the URL itself.
- **S3-compatible API** — mature SDK, well documented

**What was accepted as tradeoff:**

- Vendor lock-in
- Own the entire storage layer — presigned URL generation, lifecycle rules, file expiry, usage tracking (R2 just handles the byte storage and egress)
- No managed per-customer isolation — you handle that in your application layer

## Consequences

### Positive
- We can handle as much videos with little cost considering the generous free tier and no egress cost R2 offers.

### Negative
- We own a large part of this layer, like building the per customer isolation, lifecycle rules, file expiry, etc.

### Risks Mitigated
- Storage is an integral part of the system, since we are a video processing system, and videos are basically large compared to other medias. Choosing R2 helps us process and store more data due to its generous free tier.

### Risks Accepted
- We are going to handle most of the business logic in this layer. Functionalities like per customer isolation; user A should not be able to access user B videos, lifecycle rules, file expiry, usage tracking.

---

## Four Questions

| Question | Answer |
|---|---|
| What breaks if I get this wrong? | This layer is core. The cost of not choosing a good vendor for our use case could affect us in so many ways from losing user data, operational cost |
| What did I choose and what did I reject? | Chose Cloudflare R2; rejected AWS S3 due to egress costs and Byteship due to it's storage limit |
| How do I know it's working? | I will measure this by storage capacity, how much videos we can store on the free tier before needing to upgrade, the latency and bandwidth |
| What assumptions am I making that could be wrong? | All of these decisions are marely from documentation and other people experience, so I could be wrong about everything, until I implement and have users test it |

---

## Notes

Egress/Bandwidth means data leaving storage and going out to the internet.

The journey of a file in Flume:

1. User sends a video link to Flume
2. Flume downloads it, processes it with FFmpeg
3. Output gets stored in your storage bucket
4. User requests the file — it travels from your storage bucket, across the internet, to the user's device

That last step — bytes leaving storage to reach the user — is egress (this is where AWS S3 charges + storage).