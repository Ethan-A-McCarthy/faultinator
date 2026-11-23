#using fastapi for frontend and backend communication
import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from riotAPIs import get_account_info, get_match_history, get_single_match
from analyzer import calculate_score, load_yaml
    
load_dotenv()

app = FastAPI(title="LoL Analyzer API")
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)
 
@app.get("/api/analyze/{name}/{tag}")
async def analyze(name: str, tag: str, games: int = 5):
    if not os.getenv("RIOT_API_KEY"):
        raise HTTPException(status_code=500, detail="RIOT_API_KEY not set in environment")
    try:
        account_info = get_account_info(name, tag)
        puuid = account_info
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Summoner '{name}#{tag}' not found {str(e)}")
 
    try:
        match_ids   = get_match_history(puuid, games)
        constraints = load_yaml()
        results     = []
        for mid in match_ids:
            match  = get_single_match(mid)
            scores = calculate_score(match, puuid, constraints)
            stats = scores["stats"]
            breakdown = {
                key: value for key, value in scores.items()
                if isinstance(value, dict) and "score" in value
            }
            results.append({
                "match_id": mid,
                "champion": stats["champion"],
                "win": stats["win"],
                "kills": stats["kills"],
                "deaths": stats["deaths"],
                "assists": stats["assists"],
                "duration_mins": stats["duration_minutes"],
                "role": stats["role"],
                "overall": scores["total_score"],
                "total_score": scores["total_score"],
                "stats": stats,
                "breakdown": breakdown,
            })
        return {"summoner": f"{name}#{tag}", "matches": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while analyzing matches: {str(e)}")

# Serve the frontend at /
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
