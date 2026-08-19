import pandas as pd

from recommendation.recommendation_engine import (
    build_recommendation,
)


funds = pd.read_csv(
    "data/processed/fund_metrics_clean.csv"
)

result = build_recommendation(
    funds=funds,
    goal_type="House Down Payment",
    target_amount=2_500_000,
    horizon_years=8,
    risk_profile="Moderate",
)

print("\n=== GOAL ===")
print(result["goal_type"])
print("Target:", result["target_amount"])
print("Horizon:", result["horizon_years"])

print("\n=== RISK ===")
print(result["risk_profile"])

print("\n=== ALLOCATION ===")
print(result["allocation"])

print("\n=== RETURN ===")
print(result["expected_return"])

print("\n=== SIP ===")
print(result["required_monthly_sip"])

print("\n=== SIP ALLOCATION ===")
print(result["sip_allocation"])

print("\n=== FUNDS ===")

for asset, funds_list in result[
    "recommendations"
].items():

    print(f"\n{asset}:")

    for fund in funds_list:
        print(
            " ",
            fund["scheme_name"],
            "|",
            fund["category"],
            "| score:",
            round(fund["fund_score"], 2),
        )

print("\n=== PROJECTION ===")
print("Months:", len(result["projection"]))
print("Start:", result["projection"][0])
print("End:", result["projection"][-1])