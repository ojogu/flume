# Flume Documentation

Documentation is a key part of this project. Good documentation is how you think clearly, ship confidently, and communicate your work effectively — to your future self, to collaborators, and to interviewers.

Flume follows industry-standard documentation practices. This guide explains what each document is, why it exists, and how to use it.

---

## Documentation Structure

```
docs/
├── readme.md              ← you are here
├── architecture.md        # high-level system design
├── tradeoffs.md           # significant decisions — what you chose and rejected
├── decisions/              # individual ADRs — one file per decision
│   └── 000-template.md    # use this template for new decisions
├── design/                 # detailed subsystem designs — logging, observability, services
│   └── images/            # diagrams for design docs
├── postmortem/            # incident reports — what broke and what changed
│   └── 000-template.md    # use this template for new postmortems
├── prd.md                 # product requirements
└── learn.md               # learning goals and project overview
```

---

## Why Documentation Matters

There are three reasons to maintain good documentation:

### 1. It forces you to think clearly

When you write down a decision — why you chose X over Y, what you're assuming, how you'll know if it worked — you catch gaps in your reasoning. Ideas feel clear in your head until you try to write them down. Documentation is a forcing function for clear thinking.

### 2. It becomes your memory

Six months from now, you won't remember why you chose RabbitMQ over Redis, or why the output delivery logic is split the way it is. The documentation is the record. It lets you make decisions once and not revisit them from scratch every time.

### 3. It writes your interview prep for you

When you say "I maintain Architecture Decision Records for every significant technical choice in my projects," it signals something most junior and even mid-level engineers don't do. It shows you think systematically, not just tactically. The decisions folder is your evidence.

---

## The Document Types

### `architecture.md` — Why You Built It This Way

This is the overview. It answers the question: what does this system look like at a high level, and why is it organized the way it is?

It includes:
- What the system does (one sentence)
- The tech stack and why each piece was chosen
- The high-level data flow
- The internal module structure
- Links to relevant decisions in `tradeoffs.md`

This is the document you hand to someone who has never seen the codebase. It should give them a solid mental model in five minutes.

**When to update:** When the overall structure changes — a new component, a major architecture shift, a new external dependency.

---

### `tradeoffs.md` — What You Chose and What You Rejected

This is the running record of every significant decision made during the build. It's not just "we chose X" — it's "we considered A, B, and C, here's why X won, and here's what we're accepting as a tradeoff."

This is the most valuable document in the project. It captures your judgment, not just your implementation.

**Format:** One section per decision. Each section should include:
- What was considered (all options)
- What was chosen
- Why (the reasoning)
- What was accepted as a tradeoff

**When to update:** Every time you make a significant decision — a new tool, a new pattern, a rejection of an obvious choice.

---

### `decisions/` — Individual ADRs

The `decisions/` directory holds individual Architecture Decision Records. Use this when a decision is complex enough to warrant its own file — when the reasoning is long, when there are multiple options to track, when the consequences matter.

Not every decision needs a file. Not every decision needs to be in `tradeoffs.md` either. Use your judgment:
- **In `tradeoffs.md`:** Decisions that fit in a paragraph or two. Decisions that are part of a pattern.
- **In `decisions/:** Decisions that have a long trail of reasoning, a complex tradeoff, or consequences that need to be tracked over time.

**The ADR format** (Architecture Decision Record) is a lightweight structure for documenting a decision. Each ADR answers four questions:

| Question | What It Captures |
|---|---|
| What breaks if I get this wrong? | The stakes. What is the cost of a bad decision here? This defines why the decision is hard. |
| What did I choose and what did I reject? | The tradeoff. What you picked and what you left on the table. |
| How do I know it's working? | The metric. How do you measure success? This defines the outcome. |
| What assumptions am I making that could be wrong? | Where you're most likely to have to revisit this. |

These four questions are the whole framework. Every decision in this project should be traceable to them.

**Naming:** Use a numbered prefix — `001-`, `002-` — so the order is clear and new files slot in chronologically.

---

### `design/` — How Specific Subsystems Work

The `design/` directory holds detailed design documents for individual subsystems — logging, observability, services, and other focused areas. While `architecture.md` gives the ten-thousand-foot view, these files dive into the component-level details: data flow, configuration, integration points, and diagrams.

**When to update:** When a subsystem's design changes in a meaningful way — a new log handler, a different OTel exporter, an additional service.

---

### `postmortem/` — What Broke and What Changed

A postmortem is a record of something that went wrong in production. It documents what happened, why it happened, what you changed, and what you learned.

Most people hide their failures. Documenting them shows production thinking — that you understand systems fail and you have a process for learning from it.

**The format:**
- **Incident summary** — date, duration, severity, one-line description
- **Timeline** — what happened and when
- **Impact** — what was affected
- **Root cause** — the actual cause, not the symptom
- **What went well** — where the response worked
- **What went wrong** — where it was slow or missing
- **Action items** — specific follow-ups with owners
- **Lessons learned** — the key takeaways

**One important rule:** Postmortems are blameless. The goal is to understand what happened, not to assign fault. Systems fail. The goal is to build resilience, not to punish people.

**When to write one:** Any time something breaks in a way that taught you something. A Celery OOM, a webhook failure that took an hour to detect, a deployment that caused downtime — all of these deserve a postmortem.

---

### `prd.md` — What You're Building

The Product Requirements Document. It describes the product in detail — the goals, the users, the features, the non-goals, the success metrics.

This is where the product thinking lives. It keeps the engineering work grounded in user needs and business outcomes.

---

### `learn.md` — Why You're Building It

The learning guide. It captures what concepts this project teaches, and why each concept matters.

This is personal documentation — it exists because this project is as much a learning exercise as a product build. It tracks what you'll understand by the end that you don't fully understand now.

---

## How to Use This System

### When you make a decision

1. Ask: does this fit in `tradeoffs.md` or does it need its own file in `decisions/`?
2. If it's in `decisions/`, use the template (`000-template.md`)
3. Answer the four questions: what breaks if you get it wrong, what you chose vs. rejected, how you know it's working, what assumptions you're making

### When something breaks in production

1. Write a postmortem. Use the template (`000-template.md` in `postmortem/`)
2. Be specific about the root cause
3. Make action items concrete and assign them owners
4. Keep it blameless

### When you design a subsystem

1. Add or update the relevant document in `design/`
2. Include a diagram in `design/images/` if the data flow is complex
3. Update `architecture.md` if the high-level structure changes

### When the system changes

1. Update `architecture.md` to reflect the new structure
2. Document the decision that caused the change in `tradeoffs.md` or `decisions/`

---

## The Underrated Value of Postmortems

Most engineers don't write postmortems. They fix the problem and move on. This is a missed opportunity.

A good postmortem does three things:

1. **It slows you down just enough to learn.** When something breaks, the instinct is to move fast. Writing a postmortem forces you to pause, understand, and extract the lesson. Without it, you make the same mistakes.

2. **It creates a record of your judgment in action.** The decision that led to the incident was made months ago. The postmortem connects the outcome back to the decision. This is how you build intuition over time.

3. **It signals production thinking.** When you say "I write postmortems for every significant incident," it tells interviewers that you understand systems fail and that you have a systematic process for learning from failure. Most engineers don't do this.

---

## A Note on Over-Engineering Documentation

Don't. This system is lightweight by design:

- `architecture.md` is a few paragraphs and a diagram
- `tradeoffs.md` is a running list, not a formal document
- ADRs are freeform — the template is a guide, not a law
- Postmortems are as long as they need to be, no longer

The goal is clarity, not completeness. If you're spending more time writing about a decision than making it, something is wrong.

---

*Questions about this documentation system? Add context here rather than leaving it in your head.*