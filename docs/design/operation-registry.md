# Operation Registry

The operation registry is the authoritative list of every operation Flume supports — what each one is called, what it accepts as input, what it produces as output, what params it takes, and what position it's allowed to occupy in a pipeline. This is what the pipeline spec is built on. The intake stage consults it when building and validating a submitted job.

---

## Operation Entry

Each operation defines:

| Field | Description |
|-------|-------------|
| **Name** | `trim`, `compress`, `extract_audio`, etc. |
| **Input type** | What artifact type it consumes — `video`, `audio`, or both |
| **Output type** | What artifact type it produces |
| **Allowed params** | What configuration it accepts and their types |
| **Position constraints** | Where in the pipeline it's valid |

---

## Operation Categories

Flume's 13 operations are grouped into 3 categories:

| Category | Operations |
|----------|------------|
| **Transformative** | trim, cut, compress, transcode, resize, watermark, subtitle, mute, convert_to_audio |
| **Combinatory** | join |
| **Terminal** | extract_audio, thumbnail, gif |

### Transformative

Operations that take one input artifact and produce one output artifact of the same or compatible type. The pipeline continues after them. They modify, reshape, or enrich the artifact without changing the fundamental nature of the job. The majority of operations fall here.

### Combinatory

Operations that take multiple input artifacts and merge them into one output artifact. They are structurally different from transformative operations because they require more than one source — their params carry the additional inputs explicitly. The pipeline continues after them. `join` is the only combinatory operation in V1.

### Terminal

Operations that derive a new artifact type from the pipeline and end execution. Nothing can follow a terminal operation because the output format — an image, a gif, an audio file — has no further meaningful transformation in Flume's operation set. They represent the final export intent of the pipeline.

---

## Schema Design

The schema is tight to provide full validation at intake time. Bad params get rejected before any worker touches the job. Loose design means param errors surface at FFmpeg execution time, mid-pipeline.

```json
{
  "name": "trim",
  "category": "transformative",
  "input_types": ["video", "audio"],
  "output_type": "video | audio",
  "params": {
    "start": {
      "type": "float",
      "required": true,
      "default": null,
      "min": 0.0,
      "max": null
    },
    "end": {
      "type": "float",
      "required": true,
      "default": null,
      "min": 0.0,
      "max": null
    }
  }
}
```

### Param Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | Free text | A file key, a label |
| `enum` | Fixed set of allowed values | `"low" \| "medium" \| "high"` |
| `integer` | Whole numbers | Width in pixels, fps |
| `float` | Decimal numbers | Timestamps like `10.5` |
| `boolean` | True or false | `auto: true` for subtitles |
| `array` | List of values | Clips for join, segments for cut |
| `url` | String validated as a proper URL | `image_url` for watermark |

### Param Fields

| Field | Applies To | Description |
|-------|------------|-------------|
| `required` | All | If true and missing, intake rejects the job immediately |
| `default` | All | Value used when optional and not sent. `null` means no fallback |
| `values` | `enum` only | Exact allowed values. Anything outside rejected at intake |
| `min` / `max` | `integer`, `float` | Bounds on the value. Anything outside rejected |

---

## Position Constraints

Operations have ordering rules — A must come before B, C before D. That ordering lives in the registry. It gives granular control of the operation flow.

---

## Pipeline Validation

Validation uses **operation-level type compatibility** between adjacent steps. The validator looks at each adjacent pair and asks one question: can the next operation consume what the previous one produced?

```
trim → compress → extract_audio → subtitle
```

**Operation-level check:**

| Adjacent Pair | Check | Result |
|---------------|-------|--------|
| trim outputs video → compress accepts video | Type match | ✅ |
| compress outputs video → extract_audio accepts video | Type match | ✅ |
| extract_audio outputs audio → subtitle accepts video | Type mismatch | ❌ rejected |

No concept of phases — just type matching between steps. The registry's `input_types` and `output_type` fields power this.

### Why operation-level over phase-level

The alternative was **phase-level validation** — grouping operations into ordered phases (sourcing → cutting → transformation → enrichment → export) and checking that steps follow phase order, not just type compatibility. This is more explicit but less flexible.

Operation-level fits better because strictness comes naturally from type compatibility, not from a manually defined phase order. Phases would be an extra constraint on top of something type matching already handles cleanly.

---

## Storage Strategy

The operation registry is a hardcoded JSON file read at runtime, kept in-app memory. Not the database.

**Why not the DB:**
- No query overhead — always in memory, zero latency
- Version-controlled with application code
- Prevents having an operation defined in the DB with no FFmpeg controller to handle it
- Simple to update — it's just a file change in the codebase

A database would introduce many moving parts: a call to fetch operations adds latency, DB overhead becomes a bottleneck, and the registry would drift from the code that implements it.
