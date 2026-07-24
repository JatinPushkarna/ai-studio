"""Unit tests for the duration-budget formula against the PRD's own worked
examples (AI_Studio_PRD.md, 'Duration Budget Formula')."""

import pytest

from script_engine.duration import (
    beat_pacing,
    duration_budget,
    is_within_budget,
    seconds_to_approx_words,
    words_to_seconds,
)


@pytest.mark.parametrize(
    "target_duration_seconds, expected_spoken_target, expected_low, expected_high",
    [
        (30, 25.5, 22.95, 28.05),
        (45, 38.25, 34.425, 42.075),
        (60, 51.0, 45.9, 56.1),
    ],
)
def test_duration_budget_matches_prd_worked_examples(
    target_duration_seconds, expected_spoken_target, expected_low, expected_high
):
    budget = duration_budget(target_duration_seconds)
    assert budget.spoken_target == pytest.approx(expected_spoken_target)
    assert budget.low == pytest.approx(expected_low)
    assert budget.high == pytest.approx(expected_high)


def test_words_to_seconds_uses_avg_speaking_wpm():
    # 150 WPM == 2.5 words/sec -> 75 words should take 30s.
    assert words_to_seconds(75) == pytest.approx(30.0)


def test_seconds_to_approx_words_is_the_inverse_direction():
    assert seconds_to_approx_words(30.0) == 75


def test_is_within_budget_true_inside_range():
    assert is_within_budget(25.5, target_duration_seconds=30) is True


def test_is_within_budget_false_outside_range():
    assert is_within_budget(15.0, target_duration_seconds=30) is False


@pytest.mark.parametrize(
    "target_duration_seconds, expected_content_seconds, expected_content_words",
    [
        (30, 18.5, 46),
        (45, 31.25, 78),
        (60, 44.0, 110),
    ],
)
def test_beat_pacing_content_absorbs_remainder(
    target_duration_seconds, expected_content_seconds, expected_content_words
):
    pacing = beat_pacing(target_duration_seconds)
    assert pacing.content_seconds == pytest.approx(expected_content_seconds)
    assert pacing.content_words == expected_content_words


@pytest.mark.parametrize("target_duration_seconds", [30, 45, 60])
def test_beat_pacing_hook_and_cta_are_fixed_regardless_of_target(target_duration_seconds):
    # Hook/CTA don't scale with video length -- same seconds/words at every target.
    pacing = beat_pacing(target_duration_seconds)
    assert pacing.hook_seconds == 3.0
    assert pacing.hook_words == 8
    assert pacing.cta_seconds == 4.0
    assert pacing.cta_words == 10
