# Architecture: Three-Layer Model

This document introduces a second classification system for Flume's operations.

Previously, every operation belonged to one of three execution categories:

- Transformative
- Combinatory
- Conversion

These categories are designed solely for pipeline execution and validation. They describe **how the engine executes operations**, not **what capabilities Flume provides**.

This document introduces a **Capability Layer** that sits above the execution engine.

The execution model remains unchanged.

Only the product and developer-facing abstraction changes.

---

## Design Goals

The Capability Layer exists to solve several problems.

### 1. Better product positioning

Instead of presenting Flume as a collection of editing commands:

- Trim
- Resize
- Compress
- Watermark

Flume can now be presented as a media infrastructure platform offering core media capabilities.

Example:

Media Processing Capabilities

- Transform Media
- Extract Media
- Combine Media
- Analyze Media
- Generate Media

This better aligns with Flume's positioning as media processing infrastructure.

---

### 2. Better documentation

Without capability grouping:

Operations become one long flat list.

With capability grouping:

Transform Media

- Trim
- Resize
- Compress
- Watermark

Extract Media

- Extract Audio
- Thumbnail

Developers immediately understand where to look.

---

### 3. Better SDK organization

Instead of

```python
flume.trim(...)
flume.resize(...)
flume.thumbnail(...)
```

SDKs can expose namespaces.

Python

```python
flume.transform.trim(...)
flume.transform.resize(...)

flume.extract.audio(...)
flume.extract.thumbnail(...)

flume.combine.join(...)
```

TypeScript

```ts
flume.transform.trim(...)
flume.extract.audio(...)
flume.analyze.transcribe(...)
```

This improves discoverability through autocomplete.

---

### 4. Better future scalability

As Flume grows beyond FFmpeg-backed operations, new capabilities naturally fit.

Future examples

Analyze Media

- Transcribe
- Detect Language
- Detect Silence
- Detect Scenes

Generate Media

- GIF
- Preview Clip
- Waveform
- Contact Sheet

The platform scales without creating a disorganized list of unrelated operations.

---

## The Three-Layer Architecture

Flume now has three conceptual layers.

---

### Layer 1 — Capability Layer

**Audience:** Developers

**Purpose:** Product taxonomy.

Used for:

- Website
- Documentation
- SDK namespaces
- API reference
- Marketing

Example

Transform Media

- Trim
- Resize
- Compress
- Watermark

Extract Media

- Extract Audio
- Thumbnail

Combine Media

- Join

Analyze Media

- Transcribe

Generate Media

- GIF

This layer answers: "What can Flume do?"

---

### Layer 2 — Operation Layer

**Audience:** Developers and Consumers

**Purpose:** Concrete executable operations.

Examples

trim

compress

resize

join

thumbnail

extract_audio

watermark

subtitle

Every operation has:

- Parameters
- Validation
- Documentation
- Implementation

Operations are what users actually invoke.

Example

```json
{
  "pipeline": [
    { "operation": "trim" },
    { "operation": "compress" }
  ]
}
```

This layer answers: "What operation should be executed?"

---

### Layer 3 — Execution Layer

**Audience:** Pipeline Engine

**Purpose:** Determine execution semantics.

Categories

- Transformative
- Combinatory
- Conversion

These categories are never exposed as product concepts. Instead they drive pipeline validation.

Examples

Transformative

- accepts one input
- outputs one media artifact
- pipeline continues

Combinatory

- accepts multiple inputs
- outputs one media artifact
- pipeline continues

Conversion

- changes the artifact's media type (e.g. video → audio)
- pipeline continues

No category is intrinsically terminal — the pipeline ends when the executor reaches the last operation in the array.

This layer answers: "How should the pipeline execute this operation?"

---

## Relationship Between Layers

Every operation belongs to two independent classifications.

Example

trim

- Capability: Transform Media
- Execution: Transformative

---

join

- Capability: Combine Media
- Execution: Combinatory

---

thumbnail

- Capability: Extract Media
- Execution: Conversion

---

transcribe (future)

- Capability: Analyze Media
- Execution: Conversion

---

These classifications are independent.

- Capability answers "What does this operation provide?"
- Execution answers "How does the engine execute it?"

---

## Consumer Application

The consumer application should not expose capabilities.

Consumers care about tasks.

Examples

- Trim Video
- Compress Video
- Add Watermark
- Convert to Audio
- Generate Thumbnail

They do not care whether the operation belongs to Transform Media or Extract Media.

The consumer UI remains task-oriented.

---

## Developer Experience

Developers interact with capabilities.

Example documentation

Transform Media

- Trim
- Resize
- Compress

Extract Media

- Thumbnail
- Extract Audio

Combine Media

- Join

Analyze Media

- Transcribe

This creates a much more intuitive navigation model.

---

## Internal Engine

Internally nothing changes.

The registry continues storing execution semantics.

Example

Operation: trim
- Execution: Transformative
- Capability: Transform Media

Validation still depends only on execution type.

The capability layer never affects execution.

---

## Benefits

**Product:**
- Better positioning
- Easier to explain
- More infrastructure-oriented

**Documentation:**
- Better discoverability
- Cleaner organization
- Easier onboarding

**SDK:**
- Better autocomplete
- Logical namespaces
- Easier navigation

**Architecture:**
- Separation of concerns
- No impact on execution engine
- Future-proof for AI and advanced media operations

**Consumer UX:**
- Task-based interface
- No unnecessary technical concepts

**Pipeline Engine:**
- Existing validation remains unchanged

---

## Core Principle

Execution describes engine behavior.

Capability describes product behavior.

Operations connect the two.

This separation allows Flume to evolve into a comprehensive media processing platform without changing the underlying execution architecture.
