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
        )

        if selected.empty:
            recommendations[asset_class] = []
            continue

        recommendations[asset_class] = (
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