import pytest

from planning.sip_calculator import (
    calculate_required_sip_variable_return,
    generate_projection_variable_return,
)


def test_variable_return_projection_reaches_target():

    monthly_returns = [0.0] * 12

    sip = calculate_required_sip_variable_return(
        target_amount=12000,
        monthly_returns=monthly_returns,
    )

    assert sip == pytest.approx(1000)

    projection = generate_projection_variable_return(
        monthly_sip=sip,
        monthly_returns=monthly_returns,
    )

    assert projection[-1]["portfolio_value"] == pytest.approx(
        12000
    )


def test_variable_return_projection_with_growth():

    monthly_returns = [0.01] * 12

    sip = calculate_required_sip_variable_return(
        target_amount=12000,
        monthly_returns=monthly_returns,
    )

    projection = generate_projection_variable_return(
        monthly_sip=sip,
        monthly_returns=monthly_returns,
    )

    assert projection[-1]["portfolio_value"] == pytest.approx(
        12000
    )


def test_empty_return_sequence():

    with pytest.raises(ValueError):

        calculate_required_sip_variable_return(
            target_amount=100000,
            monthly_returns=[],
        )


def test_invalid_target():

    with pytest.raises(ValueError):

        calculate_required_sip_variable_return(
            target_amount=0,
            monthly_returns=[0.01] * 12,
        )


def test_projection_length():

    monthly_returns = [0.005] * 24

    projection = generate_projection_variable_return(
        monthly_sip=1000,
        monthly_returns=monthly_returns,
    )

    assert len(projection) == 24


def test_projection_invested_amount():

    monthly_returns = [0.0] * 12

    projection = generate_projection_variable_return(
        monthly_sip=1000,
        monthly_returns=monthly_returns,
    )

    assert projection[-1]["invested"] == pytest.approx(
        12000
    )