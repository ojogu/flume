# Operation Registry

The operation registry is the authoritative list of every operation Flume supports — what each one is called, what it accepts as input, what it produces as output, and what params it takes. This is what the pipeline spec is built on. The intake stage consults it when building and validating a submitted job.

---

## Operation Entry

Each operation defines:

| Field | Description |
|-------|-------------|
| **Name** | `trim`, `compress`, `extract_audio`, etc. |
| **Input type** | What artifact type it consumes — `video`, `audio`, or both |
| **Output type** | What artifact type it produces |
| **Allowed params** | What configuration it accepts and their types |

---

## Operation Categories

Flume's 12 operations are grouped into 3 categories:

| Category | Operations |
|----------|------------|
| **Transformative** | trim, cut, compress, transcode, resize, watermark, subtitle, mute |
| **Combinatory** | join |
| **Conversion** | extract_audio, thumbnail, gif |

The categories exist solely for **operation-level type validation** — they check whether an operation's `input_types` match the previous step's `output_type`. They do **not** constrain where an operation can appear in the pipeline. The pipeline ends when there are no more operations in the list, not because any operation is intrinsically terminal.

### Transformative

Operations that take one input artifact and produce one output artifact of the same or compatible type. They modify, reshape, or enrich the artifact without changing the fundamental media type. The majority of operations fall here.

### Combinatory

Operations that take multiple input artifacts and merge them into one output artifact. They are structurally different from transformative operations because they require more than one source — their params carry the additional inputs explicitly. `join` is the only combinatory operation in V1.

### Conversion

Operations that change the asset's media type — e.g. video → audio (`extract_audio`), video → image (`thumbnail`), video → GIF (`gif`). Unlike the old Terminal category, the pipeline does **not** end here. The new artifact type is simply passed to the next operation, which must accept it. Operation-level type validation still applies between steps.

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

## Pipeline Validation

Validation uses **operation-level type compatibility** between adjacent steps. The validator looks at each adjacent pair and asks one question: can the next operation consume what the previous one produced?

```
trim → extract_audio → normalize_audio → compress
```

**Operation-level check:**

| Adjacent Pair | Check | Result |
|---------------|-------|--------|
| trim outputs video → extract_audio accepts video | Type match | ✅ |
| extract_audio outputs audio → normalize_audio accepts audio | Type match | ✅ |
| normalize_audio outputs audio → compress accepts audio | Type match | ✅ |

No concept of phases — just type matching between steps. The registry's `input_types` and `output_type` fields power this.

### Why operation-level over phase-level

The alternative was **phase-level validation** — grouping operations into ordered phases (sourcing → cutting → transformation → enrichment → export) and checking that steps follow phase order, not just type compatibility. This is more explicit but less flexible.

Operation-level fits better because strictness comes naturally from type compatibility, not from a manually defined phase order. Phases would be an extra constraint on top of something type matching already handles cleanly.

---

## Pipeline Termination

There is no "terminal" operation category. The pipeline ends when the executor reaches the last operation in the array, not because any operation is intrinsically terminal. After the final operation completes, the **outputs** defined in the job request are processed (generate a download link, upload to a URL, etc.), then the job is marked complete.

## Storage Strategy

The operation registry is a hardcoded Python dictionary (`REGISTRY`) imported at runtime. Not the database.

**Why not the DB:**
- No query overhead — always in memory, zero latency
- Version-controlled with application code
- Prevents having an operation defined in the DB with no FFmpeg controller to handle it
- Simple to update — it's just a code change in the codebase

A database would introduce many moving parts: a call to fetch operations adds latency, DB overhead becomes a bottleneck, and the registry would drift from the code that implements it.
