from typing import Dict


def get_time_horizon_years(horizon: str) -> float:
    """Convert horizon label to representative years."""

    horizons = {
        "Less than 3 years": 2,
        "3–5 years": 4,
        "5–10 years": 7,
        "10+ years": 15,
    }

    if horizon not in horizons:
        raise ValueError(
            f"Invalid horizon: {horizon}"
        )

    return horizons[horizon]


def get_glide_path(
    risk_profile: str,
    horizon_years: float,
) -> Dict[str, float]:
    """
    Determine asset allocation using risk profile
    and investment horizon.

    Short horizons override aggressive risk preferences.
    """

    allocations = {
        "Conservative": {
            "short":  {"Equity": 0, "Debt": 90, "Gold": 10},
            "medium": {"Equity": 35, "Debt": 55, "Gold": 10},
            "long":   {"Equity": 45, "Debt": 45, "Gold": 10},
        },

        "Moderate": {
            "short":  {"Equity": 0, "Debt": 90, "Gold": 10},
            "medium": {"Equity": 50, "Debt": 40, "Gold": 10},
            "long":   {"Equity": 65, "Debt": 25, "Gold": 10},
        },

        "Aggressive": {
            "short":  {"Equity": 0, "Debt": 90, "Gold": 10},
            "medium": {"Equity": 65, "Debt": 25, "Gold": 10},
            "long":   {"Equity": 80, "Debt": 10, "Gold": 10},
        },
    }

    if risk_profile not in allocations:
        raise ValueError(
            f"Invalid risk profile: {risk_profile}"
        )

    if horizon_years < 3:
        period = "short"

    elif horizon_years < 10:
        period = "medium"

    else:
        period = "long"

    return allocations[risk_profile][period].copy() # type: ignore

def generate_glide_path(
    risk_profile: str,
    horizon_years: float,
) -> list[dict]:
    """
    Generate a staged, monotonic de-risking path.

    The investor starts with the allocation appropriate for
    their risk profile and investment horizon, then gradually
    moves toward the short-horizon defensive allocation.
    """

    if horizon_years <= 0:
        raise ValueError(
            "Investment horizon must be positive."
        )

    # Validate risk profile and obtain the starting allocation.
    starting = get_glide_path(
        risk_profile,
        horizon_years,
    )

    defensive = get_glide_path(
        risk_profile,
        2,
    )

    # Very short goals are already defensive.
    if horizon_years <= 3:
        return [
            {
                "stage": "Current",
                "year": 0.0,
                "allocation": starting,
            }
        ]

    # We use four stages for longer goals.
    stage_years = [
        0.0,
        horizon_years * 0.33,
        horizon_years * 0.66,
        max(horizon_years - 2, 0),
    ]

    stages = []

    for index, year in enumerate(stage_years):

        progress = (
            year / max(horizon_years - 2, 1)
        )

        progress = min(
            max(progress, 0.0),
            1.0,
        )

        equity = round(
            starting["Equity"]
            + (
                defensive["Equity"]
                - starting["Equity"]
            )
            * progress
        )

        debt = 100 - equity - starting["Gold"]

        if index == 0:
            stage_name = "Current"
        elif index == len(stage_years) - 1:
            stage_name = "Final 2 years"
        else:
            stage_name = f"Stage {index + 1}"

        stages.append({
            "stage": stage_name,
            "year": round(year, 2),
            "allocation": {
                "Equity": equity,
                "Debt": debt,
                "Gold": starting["Gold"],
            },
        })

    return stages


def generate_monthly_returns_from_glide_path(
    risk_profile: str,
    horizon_years: float,
) -> list[float]:
    """
    Generate monthly portfolio returns from the staged
    glide path.

    Each stage's annual expected return is converted to
    an equivalent monthly return and applied according to
    the stage's time boundary.
    """

    from planning.return_assumptions import (
        get_return_assumption,
    )

    if horizon_years <= 0:
        raise ValueError(
            "Investment horizon must be positive."
        )

    total_months = int(horizon_years * 12)

    stages = generate_glide_path(
        risk_profile,
        horizon_years,
    )

    monthly_returns = []

    for index, stage in enumerate(stages):
        annual_return = get_return_assumption(
            stage["allocation"]
        )

        # Use an effective monthly rate rather than
        # simply dividing the annual rate by 12.
        monthly_return = (
            (1 + annual_return) ** (1 / 12)
        ) - 1

        start_month = int(
            stage["year"] * 12
        )

        if index + 1 < len(stages):
            end_month = int(
                stages[index + 1]["year"] * 12
            )
        else:
            end_month = total_months

        monthly_returns.extend(
            [monthly_return]
            * max(end_month - start_month, 0)
        )

    return monthly_returns[:total_months]