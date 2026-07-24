"""Script Engine generation chain. See ../../../../AI_Studio_PRD.md Section 4,
Error Handling & Retry Policy.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from ai_studio_schemas import Beat, Script, ScriptOrigin
from ai_studio_schemas.script import BeatType
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, model_validator

from script_engine.duration import duration_budget, words_to_seconds
from script_engine.prompt import build_system_prompt
from script_engine.schemas import (
    GenerationError,
    GenerationRequest,
    GenerationResponse,
    GenerationStatus,
)

# Load the repo-root .env regardless of the caller's working directory --
# services/script-engine/src/script_engine/generation.py -> AI Studio/.env
load_dotenv(Path(__file__).resolve().parents[4] / ".env")

logger = logging.getLogger(__name__)

MODEL_NAME = "claude-sonnet-5"
MAX_ATTEMPTS = 3
# No temperature/top_p/top_k -- current-generation flagship models (Sonnet 5,
# Opus 4.8, Fable 5) reject any non-default sampling parameter with a 400
# error. See PRD Section 4, "Creativity Control" (formerly "Temperature").


class GeneratedBeat(BaseModel):
    """LLM-facing beat shape. No beat_id/duration_seconds -- those are
    computed by our code after generation, never authored by the model."""

    type: BeatType
    content: str


class GeneratedScript(BaseModel):
    """LLM-facing script shape. No script_id/total_duration_seconds/
    advisories -- see GeneratedBeat docstring for the same reasoning."""

    beats: list[GeneratedBeat]

    @model_validator(mode="after")
    def _check_beat_structure(self) -> "GeneratedScript":
        if len(self.beats) < 3:
            raise ValueError(
                "Script must have at least 3 beats: one hook, one or more "
                "content, one cta."
            )
        if self.beats[0].type != BeatType.HOOK:
            raise ValueError("First beat must be type 'hook'.")
        if self.beats[-1].type != BeatType.CTA:
            raise ValueError("Last beat must be type 'cta'.")
        hook_count = sum(1 for b in self.beats if b.type == BeatType.HOOK)
        cta_count = sum(1 for b in self.beats if b.type == BeatType.CTA)
        if hook_count != 1:
            raise ValueError(f"Expected exactly one hook beat, got {hook_count}.")
        if cta_count != 1:
            raise ValueError(f"Expected exactly one cta beat, got {cta_count}.")
        return self


def _build_chain():
    llm = ChatAnthropic(model=MODEL_NAME)
    # include_raw=True: lets us inspect the raw tool call and attempt a
    # mechanical repair (see _repair_double_encoded_beats) instead of
    # immediately burning a retry attempt on a recognizable, fixable quirk.
    return llm.with_structured_output(GeneratedScript, include_raw=True)


def _repair_double_encoded_beats(raw_message) -> GeneratedScript | None:
    """Observed model quirk (real API testing, dense/long topics): instead of
    returning the tool argument {"beats": [...]} directly, the model
    occasionally re-encodes the whole object as a JSON string one level too
    deep -- {"beats": "{\\"beats\\": [...]}"}. Pydantic correctly rejects a
    string where a list is expected. This is a recognizable, mechanical
    double-encoding, not a content problem, so it's repaired here rather than
    spent as a retry attempt (schema and duration failures share one 3-attempt
    budget -- see generate_script docstring -- so silently eating an attempt
    on this would starve legitimate duration-correction retries).
    """
    tool_calls = getattr(raw_message, "tool_calls", None)
    if not tool_calls:
        return None
    beats_value = tool_calls[0].get("args", {}).get("beats")
    if not isinstance(beats_value, str):
        return None
    try:
        inner = json.loads(beats_value)
    except (json.JSONDecodeError, TypeError):
        return None
    try:
        return GeneratedScript.model_validate(inner)
    except Exception:  # noqa: BLE001 -- repair is best-effort, fall through to normal retry
        return None


def assemble_script(generated: GeneratedScript, target_duration_seconds: int) -> Script:
    """Maps LLM output -> canonical Script, computing every field the LLM
    never authored (beat_id, duration_seconds, script_id, total_duration_seconds,
    advisories) -- PRD line ~100: duration is a downstream measurement, not
    something the LLM plans upfront."""
    beats: list[Beat] = []
    for i, generated_beat in enumerate(generated.beats, start=1):
        word_count = len(generated_beat.content.split())
        duration = round(words_to_seconds(word_count))
        beats.append(
            Beat(
                beat_id=f"beat_{i}",
                type=generated_beat.type,
                content=generated_beat.content,
                duration_seconds=duration,
            )
        )
    total_duration = sum(b.duration_seconds for b in beats)
    return Script(
        script_id=None,
        origin=ScriptOrigin.GENERATED,
        target_duration_seconds=target_duration_seconds,
        total_duration_seconds=total_duration,
        beats=beats,
        advisories=[],
    )


@dataclass
class _Attempt:
    script: Script
    distance_from_range: float


def generate_script(request: GenerationRequest) -> GenerationResponse:
    """Up to MAX_ATTEMPTS total, per PRD Error Handling & Retry Policy.
    Schema validity is checked first each attempt, then duration -- both
    failure modes share this one retry budget rather than getting 3 each.

    Terminal fallback:
      - Schema never validates in 3 attempts -> status=error, no script.
      - Duration never lands in range in 3 attempts -> accept the
        closest-to-range attempt seen, status=success (a usable script was
        produced) -- callers can detect the accepted-as-closest case by
        re-checking is_within_budget() themselves, same as any consumer would.
    """
    chain = _build_chain()
    system_prompt = build_system_prompt(
        creator_profile=request.creator_profile,
        audience_profile=request.audience_profile,
        target_duration_seconds=request.target_duration_seconds,
        is_identity_relevant=False,  # gate logic depends on RAG retrieval, not yet built
    )
    budget = duration_budget(request.target_duration_seconds)

    messages: list[tuple[str, str]] = [
        ("system", system_prompt),
        ("human", f"Write the script. Topic: {request.topic}"),
    ]

    best_attempt: _Attempt | None = None
    last_schema_error: str | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            result = chain.invoke(messages)
        except Exception as exc:  # noqa: BLE001 -- genuine API-level failures
            # (network, rate limit, auth) -- distinct from schema/parsing
            # issues, which include_raw=True now surfaces without raising.
            last_schema_error = str(exc)
            logger.warning("Attempt %d: API call failed: %s", attempt, exc)
            messages.append(
                (
                    "human",
                    f"Your previous attempt failed: {exc}. Please retry, "
                    "correcting this.",
                )
            )
            continue

        generated: GeneratedScript | None = result["parsed"]
        if generated is None:
            generated = _repair_double_encoded_beats(result["raw"])
            if generated is not None:
                logger.info("Attempt %d: repaired double-encoded beats field", attempt)

        if generated is None:
            last_schema_error = str(result["parsing_error"])
            logger.warning("Attempt %d: schema validation failed: %s", attempt, last_schema_error)
            messages.append(
                (
                    "human",
                    f"Your previous output failed schema validation: "
                    f"{last_schema_error}. Please retry, correcting this.",
                )
            )
            continue

        script = assemble_script(generated, request.target_duration_seconds)

        if budget.low <= script.total_duration_seconds <= budget.high:
            logger.info(
                "Attempt %d: duration %ss within range %.1f-%.1fs",
                attempt,
                script.total_duration_seconds,
                budget.low,
                budget.high,
            )
            return GenerationResponse(script=script, status=GenerationStatus.SUCCESS)

        distance = min(
            abs(script.total_duration_seconds - budget.low),
            abs(script.total_duration_seconds - budget.high),
        )
        if best_attempt is None or distance < best_attempt.distance_from_range:
            best_attempt = _Attempt(script=script, distance_from_range=distance)

        logger.warning(
            "Attempt %d: duration %ss outside range %.1f-%.1fs",
            attempt,
            script.total_duration_seconds,
            budget.low,
            budget.high,
        )

        if attempt < MAX_ATTEMPTS:
            direction = "Shorten" if script.total_duration_seconds > budget.high else "Lengthen"
            messages.append(
                (
                    "human",
                    f"Your script measured {script.total_duration_seconds}s of "
                    f"spoken time, but the target range is {budget.low:.1f}-"
                    f"{budget.high:.1f}s. {direction} it and retry.",
                )
            )

    if best_attempt is not None:
        logger.warning(
            "Terminal fallback: accepting closest attempt (%ss, target %.1f-%.1fs)",
            best_attempt.script.total_duration_seconds,
            budget.low,
            budget.high,
        )
        return GenerationResponse(script=best_attempt.script, status=GenerationStatus.SUCCESS)

    logger.error("Terminal fallback: no valid schema after %d attempts", MAX_ATTEMPTS)
    return GenerationResponse(
        script=None,
        status=GenerationStatus.ERROR,
        error=GenerationError(
            code="schema_validation_failed",
            message=last_schema_error or "Unknown schema validation failure",
        ),
    )