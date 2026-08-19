import pandas as pd


def min_max_score(
    series: pd.Series,
    higher_is_better: bool = True,
) -> pd.Series:
    """Normalize a metric to a 0–100 score."""

    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(50.0, index=series.index)

    score = (
        (series - minimum)
        / (maximum - minimum)
    ) * 100

    if not higher_is_better:
        score = 100 - score

    return score


def calculate_category_scores(
    funds: pd.DataFrame,
) -> pd.DataFrame:
    """
    Score funds relative to other funds
    in the same category.
    """

    df = funds.copy()

    def score_group(group: pd.DataFrame) -> pd.DataFrame:
        group = group.copy()

        group["cagr_score"] = min_max_score(
            group["cagr"]
        )

        group["sharpe_score"] = min_max_score(
            group["sharpe_ratio"]
        )

        group["volatility_score"] = min_max_score(
            group["volatility"],
            higher_is_better=False,
        )

        group["drawdown_score"] = min_max_score(
            group["max_drawdown"]
        )

        group["fund_score"] = (
            group["cagr_score"] * 0.30
            + group["sharpe_score"] * 0.30
            + group["volatility_score"] * 0.20
            + group["drawdown_score"] * 0.20
        )

        return group

    scored_groups = []

    for category, group in df.groupby("category"):
        scored_groups.append(
            score_group(group)
        )

    result = pd.concat(
        scored_groups,
        ignore_index=True,
    )

    return result.sort_values(
        "fund_score",
        ascending=False,
    ).reset_index(drop=True)

    df = (
        df.groupby(
            "category",
            group_keys=False,
        )
        .apply(
            score_group,
            include_groups=False, # type: ignore
        ) # type: ignore
        .reset_index(drop=True)
    )

    return df.sort_values(
        "fund_score",
        ascending=False,
    ).reset_index(drop=True)