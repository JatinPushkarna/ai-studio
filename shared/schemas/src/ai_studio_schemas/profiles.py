"""Creator/Audience Profile models. See ../../../AI_Studio_PRD.md Section 4, Inputs."""

from pydantic import BaseModel, Field


class AgeRange(BaseModel):
    min: int
    max: int


class CreatorProfile(BaseModel):
    alias: str
    category: str
    adjacent_topics: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)
    style_tone: str
    # Optional: only injected into the generation prompt when the topic is
    # classified as identity-relevant (relevance-gate logic depends on RAG
    # retrieval, not yet built).
    age: int | None = None
    gender: str | None = None


class AudienceProfile(BaseModel):
    age_range: AgeRange
    gender: str
    platform: str
    interest_areas: list[str] = Field(default_factory=list)
