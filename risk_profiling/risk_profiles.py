RISK_PROFILES = {
    "Conservative": {
        "min_score": 5,
        "max_score": 8,
        "description": (
            "Prioritizes capital preservation and accepts "
            "lower expected returns for lower volatility."
        ),
        "base_allocation": {
            "Equity": 30,
            "Debt": 60,
            "Gold": 10,
        },
    },

    "Moderate": {
        "min_score": 9,
        "max_score": 12,
        "description": (
            "Seeks a balance between growth and capital "
            "preservation."
        ),
        "base_allocation": {
            "Equity": 60,
            "Debt": 30,
            "Gold": 10,
        },
    },

    "Aggressive": {
        "min_score": 13,
        "max_score": 18,
        "description": (
            "Prioritizes long-term capital growth and accepts "
            "higher volatility."
        ),
        "base_allocation": {
            "Equity": 80,
            "Debt": 10,
            "Gold": 10,
        },
    },
}