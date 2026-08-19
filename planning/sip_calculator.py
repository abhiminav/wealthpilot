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


def calculate_required_sip_variable_return(
    target_amount: float,
    monthly_returns: list[float],
) -> float:
    """
    Calculate the monthly SIP required to reach a target
    when the monthly return changes over time.

    SIPs are assumed to be invested at the beginning
    of each month.
    """

    if target_amount <= 0:
        raise ValueError(
            "Target amount must be positive."
        )

    if not monthly_returns:
        raise ValueError(
            "Monthly return sequence cannot be empty."
        )

    # Calculate the future value of one unit invested
    # at the beginning of every month.
    accumulation_factor = 0.0

    for monthly_return in monthly_returns:
        accumulation_factor = (
            accumulation_factor
            * (1 + monthly_return)
            + (1 + monthly_return)
        )

    if accumulation_factor <= 0:
        raise ValueError(
            "Invalid return sequence."
        )

    return target_amount / accumulation_factor


def generate_projection_variable_return(
    monthly_sip: float,
    monthly_returns: list[float],
) -> list[dict]:
    """
    Generate monthly portfolio growth using a sequence
    of monthly returns.

    SIPs are invested at the beginning of each month.
    """

    if monthly_sip < 0:
        raise ValueError(
            "Monthly SIP cannot be negative."
        )

    if not monthly_returns:
        raise ValueError(
            "Monthly return sequence cannot be empty."
        )

    projection = []
    portfolio_value = 0.0
    total_invested = 0.0

    for month, monthly_return in enumerate(
        monthly_returns,
        start=1,
    ):
        portfolio_value = (
            (portfolio_value + monthly_sip)
            * (1 + monthly_return)
        )

        total_invested += monthly_sip

        projection.append({
            "month": month,
            "year": month / 12,
            "invested": total_invested,
            "portfolio_value": portfolio_value,
            "monthly_return": monthly_return,
        })

    return projection


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