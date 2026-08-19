from recommendation.service import (
    generate_recommendation,
)


def test_service_generates_recommendation():

    result = generate_recommendation(
        goal_type="Retirement",
        target_amount=1_000_000,
        horizon_years=15,
        risk_profile="Aggressive",
    )

    assert result["risk_profile"] == "Aggressive"

    assert sum(
        result["allocation"].values()
    ) == 100

    assert (
        result["required_monthly_sip"]
        > 0
    )

    assert len(
        result["recommendations"]["Equity"]
    ) > 0

    assert len(
        result["recommendations"]["Debt"]
    ) > 0

    assert len(
        result["recommendations"]["Gold"]
    ) > 0

    assert len(
        result["projection"]
    ) == 180