# Acceptance Tests — Script Engine (Writer)

Draft only. Traces to `AI_Studio_PRD.md` Section 4 unless noted. **Not committed as final — for Jatin to review and challenge before that happens.**

## 1. Duration budget formula compliance

**Traces to:** PRD §4 Duration Budget Formula; Section 6 "Duration within tolerance"

- GIVEN a generation request with `target_duration_seconds: 30`, WHEN Script Engine produces a script, THEN `total_duration_seconds` falls within 22.95s–28.05s (spoken_target 25.5s ± 10%).
- GIVEN a generation request with `target_duration_seconds: 45`, WHEN produced, THEN `total_duration_seconds` falls within 34.425s–42.075s (spoken_target 38.25s ± 10%).
- GIVEN a generation request with `target_duration_seconds: 60`, WHEN produced, THEN `total_duration_seconds` falls within 45.9s–56.1s (spoken_target 51s ± 10%).

## 2. Beat schema conformance

**Traces to:** PRD §4 JSON Schema — Response

- GIVEN any successful generation or Structuring Step call, WHEN the response is validated, THEN `script.beats` is a non-empty array and every beat has `beat_id`, `type` ∈ {hook, content, cta}, `content` (string), `duration_seconds` (int); `script.origin` ∈ {generated, user_provided}.
- GIVEN a beat's `content` text, WHEN its `duration_seconds` is checked, THEN the value is consistent with word count at natural spoken pace — a downstream *measurement*, not a number the LLM was free to invent or plan upfront.

## 3. `script_id` minted only at export

**Traces to:** PRD §4 "`script_id` is minted at export, not generation"; `description_chain.md` Pipeline Flow step 2

- GIVEN a script mid-generation or mid-chat-refinement, WHEN inspecting the response, THEN `script_id` is absent.
- GIVEN the user exports, WHEN export completes, THEN `script_id` is present and unique.

## 4. Export is terminal / immutable

**Traces to:** PRD §4 "Export is terminal"

- GIVEN an already-exported `script_id`, WHEN the user continues refining in chat and exports again, THEN a new, distinct `script_id` is minted and the original record is never mutated in place.

## 5. Advisories mechanism — non-blocking, fires on both paths

**Traces to:** PRD §4 Structuring Step, User Stories §3.3, JSON Schema — Response

- GIVEN a generated script missing a clear hook/CTA or containing an unclear beat, WHEN generation completes, THEN `advisories` is non-empty (`type`: structural|clarity) and the response explicitly prompts the user into chat refinement.
- GIVEN the same condition arises via `user_provided_script` routed through the Structuring Step, WHEN structuring completes, THEN the identical advisory mechanism fires, same response shape.
- GIVEN advisories fired, WHEN the user chooses to export anyway, THEN export succeeds — advisories never block export.

## 6. RAG eligibility, cap, and single-retrieval shape

**Traces to:** PRD §4 RAG Retrieval Scope "Eligibility rule"; PRD §7 AI-Specific Risks "Retrieval mismatch/context overflow"; `description_chain.md` Vector database bullet

- GIVEN a script exported with non-empty `advisories`, WHEN any later generation request performs RAG retrieval (at any point in the future), THEN this script never appears in `retrieved_past_scripts`, regardless of any feedback rating given afterward.
- GIVEN more than 7 clean, eligible past scripts exist, WHEN RAG retrieval runs for a new generation request, THEN `retrieved_past_scripts` contains at most 7 entries — the cap holds regardless of how large the eligible pool grows, bounding context size as history accumulates.
- GIVEN a generation request that needs past-script context, WHEN retrieval runs, THEN exactly one retrieval call is made, and each returned script carries its own `feedback` object nested inside it — never two disconnected lists (scripts vs. feedback) requiring a separate join.

## 7. Feedback Capture endpoint — explicit call

**Traces to:** PRD §4 Feedback Capture, Error Handling table

- GIVEN a script exported clean (`advisories` empty), WHEN the Feedback Capture endpoint is called with a valid `rating`, THEN `status: success` and this is the one and only feedback record for that `script_id`.
- GIVEN feedback already captured for a `script_id`, WHEN the endpoint is called again for it, THEN `status: error`, no overwrite, user continues regardless.
- GIVEN a script exported with non-empty `advisories`, WHEN the endpoint is called for that `script_id` anyway, THEN `status: error` — junk scripts are not feedback-eligible.
- GIVEN the endpoint is called without `rating`, WHEN validated, THEN `status: error` before any write.

## 8. Implicit ranking default (origin-gated)

**Traces to:** PRD §4 RAG Retrieval Scope "Ranking default for unrated scripts" (added this session — see `description_chain.md` reconciliation)

- GIVEN a script exported clean, `origin: user_provided`, never explicitly rated, WHEN later considered for `retrieved_past_scripts` ranking, THEN it sorts as if explicitly upvoted, while its returned `feedback.rating` still reads `null` (never fabricated into the data).
- GIVEN a script exported clean, `origin: generated`, never explicitly rated, WHEN considered for ranking, THEN no boost applies — ranked purely on `relevance_score`, `feedback.rating` reads `null`.
- GIVEN a script exported with non-empty `advisories`, regardless of origin, never explicitly rated, WHEN retrieval runs, THEN it never reaches ranking at all (excluded per §6 above).

## 9. Age/gender relevance-gating

**Traces to:** PRD §4 Creator/Audience Profile inputs

- GIVEN a topic classified as identity-relevant (e.g. motherhood, men's health, life-stage-dependent advice), WHEN the generation prompt is built, THEN `creator_profile.age`/`gender` (if present) are injected.
- GIVEN a general-topic, non-identity-relevant request, WHEN the generation prompt is built, THEN `creator_profile.age`/`gender` are omitted even if present in the profile.
- GIVEN `audience_profile.age_range`/`gender`, WHEN any request is processed, THEN the same relevance-gating principle applies, though audience demographics are more consistently relevant since they can affect content correctness, not just tone.

## 10. Error / retry policy

**Traces to:** PRD §4 Error Handling & Retry Policy table

- GIVEN schema validation fails on generated output, WHEN retried, THEN up to 3 attempts (model told the specific error each time); if all fail, error surfaced to user.
- GIVEN measured duration outside spoken_target ±10%, WHEN retried, THEN up to 3 attempts with explicit correction instruction; if still outside range, closest result accepted, user flagged for chat adjustment.
- GIVEN a request missing required input fields, WHEN validated pre-call, THEN rejected immediately, no LLM call spent, user prompted to supply missing fields.
- GIVEN the vector store call fails or returns nothing, WHEN retried, THEN up to 3 attempts; if still failing, proceed without RAG context, no alarm (expected for new users).
- GIVEN a mid-session chat API error/timeout, WHEN retried, THEN auto-retry 2–3 attempts; if unresolved, error surfaced, manual retry offered.
- GIVEN chat conversation state is corrupted/lost, WHEN detected, THEN not retried — falls back to the last successfully-generated script version, user informed.

## 11. No-hallucination guardrail

**Traces to:** PRD §4 No-Hallucination Constraint

- GIVEN a generation call where the model would otherwise cite an unverifiable specific fact/statistic/study/quote, WHEN the system prompt's guardrail is checked, THEN it explicitly instructs the model to prefer general, defensible framing instead. Checkable via a test prompt designed to bait an unverifiable claim.

## 12. Structuring Step — organizes, does not author

**Traces to:** PRD §4 Structuring Step

- GIVEN a `user_provided_script`, WHEN the Structuring Step processes it, THEN beat content matches the user's original wording (only `beat_id`/`type`/`duration_seconds` assigned — no new content authored), and output conforms to the same canonical schema as generation.
- GIVEN the Structuring Step produces malformed output that fails schema validation, WHEN retried, THEN it follows the identical policy as generation's own malformed-output row in §10 above — up to 3 attempts, then surfaced to the user — since the PRD specifies the Structuring Step "uses the same schema-validation error handling as generation," not a separate policy of its own.
