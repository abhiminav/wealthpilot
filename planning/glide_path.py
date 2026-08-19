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