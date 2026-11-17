import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

load_dotenv()

from riotAPIs import get_account_info, get_match_history, get_single_match
from analyzer import calculate_score, load_yaml


app = Flask(__name__)

# Only allow the local development UI by default. Set FRONTEND_ORIGINS on the
# host to the GitHub Pages origin (for example, https://username.github.io).
allowed_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:8000,http://127.0.0.1:8000,"
        "http://localhost:8001,http://127.0.0.1:8001",
    ).split(",")
    if origin.strip()
]
CORS(app, resources={r"/api/*": {"origins": allowed_origins}})


@app.get("/api/analyze")
def analyze():
    name = request.args.get("name", "").strip()
    tag = request.args.get("tag", "").strip()
    games_value = request.args.get("games", "5")

    if not name or not tag:
        return jsonify(detail="Both Riot ID name and tag are required."), 400

    try:
        games = int(games_value)
    except ValueError:
        return jsonify(detail="Games must be a whole number between 1 and 20."), 400
    if not 1 <= games <= 20:
        return jsonify(detail="Games must be between 1 and 20."), 400

    if not os.getenv("RIOT_API_KEY"):
        app.logger.error("RIOT_API_KEY is not set")
        return jsonify(detail="The Riot API key is not configured on the server."), 500

    try:
        puuid = get_account_info(name, tag)
    except requests.HTTPError as error:
        if error.response is not None and error.response.status_code == 404:
            return jsonify(detail=f"Riot ID '{name}#{tag}' was not found."), 404
        app.logger.exception("Riot account lookup failed")
        return jsonify(detail="Riot account lookup failed. Please try again later."), 502
    except requests.RequestException:
        app.logger.exception("Riot account lookup failed")
        return jsonify(detail="Riot account lookup failed. Please try again later."), 502

    try:
        match_ids = get_match_history(puuid, count=games)
        constraints = load_yaml(os.path.join(os.path.dirname(__file__), "config.yaml"))
        results = []

        for match_id in match_ids:
            match = get_single_match(match_id)
            participant = next(
                player
                for player in match["info"]["participants"]
                if player["puuid"] == puuid
            )
            scores = calculate_score(match, puuid, constraints)

            # The frontend uses "overall" and "breakdown"; map these to the
            # analyzer's total and per-stat values so scores display correctly.
            results.append(
                {
                    "match_id": match_id,
                    "overall": scores["total_score"],
                    "breakdown": {
                        key: value
                        for key, value in scores.items()
                        if isinstance(value, dict)
                    },
                    "champion": participant.get("championName"),
                    "kills": participant.get("kills"),
                    "deaths": participant.get("deaths"),
                    "assists": participant.get("assists"),
                    "duration_mins": round(match["info"]["gameDuration"] / 60, 1),
                    "win": participant.get("win"),
                }
            )

        return jsonify(summoner=f"{name}#{tag}", matches=results)
    except requests.HTTPError:
        app.logger.exception("Riot match request failed")
        return jsonify(detail="Riot match data could not be fetched. Please try again later."), 502
    except requests.RequestException:
        app.logger.exception("Riot match request failed")
        return jsonify(detail="Riot match data could not be fetched. Please try again later."), 502
    except (KeyError, StopIteration, TypeError, ValueError):
        app.logger.exception("Could not analyze Riot match data")
        return jsonify(detail="Riot match data could not be analyzed."), 502
