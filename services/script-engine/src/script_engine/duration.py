"""Duration-budget math. See ../../../../AI_Studio_PRD.md 'Duration Budget
Formula' and 'Word Count <-> Duration Conversion'.

AVG_SPEAKING_WPM is used in two directions:
  1. Pre-generation (guidance, non-authoritative): target_duration_seconds ->
     spoken_target -> approximate target word count, told to the LLM as a
     length hint (seconds_to_approx_words).
  2. Post-generation (measurement, authoritative): actual word count -> actual
     duration_seconds, checked against the acceptable range (words_to_seconds).
"""

from dataclasses import dataclass

# v1 placeholder -- fixed, hardcoded, no per-creator calibration. Every call
# site references this one constant so a future recalibration is a one-line
# change, not a multi-file hunt.
AVG_SPEAKING_WPM = 150  # 2.5 words/sec

POST_PRODUCTION_RESERVE_RATIO = 0.15
DURATION_TOLERANCE_RATIO = 0.10

# Hook/CTA pacing: fixed seconds, not a percentage of spoken_target. A hook
# has to land within a short attention window regardless of how long the
# overall video is (people decide to keep scrolling or not in the first few
# seconds) -- making it proportionally longer on a 60s video would pad it
# with nothing but rambling, not more attention-grabbing power. Same logic
# for CTA: one clear ask doesn't need to get wordier just because the video
# is longer. Content beats absorb 100% of any extra runway a longer target
# duration provides.
HOOK_SECONDS = 3.0
CTA_SECONDS = 4.0


@dataclass(frozen=True)
class BudgetRange:
    spoken_target: float
    low: float
    high: float


@dataclass(frozen=True)
class BeatPacing:
    hook_seconds: float
    hook_words: int
    content_seconds: float
    content_words: int
    cta_seconds: float
    cta_words: int


def duration_budget(target_duration_seconds: int) -> BudgetRange:
    """PRD Duration Budget Formula: 15% post-production reserve, then +/-10%
    tolerance around the remaining spoken_target."""
    reserve = target_duration_seconds * POST_PRODUCTION_RESERVE_RATIO
    spoken_target = target_duration_seconds - reserve
    tolerance = spoken_target * DURATION_TOLERANCE_RATIO
    return BudgetRange(
        spoken_target=spoken_target,
        low=spoken_target - tolerance,
        high=spoken_target + tolerance,
    )


def beat_pacing(target_duration_seconds: int) -> BeatPacing:
    """Splits the spoken_target into fixed-length hook/cta and a
    content beat that absorbs the remainder. Prompt guidance only -- the
    generation prompt tells the model this breakdown to help it allocate
    words sensibly, but only TOTAL duration is measured/retried on after
    generation (see generation.py); individual beats aren't independently
    validated against these sub-targets.
    """
    budget = duration_budget(target_duration_seconds)
    content_seconds = budget.spoken_target - HOOK_SECONDS - CTA_SECONDS
    return BeatPacing(
        hook_seconds=HOOK_SECONDS,
        hook_words=seconds_to_approx_words(HOOK_SECONDS),
        content_seconds=content_seconds,
        content_words=seconds_to_approx_words(content_seconds),
        cta_seconds=CTA_SECONDS,
        cta_words=seconds_to_approx_words(CTA_SECONDS),
    )


def words_to_seconds(word_count: int) -> float:
    """Post-generation measurement direction -- authoritative."""
    return word_count / (AVG_SPEAKING_WPM / 60)


def seconds_to_approx_words(seconds: float) -> int:
    """Pre-generation guidance direction -- a prompt hint only, never trusted
    for the actual duration check."""
    return round(seconds * (AVG_SPEAKING_WPM / 60))


def is_within_budget(total_duration_seconds: float, target_duration_seconds: int) -> bool:
    budget = duration_budget(target_duration_seconds)
    return budget.low <= total_duration_seconds <= budget.high