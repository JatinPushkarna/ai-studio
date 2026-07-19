# Acceptance Tests — Post-Processing Engine (Editor)

Draft only. Traces to `AI_Studio_PRD.md` Section 5 unless noted. **Not committed as final — for Jatin to review and challenge before that happens.**

## 1. No root-level `script` property

**Traces to:** PRD §5 Inputs — Request Schema note

- GIVEN an Editor request, WHEN the request schema is inspected, THEN there is no root-level `script` field — script content is only reachable via `video_analyzer_output.beats[].script_text`.

## 2. `video_type` determines placement strategy

**Traces to:** PRD §5 Inputs note on `video_type`; `description_chain.md` Pipeline Flow step 5

- GIVEN `video_type: split_screen`, WHEN interpretation/generation run, THEN generated overlays/B-roll target the dedicated empty space.
- GIVEN `video_type: talking_head`, WHEN interpretation/generation run, THEN generated overlays/B-roll compose on top of the single existing footage layer.

## 3. Six-step pipeline order + progress reporting

**Traces to:** PRD §5 Pipeline Steps, Progress Reporting

- GIVEN a composite request runs to completion, WHEN progress is polled, THEN steps are reported in order: 1/6 interpretation, 2/6 generation, 3/6 sfx_selection, 4/6 assembly, 5/6 rendering, 6/6 finalizing.
- GIVEN the current step is anything other than rendering, WHEN progress is reported, THEN only a discrete in-progress/complete state is shown, never an estimated percentage.
- GIVEN the current step is rendering, WHEN progress is reported, THEN `step_detail` carries real sub-progress sourced from Remotion's own `onProgress` callback (e.g. frame count).

## 4. Graceful degradation — unmatched beat

**Traces to:** PRD §5 Error Handling "Unmatched beat from Video Analyzer"; `description_chain.md` step 5

- GIVEN `video_analyzer_output` shows `matched: false` for a beat, WHEN the Editor pipeline processes it, THEN overlay/B-roll generation is skipped for that beat only (no timestamp to anchor it to) — not treated as a pipeline failure, and the composite continues with remaining matched beats.

## 5. Graceful degradation — interpretation/generation failure

**Traces to:** PRD §5 Error Handling "Interpretation failure", "Generation failure"

- GIVEN interpretation produces an unusable/nonsensical visual concept for a beat, WHEN retried up to 3 attempts and still failing, THEN generation for that beat is skipped, flagged in the composition file for manual review, and the rest of the composite proceeds.
- GIVEN generated Remotion component code fails to compile or fails schema validation, WHEN retried up to 3 attempts (model told the specific error each time) and still failing, THEN the same skip-that-beat-only fallback applies.

## 6. SFX selection — filtered, no generation

**Traces to:** PRD §5 Pipeline Steps step 3

- GIVEN a matched beat and a Creator Profile with tone/category tags (e.g. educational), WHEN SFX selection runs, THEN only library SFX matching that tone/category are eligible candidates — SFX are matched from the library, never generated.

## 7. SFX no-match — explicitly undefined for v1

**Traces to:** PRD §5 Error Handling "SFX no match", Scope Note: SFX Fallback, Out-of-Scope section

- GIVEN no appropriately-tagged SFX exists for a beat, WHEN SFX selection runs, THEN this scenario has **no defined v1 behavior**. This test exists to assert the gap is real and must not be silently papered over with invented fallback logic — any implementation choice here requires an explicit scope conversation first, not a default picked in passing.

## 8. Assembly failure

**Traces to:** PRD §5 Error Handling "Assembly failure"

- GIVEN the composition manifest can't be built (conflicting timestamps, malformed component references), WHEN retried once and still failing, THEN a partial composition (footage + whatever beats succeeded) is returned rather than blocking entirely.

## 9. Render failure / preserved composition

**Traces to:** PRD §5 Error Handling "Render failure"; `description_chain.md` step 7

- GIVEN Remotion render errors or exceeds timeout, WHEN retried up to 3 times and still failing, THEN the composition file is preserved and accessible via MCP; the user can hand-edit or manually run `npx remotion render` — no full pipeline restart required.

## 10. Composite feedback — unconditional eligibility, download-triggered

**Traces to:** PRD §5 Feedback Capture (Composite); `description_chain.md` step 6 (amended this session — "downloaded," not "delivered")

- GIVEN any rendered composite, WHEN the Feedback Capture endpoint is called with `composite_id`, THEN it is accepted regardless of any quality signal — every composite is feedback-eligible unconditionally (no advisories-equivalent gate exists for composites).
- GIVEN a composite has been rendered but not yet downloaded, WHEN checking whether feedback has been prompted, THEN it has not — delivery/rendering alone is not the trigger.
- GIVEN the user downloads the composite file, WHEN the download completes, THEN the feedback prompt triggers.
- GIVEN feedback already captured once for a `composite_id`, WHEN the endpoint is called again for it, THEN `status: error`, no overwrite — same single-capture rule as scripts.

## 11. `retrieved_past_composites` — no exclusion tier

**Traces to:** PRD §5 Inputs note ("no equivalent to advisories-based exclusion")

- GIVEN composites with a range of feedback ratings (up/down/null), including some never rated at all, WHEN `retrieved_past_composites` is assembled for a new Editor request, THEN every composite is eligible for retrieval regardless of rating — ranking only (upvoted prioritized, downvoted deprioritized), never excluded.

## 12. Scope-boundary assertions

**Traces to:** PRD §5 Scope Note: Music; Out-of-Scope section "Automated quality eval/retry loop"

- GIVEN any composite request, WHEN the pipeline runs, THEN no background music is added at any step, and no automated visual-quality score/retry loop runs — a subjectively bad-looking or oddly-paced composite is never auto-rejected or auto-retried, only the mechanical failure conditions in tests 5/8/9 above trigger retries.
