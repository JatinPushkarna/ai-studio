"""Generation system prompt. See ../../../../AI_Studio_PRD.md Section 4,
Outputs / Temperature / No-Hallucination Constraint.
"""

from ai_studio_schemas import AudienceProfile, CreatorProfile

from script_engine.duration import beat_pacing, duration_budget

# PRD line ~311, No-Hallucination Constraint.
NO_HALLUCINATION_GUARDRAIL = (
    "Do not fabricate specific facts, statistics, studies, or quotes you "
    "cannot verify. Prefer general, defensible framing over unverifiable "
    "specifics."
)


def build_system_prompt(
    creator_profile: CreatorProfile,
    audience_profile: AudienceProfile,
    target_duration_seconds: int,
    is_identity_relevant: bool = False,
) -> str:
    """is_identity_relevant is hard-coded False at every call site today --
    the classifier that decides this depends on RAG retrieval, not yet built. The slot
    exists here so that logic has somewhere to plug into once it exists.
    """
    budget = duration_budget(target_duration_seconds)
    pacing = beat_pacing(target_duration_seconds)

    lines = [
        "You are Script Engine, the generation engine behind a short-form "
        "video app for solo content creators. Write a single script "
        "structured into narrative beats: exactly one hook beat (opens the "
        "script), one or more content beats, and exactly one cta beat "
        "(closes the script).",
        "",
        f"Write in the creator's own tone: {creator_profile.style_tone}.",
        "Creator's content category: "
        + creator_profile.category
        + (
            f" (also covers: {', '.join(creator_profile.adjacent_topics)})"
            if creator_profile.adjacent_topics
            else ""
        )
        + ".",
    ]

    if creator_profile.platforms:
        lines.append(f"Platforms: {', '.join(creator_profile.platforms)}.")

    lines.append(
        f"Audience: ages {audience_profile.age_range.min}-"
        f"{audience_profile.age_range.max}, {audience_profile.gender}, "
        f"interested in {', '.join(audience_profile.interest_areas)}."
    )

    if is_identity_relevant:
        if creator_profile.age is not None:
            lines.append(f"Creator age: {creator_profile.age}.")
        if creator_profile.gender is not None:
            lines.append(f"Creator gender: {creator_profile.gender}.")

    lines += [
        "",
        f"This script will be read aloud in a {target_duration_seconds}-second "
        f"video (spoken content should land within approximately "
        f"{budget.low:.0f}-{budget.high:.0f} seconds after a post-production "
        "reserve). People decide whether to keep watching in the first few "
        "seconds, so pace the beats accordingly -- as a length guide, not a "
        "strict requirement:",
        f"  - hook: ~{pacing.hook_seconds:.0f}s (~{pacing.hook_words} words) "
        "-- a single sharp line, not a windup. This is the entire scroll-stopping "
        "window; don't spend it on preamble.",
        f"  - content beat(s): ~{pacing.content_seconds:.0f}s "
        f"(~{pacing.content_words} words) combined -- the substance goes here.",
        f"  - cta: ~{pacing.cta_seconds:.0f}s (~{pacing.cta_words} words) -- "
        "one clear ask, not a longer sign-off just because the video is longer.",
        "This is guidance, not a strict requirement: actual duration is "
        "measured from your real word count after generation, and you may be "
        "asked to retry with a correction if it's off.",
        "",
        NO_HALLUCINATION_GUARDRAIL,
    ]

    return "\n".join(lines)