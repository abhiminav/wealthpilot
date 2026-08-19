import numpy as np
import pandas as pd


def calculate_cagr(
    nav: pd.Series,
    dates: pd.Series,
) -> float:
    """Calculate using actual elapsed calendar years."""

    valid = pd.DataFrame({
        "date": dates,
        "nav": nav,
    }).dropna()

    if len(valid) < 2:
        return np.nan

    start_value = valid["nav"].iloc[0]
    end_value = valid["nav"].iloc[-1]

    days = (
        valid["date"].iloc[-1] -
        valid["date"].iloc[0]
    ).days

    years = days / 365.25

    if start_value <= 0 or years <= 0:
        return np.nan

    return (
        (end_value / start_value) ** (1 / years)
    ) - 1

def calculate_daily_returns(
    nav: pd.Series,
) -> pd.Series:
    """Calculate daily percentage returns."""

    return nav.pct_change().dropna()


def calculate_volatility(
    nav: pd.Series,
) -> float:
    """Calculate annualized volatility."""

    returns = calculate_daily_returns(nav)

    if returns.empty:
        return np.nan

    return returns.std() * np.sqrt(252)


def calculate_sharpe_ratio(
    nav: pd.Series,
    risk_free_rate: float = 0.06,
) -> float:
    """Calculate annualized Sharpe ratio."""

    returns = calculate_daily_returns(nav)

    if returns.empty:
        return np.nan

    annualized_return = returns.mean() * 252
    annualized_volatility = returns.std() * np.sqrt(252)

    if annualized_volatility == 0:
        return np.nan

    return (
        annualized_return - risk_free_rate
    ) / annualized_volatility


def calculate_max_drawdown(
    nav: pd.Series,
) -> float:
    """Calculate maximum drawdown."""

    nav = nav.dropna()

    if nav.empty:
        return np.nan

    running_max = nav.cummax()

    drawdown = (
        nav / running_max
    ) - 1

    return drawdown.min()


def calculate_fund_metrics(
    nav_df: pd.DataFrame,
    risk_free_rate: float = 0.06,
) -> dict:
    """Calculate all major performance metrics."""

    nav_df = nav_df.sort_values("date")

    nav = nav_df["nav"]

    return {
        "scheme_code": nav_df["scheme_code"].iloc[0],
        "scheme_name": nav_df["scheme_name"].iloc[0],
        "start_date": nav_df["date"].min(),
        "end_date": nav_df["date"].max(),
        "observations": len(nav_df),
        "cagr": calculate_cagr(nav, nav_df["date"]),
        "volatility": calculate_volatility(nav),
        "sharpe_ratio": calculate_sharpe_ratio(
            nav,
            risk_free_rate,
        ),
        "max_drawdown": calculate_max_drawdown(nav),
    }

def build_metrics_dataset(
    funds: pd.DataFrame,
    risk_free_rate: float = 0.06,
) -> pd.DataFrame:
    """Calculate performance metrics for multiple funds."""

    from data_pipeline.nav_fetcher import (
        fetch_and_cache_historical_nav,
    )
    from config.settings import CACHE_DIR

    results = []

    total = len(funds)

    for i, row in funds.iterrows():

        scheme_code = str(row["amfi_code"])
        scheme_name = row["scheme_name"]

        print(
            f"[{i + 1}/{total}] {scheme_name}" # type: ignore
        )

        try:
            nav_df = fetch_and_cache_historical_nav(
                scheme_code,
                CACHE_DIR / "nav",
            )

            if nav_df.empty:
                print("  -> No NAV data")
                continue

            metrics = calculate_fund_metrics(
                nav_df,
                risk_free_rate=risk_free_rate,
            )

            metrics["category"] = row["category"]
            metrics["fund_house"] = row["fund_house"]
            metrics["scheme_category"] = row[
                "scheme_category"
            ]

            results.append(metrics)

        except Exception as exc:
            print(
                f"  -> ERROR: {exc}"
            )

    return pd.DataFrame(results)

def filter_quality_funds(
    metrics_df: pd.DataFrame,
    min_observations: int = 252,
    min_volatility: float = 0.01,
) -> pd.DataFrame:
    """
    Keep funds with sufficient history and reliable metrics.
    """

    df = metrics_df.copy()

    df = df[
        df["observations"] >= min_observations
    ]

    df = df.dropna(
        subset=[
            "cagr",
            "volatility",
            "sharpe_ratio",
            "max_drawdown",
        ]
    )

    df = df[
        (df["volatility"] >= min_volatility)
        & (df["volatility"] < 2.0)
        & (df["cagr"] > -1.0)
        & (df["cagr"] < 1.0)
        & (df["max_drawdown"] >= -1.0)
        & (df["max_drawdown"] <= 0)
        & np.isfinite(df["sharpe_ratio"])
    ]

    return df.reset_index(drop=True)