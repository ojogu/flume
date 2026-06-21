Keyword: 
Job: end to end operation

Source level — the client's raw JSON request body. Yes, this is exactly where you cross-check against the operation registry. You're right.

IR level — the pipeline spec, after you've built it from the JSON. This is where you validate type compatibility between steps — does step N's output type match step N+1's input types?
Submission time — everything that happens when the client sends POST /jobs. The request is still being handled by the API. No FFmpeg has run, no worker has started. This is where you validate, build the pipeline spec, write to DB, and return the job ID. errors caught at submission time are cheap — no compute spent.

Runtime — everything that happens after the job is handed to the orchestrator. The Celery worker is running, FFmpeg is processing, artifacts are being written to R2. The client already has their job ID and is waiting.
Errors at runtime are expensive — you're mid-job.

An artifact is the file a step produces, stored in R2, with metadata describing what it is

Step artifact — the artifact a specific step produced. Lives in job_steps.output_artifact
Typed artifact — emphasising that the artifact has a type (video, audio, image, gif)
Intermediate artifact — an artifact produced mid-pipeline, consumed by the next step, not the final output
Final artifact — the artifact the last step produces. This is what gets delivered to the client

How job_steps differs from pipeline_spec
Pipeline spec answers: what should happen?

Job steps answers: what actually happened?
Pipeline spec is written once at submission time, never changed. It's the plan.
Job steps are initialized at submission time as pending rows, then updated by the orchestrator as each step runs. They're the execution record.
Think of it like a recipe vs a cooking log. The recipe (pipeline spec) says "trim, then compress, then extract audio." The cooking log (job steps) says "trim started at 10:00, finished at 10:03, produced this file. Compress started at 10:03..."

Type system
Your type system is simple — four types: video, audio, image, gif. Every artifact has one of these types. Every operation declares what types it accepts and what type it produces.
The type system is what lets you catch invalid pipelines at submission time. If step N produces audio and step N+1 only accepts video, the type system catches it before any processing runs.

We are distintively seperating this compononent into 7 parts, so it's easier to zoom in and out on each, reducing overall complexity


**1. Intake**
API validation, operation registry check, pipeline spec construction. Input is the raw request body. Output is a valid pipeline spec written to DB.

We have 3 tables; job, job_steps, pipeline_spec
jobs is the what and who. pipeline_specs is the plan. job_steps is the live execution record the orchestrator reads and writes as it walks the plan.
One jobs row owns one pipeline_specs row and N job_steps rows — one per operation in the pipeline.

**2. Dispatch**
Publishing the job ID to RabbitMQ, returning the response to the client. Intake hands off to dispatch. This is the boundary between the API and the orchestrator.

**3. Initialization**
Celery worker picks up job ID, reads pipeline spec, initializes all job_steps as pending, marks job as running. Sets up the execution context before any processing begins.

**4. Execution Loop**
The core — walks steps by index, fetches input, dispatches to FFmpeg, writes artifact to R2, updates step state, advances cursor. This is the heart of Relay conceptually.

**5. Artifact Management**
Deserves its own part — writing to R2, reading from R2, structuring the artifact metadata. The execution loop calls into this, but it's a distinct concern.

**6. Completion**
All steps done — mark job complete, trigger client notification via webhook or make result available for polling.

**7. Failure Handling**
Step fails — retry logic, mark failed, dead letter, stop pipeline. Cuts across the execution loop but deserves its own isolated treatment.

![alt text](images/7-steps.png)


######
This is the heart of our backend. It is where the entire operation flow
In its simplest form, it's some sort of a job queue/state management system. 
A key functionality in our system is operation joining. If a user wants to perform 3 oepration on a resource; join, trim, compress, rather than calling 3 different endpoints or having to make 3 different api calls. 
Users can join the operation in one request, and we disceet it inside the system, handle the operations, and return a a final output, keeping the system abstract and lean. 

Pipeline Spec Pattern
We have 2 possible pattern; step arrays/linear and DAG/graph model todo: write more on this

We are going with the 1st pattern; linear pipeline. 
This is basically somesort of static, predefined,linear flow, from A-B-C etc. The downside is it does not have conditional branching unlike graph model. 

This means we need to have all operations/flow predefined.
Intermediary Representation (IR) 
input/output - Step A output should be compatible for stepB input etc
Steps Artifacts: Where the artifact output lives. Either to be picked up by another step, or updated by a step, or the final output. This is an ephermeral durable storage (r2 in context)
Partial failure & retry: Each step is independent, not an atomic operation. step B can fail, without affecting A, or C. it does not kill the entire job
conditional branching(skip)
typing/serielizaion: Each steps needs a common language/type system to properly communicate

Relating to IR from compiler construction
In compiler construction, IR is basically a bridge between high level syntax and the final target machine code(hardware level). This phase allows for things like optimzation etc. It's not the final hardware level code, it's a layer before it

How this maps to our workflow-orchestrator
The job submission (JSON body) is the source code
Validation and type-checking across steps is your semantic analysis
The artifact flowing between steps is your IR — machine-agnostic, just a typed reference to data
Each operation (trim, compress, extract) is an optimization/transformation pass on that artifact
The final output delivered to the user is your machine code

The key insight from compilers that applies directly: optimize and validate at the IR level, not at the source level. For Flume, that means catching type mismatches (video → compress → extract_audio in wrong order) at job submission time, before any compute runs. Exactly like a compiler catching errors before generating machine code.

Orchestrator
This is the control plane of the entire architecure
