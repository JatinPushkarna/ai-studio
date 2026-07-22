"""Real generation test against a real Creator/Audience Profile and 3 real
topics. Hits the live Anthropic API (Claude Sonnet 5) via generate_script();
costs a small amount of money per run. Run explicitly with:

    uv run --package script-engine pytest -m integration -v -s

(-s so print() output showing full results, including failures, is visible.)
"""

import pytest
from ai_studio_schemas import AgeRange, AudienceProfile, CreatorProfile

from script_engine.duration import duration_budget
from script_engine.generation import generate_script
from script_engine.schemas import GenerationRequest, GenerationStatus

CREATOR_PROFILE = CreatorProfile(
    alias="AI Builder",
    category="AI for Small Business",
    adjacent_topics=["Automation", "Productivity", "AI Revolution"],
    platforms=["Instagram", "YouTube", "TikTok"],
    style_tone="Warm, inviting",
)

AUDIENCE_PROFILE = AudienceProfile(
    age_range=AgeRange(min=35, max=55),
    gender="Male",
    platform="Instagram, YouTube, TikTok",
    interest_areas=["Business", "Entrepreneurship", "Tech", "AI", "Economy", "Productivity"],
)

REAL_TOPICS = [
    ("AI & Trust", 30),
    ("AI Hype vs Reality", 30),
    ("AI Implementation: Baby Steps", 30),
]


@pytest.mark.integration
@pytest.mark.parametrize("topic, target_duration_seconds", REAL_TOPICS)
def test_generate_real_script(topic, target_duration_seconds):
    request = GenerationRequest(
        creator_profile=CREATOR_PROFILE,
        audience_profile=AUDIENCE_PROFILE,
        topic=topic,
        target_duration_seconds=target_duration_seconds,
    )

    response = generate_script(request)
    budget = duration_budget(target_duration_seconds)

    print(f"\n{'=' * 70}\nTOPIC: {topic} (target {target_duration_seconds}s)\n{'=' * 70}")
    print(f"status: {response.status.value}")

    if response.status != GenerationStatus.SUCCESS or response.script is None:
        print(f"FAILURE -- no script produced. error: {response.error}")
        pytest.fail(
            f"'{topic}': generation failed after retries -- {response.error}"
        )

    script = response.script
    in_range = budget.low <= script.total_duration_seconds <= budget.high

    print(f"script_id: {script.script_id!r} (expected None pre-export)")
    print(f"target_duration_seconds: {script.target_duration_seconds}")
    print(f"total_duration_seconds: {script.total_duration_seconds}")
    print(f"acceptable range: {budget.low:.1f}s - {budget.high:.1f}s")
    print(f"WITHIN BUDGET: {in_range}" + ("" if in_range else "  <-- ACCEPTED AS CLOSEST (terminal fallback)"))
    print(f"beat count: {len(script.beats)} -- types: {[b.type.value for b in script.beats]}")

    for beat in script.beats:
        word_count = len(beat.content.split())
        print(f"  [{beat.beat_id} | {beat.type.value} | {beat.duration_seconds}s | {word_count}w] {beat.content}")

    # Hard requirements regardless of duration outcome: schema-valid beat
    # structure (already enforced by GeneratedScript's validator, but assert
    # here too as a black-box check on what the caller actually receives).
    assert script.script_id is None
    assert script.beats[0].type.value == "hook"
    assert script.beats[-1].type.value == "cta"
    assert script.advisories == []

    if not in_range:
        # Not a hard test failure -- this is documented terminal-fallback
        # behavior (PRD: accept closest, flag for chat adjustment) -- but
        # surfaced loudly so it isn't mistaken for a quiet pass.
        print(f"NOTE: '{topic}' landed outside the duration budget after retries.")