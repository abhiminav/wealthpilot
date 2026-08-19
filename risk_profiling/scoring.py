SCORE_MAP = {
    "income_stability": {
        "Very Stable": 4,
        "Stable": 3,
        "Somewhat Unstable": 2,
        "Unstable": 1,
    },
    "horizon": {
        "Less than 3 years": 1,
        "3–5 years": 2,
        "5–10 years": 3,
        "10+ years": 4,
    },
    "loss_tolerance": {
        "Sell everything": 1,
        "Sell some": 2,
        "Hold": 3,
        "Invest more": 4,
    },
    "experience": {
        "None": 1,
        "Beginner": 2,
        "Intermediate": 3,
        "Experienced": 4,
    },
}


def calculate_risk_score(answers: dict) -> int:
    """Calculate transparent rule-based risk score."""

    score = 0

    for question, mapping in SCORE_MAP.items():
        answer = answers.get(question)

        if answer not in mapping:
            raise ValueError(
                f"Invalid answer for {question}: {answer}"
            )

        score += mapping[answer]

    age = answers.get("age")

    if age is None:
        raise ValueError("Age is required.")

    if age < 30:
        score += 2
    elif age < 45:
        score += 1

    return score


def classify_risk(score: int) -> str:
    """Map score to risk profile."""

    if score <= 8:
        return "Conservative"

    if score <= 12:
        return "Moderate"

    return "Aggressive"

from risk_profiling.risk_profiles import RISK_PROFILES


def get_risk_profile(score: int) -> dict:
    """Return complete risk profile for a score."""

    for profile_name, profile in RISK_PROFILES.items():

        if (
            profile["min_score"]
            <= score
            <= profile["max_score"]
        ):
            return {
                "profile": profile_name,
                **profile,
            }

    raise ValueError(
        f"Invalid risk score: {score}"
    )