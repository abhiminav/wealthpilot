from planning.sip_calculator import (
    calculate_future_value,
    calculate_required_sip,
    generate_projection,
)


def test_required_sip_reaches_target():
    sip = calculate_required_sip(
        1_000_000,
        0.10,
        10,
    )

    future_value = calculate_future_value(
        sip,
        0.10,
        10,
    )

    assert abs(future_value - 1_000_000) < 1


def test_zero_return():
    sip = calculate_required_sip(
        120_000,
        0.0,
        2,
    )

    assert sip == 5_000


def test_projection_length():
    projection = generate_projection(
        5_000,
        0.10,
        10,
    )

    assert len(projection) == 120


def test_invalid_horizon():
    try:
        calculate_required_sip(
            100_000,
            0.10,
            0,
        )
        assert False
    except ValueError:
        assert True