"""Script-Engine-local request/response models. See ../../../../AI_Studio_PRD.md
Section 4, JSON Schema -- Request/Response.

Deliberately NOT in shared/ai_studio_schemas: GenerationRequest and
GenerationResponse are Script Engine's own API shapes. Only the inner `Script`
object (ai_studio_schemas.Script) is the cross-service contract Video Analyzer
consumes (PRD line ~336) -- merging status/error into it would leak
Script-Engine-specific bookkeeping into a payload other services receive.
"""

from enum import Enum
from typing import Literal

from ai_studio_schemas import AudienceProfile, CreatorProfile, Script
from pydantic import BaseModel, Field


class PastScriptFeedback(BaseModel):
    rating: Literal["up", "down"] | None = None
    reason: str | None = None


class RetrievedPastScript(BaseModel):
    script_id: str
    content: str
    relevance_score: float
    feedback: PastScriptFeedback


class GenerationRequest(BaseModel):
    creator_profile: CreatorProfile
    audience_profile: AudienceProfile
    topic: str
    target_duration_seconds: Literal[30, 45, 60]
    user_provided_script: str | None = None
    # RAG retrieval doesn't exist yet -- field present for contract
    # completeness, always empty until then.
    retrieved_past_scripts: list[RetrievedPastScript] = Field(default_factory=list)


class GenerationStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class GenerationError(BaseModel):
    code: str
    message: str


class GenerationResponse(BaseModel):
    script: Script | None = None
    status: GenerationStatus
    error: GenerationError | None = None