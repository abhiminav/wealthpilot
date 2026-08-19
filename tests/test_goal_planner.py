import pytest

from planning.goal_planner import create_goal_plan


def test_invalid_target_amount():
    with pytest.raises(ValueError):
        create_goal_plan(
            "Retirement",
            0,
            15,
            "Aggressive",
        )


def test_negative_target_amount():
    with pytest.raises(ValueError):
        create_goal_plan(
            "Retirement",
            -100000,
            15,
            "Aggressive",
        )


def test_invalid_horizon():
    with pytest.raises(ValueError):
        create_goal_plan(
            "Retirement",
            1000000,
            0,
            "Aggressive",
        )


def test_negative_horizon():
    with pytest.raises(ValueError):
        create_goal_plan(
            "Retirement",
            1000000,
            -5,
            "Aggressive",
        )


def test_valid_plan():
    result = create_goal_plan(
        "Retirement",
        1000000,
        15,
        "Aggressive",
    )

    assert result["risk_profile"] == "Aggressive"
    assert result["target_amount"] == 1000000
    assert result["horizon_years"] == 15
    assert result["required_monthly_sip"] > 0