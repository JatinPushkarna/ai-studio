# AI Studio — Product Requirements Document

**Author:** [Owner] | **Status:** Phase 1 (Theory + PRD) — in progress | **Target build window:** ~4 weeks

**Tagline:** From idea to publish-ready content in minutes.

## Naming Conventions

| User-Facing Name | Internal / Technical Name | Architecture |
|---|---|---|
| Writer | Script Engine | LangChain linear pipeline (generation chain); chat refinement layer uses a stateful multi-turn session with prompt caching |
| Editor | Post-Processing Engine | LangGraph stateful loop |
| — | Video Analyzer | Intermediate step between Writer and Editor (no user-facing name — backend only) |

Writer/Editor are shown to end users in-product. Script Engine / Post-Processing Engine are used throughout this document for precision.

---

## 1. Problem Statement

Solo content creators who want to build a consistent presence face a structural bottleneck in manual video editing. In practice, editing short-form reels in CapCut routinely takes 2–3 hours for a single 60-second video — not because of a fixed checklist of tasks, but because editing invites a rabbit hole: each micro-decision (which caption style, which sound effect, whether a cut feels right) reopens the question of whether the last one was good enough, with no natural stopping point without real discipline. Even skilled editors report finishing in 30 minutes to 2 hours — a bar not yet hit here. Adding B-roll or motion graphics is effectively out of reach without real editing skill, and hiring a professional editor is financially unrealistic for a solo creator.

The result is a cycle of procrastination and decision fatigue: without a repeatable, structured process, every video becomes a fresh, effortful, open-ended decision space — which slows output and directly conflicts with the consistency that platform algorithms reward.

Beyond the time cost, there's a second, separate gap: knowing *how* to write a script that actually retains viewers. Even creators comfortable using AI tools directly haven't been able to reliably produce a high-retention script — ChatGPT or Claude, prompted generically, produces a script, not necessarily a good one. This requires knowledge of retention-driving structure (hook placement, pacing, pattern interrupts, CTA clarity) that most creators, AI-fluent or not, don't have — and generic AI prompting doesn't supply on its own. This is a general communication/clarity gap as much as a script-craft gap — the same gap Toastmasters exists to address — not specific to any single audience.

AI Studio removes both bottlenecks by automating the two most time- and skill-intensive stages of content production — scripting (with a proven, hook-first structure) and post-production (graphics, B-roll, sound design) — so a solo creator can go from raw idea to publish-ready video without editing software, an editor, or the open-ended decision-making that manual editing invites.

---

## 2. User Persona

### The Time-Constrained Solo Creator

Primary v1 user: a solo content creator (the case study for this PRD is the author, used as a concrete v1 user) with a full-time job, aspiring to build an audience through consistent short-form video (30–60 second Reels). Four core constraints define this persona:

- **Script-craft novice, despite AI fluency.** Comfortable using AI tools directly, but lacks knowledge of retention-driving script structure (hook placement, pacing, pattern interrupts) — prompting an LLM generically doesn't close this gap.
- **Structural time scarcity.** Wants daily *publishing* cadence to satisfy platform consistency demands, but a full-time job leaves no room for daily *production* — the 2–4 hours a single reel's post-production currently costs simply don't fit around a full-time job on a daily basis. This is a hard calendar constraint, not a discipline problem.
- **Editing rabbit-hole behavior.** Not a seasoned editor; once inside a tool like CapCut, gets pulled into exploring options (captions, effects, transitions) without a clear stopping point, turning even the time available into inefficient, open-ended work.
- **No motion graphics/animation skill.** Cannot produce B-roll or visual interest beyond raw talking-head footage, capping production quality regardless of time invested.

**Current Workflow (Without AI Studio):** Idea → generic AI chat for a script (no structure, inconsistent quality) → shoot raw footage → CapCut for editing, captions, effects, transitions → 2–3 hours per 60-second video → often abandoned mid-process (procrastination) rather than published.

**Cadence Model: Batch Production, Daily Publishing.** Content *creation* is batched into a single weekly session (Sunday); content *publishing* is spread across the week from that batch. Daily content *production* is not the goal — daily *posting* is, achieved by producing a week's worth of content in one sitting.

**Success Looks Like:** Sunday, 8:00–10:00am: generate scripts via Writer for the week's content. 10:00–11:00am: shoot footage against all scripts. Hand off to Editor. By 12:00pm: multiple fully composited, publish-ready videos requiring no further editing — postable throughout the week without manual touch-up.

**Note on Broader Applicability:** While this PRD's v1 build and persona are anchored to a single concrete user (the author) for scope discipline and specificity, the underlying capability is not niche-bound — Writer's structure and Editor's automation apply to any short-form content topic, and the product is intended for solo creators generally beyond v1.

---

## 3. User Stories

### Script Engine (Writer)

1. As a content creator, I want Script Engine to suggest content topics based on my past scripts and general subject relevance, so that I don't stall when I don't know what to make content about this week.
2. As a content creator, I want Script Engine to help me polish and clarify a raw idea into concise, well-worded language, so that my content connects with viewers even when I struggle to express the idea cleanly myself — a general communication gap, not an English-fluency one.
3. As a content creator, I want Script Engine to structure my polished idea into a proven retention format (hook → problem → solution → CTA), so that the finished script holds viewer attention rather than losing them partway through.

> All three stories are served by a single, continuous chat session (rough idea → polish → structure → generate → further refine), using prompt caching to carry context throughout — not three separate mechanisms. Story 3's retention-format guarantee is enforced by the advisory mechanism in Section 4: if the structured script is missing a clear hook/CTA or a beat reads as unclear, the response explicitly prompts the user to open chat refinement — this applies whether the script came from generation or the Structuring Step (user-provided path), not just the latter.

### Video Analyzer

1. As a content creator, I want the tool to analyze my script and footage to identify what's being said and when, tagging each beat's underlying concept, so that the Editor knows what content and timing to generate visuals and sound for.

### Post-Processing Engine (Editor)

1. As a content creator, I want the Editor to generate overlay graphics and visuals that represent the meaning behind what I'm saying — not just restate the words literally — so viewers grasp my point intuitively at a glance.
2. As a content creator, I want the Editor to generate synthetic B-roll that actually depicts the specific idea I'm discussing, so my reel doesn't rely on generic or irrelevant filler.
3. As a content creator, I want the Editor to add relevant sound effects tied to visual/content beats, so the video feels polished without me manually sourcing and placing audio.
4. As a content creator, I want the final output to be a single composited, publish-ready video, so I don't have to manually merge graphics onto my footage in another tool.

---

## 4. Feature Spec — Script Engine (Writer)

### Inputs

**Creator Profile** (persistent, user-overridable per generation):

- Name / alias
- Category (primary niche/specialty) + adjacent/related topics (free text, e.g. "real estate, with occasional economics/geopolitics commentary")
- Platform(s)
- Style / tone (voice preserved from — not overridden by — RAG-retrieved past scripts; model instructed not to normalize or "correct" existing creator voice toward generic neutral prose)
- Age, gender — *always captured, injected into the generation prompt only when the current Topic is classified as identity-relevant* (e.g. motherhood, men's health, life-stage-dependent advice, niche demographic-matched targeting; also applies to audience-appropriateness cases like life-stage-gated financial advice). Left out of the prompt for general-topic content to avoid stereotyping / forced-tone failure modes.

**Audience Profile** (persistent, user-overridable per generation):

- Demographics (age range, gender) — same relevance-gated injection logic as Creator Profile, though audience demographics are more consistently relevant since they can affect content correctness (e.g. life-stage-gated financial advice), not just tone
- Platform
- Interest areas (plural — audience interests can legitimately extend beyond the creator's own primary category, e.g. a real estate audience may also be interested in economics or geopolitics)

**Per-generation inputs:**

- Topic (user-provided free text, or selected from Writer-suggested topics)
- Target duration (30s, 45s, or 60s)

### Outputs

A structured script broken into **beats** — discrete segments defined by narrative/content-flow role (hook, content, cta), not by fixed time allocation. Duration per beat is a downstream *measurement* (estimated from word count at natural spoken pace), not something the LLM plans upfront. Generated output is also evaluated against the same structural/clarity advisory checks defined under Structuring Step below — an auto-generated script can still land with a weak hook or an unclear beat, especially early on with little RAG history to draw from, so the advisory mechanism is shared across both the generation and Structuring Step paths, not exclusive to user-provided scripts.

### Duration Budget Formula

```
post_production_reserve = total_duration x 0.15
spoken_target = total_duration - post_production_reserve
acceptable_range = spoken_target +/- 10%

Example (30s video):
  reserve = 4.5s -> spoken_target = 25.5s -> range = 22.95s - 28.05s
Example (45s video):
  reserve = 6.75s -> spoken_target = 38.25s -> range = 34.425s - 42.075s
Example (60s video):
  reserve = 9s -> spoken_target = 51s -> range = 45.9s - 56.1s
```

The 15% post-production reserve holds room for transitions, B-roll cutaways, SFX gaps, and future animation timing without pre-defining exactly how it's spent — that allocation is the Editor's responsibility, not Script Engine's.

### JSON Schema — Request

```json
{
  "creator_profile": {
    "alias": "string",
    "category": "string",
    "adjacent_topics": ["string"],
    "platforms": ["string"],
    "style_tone": "string",
    "age": "integer (optional)",
    "gender": "string (optional)"
  },
  "audience_profile": {
    "age_range": { "min": "integer", "max": "integer" },
    "gender": "string",
    "platform": "string",
    "interest_areas": ["string"]
  },
  "topic": "string (optional if user_provided_script is present)",
  "target_duration_seconds": "integer (enum: 30, 45, 60)",
  "user_provided_script": "string (optional - raw user draft, routed through the Structuring Step below, not directly into generation)",
  "retrieved_past_scripts": [
    {
      "script_id": "string",
      "content": "string",
      "relevance_score": "float (topic/category similarity to current request, via embedding similarity)",
      "feedback": {
        "rating": "enum: up | down | null",
        "reason": "string (optional, free text)"
      }
    }
  ]
}
```

`retrieved_past_scripts`: single retrieval (server-side, not user-supplied), ranked by `relevance_score` with upvoted scripts prioritized and downvoted deprioritized (not excluded) — see RAG Retrieval Scope below for the exclusion exception. Each returned script carries its own `feedback` nested inside it — not a separate, disconnected list — since a dislike-reason only makes sense as avoid-guidance when it's attached to the specific script it was about. When `user_provided_script` is present, it is first passed through the Structuring Step (below) before entering the same chat refinement session used by generated scripts — both paths converge on one canonical schema before Video Analyzer or Editor ever see the script.

| Property | Type | Description |
|---|---|---|
| `creator_profile.alias` | string | Creator's name/alias |
| `creator_profile.category` | string | Primary niche/specialty; free text, can include related areas covered |
| `creator_profile.adjacent_topics` | array[string] | Related topics the creator also covers |
| `creator_profile.platforms` | array[string] | Platform(s) the creator publishes to |
| `creator_profile.style_tone` | string | Voice/tone — informed by, not overriding, voice in RAG-retrieved past scripts |
| `creator_profile.age` | integer, optional | Injected into prompt only when topic is identity-relevant |
| `creator_profile.gender` | string, optional | Same relevance-gating as age |
| `audience_profile.age_range` | object {min,max} | Audience age range — more consistently relevant than creator's own age |
| `audience_profile.gender` | string | Audience gender |
| `audience_profile.platform` | string | Audience's platform |
| `audience_profile.interest_areas` | array[string] | Can extend beyond creator's own primary category |
| `topic` | string | Content topic; optional if `user_provided_script` is present |
| `target_duration_seconds` | int, enum 30/45/60 | Target full video duration |
| `user_provided_script` | string, optional | Raw user draft, routed through the Structuring Step, not directly into generation |
| `retrieved_past_scripts[].script_id` | string | Reference ID of the retrieved past script |
| `retrieved_past_scripts[].content` | string | Past script's text |
| `retrieved_past_scripts[].relevance_score` | float | Embedding similarity to current request |
| `retrieved_past_scripts[].feedback.rating` | enum up/down/null | Prior user rating of this past script |
| `retrieved_past_scripts[].feedback.reason` | string, optional | Free-text reason, used as avoid-guidance if downvoted |

### Structuring Step (User-Provided Scripts)

A distinct LLM call, separate from generation: its job is to **organize** the user's existing raw text into the beat schema (assign `beat_id`, classify each portion as hook/content/cta, calculate `duration_seconds` from word count) — not to author new content. Uses the same schema-validation error handling as generation (3 retries, terminal fallback).

In addition to structuring, this step evaluates the script against two advisory checks and returns any that fire — non-blocking, informational only:

- **Structural** — e.g. no clear hook or CTA detected
- **Clarity** — a beat is unclear or unfocused, using the same clarity lens already established for chat refinement (concise, single clear idea per beat) in detection mode rather than rewriting mode. When this fires, the response explicitly recommends the user route the script through chat refinement.

No separate schema here — the Structuring Step's output is the same canonical schema defined under JSON Schema — Response below (script + advisories), whether the script came from generation or a user-provided draft. The two paths converge on one shape rather than each having their own.

The user can always export/proceed despite advisories — zero blocking friction, consistent with the persona's core time constraint. When `advisories` is non-empty, the response includes an explicit prompt directing the user into chat refinement — this is the mechanism satisfying Story 3's retention guarantee (Section 3).

### JSON Schema — Response

```json
{
  "script": {
    "script_id": "string (assigned at export, not at generation - see below)",
    "origin": "enum: generated | user_provided",
    "target_duration_seconds": "integer",
    "total_duration_seconds": "integer",
    "beats": [
      {
        "beat_id": "string",
        "type": "enum: hook | content | cta",
        "content": "string",
        "duration_seconds": "integer"
      }
    ],
    "advisories": [
      { "type": "structural | clarity", "message": "string" }
    ]
  },
  "status": "enum: success | error",
  "error": { "code": "string", "message": "string" }
}
```

`script_id` is minted at export, not at generation or structuring — export is the single event that makes a script trackable, regardless of whether it originated from generation or the Structuring Step, and regardless of how much chat refinement happened in between. `origin` is retained for traceability but does not affect downstream handling — Video Analyzer and Editor consume the same canonical schema either way.

**Export is terminal.** An exported `script_id` is never mutated in place. If the user wants to fix a flawed script — one that carries advisories, or one they simply want to improve — they keep working in chat refinement and export again, which mints a **new** `script_id`. There's no in-place editing of an already-exported record; each export is its own immutable, distinct script.

**`advisories` is the single signal that determines everything downstream** — no separate flag needed. If a script is exported with a non-empty `advisories` array (the user chose to proceed despite a structural or clarity warning), it's treated as **junk**: stored, but never entered into RAG, never feedback-eligible, never surfaced as reference for future generations (see RAG Retrieval Scope below). If `advisories` is empty at export, the script is clean and eligible normally. `feedback` is intentionally not part of this response — it's a separate concern, captured only for clean scripts via the endpoint below, not something generation/export itself returns.

| Property | Type | Description |
|---|---|---|
| `script.script_id` | string | Assigned at export, not at generation. Immutable — a new export always gets a new ID |
| `script.origin` | enum generated/user_provided | Traceability only *for Video Analyzer/Editor consumption* — both consume the same canonical schema regardless of origin. Does affect Script Engine's own RAG ranking (see RAG Retrieval Scope below) — not downstream-neutral in an absolute sense |
| `script.target_duration_seconds` | integer | Requested duration |
| `script.total_duration_seconds` | integer | Actual measured duration |
| `script.beats[].beat_id` | string | Unique per-beat identifier |
| `script.beats[].type` | enum hook/content/cta | Narrative role of the beat |
| `script.beats[].content` | string | Beat's script text |
| `script.beats[].duration_seconds` | integer | Measured from word count, not planned upfront |
| `script.advisories[].type` | enum structural/clarity | Which check fired |
| `script.advisories[].message` | string | Human-readable advisory text; kept on record even if the user proceeds anyway |
| `status` | enum success/error | Generation outcome |
| `error.code` / `error.message` | string | Present only when status is error |

### Feedback Capture — Request/Response Schema

A small, separate endpoint from generation — surfaced in the UI at exactly one moment: when the script finishes processing and is exported, **and only if the export is clean** (empty `advisories`). A script exported with active advisories is junk regardless of any rating (see RAG Retrieval Scope below), so there's nothing useful a rating would change — the endpoint isn't offered for it. `script_id` doesn't exist until export, so there's nothing for feedback to attach to any earlier either way. This holds identically whether the script came from generation or the Structuring Step (user-provided path) — neither produces a `script_id` on its own. **Not offered during chat refinement** — the user isn't asked to rate anything mid-conversation, only once, at that final step, and only for clean exports. One feedback record per script.

**Non-blocking:** if this call fails, the user is not held up — they proceed to Video Analyzer regardless. Feedback capture is a nice-to-have signal for future RAG ranking, not a gate on the user's actual workflow.

```json
// Request
{
  "script_id": "string (required)",
  "rating": "enum: up | down (required)",
  "reason": "string (optional, free text — most useful when rating is down, since this is the text injected as avoid-guidance on future retrieval, per RAG Retrieval Scope below)"
}
```

```json
// Response
{
  "status": "enum: success | error",
  "message": "string"
}
```

On success: `message` is a short confirmation (e.g. "Thanks for the feedback!"). On failure: `message` is a short, non-technical description; the frontend shows nothing blocking and lets the user continue either way.

| Property | Type | Description |
|---|---|---|
| `script_id` (request) | string, required | Identifies which script this feedback applies to (must be a clean export — non-empty `advisories` scripts don't get prompted) |
| `rating` (request) | enum up/down, required | Explicit user rating |
| `reason` (request) | string, optional | Free text; primarily meaningful on a downvote, since it becomes negative-guidance text on future retrieval |
| `status` (response) | enum success/error | Whether the write succeeded |
| `message` (response) | string | Short human-readable confirmation or failure note — not a blocking signal either way |

**Error handling:**

| Failure | Detection | Behavior |
|---|---|---|
| `script_id` not found | No matching record in the script store | `status: error`, message returned; user continues regardless |
| `script_id` refers to a script with non-empty `advisories` | Junk scripts aren't feedback-eligible — the UI shouldn't offer this in the first place, but the endpoint validates it too | `status: error`, message returned; user continues regardless |
| Feedback already captured for this `script_id` | One record already exists (one feedback per script, captured once at export) | `status: error`, message returned; user continues regardless — no overwrite |
| Missing `rating` | Validated before write | `status: error`, message returned; user continues regardless |

The identical mechanism (same request/response shape, same single-capture rule, same non-blocking behavior) is reused for Editor's composite feedback in Section 5 — one shared endpoint pattern, parameterized by whether the target is a `script_id` or `composite_id`, not two separately designed systems.

### RAG Retrieval Scope

A single retrieval against the vector store returns the 5–7 most relevant past scripts (by topic/category similarity via embedding similarity) from the pool of **clean, eligible scripts only**. Ranked by relevance, with upvoted scripts prioritized and downvoted deprioritized — not excluded. Each returned script carries its own feedback nested with it, rather than feedback being tracked as a separate, disconnected list — a dislike-reason only makes sense as avoid-guidance when it's attached to the specific script it was about.

**Eligibility rule:** a script's own `advisories` array is the single signal that determines RAG eligibility — no separate flag needed. Non-empty `advisories` at export means the script is junk: stored for the record, but **excluded entirely** from retrieval, permanently, regardless of any later rating (it isn't feedback-eligible in the first place — see above). This prevents a flawed script the system itself flagged from quietly becoming style reference for future generations ("race to the bottom"), while imposing zero extra friction on the user at export time — the exclusion is a silent system rule, not a gate the user interacts with. Since export is terminal (Section 4 above), the only way to get a clean, eligible version of a flawed script is to keep refining and export again — which mints a new `script_id` and is judged fresh, on its own merits.

**Ranking default for unrated scripts:** the stored/returned `feedback.rating` is always exactly what the user explicitly submitted via the Feedback Capture endpoint above — `up`, `down`, or `null` if never submitted; nothing is ever fabricated into that field. Separately, sort order (not the field's value) applies one origin-gated default: a `null`-rated, clean, `user_provided` script — the creator's own validated writing, already routed through a distinct flow (the Structuring Step) — is ranked *as if* upvoted, the same boost an explicit "up" gets. A `null`-rated, clean `generated` script gets no such boost and is ranked purely on `relevance_score`, since an AI-authored pass clearing its own advisory check doesn't carry the same revealed-preference weight. This is why `origin` is retained beyond mere traceability for Video Analyzer/Editor (see response schema table, Section 4 above) — Script Engine's own retrieval ranking is origin-aware, even though downstream consumers are not.

This directly mitigates the risk of the system staying anchored to a user's early, unrefined work — generation only ever draws on scripts that were clean at export, reading each one's feedback alongside its content rather than risking reinforcement of something already known to be flawed.

### Temperature

Medium (~0.5–0.7 on Claude's 0–1 scale), to be calibrated during implementation. Rationale: Script Engine needs genuine creativity (hook phrasing, voice, framing) while reliably respecting hard constraints (JSON schema, beat structure, duration budget) — medium temperature is the balance point between creative freedom and constraint adherence.

### No-Hallucination Constraint

Prompt-level guardrail (minimal prompt engineering approach for MVP, no research/citation capability): the model is explicitly instructed not to fabricate specific facts, statistics, studies, or quotes it cannot verify, and to prefer general, defensible framing over unverifiable specifics.

### Error Handling & Retry Policy

| Failure | Detection | Retry | Terminal Fallback |
|---|---|---|---|
| Malformed / invalid output | Schema validation fails | 3 attempts, model told specific error each time | Surface error to user |
| Duration mismatch | Measured duration outside spoken_target ±10% | 3 attempts with explicit correction instruction | Accept closest result, flag to user for chat adjustment |
| Missing required input fields | Validated before LLM call | No retry — reject immediately, no tokens spent | User prompted to supply missing fields |
| RAG retrieval failure / empty | Vector store call fails or returns nothing | 3 attempts | Proceed without RAG context — expected for new users, no alarm |
| Age / gender absent | N/A — optional fields | N/A | Relevance-gating simply skips demographic injection |
| Chat — transient API failure | API error / timeout mid-session | Auto-retry 2–3 attempts | Surface error, offer manual retry if unresolved |
| Chat — context / session loss | Conversation state corrupted or lost | Not retryable (history is gone) | Fall back to last successfully-generated script version, inform user |

**Architecture note:** Script Engine's core generation pipeline (profile → RAG → generate → validate → duration-check) is a bounded, fixed-sequence chain — LangChain fits this well. The chat refinement layer is architecturally different: open-ended, state-persisting, with an unknown number of turns — closer to the Editor's LangGraph pattern. Final split (LangChain for generation, stateful construct for chat) to be confirmed during Week 5 implementation.

---

## Video Analyzer (Prerequisite for Editor)

### Inputs — Request Schema

```json
{
  "script": { "...same shape as Script Engine response.script, must be canonical schema..." },
  "footage": {
    "file_path": "string (via MCP file access)",
    "format": "string",
    "duration_seconds": "float"
  }
}
```

This is the one place in the pipeline that receives the full, raw script object — Video Analyzer needs it complete (all beat content) to perform alignment. Downstream, the Editor never receives script directly; it consumes Video Analyzer's output instead, which already carries everything about script content that Editor needs.

| Property | Type | Description |
|---|---|---|
| `script` | object | Canonical script from Script Engine (Response Schema above); must include script_id |
| `footage.file_path` | string | Via MCP file access |
| `footage.format` | string | File format |
| `footage.duration_seconds` | float | Footage length |

### Outputs

Script-level reference plus a per-beat timestamped mapping:

```json
{
  "script_id": "string (references the source script, for downstream traceability)",
  "beats": [
    {
      "beat_id": "string",
      "matched": "boolean",
      "confidence": "float (0.0-1.0)",
      "script_text": "string (original beat content, carried forward since Editor never receives script directly)",
      "actual_spoken_text": "string | null (transcribed from footage; null if unmatched)",
      "start_timestamp": "float | null (required, non-null, when matched: true; null only when matched: false)",
      "end_timestamp": "float | null (required, non-null, when matched: true; null only when matched: false)"
    }
  ]
}
```

| Property | Type | Description |
|---|---|---|
| `script_id` | string | References the source script; lets Editor and downstream trace the composite back to it |
| `beats[].beat_id` | string | References the beat in the source script |
| `beats[].matched` | boolean | Whether this beat was confidently located in the footage |
| `beats[].confidence` | float 0.0-1.0 | Match confidence score |
| `beats[].script_text` | string | Original beat content — carried here since this output, not a separate script object, is what Editor consumes |
| `beats[].actual_spoken_text` | string \| null | Transcribed speech for this beat; null if unmatched |
| `beats[].start_timestamp` / `end_timestamp` | float \| null | Where in the footage this beat occurs; required (non-null) when matched — Editor needs both to anchor SFX, transitions, and rendered graphics to the right point in the footage; null when unmatched, since there's nothing to anchor to |

### Scope: Minor Drift Only

Handles **semantic, order-independent matching** tolerant of minor wording drift (rephrasing, filler words, small ad-libs) between the script and actual delivery. **Explicitly out of scope for v1:** reordering, omitted beats, and substantial ad-libbing / unscripted tangents. If a beat cannot be confidently matched, this is surfaced to the user rather than silently resolved — the tool does not attempt to recover from major structural deviation.

### Error Handling

| Failure | Detection | Behavior |
|---|---|---|
| Transcription fails / garbage | Empty result, API error, or confidence below threshold | Retry transcription once; if still failing, flag to user that footage/audio quality may be the issue |
| Beat unmatched | Semantic matcher finds no confident correspondence | matched: false, script_text populated, actual_spoken_text: null — surfaced to user with the specific missing line |
| Low-confidence match | Match found but below confidence threshold (suggested: 70%, tunable) | matched: true with confidence score included — flagged to user as uncertain, not silently accepted |
| Footage fails technical validation | Wrong format, corrupted, duration mismatch vs. script | Rejected before transcription runs — user prompted to re-upload |
| Script not in canonical schema | Schema validation fails on the incoming script (bypassed Script Engine/Structuring Step entirely) | Rejected with guidance: "This script isn't in AI Studio's format — use Script Engine to generate or structure it for best results" |

---

## 5. Feature Spec — Post-Processing Engine (Editor)

### Inputs — Request Schema

```json
{
  "creator_profile": { "...same shape as Script Engine Section 4..." },
  "audience_profile": { "...same shape as Script Engine Section 4..." },
  "footage": {
    "file_path": "string (via MCP file access)",
    "format": "string",
    "duration_seconds": "float"
  },
  "video_analyzer_output": {
    "script_id": "string (references the source script for traceability)",
    "beats": [
      {
        "beat_id": "string",
        "matched": "boolean",
        "confidence": "float",
        "script_text": "string",
        "actual_spoken_text": "string | null",
        "start_timestamp": "float | null",
        "end_timestamp": "float | null"
      }
    ]
  },
  "aspect_ratio": "string",
  "video_type": "enum: talking_head | split_screen (extensible)",
  "retrieved_past_composites": [
    {
      "composite_id": "string",
      "composition_file": "string (past Remotion composition, for visual style reference)",
      "relevance_score": "float (similarity to current creator/category/style, via embedding similarity)",
      "feedback": {
        "rating": "enum: up | down | null",
        "reason": "string (optional, free text)"
      }
    }
  ]
}
```

No root-level `script` property — Editor never receives the raw script directly. Video Analyzer already validated the script and processed every beat, so its output is a complete, sufficient carrier of script content (`script_text` per beat) plus `script_id` for traceability. This removes a redundant second path for script data into the pipeline — script flows Script Engine → Video Analyzer → Editor, once, not to both Video Analyzer and Editor independently. `video_type` affects B-roll/overlay placement strategy: split_screen has dedicated empty space to fill; talking_head requires compositing on top of the single existing visual layer. Creator/Audience Profile fields are relevance-gated for visual style (e.g. a teen-oriented creator's visuals skew punchier/higher-contrast, an educator's skew calmer/measured), same gating principle as Script Engine.

`retrieved_past_composites` mirrors Script Engine's `retrieved_past_scripts` exactly, including the lesson already learned there: feedback is nested inside each returned composite, not tracked as a separate disconnected list, since a rating only means something attached to the specific composite it was about. **One real difference from scripts:** there's no equivalent to `advisories`-based exclusion here — Editor has no automated quality check, so there's no "junk" tier. Every past composite is retrieval-eligible; feedback only affects ranking (upvoted prioritized, downvoted deprioritized), never exclusion. Retrieval is scoped at the whole-composite level (similar creator/category/style), matching Script Engine's granularity — not per-beat; per-beat retrieval (matching individual past beat treatments) is a plausible future refinement, not v1 scope.

| Property | Type | Description |
|---|---|---|
| `creator_profile` / `audience_profile` | object | Same shape as Script Engine (Section 4); relevance-gated for visual style |
| `footage.file_path` | string | Via MCP file access |
| `footage.format` | string | File format |
| `footage.duration_seconds` | float | Footage length |
| `video_analyzer_output.script_id` | string | References the source script; Editor's only link back to it |
| `video_analyzer_output.beats[].beat_id` | string | Per-beat identifier |
| `video_analyzer_output.beats[].matched` | boolean | From Video Analyzer |
| `video_analyzer_output.beats[].confidence` | float | From Video Analyzer |
| `video_analyzer_output.beats[].script_text` | string | Original beat content — Editor's only source for this, since script isn't a separate input |
| `video_analyzer_output.beats[].actual_spoken_text` | string \| null | From Video Analyzer |
| `video_analyzer_output.beats[].start`/`end_timestamp` | float \| null | From Video Analyzer |
| `aspect_ratio` | string | Target output aspect ratio |
| `video_type` | enum talking_head/split_screen | Determines B-roll/overlay placement strategy (extensible) |
| `retrieved_past_composites[].composite_id` | string | Reference ID of the retrieved past composite |
| `retrieved_past_composites[].composition_file` | string | Past Remotion composition, used as visual style reference |
| `retrieved_past_composites[].relevance_score` | float | Embedding similarity to current creator/category/style |
| `retrieved_past_composites[].feedback.rating` | enum up/down/null | Prior user rating of this past composite |
| `retrieved_past_composites[].feedback.reason` | string, optional | Free-text reason, used as avoid-guidance if downvoted |

### Outputs

```json
{
  "composite": {
    "composite_id": "string",
    "composition_file": "Remotion composition (code + SFX references + timing manifest)",
    "render_output_path": "string (final rendered video, once composition is rendered)"
  },
  "status": "enum: success | error",
  "error": { "code": "string", "message": "string" }
}
```

Earlier drafts tracked separate arrays (animation, music, text overlays, timeline) as distinct top-level outputs — simplified to a single `composition_file`, since these are all just the composition's internal contents. `feedback` is not part of this response — same principle as Section 4's Script Engine schema: feedback is a separate concern, captured only via the Feedback Capture endpoint (Section 4, parameterized by `composite_id` instead of `script_id`), not returned as part of the render itself.

| Property | Type | Description |
|---|---|---|
| `composite.composite_id` | string | Unique ID for this render |
| `composite.composition_file` | Remotion composition | Code + SFX references + timing manifest |
| `composite.render_output_path` | string | Final rendered video, once composition is rendered |
| `status` | enum success/error | Editor pipeline outcome |
| `error.code` / `error.message` | string | Present only when status is error |

### Feedback Capture (Composite)

Yes — the generated video is feedback-eligible, using the same shared endpoint as Script Engine (Section 4), parameterized by `composite_id` instead of `script_id`. Request/response shape, non-blocking behavior, single-capture-per-`composite_id` rule: all identical.

**One real difference from scripts, worth being explicit about:** script feedback is gated — a script exported with active `advisories` isn't offered feedback at all, since it's already excluded from RAG regardless of rating (Section 4). Composites have **no equivalent gate**. Editor has no automated quality check (deliberately — visual/audio quality was judged too subjective to build a trustworthy rubric for v1), so there's no signal to gate on. Every composite is feedback-eligible, unconditionally.

**Trigger: after the user downloads the file** — not merely after the composite is delivered/rendered. Delivery just means the file is ready; download is the concrete action confirming the user actually took it, mirroring how script feedback triggers on the concrete action of export, not the vaguer "when the script is done." One feedback record per composite.

| Property | Type | Description |
|---|---|---|
| `composite_id` (request) | string, required | Identifies which composite this feedback applies to — no eligibility precondition, unlike script feedback |
| `rating`, `reason` (request) | — | Same shape as Script Engine's Feedback Capture (Section 4) |
| `status`, `message` (response) | — | Same shape as Script Engine's Feedback Capture (Section 4) |

**What it's actually for:** feeds `retrieved_past_composites` above — the same role Script Engine's feedback plays for `retrieved_past_scripts`. A downloaded composite's rating and reason become the signal that ranks it (or steers away from it) as visual-style reference for future generations. This is a real v1 mechanism now, not just a future seed for the deferred Instagram feedback loop — though it will also feed that once it exists.

### Pipeline Steps

1. **Interpretation** — per matched beat, LLM determines the visual concept representing that beat's meaning (e.g. "circadian rhythm / morning energy" → sunrise imagery, energy visualization). Output is a concept description, not code.
2. **Generation** — LLM writes the actual Remotion component code (React/JSX) for that concept, given technical constraints (timestamp, duration available, aspect ratio, video_type). This is code generation, not pixel/image generation — a materially cheaper and more controllable category than AI-generated video.
3. **SFX selection** — matches beat content/type against a pre-built, category/tone-tagged SFX library (no generation). Selection is filtered by Creator Profile tone/category (e.g. an educational-content creator's profile excludes goofy/comedic-tagged SFX).
4. **Assembly** — all generated component code + SFX file references + original footage + Video Analyzer timestamps are assembled into one master Remotion composition (manifest of what renders at each timestamp).
5. **Render** — Remotion's own rendering engine (non-LLM, compute-based — headless browser + encoding) takes the composition and outputs the final video file.

### Progress Reporting

Editor reports step-level progress rather than a single opaque percentage — honest about where real granular data exists (only the render step has genuine sub-progress, sourced from Remotion's own `onProgress` callback) versus where it doesn't (the other five steps show as discrete in-progress/complete states, not estimated percentages).

```
progress: {
  current_step: integer (1-6),
  total_steps: 6,
  step_name: enum ["interpretation", "generation", "sfx_selection",
                   "assembly", "rendering", "finalizing"],
  step_detail: string (optional - Remotion frame count during "rendering")
}
```

| Step | Display |
|---|---|
| 1/6 | Interpreting your script... |
| 2/6 | Generating visuals... |
| 3/6 | Selecting sound effects... |
| 4/6 | Assembling your video... |
| 5/6 | Rendering... (live frame count from Remotion) |
| 6/6 | Finalizing... |

Frontend polls for this status; push-based updates (e.g. webhook) considered unnecessary complexity at v1's solo-use scale.

### Error Handling & Retry Policy

| Failure | Detection | Retry | Behavior / Fallback |
|---|---|---|---|
| video_analyzer_output malformed/missing script_id | video_analyzer_output fails schema validation or lacks script_id (would indicate Video Analyzer's own validation was bypassed) | No retry — reject before pipeline starts | Rejected with guidance: "This script isn't in AI Studio's format — use Script Engine to generate or structure it for best results" |
| Footage inaccessible | MCP file read fails (moved, deleted, or corrupted since Video Analyzer ran) | 1 retry | Surface error, prompt user to re-upload footage |
| Unmatched beat from Video Analyzer | video_analyzer_output shows matched: false for a beat | N/A — not a failure, expected state | Overlay/B-roll generation skipped for that beat only (no timestamp to anchor it to); pipeline continues with remaining matched beats, not treated as a pipeline error |
| Interpretation failure | LLM produces an unusable or nonsensical visual concept for a beat | 3 attempts | After 3 failed attempts, skip generation for that beat (proceed without overlay/B-roll there), flag it in the composition file for manual review |
| Generation failure (invalid Remotion code) | Generated component code doesn't compile / fails schema | 3 attempts, model told the specific error each time | Same terminal fallback as interpretation — skip that beat's visual, don't fail the whole composite over one beat |
| SFX no match | No appropriately-tagged SFX exists for a beat | N/A | Deferred to v2 — undefined behavior for v1 |
| Assembly failure | Composition manifest can't be built (e.g. conflicting timestamps, malformed component references) | 1 retry | If still failing, return partial composition (footage + whatever beats succeeded) rather than blocking entirely |
| Render failure / excessive time | Remotion render errors, or exceeds timeout (threshold TBD) | 3 attempts | Composition file preserved and accessible via MCP; user can hand-edit or manually run `npx remotion render` — no full pipeline restart required |

The unmatched-beat and interpretation/generation-failure fallbacks share a principle: a single problematic beat degrades that beat's treatment, not the entire composite. The user gets a usable video with one plain segment rather than a hard failure over one bad beat.

**Render timeout:** deliberately left undefined for v1 — to be calibrated empirically once real videos have been produced and render times observed.

### Scope Note: SFX Fallback

SFX selection is in v1 scope. Fallback behavior when no appropriately-tagged SFX exists for a given beat is explicitly deferred to v2 — undefined for now.

### Scope Note: Music

Background music is out of v1 scope entirely — no proposal was made to include it, and the default is to leave it as a named future direction alongside other deferred features.

---

## 6. Success Metrics

### Script Engine (Writer)

| Metric | Definition / Target |
|---|---|
| Structured content | Generated script conforms to agreed beat structure (schema validation, binary pass/fail) |
| Topical relevance | Script matches Creator/Audience Profile category and topic (checkable) |
| Communication clarity | Subjective creator review (self-assessed, not automated in v1) |
| View counts | Self-benchmarked against own future videos over time, once posting history exists — not an absolute or v1-week-one metric |
| Time-to-script | Target: under 15 minutes, topic input to accepted structured output |
| Refinement time | ≤15 minutes in chat back-and-forth per script |
| Duration within tolerance | spoken_target ±10% (per Section 4 formula) |

### Post-Processing Engine (Editor)

| Metric | Definition / Target |
|---|---|
| SFX/VFX category-appropriate | Selection respects Creator Profile tone/category tags (checkable, via SFX library tagging + filtering) |
| No manual intervention | Composition accepted and rendered without hand-editing (binary, tracked as % over first N videos) |
| Resolution/aspect ratio aligned | Matches requested output spec (binary) |
| Overall acceptance rate | Composited video posted as-is without manual re-edit, on first generation (consolidates subjective quality checks into one tracked percentage) |

### Overall Product — Headline Success Criterion

Sunday 8:00–10:00am: generate 7 scripts via Writer. 10:00–11:00am: shoot footage against all 7. Hand off to Editor. By 12:00pm: 7 fully composited, publish-ready videos, postable throughout the week without further editing. (15 min/script target × 7 scripts = 105 min, fits within the 2-hour Writer block.)

---

## 7. AI-Specific Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Hallucination / fabricated facts | Prompt-level guardrail against fabricated stats, quotes, or unverifiable claims (Section 4) |
| Retrieval mismatch / context overflow (RAG) | Capped at 5–7 most relevant past scripts, bounding context size as history grows; same principle applies to `retrieved_past_composites` in Section 5 |
| Malformed structured output | Schema-constrained generation via API, 3 retries, terminal fallback (accept closest / surface to user) |
| Duration mismatch | Measured post-generation from word count (not self-reported), 3 retries with correction, accept-closest fallback |
| Video Analyzer script/footage mismatch | Scoped to minor wording drift only; major deviation (reordering, omission, ad-libbing) surfaced as unmatched beats, not silently resolved |
| Composition/render failure or excessive time | 3 retries per pipeline stage; composition file always preserved for manual fallback (hand-edit or manual Remotion render) |
| Chat session state loss | Transient failures auto-retried; state loss falls back to last successfully-generated script version, user informed |
| Demographic bias in generation | Age/gender relevance-gated — injected into prompt only when topic is genuinely identity-relevant, avoiding stereotyping/forced-tone failure modes on general content |
| Generation & render cost | LLM cost is code-generation (relatively low, not pixel-generation); Remotion render is separate compute cost. Both flagged for empirical validation during build, not estimated in advance. |
| Trend / source trustworthiness | Live trend search explicitly deferred to v2 in full — v1 topic suggestions use only RAG-retrieved past scripts and general subject relevance, no external/live data requiring trust verification |
| SFX no-match fallback | Not handled in v1 — behavior for an unmatched beat (no appropriately-tagged SFX) is deferred, undefined for now |
| Anchoring to early/unrefined work | Scripts exported with any active advisory are excluded from RAG entirely (junk, permanently) — generation only ever draws on scripts that were clean at export. Composites have no equivalent exclusion tier (no advisories mechanism exists for Editor) — a poorly-rated composite is deprioritized via `retrieved_past_composites[].feedback`, not excluded, a smaller residual version of the same risk |

---

## Explicitly Out of Scope for v1

The following were deliberately considered and cut during scoping, with reasoning — not oversights:

- **Retake / pause removal** — user uploads their own rough-cut footage; this pre-processing stage would sit before Video Analyzer and adds a new class of quality-eval problem (how do you know a cut was correct?).
- **Live trend search** — cut after honest self-assessment of unknown implementation risk (no clear trusted trend data sources, staleness concerns). Trend-aware script framing (title/hook/hashtag adaptation to current events) is a strong v2 candidate once these are resolved.
- **Automated quality eval / retry loop (Editor)** — visual quality criteria are genuinely subjective and not yet well-defined enough to build a trustworthy automated rubric against. v1 relies on manual creator review instead of a fabricated objectivity.
- **Background music** — no case was made for it during scoping; sits alongside other deferred audio/visual enhancements.
- **Stock or AI-generated video B-roll** — rejected in favor of Remotion-generated synthetic graphics, which keeps the entire pipeline in the "LLM writes code" lane (cheaper, more controllable, no dependency on a third-party video-generation API or footage-rights question).
- **Live, iterative co-writing as a separate mode** — resolved into the single chat-refinement mechanism already covering both auto-generated and user-provided script starting points, rather than a second parallel feature.
- **Instagram performance feedback loop** — no ground truth exists yet to validate against; a natural v2 extension once the product has real posting history. Would also strengthen future trend-search and self-assessment features that were cut from v1 for the same lack-of-data reason.
- **Resolution / aspect-ratio reformatting as a standalone feature** — folded into the Editor's existing render configuration (a Remotion composition parameter) rather than treated as separate scope.

### V2 Direction (Named, Not Scoped)

Instagram performance feedback loop → informs both script retention criteria and future trend-search trustworthiness. Live trend search. SFX no-match fallback behavior. Demographic-aware voice calibration validated against real performance data rather than assumption. Live, iterative co-writing mode.
