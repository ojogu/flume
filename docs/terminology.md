# Terminology

In Flume, a **job** is one user request to process video, tracked from submission to completion.

Concretely: a user sends something ("download this and trim it to 30 seconds"). That becomes one job. The job is the unit you persist, track status on (queued → running → done/failed), and report back to the user. It's the thing that has an ID, an owner, a created-at, a status.

What's *inside* a job is the pipeline — the ordered steps (download → trim → output). The job is the container and the record; the pipeline spec is the plan of what to do; the individual steps are the execution of each operation.

So the layering, in your own terms:

- **Job** — the request. One per user submission. Status, ownership, result live here. (jobs table)
- **Pipeline spec** — what this job should do, the ordered operations. (pipeline_specs)
- **Job steps** — each operation's actual execution and its produced artifact. (job_steps)

One job, one pipeline, many steps. The job is what the user "sees" and what your API returns; the steps are the internal machinery.
