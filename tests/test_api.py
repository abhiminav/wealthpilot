from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == (
        "Goal-Based Robo-Advisor API"
    )
    assert data["status"] == "running"
    assert data["version"] == "1.0.0"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }


def test_valid_recommendation_request():
    response = client.post(
        "/api/recommendation",
        json={
            "goal_type": "Retirement",
            "target_amount": 1_000_000,
            "horizon_years": 15,
            "risk_profile": "Aggressive",
            "funds_per_asset": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["goal_type"] == "Retirement"
    assert data["target_amount"] == 1_000_000
    assert data["horizon_years"] == 15
    assert data["risk_profile"] == "Aggressive"


def test_invalid_goal_type():
    response = client.post(
        "/api/recommendation",
        json={
            "goal_type": "Invalid Goal",
            "target_amount": 1_000_000,
            "horizon_years": 15,
            "risk_profile": "Aggressive",
        },
    )

    assert response.status_code == 422


def test_invalid_risk_profile():
    response = client.post(
        "/api/recommendation",
        json={
            "goal_type": "Retirement",
            "target_amount": 1_000_000,
            "horizon_years": 15,
            "risk_profile": "YOLO",
        },
    )

    assert response.status_code == 422


def test_zero_target_amount():
    response = client.post(
        "/api/recommendation",
        json={
            "goal_type": "Retirement",
            "target_amount": 0,
            "horizon_years": 15,
            "risk_profile": "Aggressive",
        },
    )

    assert response.status_code == 422


def test_negative_target_amount():
    response = client.post(
        "/api/recommendation",
        json={
            "goal_type": "Retirement",
            "target_amount": -100_000,
            "horizon_years": 15,
            "risk_profile": "Aggressive",
        },
    )

    assert response.status_code == 422


def test_zero_horizon():
    response = client.post(
        "/api/recommendation",
        json={
            "goal_type": "Retirement",
            "target_amount": 1_000_000,
            "horizon_years": 0,
            "risk_profile": "Aggressive",
        },
    )

    assert response.status_code == 422


def test_invalid_funds_per_asset():
    response = client.post(
        "/api/recommendation",
        json={
            "goal_type": "Retirement",
            "target_amount": 1_000_000,
            "horizon_years": 15,
            "risk_profile": "Aggressive",
            "funds_per_asset": 10,
        },
    )

    assert response.status_code == 422


def test_missing_required_field():
    response = client.post(
        "/api/recommendation",
        json={
            "goal_type": "Retirement",
            "target_amount": 1_000_000,
            "risk_profile": "Aggressive",
        },
    )

    assert response.status_code == 422