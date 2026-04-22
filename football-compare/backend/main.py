from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pathlib

from api_client import search_players, get_player_stats, LEAGUES, LEAGUE_NAMES

app = FastAPI(title="Football Player Comparison")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

FRONTEND_DIR = pathlib.Path(__file__).parent.parent / "frontend"


@app.get("/api/leagues")
async def list_leagues():
    return [{"id": v, "name": LEAGUE_NAMES[v]} for v in LEAGUES.values()]


@app.get("/api/players/search")
async def search(
    q: str = Query(..., min_length=2, description="Player name"),
    league_id: int | None = Query(None, description="Filter by league ID"),
):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    results = await search_players(q.strip(), league_id)
    return results


@app.get("/api/players/{player_id}/stats")
async def player_stats(
    player_id: int,
    league_id: int = Query(..., description="League ID"),
    season: int = Query(2024, description="Season year"),
):
    data = await get_player_stats(player_id, league_id, season)
    if data is None:
        raise HTTPException(status_code=404, detail="Player stats not found")
    return data


app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")


@app.get("/")
async def root():
    return FileResponse(str(FRONTEND_DIR / "index.html"))
