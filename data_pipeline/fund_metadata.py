from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class FundMetadata:
    scheme_name: str
    amfi_code: str
    category: str
    fund_house: Optional[str] = None
    benchmark: Optional[str] = None
    expense_ratio: Optional[float] = None


def build_scheme_catalog(nav_df: pd.DataFrame) -> pd.DataFrame:
    """Build clean scheme catalog from AMFI NAV data."""

    catalog = nav_df[
        ["scheme_code", "scheme_name"]
    ].copy()

    catalog = catalog.rename(
        columns={"scheme_code": "amfi_code"}
    )

    catalog["amfi_code"] = (
        catalog["amfi_code"]
        .astype(str)
        .str.strip()
    )

    catalog["scheme_name"] = (
        catalog["scheme_name"]
        .astype(str)
        .str.strip()
    )

    return (
        catalog
        .drop_duplicates("amfi_code")
        .sort_values("scheme_name")
        .reset_index(drop=True)
    )


def search_funds(
    catalog: pd.DataFrame,
    query: str,
) -> pd.DataFrame:
    """Search funds by name or AMFI code."""

    query = str(query).strip().lower()

    mask = (
        catalog["scheme_name"]
        .str.lower()
        .str.contains(query, na=False)
        |
        catalog["amfi_code"]
        .str.lower()
        .str.contains(query, na=False)
    )

    return catalog[mask].copy()


def filter_investment_schemes(
    catalog: pd.DataFrame,
) -> pd.DataFrame:
    """Keep Direct Growth schemes and exclude dividend variants."""

    name = catalog["scheme_name"].str.upper()

    direct = name.str.contains(
        "DIRECT",
        na=False,
    )

    growth = name.str.contains(
        "GROWTH",
        na=False,
    )

    excluded = (
        name.str.contains("IDCW", na=False)
        | name.str.contains("DIVIDEND", na=False)
        | name.str.contains("BONUS", na=False)
    )

    return catalog[
        direct & growth & ~excluded
    ].reset_index(drop=True)


def save_scheme_catalog(
    catalog: pd.DataFrame,
    output_path: str,
) -> None:
    """Save scheme catalog to CSV."""

    catalog.to_csv(
        output_path,
        index=False,
    )


def classify_scheme(scheme_name: str) -> str:
    """Classify a mutual fund using scheme-name patterns."""

    name = scheme_name.upper()
    normalized = (
        name.replace("-", " ")
        .replace("&", " AND ")
        .replace("/", " ")
    )

    rules = [
        ("Balanced Advantage", ["BALANCED ADVANTAGE"]),
        ("Aggressive Hybrid", ["AGGRESSIVE HYBRID", "EQUITY AND DEBT"]),
        ("Conservative Hybrid", ["CONSERVATIVE HYBRID"]),
        ("Multi Asset", ["MULTI ASSET"]),
        ("Large & Mid Cap", ["LARGE AND MID", "LARGE MID"]),
        ("Small Cap", ["SMALL CAP"]),
        ("Mid Cap", ["MID CAP"]),
        ("Large Cap", ["LARGE CAP"]),
        ("Flexi Cap", ["FLEXI CAP", "FLEXICAP"]),
        ("Multi Cap", ["MULTI CAP", "MULTICAP"]),
        ("Focused", ["FOCUSED"]),
        ("Value", ["VALUE FUND", "VALUE"]),
        ("Contra", ["CONTRA"]),
        ("Dividend Yield", ["DIVIDEND YIELD"]),
        ("ELSS", ["ELSS", "TAX SAVER"]),

        ("Gold", [
            "GOLD ETF",
            "GOLD FUND",
            "GOLD FOF",
            "GOLD ETF FOF",
        ]),

        ("Silver", [
            "SILVER ETF",
            "SILVER FUND",
            "SILVER FOF",
        ]),

        ("Index", [
            "INDEX FUND",
            "INDEX",
            "NIFTY",
            "SENSEX",
            "S&P 500",
        ]),

        ("Overnight", ["OVERNIGHT"]),
        ("Liquid", ["LIQUID"]),
        ("Gilt", ["GILT"]),
        ("Short Duration", ["SHORT DURATION"]),
        ("Dynamic Bond", ["DYNAMIC BOND"]),
        ("Corporate Bond", ["CORPORATE BOND"]),
        ("Debt", [
            "DEBT",
            "BOND",
            "TREASURY",
            "MONEY MARKET",
            "BANKING AND PSU",
        ]),
    ]

    for category, keywords in rules:
        if any(keyword in normalized for keyword in keywords):
            return category

    return "Other"


def add_categories(
    catalog: pd.DataFrame,
) -> pd.DataFrame:
    """Add estimated fund categories."""

    result = catalog.copy()

    result["category"] = result[
        "scheme_name"
    ].apply(classify_scheme)

    return result

def category_summary(
    catalog: pd.DataFrame,
) -> pd.DataFrame:
    """Return category counts."""

    return (
        catalog["category"]
        .value_counts()
        .rename_axis("category")
        .reset_index(name="fund_count")
    )

def map_scheme_category(scheme_category: str) -> str:
    """Map MFapi/SEBI scheme categories to project categories."""

    category = str(scheme_category).strip().lower()

    mappings = {
        # Equity
        "large cap": "Large Cap",
        "mid cap": "Mid Cap",
        "small cap": "Small Cap",
        "large & mid cap": "Large & Mid Cap",
        "large and mid cap": "Large & Mid Cap",
        "flexi cap": "Flexi Cap",
        "multi cap": "Multi Cap",
        "focused": "Focused",
        "value": "Value",
        "contra": "Contra",
        "dividend yield": "Dividend Yield",
        "elss": "ELSS",
        "sectoral": "Sectoral",
        "thematic": "Thematic",

        # Hybrid
        "balanced advantage": "Balanced Advantage",
        "balanced hybrid": "Balanced Hybrid",
        "aggressive hybrid": "Aggressive Hybrid",
        "conservative hybrid": "Conservative Hybrid",
        "equity savings": "Equity Savings",
        "multi asset": "Multi Asset",
        "arbitrage": "Arbitrage",

        # Debt
        "overnight": "Overnight",
        "liquid": "Liquid",
        "ultra short": "Ultra Short Duration",
        "short duration": "Short Duration",
        "low duration": "Low Duration",
        "medium duration": "Medium Duration",
        "long duration": "Long Duration",
        "dynamic bond": "Dynamic Bond",
        "dynamic term": "Dynamic Bond",
        "corporate bond": "Corporate Bond",
        "credit risk": "Credit Risk",
        "banking and psu": "Banking & PSU",
        "gilt": "Gilt",
        "floater": "Floating Rate",
        "floating rate": "Floating Rate",
        "money market": "Money Market",
        "income": "Debt",
        "debt": "Debt",
        "bond": "Debt",

        # Index / commodities
        "index": "Index",
        "gold": "Gold",
        "silver": "Silver",
        "etf": "ETF",

        # Fund of Funds
        "other scheme - fof": "Fund of Funds",
        "fof": "Fund of Funds",
        "fund of funds": "Fund of Funds",

        # Solution-oriented
        "retirement": "Retirement",
        "children": "Children",
        "life cycle": "Solution Oriented",
        "solution oriented": "Solution Oriented",

        # Fixed maturity / target maturity
        "fixed maturity": "Fixed Maturity",
        "fixed term": "Fixed Maturity",

        # Infrastructure
        "idf": "Infrastructure Debt",
    }

    # More specific categories must be checked first.
    priority_mappings = [
        ("income/debt oriented schemes - ultra short to short term",
         "Ultra Short Duration"),
        ("income/debt oriented schemes - ultra short term",
         "Ultra Short Duration"),
        ("income/debt oriented schemes - short term",
         "Short Duration"),
        ("income/debt oriented schemes - medium term",
         "Medium Duration"),
        ("income/debt oriented schemes - dynamic term",
         "Dynamic Bond"),
        ("income/debt oriented schemes - money market",
         "Money Market"),
        ("debt scheme - low duration fund",
         "Low Duration"),
        ("debt scheme - money market fund",
         "Money Market"),
        ("other scheme - fof domestic",
         "Fund of Funds"),
        ("other scheme - fof overseas",
         "Fund of Funds"),
    ]

    for keyword, project_category in priority_mappings:
        if keyword in category:
            return project_category

    # Fixed-maturity schemes such as "1099 Days", "1100 Days", etc.
    if "days" in category:
        return "Fixed Maturity"

    # Normal category matching.
    for keyword, project_category in mappings.items():
        if keyword in category:
            return project_category

    # Known non-category metadata values.
    ignored_values = {
        "growth",
        "direct",
        "formerly known",
        "half yearly dividend",
        "fv rs",
    }

    for value in ignored_values:
        if value in category:
            return "Other"

    return "Other"


def enrich_scheme_catalog(
    catalog: pd.DataFrame,
) -> pd.DataFrame:
    """
    Fetch official scheme metadata and enrich catalog.
    """

    from data_pipeline.nav_fetcher import fetch_scheme_metadata

    records = []

    for i, row in catalog.iterrows():

        code = str(row["amfi_code"])

        try:
            metadata = fetch_scheme_metadata(code)

            records.append({
                "amfi_code": code,
                "scheme_name": metadata["scheme_name"],
                "fund_house": metadata["fund_house"],
                "scheme_type": metadata["scheme_type"],
                "scheme_category": metadata["scheme_category"],
                "category": map_scheme_category(
                    metadata["scheme_category"]
                ),
                "isin_growth": metadata["isin_growth"],
            })

        except Exception as exc:
            print(
                f"Skipping {code}: {exc}"
            )

        if (i + 1) % 100 == 0: # type: ignore
            print(
                f"Processed {i + 1}/{len(catalog)}" # type: ignore
            )

    return pd.DataFrame(records)


def filter_recommendation_universe(
    catalog: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create the final fund universe suitable for recommendations.
    """

    df = catalog.copy()

    name = df["scheme_name"].str.upper()
    scheme_type = df["scheme_type"].str.upper()

    # Must be open-ended.
    open_ended = scheme_type.str.contains(
        "OPEN ENDED",
        na=False,
    )

    # Exclude products that are not suitable for our
    # general goal-based recommendation engine.
    excluded_patterns = (
        "SEGREGATED PORTFOLIO",
        "CLOSE ENDED",
        "CLOSED ENDED",
        "INTERVAL FUND",
        "FIXED HORIZON",
        "FIXED MATURITY",
        "SERIES",
        "1100D",
        "1104 DAYS",
        "1102 DAYS",
        "1150 DAYS",
        "2195 DAYS",
    )

    excluded = name.apply(
        lambda value: any(
            pattern in value
            for pattern in excluded_patterns
        )
    )

    # Remove schemes without a useful classification.
    classified = df["category"] != "Other"

    result = df[
        open_ended
        & ~excluded
        & classified
    ].copy()

    return result.reset_index(drop=True)