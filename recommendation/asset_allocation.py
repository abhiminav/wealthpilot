EQUITY_CATEGORIES = {
    "Large Cap",
    "Mid Cap",
    "Small Cap",
    "Large & Mid Cap",
    "Flexi Cap",
    "Multi Cap",
    "Focused",
    "Value",
    "Contra",
    "Dividend Yield",
    "ELSS",
    "Sectoral",
    "Thematic",
    "Index",
}

DEBT_CATEGORIES = {
    "Debt",
    "Liquid",
    "Overnight",
    "Ultra Short Duration",
    "Low Duration",
    "Short Duration",
    "Medium Duration",
    "Long Duration",
    "Dynamic Bond",
    "Corporate Bond",
    "Banking & PSU",
    "Credit Risk",
    "Gilt",
    "Floating Rate",
    "Money Market",
}

GOLD_CATEGORIES = {
    "Gold",
}


EXCLUDED_CATEGORIES = {
    "Fund of Funds",
    "ETF",
    "Retirement",
    "Children",
    "Solution Oriented",
    "Fixed Maturity",
    "Infrastructure Debt",
}


def get_asset_class(category: str) -> str | None:
    """Map a fund category to an asset class."""

    if category in EXCLUDED_CATEGORIES:
        return None

    if category in EQUITY_CATEGORIES:
        return "Equity"

    if category in DEBT_CATEGORIES:
        return "Debt"

    if category in GOLD_CATEGORIES:
        return "Gold"

    return None


def get_asset_class_from_fund(
    category: str,
    scheme_name: str,
) -> str | None:
    """Determine asset class using official category plus
    a narrow commodity-name override."""

    name = scheme_name.upper()

    # Narrow exception for commodity funds.
    if "GOLD" in name and (
        "ETF" in name or "FOF" in name
    ):
        return "Gold"

    # Silver is not currently part of our target allocation.
    if "SILVER" in name and (
        "ETF" in name or "FOF" in name
    ):
        return None

    # Some debt index funds are classified simply as "Index".
    # Use explicit debt-related scheme-name signals to
    # distinguish them from equity index funds.
    if category == "Index":
        debt_index_terms = (
            "GILT",
            "SDL",
            "BOND",
            "PSU",
            "G-SEC",
            "GSEC",
        )

        if any(
            term in name
            for term in debt_index_terms
        ):
            return "Debt"

    return get_asset_class(category)