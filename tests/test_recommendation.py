import pandas as pd

from recommendation.asset_allocation import (
    get_asset_class,
)
from recommendation.scoring import (
    calculate_category_scores,
)


def test_category_scoring():
    data = pd.DataFrame(
        {
            "category": [
                "Large Cap",
                "Large Cap",
                "Debt",
                "Debt",
            ],
            "cagr": [
                0.10,
                0.12,
                0.07,
                0.08,
            ],
            "sharpe_ratio": [
                0.8,
                1.0,
                0.5,
                0.7,
            ],
            "volatility": [
                0.15,
                0.14,
                0.05,
                0.04,
            ],
            "max_drawdown": [
                -0.20,
                -0.15,
                -0.05,
                -0.03,
            ],
        }
    )

    scored = calculate_category_scores(data)

    assert "fund_score" in scored.columns
    assert len(scored) == 4


def test_equity_mapping():
    assert get_asset_class("Large Cap") == "Equity"