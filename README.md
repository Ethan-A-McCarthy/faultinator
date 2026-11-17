# not-my-faultinator
Trying to make a web app thingy to judge my league gameplay and ultimately determine if it is my fault or not.

Might expand on it a little bit and make an in depth scoring system on a per-role basis as my current version is weighting each role the same when these roles do very different things and will hurt the scores of more passive roles (tanks, enchanters look to be the most affected). May also start some machine learning things and craft up some win probability and maybe calculating a player's "projected score" i.e. how good they should expect to do given their recent history and opponents. I think that would be cool but this is just the start. Will probably focus on getting some kind of front end that is nice and then apply for a persistent api key or smth.

## GitHub Pages frontend and Flask API

GitHub Pages serves the files in `frontend/` as a static site. The Flask API runs
separately because Pages cannot run Python or keep the Riot API key secret. The
frontend calls the API over HTTPS; the API uses `riotAPIs.py` and `analyzer.py`
to retrieve and score matches.

### Local development

1. Install the backend dependencies with `pip install -r requirements.txt`.
2. Put `RIOT_API_KEY=your-key` in the ignored `.env` file.
3. Set `window.FAULTINATOR_API_BASE_URL` in `frontend/config.js` to
   `"http://127.0.0.1:5000"`.
4. In one terminal, start Flask with `flask --app api run`.
5. In another terminal, serve the frontend with
   `python -m http.server 8000 --directory frontend`.
6. Open `http://127.0.0.1:8000/` in your browser.

The common local frontend origins on ports 8000 and 8001 are allowed by default
for CORS.

### Deployment

1. Deploy the Flask API to a Python host that supports WSGI, with
   `gunicorn api:app` as its start command.
2. Configure `RIOT_API_KEY` as a secret/environment variable on that host.
   Configure `FRONTEND_ORIGINS` to the GitHub Pages **origin** (for example,
   `https://username.github.io`, without the repository path).
3. Set `window.FAULTINATOR_API_BASE_URL` in `frontend/config.js` to the API's
   HTTPS origin (for example, `"https://your-api-host.example.com"`).
4. Enable GitHub Pages to use GitHub Actions. The workflow at
   `.github/workflows/pages.yml` publishes `frontend/` whenever `main` is
   updated (or when manually run).

Do not put the Riot API key in `frontend/`: all files published by Pages are
public. The frontend configuration contains only the API's public URL.
