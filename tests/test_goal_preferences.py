import pytest

from recommendation.goal_preferences import (
    calculate_goal_adjusted_score,
    get_goal_weights,
)


def test_all_goals_have_valid_weights():

    goals = [
        "Emergency Fund",
        "House Down Payment",
        "Education",
        "Retirement",
        "Wealth Creation",
    ]

    for goal in goals:

        weights = get_goal_weights(goal)

        assert set(weights.keys()) == {
            "cagr_score",
            "sharpe_score",
            "volatility_score",
            "drawdown_score",
        }

        assert abs(
            sum(weights.values()) - 1.0
        ) < 1e-9


def test_invalid_goal():

    with pytest.raises(ValueError):

        get_goal_weights(
            "Invalid Goal"
        )


def test_goal_adjusted_score():

    fund = {
        "cagr_score": 80.0,
        "sharpe_score": 70.0,
        "volatility_score": 60.0,
        "drawdown_score": 50.0,
    }

    score = calculate_goal_adjusted_score(
        fund,
        "Wealth Creation",
    )

    expected = (
        80.0 * 0.40
        + 70.0 * 0.30
        + 60.0 * 0.15
        + 50.0 * 0.15
    )

    assert score == pytest.approx(
        expected
    )


def test_emergency_fund_prioritizes_stability():

    emergency_weights = get_goal_weights(
        "Emergency Fund"
    )

    wealth_weights = get_goal_weights(
        "Wealth Creation"
    )

    assert (
        emergency_weights["volatility_score"]
        > wealth_weights["volatility_score"]
    )

    assert (
        emergency_weights["drawdown_score"]
        > wealth_weights["drawdown_score"]
    )

    assert (
        wealth_weights["cagr_score"]
        > emergency_weights["cagr_score"]
    )