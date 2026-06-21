# yt-dlp Layer

Core download layer that wraps yt-dlp to handle media extraction across supported platforms. Outputs structured artifacts consumed by the FFmpeg pipeline.

## Supported Platforms

- YouTube (videos, playlists, post-stream VODs, channels)
- Instagram
- TikTok
- Twitter/X
- Facebook
- Vimeo
- Dailymotion
- Twitch (VODs)
- Reddit

yt-dlp supports ~1500 extractors, but platform breakage is common. A `/platforms` public endpoint returns a curated list of actively tested platforms rather than the raw extractor list. This list is maintained via periodic real-URL test runs. Entries include: name, base URL pattern, supported content types (single video, playlist, VOD), and known limitations.

## Pipeline Phases

### 1. URL Validation

yt-dlp handles redirects, partial links, and video ID resolution. No custom URL parsing needed. A lightweight platform detection check can reject unsupported platforms early.

### 2. Content Type Detection

Three content types:

- **Single video** — routes to a direct job
- **Playlist** — routes to a fan-out job (1 parent → N children)
- **Post-stream VOD** — treated as single video

Active livestreams are rejected with "not supported" (deferred to v2).

### 3. Metadata Extraction

Extract full metadata from the source without downloading. For playlists, returns a parent object with an `entries` list. For single videos, returns a flat object.

The extracted metadata must contain ≥80% of what the FFmpeg layer needs. FFmpeg reads from the artifact metadata — it never runs `ffprobe` on the downloaded file.

### 4. Playlist Feature Gating

| Plan | Max videos per playlist |
|------|------------------------|
| Free | 10 |
| Pro | 40 |
| Max | 100 |

Checked after metadata extraction, before any job is created. Over-limit requests are rejected immediately with `count` + `limit` in the error response — no truncation, no partial processing.

### 5. Job Creation

**Single video:** one job, one DB write, one queue push.

**Playlist:** fan-out pattern — one parent job spawns N independent child jobs. Each child has its own lifecycle, can fail independently, and produces its own artifacts. Failure in one child does not affect others.

Parent job states: `Spawning → In Progress → Completed | Partial`

Child jobs can be tracked independently via webhook events, polling, or dashboard.

### 6. Codec Selection (Internal Policy)

Not exposed to the API. Default preference: **H.264 for video, AAC for audio** — compatibility first, efficiency second. This ensures the FFmpeg layer can process output cleanly without re-encoding surprises.

### 7. Format Selection (User-Facing)

After metadata extraction, yt-dlp returns available formats. The developer can optionally request a quality preference:

- `best` — highest available resolution (default)
- `720p`, `1080p`, `480p` — specific target
- `smallest` — lowest resolution

If the exact resolution is unavailable, pick the closest available option. Never fail the job over format availability.

### 8. Artifact Schema

Contract between the yt-dlp layer and FFmpeg layer. Metadata is extracted once in phase 3 and stored on the artifact. FFmpeg reads from this — never re-inspects the file.

```jsonc
{
  "id": "art_abc123",                                // string
  "job_id": "job_xyz456",                            // string
  "source": {
    "platform": "youtube",                          // string
    "video_id": "dQw4w9WgXcQ",                     // string
    "url": "https://youtube.com/watch?v=dQw4w9WgXcQ"  // string
  },
  "file": {
    "path": "/artifacts/abc123.mp4",               // string
    "size_bytes": 52428800,                        // number
    "container": "mp4"                             // string
  },
  "media": {
    "duration_seconds": 212,                       // number
    "width": 1920,                                  // number
    "height": 1080,                                 // number
    "fps": 30,                                      // number
    "video_codec": "h264",                         // string
    "audio_codec": "aac",                          // string
    "video_bitrate": 2500000,                      // number
    "audio_bitrate": 128000                        // number
  },
  "status": "completed",                            // string
  "created_at": "2026-06-20T12:00:00Z"              // string
}
```
