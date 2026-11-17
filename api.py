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
    print("KEY LOADED:", os.getenv("RIOT_API_KEY"))
    if not os.getenv("RIOT_API_KEY"):
        raise HTTPException(status_code=500, detail="RIOT_API_KEY not set in environment")
    try:
        account_info = get_account_info(name, tag)
        puuid = account_info
        print(puuid)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Summoner '{name}#{tag}' not found {str(e)}")
 
    try:
        match_ids   = get_match_history(puuid, games)
        constraints = load_yaml()
        results     = []
        for mid in match_ids:
            match  = get_single_match(mid)
            scores = calculate_score(match, puuid, constraints)
            results.append({"match_id": mid, **scores})
        return {"summoner": f"{name}#{tag}", "matches": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while analyzing matches: {str(e)}")

# Serve the frontend at /
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
