import os 
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('RIOT_API_KEY')
HEADER = {"X-Riot-Token": API_KEY}

BASE_ACCOUNT = "https://americas.api.riotgames.com"
BASE_MATCH = "https://americas.api.riotgames.com"
BASE_SUMMONER = "https://na1.api.riotgames.com"

def get_account_info(name:str, tag:str):
    url = f"{BASE_ACCOUNT}/riot/account/v1/accounts/by-riot-id/{name}/{tag}"
    response = requests.get(url, headers=HEADER)
    response.raise_for_status()
    return response.json()["puuid"]

def get_match_history(puuid:str, count:int=20, start:int=0):
    url = f"{BASE_MATCH}/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {"start": start, "count": count}
    response = requests.get(url, headers=HEADER, params=params)
    response.raise_for_status()
    return response.json()

def get_single_match(match_id:str):
    url = f"{BASE_MATCH}/riot/match/v1/matches/{match_id}"
    response = requests.get(url, headers=HEADER)
    response.raise_for_status()
    return response.json()

def get_match_timeline(match_id:str):
    url = f"{BASE_MATCH}/riot/match/v1/matches/{match_id}/timeline"
    response = requests.get(url, headers=HEADER)
    response.raise_for_status()
    return response.json()