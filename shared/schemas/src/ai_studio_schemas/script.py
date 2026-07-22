"""Canonical Script/Beat schema. See ../../../AI_Studio_PRD.md Section 4,
JSON Schema -- Response. This is the contract the Structuring Step converges
on, Video Analyzer aligns against, and the Editor consumes descendants of --
changing these fields after those services exist is a breaking change."""

from enum import Enum

from pydantic import BaseModel, Field


class BeatType(str, Enum):
    HOOK = "hook"
    CONTENT = "content"
    CTA = "cta"


class Beat(BaseModel):
    # Sequential per-generation ("beat_1", "beat_2", ...), assigned by our
    # code after the LLM responds -- not authored by the LLM, and not needed
    # for retrieval within a script (beats are just a list under script_id).
    # Kept because Video Analyzer's own output schema reports per-beat match
    # results keyed by beat_id.
    beat_id: str
    type: BeatType
    content: str
    # Measured from word count after generation, never LLM-authored.
    duration_seconds: int


class AdvisoryType(str, Enum):
    STRUCTURAL = "structural"
    CLARITY = "clarity"


class Advisory(BaseModel):
    type: AdvisoryType
    message: str


class ScriptOrigin(str, Enum):
    GENERATED = "generated"
    USER_PROVIDED = "user_provided"


class Script(BaseModel):
    # Null for the entire pre-export lifetime (generation + every chat
    # refinement turn). Minted only at export -- which doesn't exist yet.
    script_id: str | None = None
    origin: ScriptOrigin
    target_duration_seconds: int
    total_duration_seconds: int
    beats: list[Beat]
    # Structural/clarity advisory-check logic is not in scope yet -- always
    # empty for now. Field exists because Video Analyzer/Editor expect it.
    advisories: list[Advisory] = Field(default_factory=list)
