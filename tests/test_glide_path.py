import pytest

from planning.glide_path import (
    generate_glide_path,
)


def test_generate_glide_path_returns_current_stage():

    stages = generate_glide_path(
        "Moderate",
        8,
    )

    assert stages[0]["stage"] == "Current"
    assert stages[0]["year"] == 0


def test_glide_path_allocations_sum_to_100():

    stages = generate_glide_path(
        "Moderate",
        15,
    )

    for stage in stages:
        assert sum(
            stage["allocation"].values()
        ) == 100


def test_long_horizon_has_multiple_stages():

    stages = generate_glide_path(
        "Aggressive",
        15,
    )

    assert len(stages) == 4


def test_equity_exposure_never_increases():

    stages = generate_glide_path(
        "Aggressive",
        15,
    )

    equities = [
        stage["allocation"]["Equity"]
        for stage in stages
    ]

    assert equities == sorted(
        equities,
        reverse=True,
    )


def test_debt_exposure_never_decreases():

    stages = generate_glide_path(
        "Aggressive",
        15,
    )

    debt = [
        stage["allocation"]["Debt"]
        for stage in stages
    ]

    assert debt == sorted(debt)


def test_gold_remains_constant():

    stages = generate_glide_path(
        "Moderate",
        15,
    )

    gold = [
        stage["allocation"]["Gold"]
        for stage in stages
    ]

    assert len(set(gold)) == 1
    assert gold[0] == 10


def test_short_horizon_is_defensive():

    stages = generate_glide_path(
        "Aggressive",
        2,
    )

    assert stages[0]["allocation"] == {
        "Equity": 0,
        "Debt": 90,
        "Gold": 10,
    }


def test_invalid_horizon():

    with pytest.raises(ValueError):

        generate_glide_path(
            "Moderate",
            0,
        )


def test_invalid_risk_profile():

    with pytest.raises(ValueError):

        generate_glide_path(
            "Unknown",
            8,
        )


def test_monthly_return_sequence_has_correct_length():

    from planning.glide_path import (
        generate_monthly_returns_from_glide_path,
    )

    returns = generate_monthly_returns_from_glide_path(
        "Moderate",
        15,
    )

    assert len(returns) == 180


def test_monthly_returns_are_non_increasing():

    from planning.glide_path import (
        generate_monthly_returns_from_glide_path,
    )

    returns = generate_monthly_returns_from_glide_path(
        "Moderate",
        15,
    )

    assert returns == sorted(
        returns,
        reverse=True,
    )


def test_short_horizon_monthly_returns():

    from planning.glide_path import (
        generate_monthly_returns_from_glide_path,
    )

    returns = generate_monthly_returns_from_glide_path(
        "Aggressive",
        2,
    )

    assert len(returns) == 24
    assert len(set(returns)) == 1


def test_eight_year_monthly_returns():

    from planning.glide_path import (
        generate_monthly_returns_from_glide_path,
    )

    returns = generate_monthly_returns_from_glide_path(
        "Moderate",
        8,
    )

    assert len(returns) == 96
    assert returns == sorted(
        returns,
        reverse=True,
    )


def test_invalid_monthly_return_horizon():

    from planning.glide_path import (
        generate_monthly_returns_from_glide_path,
    )

    with pytest.raises(ValueError):

        generate_monthly_returns_from_glide_path(
            "Moderate",
            0,
        )