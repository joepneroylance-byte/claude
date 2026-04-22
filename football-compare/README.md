# Football Player Comparison

Side-by-side player comparison tool covering the Premier League, Championship, Bundesliga, Ligue 1, and La Liga.

## Setup

1. Get a free API key from [API-Football on RapidAPI](https://rapidapi.com/api-sports/api/api-football)
2. Copy `.env.example` to `.env` and paste your key
3. Install dependencies and run:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

4. Open http://localhost:8000

## Stats covered

- General: appearances, starts, minutes, avg rating
- Attacking: goals, assists, shots, shot accuracy, mins per goal, penalties
- Passing: total passes, key passes, pass accuracy
- Dribbling & duels: dribble attempts/success %, duel win %
- Defensive: tackles, interceptions, blocks, fouls
- Discipline: yellow/red cards

## Enrichment ideas

- xG / xA (upgrade API tier or add FBref scraper)
- Season selector (compare across multiple seasons)
- Heatmaps / position maps
- Export comparison as image
- Top N players by stat for a league
- Save/share comparison via URL
