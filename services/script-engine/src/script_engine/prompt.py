"""Generation system prompt. See ../../../../AI_Studio_PRD.md Section 4,
Outputs / Temperature / No-Hallucination Constraint.
"""

from ai_studio_schemas import AudienceProfile, CreatorProfile

from script_engine.duration import duration_budget, seconds_to_approx_words

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
    approx_words = seconds_to_approx_words(budget.spoken_target)

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
        f"Aim for approximately {approx_words} words total across all beats "
        "-- this is a rough length guide to help you land close on the "
        "first try, not a strict requirement you need to hit exactly.",
        "",
        NO_HALLUCINATION_GUARDRAIL,
    ]

    return "\n".join(lines)