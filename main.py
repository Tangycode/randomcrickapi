from fastapi import FastAPI, HTTPException
from typing import List, Dict

app = FastAPI()

# Sample over-wise data (replace with DB or computed data)
OVER_DATA = {
    "innings_1": [
        {"over": 1, "runs": 8, "wickets": 0},
        {"over": 2, "runs": 12, "wickets": 0},
        {"over": 3, "runs": 5, "wickets": 1},
        {"over": 4, "runs": 15, "wickets": 0},
        {"over": 5, "runs": 6, "wickets": 2},
        {"over": 6, "runs": 10, "wickets": 0},
    ]
}


def classify_momentum(runs: int, wickets: int) -> str:
    """
    Rule-based momentum classification:
    - Positive: runs >= 10 and no wickets
    - Neutral: runs between 6–9 and <=1 wicket
    - Negative: low runs OR multiple wickets
    """
    if runs >= 10 and wickets == 0:
        return "Positive"
    elif 6 <= runs <= 9 and wickets <= 1:
        return "Neutral"
    else:
        return "Negative"


def build_momentum(data: List[Dict]) -> List[Dict]:
    if not data:
        raise HTTPException(status_code=400, detail="No over data available")

    result = []
    prev_runs = None

    for over_data in data:
        # Validate fields
        if not all(k in over_data for k in ("over", "runs", "wickets")):
            continue

        over = over_data["over"]
        runs = over_data["runs"]
        wickets = over_data["wickets"]

        if not isinstance(runs, int) or not isinstance(wickets, int):
            continue

        momentum = classify_momentum(runs, wickets)

        # Trend logic
        trend = "Stable"
        if prev_runs is not None:
            if runs > prev_runs:
                trend = "Increasing"
            elif runs < prev_runs:
                trend = "Decreasing"

        prev_runs = runs

        result.append({
            "over": over,
            "runs": runs,
            "wickets": wickets,
            "momentum": momentum,
            "trend": trend
        })

    if not result:
        raise HTTPException(status_code=400, detail="Invalid over data")

    return result


@app.get("/momentum/{innings_id}")
def get_momentum(innings_id: str):
    if innings_id not in OVER_DATA:
        raise HTTPException(status_code=404, detail="Innings not found")

    try:
        momentum_data = build_momentum(OVER_DATA[innings_id])

        return {
            "innings_id": innings_id,
            "momentum_summary": momentum_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
