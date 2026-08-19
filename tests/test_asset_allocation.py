from planning.glide_path import get_glide_path
from recommendation.asset_allocation import (
    get_asset_class,
)


def test_asset_class_mapping():
    assert get_asset_class("Large Cap") == "Equity"
    assert get_asset_class("Index") == "Equity"
    assert get_asset_class("Corporate Bond") == "Debt"
    assert get_asset_class("Gold") == "Gold"


def test_short_horizon_reduces_equity_exposure():
    allocation = get_glide_path(
        "Aggressive",
        2,
    )

    assert allocation["Equity"] == 0
    assert allocation["Debt"] == 90
    assert allocation["Gold"] == 10


def test_long_aggressive_horizon():
    allocation = get_glide_path(
        "Aggressive",
        15,
    )

    assert allocation == {
        "Equity": 80,
        "Debt": 10,
        "Gold": 10,
    }