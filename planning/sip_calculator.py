def calculate_future_value(
    monthly_sip: float,
    annual_return: float,
    years: float,
) -> float:
    """Calculate future value of a monthly SIP."""

    months = int(years * 12)
    monthly_rate = annual_return / 12

    if months <= 0:
        return 0.0

    if monthly_rate == 0:
        return monthly_sip * months

    return monthly_sip * (
        ((1 + monthly_rate) ** months - 1)
        / monthly_rate
    ) * (1 + monthly_rate)


def calculate_required_sip(
    target_amount: float,
    annual_return: float,
    years: float,
) -> float:
    """Calculate monthly SIP required to reach a target."""

    months = int(years * 12)
    monthly_rate = annual_return / 12

    if months <= 0:
        raise ValueError(
            "Investment period must be positive."
        )

    if target_amount <= 0:
        raise ValueError(
            "Target amount must be positive."
        )

    if monthly_rate == 0:
        return target_amount / months

    sip = target_amount * monthly_rate / (
        ((1 + monthly_rate) ** months - 1)
        * (1 + monthly_rate)
    )

    return sip


def generate_projection(
    monthly_sip: float,
    annual_return: float,
    years: float,
) -> list[dict]:
    """Generate monthly portfolio growth projection."""

    months = int(years * 12)
    monthly_rate = annual_return / 12

    projection = []
    portfolio_value = 0.0
    total_invested = 0.0

    for month in range(1, months + 1):

        # SIP is invested at the beginning of the month.
        portfolio_value = (
            (portfolio_value + monthly_sip)
            * (1 + monthly_rate)
        )

        total_invested += monthly_sip

        projection.append({
            "month": month,
            "year": month / 12,
            "invested": total_invested,
            "portfolio_value": portfolio_value,
        })

    return projection


def generate_scenario_projections(
    monthly_sip: float,
    base_return: float,
    years: float,
) -> dict:
    """
    Generate conservative, base, and optimistic
    portfolio projections using the same monthly SIP.
    """

    scenarios = {
        "conservative": base_return - 0.02,
        "base": base_return,
        "optimistic": base_return + 0.02,
    }

    return {
        name: {
            "annual_return": annual_return,
            "projection": generate_projection(
                monthly_sip=monthly_sip,
                annual_return=annual_return,
                years=years,
            ),
        }
        for name, annual_return in scenarios.items()
    }