import os
import unittest
from unittest.mock import patch

import api


class AnalyzeEndpointTests(unittest.TestCase):
    def setUp(self):
        self.client = api.app.test_client()

    def test_rejects_invalid_game_count(self):
        with patch.object(api, "get_account_info") as get_account:
            response = self.client.get(
                "/api/analyze?name=Player&tag=NA1&games=not-a-number"
            )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Games must", response.get_json()["detail"])
        get_account.assert_not_called()

    def test_allows_alternate_local_frontend_origin(self):
        response = self.client.get(
            "/api/analyze",
            headers={"Origin": "http://127.0.0.1:8001"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.headers["Access-Control-Allow-Origin"],
            "http://127.0.0.1:8001",
        )

    def test_returns_frontend_match_shape_and_cors_header(self):
        match = {
            "info": {
                "participants": [
                    {
                        "puuid": "player-puuid",
                        "championName": "Annie",
                        "kills": 3,
                        "deaths": 2,
                        "assists": 7,
                        "win": True,
                    }
                ],
                "gameDuration": 1800,
            }
        }
        scores = {
            "total_score": 82.5,
            "cs_per_minute": {
                "raw": 6.0,
                "score": 75,
                "weight": 25,
                "weighted_score": 18.75,
            },
        }

        with patch.dict(os.environ, {"RIOT_API_KEY": "test-key"}), \
             patch.object(api, "get_account_info", return_value="player-puuid"), \
             patch.object(api, "get_match_history", return_value=["match-1"]), \
             patch.object(api, "get_single_match", return_value=match), \
             patch.object(api, "load_yaml", return_value={}), \
             patch.object(api, "calculate_score", return_value=scores):
            response = self.client.get(
                "/api/analyze?name=Player&tag=NA1&games=1",
                headers={"Origin": "http://localhost:8000"},
            )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["matches"][0]["overall"], 82.5)
        self.assertEqual(
            payload["matches"][0]["breakdown"]["cs_per_minute"]["score"], 75
        )
        self.assertEqual(payload["matches"][0]["champion"], "Annie")
        self.assertTrue(payload["matches"][0]["win"])
        self.assertEqual(
            response.headers["Access-Control-Allow-Origin"],
            "http://localhost:8000",
        )


if __name__ == "__main__":
    unittest.main()
