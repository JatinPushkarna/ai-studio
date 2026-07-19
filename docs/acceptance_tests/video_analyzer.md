# Acceptance Tests — Video Analyzer

Draft only. Traces to `AI_Studio_PRD.md` "Video Analyzer (Prerequisite for Editor)" section unless noted. **Not committed as final — for Jatin to review and challenge before that happens.**

## 1. Output schema shape

**Traces to:** PRD Video Analyzer Outputs

- GIVEN a valid script + footage input, WHEN Video Analyzer completes processing, THEN output is `{script_id, beats: [{beat_id, matched, confidence, script_text, actual_spoken_text, start_timestamp, end_timestamp}]}` for every beat in the source script.

## 2. Minor-drift-only matching scope

**Traces to:** PRD "Scope: Minor Drift Only"

- GIVEN footage with minor rephrasing/filler words/small ad-libs relative to the script, WHEN matching runs, THEN affected beats are `matched: true` with an appropriate confidence score.
- GIVEN footage with reordered beats, omitted beats, or substantial ad-libbing/unscripted tangents, WHEN matching runs, THEN these are surfaced as unmatched (`matched: false`) rather than the tool attempting to reorder, recover, or otherwise resolve them.

## 3. Confidence threshold behavior

**Traces to:** PRD Error Handling "Low-confidence match"

- GIVEN a beat matched with confidence below the ~70% threshold (tunable), WHEN returned, THEN `matched: true` but flagged to the user as uncertain — not silently accepted as a clean match.

## 4. Unmatched beat handling

**Traces to:** PRD Error Handling "Beat unmatched"

- GIVEN a beat the semantic matcher cannot confidently place, WHEN returned, THEN `matched: false`, `script_text` populated, `actual_spoken_text: null`, and the specific missing line is surfaced to the user.

## 5. Transcription failure retry

**Traces to:** PRD Error Handling "Transcription fails/garbage"

- GIVEN transcription returns empty/garbage or an API error, WHEN this occurs, THEN transcription is retried once; if still failing, the user is flagged that footage/audio quality may be the issue.

## 6. Footage technical validation

**Traces to:** PRD Error Handling "Footage fails technical validation"

- GIVEN footage with the wrong format, corruption, or a duration mismatch vs. the script, WHEN validation runs, THEN the footage is rejected before transcription starts, and the user is prompted to re-upload.

## 7. Non-canonical script rejected

**Traces to:** PRD Error Handling "Script not in canonical schema"

- GIVEN an incoming script that fails schema validation (bypassed Script Engine/Structuring Step entirely), WHEN Video Analyzer receives it, THEN rejected with guidance: "This script isn't in AI Studio's format — use Script Engine to generate or structure it for best results."
