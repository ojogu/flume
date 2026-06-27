# API Contract

This document describes the actual B2B API contract as implemented. The API is mounted at `/v1`.

---

## Authentication

Every request requires an `X-API-Key` header. Keys are generated on registration and stored hashed.

---

## `POST /v1/job`

Create a media processing job.

### Request Body

```json
{
  "source": {
    "type": "video",
    "uri": "https://example.com/video.mp4"
  },
  "pipeline": [
    { "operation": "trim", "params": { "start": 10.0, "end": 30.0 } }
  ],
  "outputs": [
    { "type": "generate_download_link" }
  ]
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source` | object | yes | `type` (video/audio) and `uri` (URL or upload URI) |
| `pipeline` | array | yes | Ordered list of operations (min 1). Each has `operation` (string) and optional `params` (dict) |
| `outputs` | array | no | Delivery targets. Defaults to `[{"type": "generate_download_link"}]` |

### Output Types

| Type | Description |
|------|-------------|
| `generate_download_link` | Returns a presigned GET URL for the final artifact |
| `upload` | Uploads the final artifact to a client-specified URL (`params.url`) |

### Response (201 Created)

```json
{
  "status": "success",
  "message": "Job created",
  "data": {
    "id": "uuid",
    "api_key_id": "uuid",
    "status": "pending",
    "source_uri": "https://example.com/video.mp4",
    "source_type": "video",
    "pipeline_steps": [...],
    "outputs": [...],
    "created_at": "...",
    "updated_at": "..."
  }
}
```

---

## `GET /v1/job/{job_id}`

Retrieve a job's status and result.

---

## `POST /v1/uploads/presign`

Request a presigned upload URL.

### Request Body

```json
{
  "original_filename": "my_video.mp4",
  "content_type": "video/mp4",
  "file_size": 104857600
}
```

### Response (201 Created)

```json
{
  "status": "success",
  "message": "Presigned upload URL generated",
  "data": {
    "upload_id": "uuid",
    "presigned_url": "https://...",
    "object_key": "uploads/...",
    "expires_at": "..."
  }
}
```

### Upload Flow

1. `POST /v1/uploads/presign` — get a presigned PUT URL
2. `PUT <presigned_url>` — upload file bytes directly to R2 (must match `content_type`)
3. `POST /v1/uploads/{upload_id}/complete` — confirm upload landed, attaches metadata

---

## `POST /v1/uploads/{upload_id}/complete`

Confirm an upload. No request body. Verifies the object exists in R2 via `head_object`, records metadata, transitions status from `pending` to `unattached`.

---

## 12 Operations

| Operation | Category | Input | Output | Key Params |
|-----------|----------|-------|--------|------------|
| trim | transformative | video, audio | video, audio | start, end |
| cut | transformative | video, audio | video, audio | segments |
| compress | transformative | video, audio | video, audio | quality |
| transcode | transformative | video | video | format |
| resize | transformative | video | video | width, height, preset |
| watermark | transformative | video | video | image_url, position |
| subtitle | transformative | video | video | file_url, auto |
| mute | transformative | video | video | — |
| join | combinatory | video, audio | video, audio | clips |
| extract_audio | conversion | video | audio | format |
| thumbnail | conversion | video | image | timestamp |
| gif | conversion | video | gif | start, end, fps |
