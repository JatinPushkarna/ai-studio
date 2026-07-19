# AI Studio — Description Chain (Technical Spec)

*Companion artifact to the AI Studio PRD. Written in Augmentation mode: requirement defined by Jatin, technical shape proposed by Claude, refined through explicit pushback. Acceptance tests and build prompts are deferred to Claude Code (Week 5) — not covered here.*

## System Shape

Three independently deployable services, connected by plain service-to-service API calls (not MCP — MCP is reserved for LLM-invoked tool actions *within* a component, not for orchestration between components):

**Writer (Script Engine)** → **Video Analyzer** → **Editor (Post-Processing Engine)**

| Service | Compute | Why |
|---|---|---|
| Writer | Serverless (Vercel-style) | Each interaction — generation or chat turn — is a short, stateless LLM call; state lives externally, not in the function |
| Video Analyzer | Serverless (Vercel-style) | Primarily a transcription API call plus a matching step; short-lived |
| Editor | Longer-running compute (Render-style) | Remotion rendering is compute-heavy and can exceed typical serverless execution limits |

## External Dependencies

- **Session/chat database** — persists Writer's multi-turn refinement history between stateless function calls (client sends only the latest message; server reads/writes full history)
- **Vector database** (Chroma or pgvector for v1) — stores past scripts for RAG. **Single retrieval per generation**, not two: returns the 5–7 most relevant past scripts, each carrying its own `feedback` (rating + optional reason) nested inside it — not two disconnected lists of scripts vs. feedback, since a dislike-reason only means something attached to the specific script it was about. Ranked by relevance, upvoted prioritized, downvoted deprioritized. Scripts exported with a non-empty `advisories` array are excluded from retrieval entirely — the `advisories` array itself is the sole signal, no separate field (prevents a flagged-and-bypassed script from becoming style reference — "race to the bottom")
- **Blob/file storage** — raw footage uploads, composition files (accessed via MCP by the Editor's own generation step, not by orchestration code)

## Pipeline Flow

1. Script reaches export either via **generation** (topic → RAG-informed draft) or the **Structuring Step** (user pastes a raw draft; a separate LLM call organizes it into the same canonical schema — never authors new content). Both paths run the same structural/clarity advisory checks and converge on one schema before export.
2. At **export**: `script_id` is minted (not at generation — export is the single event that makes any script, regardless of origin, trackable). If advisories fired, the response explicitly prompts the user into chat refinement (non-blocking — always skippable). Optional up/down + text-reason feedback is captured here via explicit user action; the stored/returned `feedback.rating` is always exactly what the user submitted — `up`, `down`, or `null` if they never called the endpoint. Nothing is ever fabricated into that field. Separately, a **ranking-only default** applies when a script is later pulled into `retrieved_past_scripts` for a new generation: a `null`-rated, clean (`advisories` empty), `user_provided` script is sorted *as if* upvoted (same boost as an explicit "up"), since it's the creator's own validated writing; a `null`-rated, clean `generated` script gets no such boost, ranked purely on relevance. This affects sort order only — the payload still honestly shows `rating: null`. The `advisories` array itself is the sole signal for RAG exclusion — no separate field needed; non-empty `advisories` scripts never reach the ranking step at all.
3. User shoots footage against the exported script, uploads it → **Video Analyzer triggers immediately** (needs the full script as its alignment key — this is the one place downstream that receives the raw script object).
4. Video Analyzer transcribes, semantically matches transcript to script beats (minor-drift tolerant only; reordering/omission/ad-libbing explicitly out of scope, surfaced as unmatched rather than resolved) → outputs `{script_id, beats: [{beat_id, matched, confidence, script_text, actual_spoken_text, start_timestamp, end_timestamp}]}`. This output — not a separate script object — is what the Editor consumes; script content flows through the pipeline once, not to both Video Analyzer and Editor independently.
5. Editor receives Video Analyzer's output + footage + Creator/Audience Profile + aspect ratio + `video_type` (talking_head/split_screen — determines B-roll/overlay placement strategy) → runs a 6-step pipeline (interpretation → generation → SFX selection → assembly → render → finalize), reporting named step progress to the frontend; real sub-progress during rendering only, sourced from Remotion's own `onProgress` callback. A single bad beat degrades gracefully (skipped, not a pipeline failure) rather than failing the whole composite.
6. Composite downloaded (not merely delivered/rendered — the file lands on disk before in-app playback, and download is the concrete, detectable trigger) → same optional feedback mechanism as step 2, captured against the composite record.
7. On failure at any Editor stage (3 retries exhausted): composition file preserved, user can hand-edit or manually run `npx remotion render` — no full pipeline restart required.

## Editor's Six Steps

`interpretation` (LLM: what does this beat mean, visually) → `generation` (LLM: Remotion component code for that concept) → `sfx_selection` (library match, category/tone-filtered against Creator Profile — no generation) → `assembly` (compose into one Remotion manifest) → `rendering` (Remotion's own engine — non-LLM, compute-bound) → `finalizing`.

## MCP Scope (Editor only)

Reserved for actions the LLM itself takes mid-generation: (1) composition file read/write, (2) SFX library search/retrieval, (3) footage file inspection (dimensions, format, duration). Not used for Writer→Video Analyzer→Editor handoffs — those are conventional API calls.

## Open / Deferred

Render timeout threshold — undefined until real render times are observed. SFX no-match fallback — undefined for v1. Push-based (vs. polled) status updates — polling sufficient at v1 scale. Structuring Step and generation-path advisories currently share one check (structural + clarity) — no quality score, deliberately, since a scored rubric was already rejected for Editor's visual QA for the same reason (too subjective to trust yet).
