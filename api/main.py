from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from recommendation.service import (
    generate_recommendation,
)
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Goal-Based Robo-Advisor API",
    description=(
        "Investment planning and mutual fund "
        "recommendation API."
    ),
    version="1.0.0",
)
app = FastAPI(
    title="Goal-Based Robo-Advisor API",
    description="Investment planning and mutual fund recommendation API.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendationRequest(BaseModel):
    goal_type: str = Field(
        ...,
        min_length=1,
    )

    target_amount: float = Field(
        ...,
        gt=0,
    )

    horizon_years: float = Field(
        ...,
        gt=0,
    )

    risk_profile: str = Field(
        ...,
        min_length=1,
    )

    funds_per_asset: int = Field(
        default=2,
        ge=1,
        le=5,
    )


@app.get("/")
def root():
    return {
        "name": "Goal-Based Robo-Advisor API",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.post("/api/recommendation")
def recommendation(
    request: RecommendationRequest,
):
    try:
        result = generate_recommendation(
            goal_type=request.goal_type,
            target_amount=request.target_amount,
            horizon_years=request.horizon_years,
            risk_profile=request.risk_profile,
            funds_per_asset=request.funds_per_asset,
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate recommendation.",
        ) from exc