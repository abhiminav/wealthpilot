import pandas as pd

from recommendation.recommendation_engine import (
    build_recommendation,
)


DATA_PATH = "data/processed/fund_metrics_clean.csv"


def load_fund_data(
    path: str = DATA_PATH,
) -> pd.DataFrame:
    """Load cleaned fund metrics."""

    return pd.read_csv(path)


def generate_recommendation(
    goal_type: str,
    target_amount: float,
    horizon_years: float,
    risk_profile: str,
    funds_per_asset: int = 2,
) -> dict:
    """
    Public service interface for generating
    a complete investment recommendation.
    """

    funds = load_fund_data()

    return build_recommendation(
        funds=funds,
        goal_type=goal_type,
        target_amount=target_amount,
        horizon_years=horizon_years,
        risk_profile=risk_profile,
        funds_per_asset=funds_per_asset,
    )