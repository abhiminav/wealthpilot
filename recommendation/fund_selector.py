import pandas as pd

from recommendation.asset_allocation import (
    get_asset_class_from_fund,
)
from recommendation.goal_preferences import (
    calculate_goal_adjusted_score,
)


CORE_EQUITY_CATEGORIES = {
    "Large Cap",
    "Flexi Cap",
    "Multi Cap",
    "Large & Mid Cap",
    "Index",
    "Mid Cap",
    "Small Cap",
}


CORE_DEBT_CATEGORIES = {
    "Liquid",
    "Overnight",
    "Money Market",
    "Ultra Short Duration",
    "Low Duration",
    "Short Duration",
    "Medium Duration",
    "Long Duration",
    "Dynamic Bond",
    "Corporate Bond",
    "Banking & PSU",
    "Gilt",
}


def get_suitable_categories(
    asset_class: str,
    horizon_years: float,
) -> set[str]:
    """Return categories suitable for a generic goal."""

    if asset_class == "Equity":

        if horizon_years < 3:
            return set()

        if horizon_years < 7:
            return {
                "Large Cap",
                "Index",
                "Flexi Cap",
                "Large & Mid Cap",
            }

        return CORE_EQUITY_CATEGORIES

    if asset_class == "Debt":

        if horizon_years < 3:
            return {
                "Liquid",
                "Overnight",
                "Money Market",
                "Ultra Short Duration",
                "Low Duration",
                "Short Duration",
            }

        if horizon_years < 7:
            return CORE_DEBT_CATEGORIES - {
                "Long Duration",
                "Gilt",
            }

        return CORE_DEBT_CATEGORIES

    if asset_class == "Gold":
        return {"Gold", "Fund of Funds"}

    return set()


def select_funds(
    funds: pd.DataFrame,
    asset_class: str,
    horizon_years: float,
    goal_type: str,
    n: int = 3,
) -> pd.DataFrame:
    """Select suitable funds for an asset class and horizon."""

    df = funds.copy()

    df["asset_class"] = df.apply(
        lambda row: get_asset_class_from_fund(
            row["category"],
            row["scheme_name"],
        ),
        axis=1,
    )

    suitable_categories = get_suitable_categories(
        asset_class,
        horizon_years,
    )

    df = df[
        (df["asset_class"] == asset_class)
        & df["category"].isin(suitable_categories)
    ].copy()

    if df.empty:
        return df

    df["goal_adjusted_score"] = df.apply(
        lambda row: calculate_goal_adjusted_score(
            row,
            goal_type,
        ),
        axis=1,
    )

    df["category_rank"] = (
        df.groupby("category")["goal_adjusted_score"]
        .rank(
            ascending=False,
            method="first",
        )
    )

    candidates = (
        df[df["category_rank"] <= 3]
        .sort_values(
            "goal_adjusted_score",
            ascending=False,
        )
    )

    selected = []
    categories_used = set()

    for _, row in candidates.iterrows():

        if row["category"] not in categories_used:
            selected.append(row)
            categories_used.add(row["category"])

        if len(selected) == n:
            break

    return pd.DataFrame(
        selected
    ).reset_index(drop=True)