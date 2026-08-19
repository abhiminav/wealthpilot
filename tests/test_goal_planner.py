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

def test_goal_plan_contains_glide_path():

    result = create_goal_plan(
        "Retirement",
        1000000,
        15,
        "Aggressive",
    )

    assert "glide_path" in result
    assert len(result["glide_path"]) == 4


def test_goal_plan_contains_monthly_returns():

    result = create_goal_plan(
        "Retirement",
        1000000,
        15,
        "Aggressive",
    )

    assert "monthly_returns" in result
    assert len(result["monthly_returns"]) == 180


def test_goal_plan_projection_matches_horizon():

    result = create_goal_plan(
        "Retirement",
        1000000,
        15,
        "Aggressive",
    )

    projection = result["projection"]

    assert len(projection) == 180


def test_goal_plan_reaches_target():

    result = create_goal_plan(
        "Retirement",
        1000000,
        15,
        "Aggressive",
    )

    final_value = result["projection"][-1][
        "portfolio_value"
    ]

    assert final_value == pytest.approx(
        result["target_amount"],
        abs=1,
    )


def test_goal_plan_glide_path_de_risks():

    result = create_goal_plan(
        "Retirement",
        1000000,
        15,
        "Aggressive",
    )

    equity = [
        stage["allocation"]["Equity"]
        for stage in result["glide_path"]
    ]

    debt = [
        stage["allocation"]["Debt"]
        for stage in result["glide_path"]
    ]

    assert equity == sorted(
        equity,
        reverse=True,
    )

    assert debt == sorted(debt)


def test_expected_return_remains_available():

    result = create_goal_plan(
        "Retirement",
        1000000,
        15,
        "Aggressive",
    )

    assert "expected_return" in result
    assert result["expected_return"] > 0