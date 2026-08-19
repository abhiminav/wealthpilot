from planning.glide_path import (
    get_glide_path,
)
from planning.return_assumptions import (
    get_return_assumption,
)
from planning.sip_calculator import (
    calculate_required_sip,
    generate_scenario_projections,
)


def create_goal_plan(
    goal_type: str,
    target_amount: float,
    horizon_years: float,
    risk_profile: str,
) -> dict:
    """
    Create a complete goal-based investment plan.
    """

    if target_amount <= 0:
        raise ValueError(
            "Target amount must be positive."
        )

    if horizon_years <= 0:
        raise ValueError(
            "Investment horizon must be positive."
        )

    allocation = get_glide_path(
        risk_profile,
        horizon_years,
    )

    expected_return = get_return_assumption(
        allocation
    )

    required_sip = calculate_required_sip(
        target_amount,
        expected_return,
        horizon_years,
    )

    scenario_projections = generate_scenario_projections(
        monthly_sip=required_sip,
        base_return=expected_return,
        years=horizon_years,
    )


    return {
        "goal_type": goal_type,
        "target_amount": target_amount,
        "horizon_years": horizon_years,
        "risk_profile": risk_profile,
        "allocation": allocation,
        "expected_return": expected_return,
        "required_monthly_sip": required_sip,
        "scenario_projections": scenario_projections,
    }


def calculate_sip_allocation(
    monthly_sip: float,
    allocation: dict,
) -> dict:
    """Calculate monthly SIP amount for each asset class."""

    return {
        asset: monthly_sip * (percentage / 100)
        for asset, percentage in allocation.items()
    }


def build_portfolio_projection(
    monthly_sip: float,
    annual_return: float,
    years: float,
    target_amount: float,
) -> list[dict]:
    """Build portfolio growth projection against the goal."""

    from planning.sip_calculator import (
        generate_projection,
    )

    projection = generate_projection(
        monthly_sip=monthly_sip,
        annual_return=annual_return,
        years=years,
    )

    for row in projection:
        row["target_amount"] = target_amount
        row["surplus_or_gap"] = (
            row["portfolio_value"]
            - target_amount
        )

    return projection