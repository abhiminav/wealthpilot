import pandas as pd
import pytest

from recommendation.scoring import (
    min_max_score,
    calculate_category_scores,
)


def test_min_max_score_higher_is_better():
    series = pd.Series([10, 20, 30])

    result = min_max_score(series)

    assert result.tolist() == [0.0, 50.0, 100.0]


def test_min_max_score_lower_is_better():
    series = pd.Series([10, 20, 30])

    result = min_max_score(
        series,
        higher_is_better=False,
    )

    assert result.tolist() == [100.0, 50.0, 0.0]


def test_min_max_score_constant_series():
    series = pd.Series([10, 10, 10])

    result = min_max_score(series)

    assert result.tolist() == [50.0, 50.0, 50.0]


def test_category_scores_are_calculated():
    funds = pd.DataFrame(
        {
            "category": [
                "Large Cap",
                "Large Cap",
                "Large Cap",
            ],
            "cagr": [
                0.08,
                0.12,
                0.10,
            ],
            "sharpe_ratio": [
                0.5,
                1.2,
                0.8,
            ],
            "volatility": [
                0.18,
                0.12,
                0.15,
            ],
            "max_drawdown": [
                -0.25,
                -0.10,
                -0.18,
            ],
        }
    )

    result = calculate_category_scores(funds)

    assert "cagr_score" in result.columns
    assert "sharpe_score" in result.columns
    assert "volatility_score" in result.columns
    assert "drawdown_score" in result.columns
    assert "fund_score" in result.columns


def test_category_scores_rank_best_fund_highest():
    funds = pd.DataFrame(
        {
            "category": [
                "Large Cap",
                "Large Cap",
                "Large Cap",
            ],
            "cagr": [
                0.08,
                0.12,
                0.10,
            ],
            "sharpe_ratio": [
                0.5,
                1.2,
                0.8,
            ],
            "volatility": [
                0.18,
                0.12,
                0.15,
            ],
            "max_drawdown": [
                -0.25,
                -0.10,
                -0.18,
            ],
        }
    )

    result = calculate_category_scores(funds)

    best_fund = result.iloc[0]

    assert best_fund["cagr"] == pytest.approx(0.12)
    assert best_fund["sharpe_ratio"] == pytest.approx(1.2)
    assert best_fund["volatility"] == pytest.approx(0.12)
    assert best_fund["max_drawdown"] == pytest.approx(-0.10)


def test_scores_stay_between_zero_and_hundred():
    funds = pd.DataFrame(
        {
            "category": [
                "Large Cap",
                "Large Cap",
                "Large Cap",
            ],
            "cagr": [0.08, 0.12, 0.10],
            "sharpe_ratio": [0.5, 1.2, 0.8],
            "volatility": [0.18, 0.12, 0.15],
            "max_drawdown": [-0.25, -0.10, -0.18],
        }
    )

    result = calculate_category_scores(funds)

    assert result["fund_score"].between(0, 100).all()