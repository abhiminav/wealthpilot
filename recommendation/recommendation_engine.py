import pandas as pd

from planning.goal_planner import (
    build_portfolio_projection,
    calculate_sip_allocation,
    create_goal_plan,
)
from recommendation.scoring import (
    calculate_category_scores,
)
from recommendation.fund_selector import (
    select_funds,
)


def build_fund_explanation(
    fund,
    asset_class: str,
    horizon_years: float,
    allocation: float,
) -> list[str]:
    """Generate transparent reasons for a fund recommendation."""

    reasons = []

    # Category-relative score
    if fund["fund_score"] >= 85:
        reasons.append(
            "Strong category-relative fund score"
        )
    elif fund["fund_score"] >= 70:
        reasons.append(
            "Good category-relative fund score"
        )
    else:
        reasons.append(
            "Competitive category-relative fund score"
        )

    # Sharpe ratio
    if fund["sharpe_ratio"] >= 1.5:
        reasons.append(
            "Strong risk-adjusted performance"
        )
    elif fund["sharpe_ratio"] >= 1.0:
        reasons.append(
            "Good risk-adjusted performance"
        )

    # Volatility
    if fund["volatility"] <= 0.08:
        reasons.append(
            "Relatively low historical volatility"
        )
    elif fund["volatility"] <= 0.15:
        reasons.append(
            "Moderate historical volatility"
        )

    # Drawdown
    if fund["max_drawdown"] >= -0.10:
        reasons.append(
            "Limited historical maximum drawdown"
        )
    elif fund["max_drawdown"] >= -0.20:
        reasons.append(
            "Moderate historical drawdown"
        )

    # Horizon / allocation
    reasons.append(
        f"Suitable for your {horizon_years:g}-year investment horizon"
    )

    reasons.append(
        f"Selected for the {allocation:.0f}% "
        f"{asset_class.lower()} allocation"
    )

    return reasons


def build_recommendation(
    funds: pd.DataFrame,
    goal_type: str,
    target_amount: float,
    horizon_years: float,
    risk_profile: str,
    funds_per_asset: int = 2,
) -> dict:
    """
    Build a complete goal-based investment recommendation.

    Combines:

    - Goal planning
    - Risk profile
    - Time horizon
    - Asset allocation
    - Expected return
    - Required SIP
    - Fund scoring
    - Fund selection
    - SIP allocation
    - Portfolio projection
    """

    # ---------------------------------------------------------
    # 1. Create goal plan
    # ---------------------------------------------------------

    plan = create_goal_plan(
        goal_type=goal_type,
        target_amount=target_amount,
        horizon_years=horizon_years,
        risk_profile=risk_profile,
    )

    # ---------------------------------------------------------
    # 2. Calculate category-relative fund scores
    # ---------------------------------------------------------

    scored = calculate_category_scores(
        funds.copy()
    )

    # ---------------------------------------------------------
    # 3. Select suitable funds for each asset class
    # ---------------------------------------------------------

    recommendations = {}

    for asset_class, allocation in plan[
        "allocation"
    ].items():

        if allocation <= 0:
            continue

        selected = select_funds(
            scored,
            asset_class=asset_class,
            horizon_years=horizon_years,
            n=funds_per_asset,
            goal_type=goal_type,
        )

        if selected.empty:
            recommendations[asset_class] = []
            continue

        fund_records = (
            selected[
                [
                    "scheme_code",
                    "scheme_name",
                    "fund_house",
                    "category",
                    "fund_score",
                    "cagr",
                    "volatility",
                    "sharpe_ratio",
                    "max_drawdown",
                ]
            ]
            .to_dict("records")
        )

        for fund in fund_records:
            fund["explanation"] = build_fund_explanation(
                fund=fund,
                asset_class=asset_class,
                horizon_years=horizon_years,
                allocation=allocation,
            )

        recommendations[asset_class] = fund_records

    # ---------------------------------------------------------
    # 4. Validate fund availability
    # ---------------------------------------------------------

    missing_assets = [
        asset_class
        for asset_class, allocation
        in plan["allocation"].items()
        if allocation > 0
        and not recommendations.get(asset_class)
    ]

    if missing_assets:
        raise ValueError(
            "No suitable funds available for: "
            + ", ".join(missing_assets)
        )

    # ---------------------------------------------------------
    # 5. Calculate SIP allocation by asset class
    # ---------------------------------------------------------

    sip_allocation = calculate_sip_allocation(
        plan["required_monthly_sip"],
        plan["allocation"],
    )

    # ---------------------------------------------------------
    # 6. Build portfolio projection
    # ---------------------------------------------------------

    projection = build_portfolio_projection(
        monthly_sip=plan["required_monthly_sip"],
        annual_return=plan["expected_return"],
        years=plan["horizon_years"],
        target_amount=plan["target_amount"],
    )

    # ---------------------------------------------------------
    # 7. Return complete recommendation
    # ---------------------------------------------------------

    return {
        **plan,
        "sip_allocation": sip_allocation,
        "recommendations": recommendations,
        "projection": projection,
    }