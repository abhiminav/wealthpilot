import pandas as pd

from recommendation.recommendation_engine import (
    build_recommendation,
)


def test_full_recommendation_pipeline():

    funds = pd.read_csv(
        "data/processed/fund_metrics_clean.csv"
    )

    result = build_recommendation(
        funds=funds,
        goal_type="House Down Payment",
        target_amount=2_500_000,
        horizon_years=8,
        risk_profile="Moderate",
    )

    # Goal
    assert result["goal_type"] == "House Down Payment"
    assert result["target_amount"] == 2_500_000
    assert result["horizon_years"] == 8

    # Allocation
    assert sum(
        result["allocation"].values()
    ) == 100

    # SIP
    assert result["required_monthly_sip"] > 0

    # SIP allocation
    assert abs(
        sum(result["sip_allocation"].values())
        - result["required_monthly_sip"]
    ) < 0.01

    # Recommendations
    for asset_class, allocation in (
        result["allocation"].items()
    ):
        if allocation > 0:
            assert (
                len(
                    result["recommendations"][
                        asset_class
                    ]
                )
                > 0
            )

    # Projection
    projection = result["projection"]

    assert len(projection) == 96

    final_value = projection[-1][
        "portfolio_value"
    ]

    assert abs(
        final_value
        - result["target_amount"]
    ) < 1
