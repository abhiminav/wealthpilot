ASSET_RETURN_ASSUMPTIONS = {
    "Equity": 0.12,
    "Debt": 0.07,
    "Gold": 0.08,
}


def calculate_portfolio_return(
    allocation: dict,
) -> float:
    """
    Calculate weighted expected annual portfolio return.
    """

    total = 0.0

    for asset, weight in allocation.items():

        if asset not in ASSET_RETURN_ASSUMPTIONS:
            raise ValueError(
                f"Unknown asset class: {asset}"
            )

        total += (
            weight / 100
        ) * ASSET_RETURN_ASSUMPTIONS[asset]

    return total


def get_return_assumption(
    allocation: dict,
) -> float:
    """Return weighted annual portfolio return."""

    return calculate_portfolio_return(
        allocation
    )