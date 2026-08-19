from typing import Dict


GOAL_WEIGHTS: Dict[str, Dict[str, float]] = {
    "Emergency Fund": {
        "cagr_score": 0.10,
        "sharpe_score": 0.25,
        "volatility_score": 0.30,
        "drawdown_score": 0.35,
    },

    "House Down Payment": {
        "cagr_score": 0.15,
        "sharpe_score": 0.30,
        "volatility_score": 0.25,
        "drawdown_score": 0.30,
    },

    "Education": {
        "cagr_score": 0.25,
        "sharpe_score": 0.30,
        "volatility_score": 0.20,
        "drawdown_score": 0.25,
    },

    "Retirement": {
        "cagr_score": 0.35,
        "sharpe_score": 0.30,
        "volatility_score": 0.15,
        "drawdown_score": 0.20,
    },

    "Wealth Creation": {
        "cagr_score": 0.40,
        "sharpe_score": 0.30,
        "volatility_score": 0.15,
        "drawdown_score": 0.15,
    },
}


def get_goal_weights(
    goal_type: str,
) -> Dict[str, float]:
    """Return metric weights for a specific investment goal."""

    if goal_type not in GOAL_WEIGHTS:
        raise ValueError(
            f"Invalid goal type: {goal_type}"
        )

    return GOAL_WEIGHTS[goal_type].copy()


def calculate_goal_adjusted_score(
    fund,
    goal_type: str,
) -> float:
    """
    Calculate a goal-specific score using the existing
    category-relative metric scores.

    The original fund_score remains unchanged.
    """

    weights = get_goal_weights(goal_type)

    return (
        fund["cagr_score"] * weights["cagr_score"]
        + fund["sharpe_score"] * weights["sharpe_score"]
        + fund["volatility_score"]
        * weights["volatility_score"]
        + fund["drawdown_score"]
        * weights["drawdown_score"]
    )