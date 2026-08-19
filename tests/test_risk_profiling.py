from risk_profiling.scoring import (
    calculate_risk_score,
    classify_risk,
    get_risk_profile,
)
from risk_profiling.risk_profiles import RISK_PROFILES


def test_aggressive_score():
    score = calculate_risk_score(
        {
            "age": 25,
            "income_stability": "Very Stable",
            "horizon": "10+ years",
            "loss_tolerance": "Invest more",
            "experience": "Experienced",
        }
    )

    assert score == 18


def test_aggressive_classification():
    assert classify_risk(18) == "Aggressive"


def test_aggressive_profile():
    profile = get_risk_profile(18)

    assert profile["profile"] == "Aggressive"
    assert profile["min_score"] == 13
    assert profile["max_score"] == 18


def test_risk_profiles_have_valid_ranges():
    for profile in RISK_PROFILES.values():
        assert profile["min_score"] <= profile["max_score"]
        assert sum(
            profile["base_allocation"].values()
        ) == 100