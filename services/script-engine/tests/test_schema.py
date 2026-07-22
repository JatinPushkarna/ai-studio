"""Unit tests for the canonical Script/Beat schema and Script-Engine-local
request/response envelope."""

import pytest
from ai_studio_schemas import (
    AgeRange,
    AudienceProfile,
    Beat,
    BeatType,
    CreatorProfile,
    Script,
    ScriptOrigin,
)
from pydantic import ValidationError

from script_engine.schemas import GenerationRequest


def _make_beat(beat_id: str = "beat_1", beat_type: BeatType = BeatType.HOOK) -> Beat:
    return Beat(beat_id=beat_id, type=beat_type, content="Some beat text.", duration_seconds=5)


def test_script_id_defaults_to_none():
    script = Script(
        origin=ScriptOrigin.GENERATED,
        target_duration_seconds=30,
        total_duration_seconds=25,
        beats=[_make_beat()],
    )
    assert script.script_id is None


def test_advisories_defaults_to_empty_list():
    script = Script(
        origin=ScriptOrigin.GENERATED,
        target_duration_seconds=30,
        total_duration_seconds=25,
        beats=[_make_beat()],
    )
    assert script.advisories == []


def test_beat_type_rejects_invalid_enum_value():
    with pytest.raises(ValidationError):
        Beat(beat_id="beat_1", type="not_a_real_type", content="x", duration_seconds=1)


def test_generation_request_rejects_invalid_target_duration():
    with pytest.raises(ValidationError):
        GenerationRequest(
            creator_profile=CreatorProfile(alias="a", category="c", style_tone="t"),
            audience_profile=AudienceProfile(
                age_range=AgeRange(min=20, max=30), gender="g", platform="p"
            ),
            topic="topic",
            target_duration_seconds=37,  # only 30/45/60 allowed
        )


def test_generation_request_defaults_retrieved_past_scripts_to_empty():
    request = GenerationRequest(
        creator_profile=CreatorProfile(alias="a", category="c", style_tone="t"),
        audience_profile=AudienceProfile(
            age_range=AgeRange(min=20, max=30), gender="g", platform="p"
        ),
        topic="topic",
        target_duration_seconds=30,
    )
    assert request.retrieved_past_scripts == []