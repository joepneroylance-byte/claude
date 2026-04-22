import os
import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://v3.football.api-sports.io"
API_KEY = os.getenv("API_FOOTBALL_KEY", "")

LEAGUES = {
    "premier_league": 39,
    "championship": 40,
    "bundesliga": 78,
    "ligue_1": 61,
    "la_liga": 140,
}

LEAGUE_NAMES = {v: k.replace("_", " ").title() for k, v in LEAGUES.items()}

CURRENT_SEASON = 2024


def _headers() -> dict:
    return {
        "x-rapidapi-host": "v3.football.api-sports.io",
        "x-rapidapi-key": API_KEY,
    }


async def search_players(name: str, league_id: int | None = None) -> list[dict]:
    """Search players by name, optionally filtered to a league."""
    params: dict = {"search": name, "season": CURRENT_SEASON}
    if league_id:
        params["league"] = league_id

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BASE_URL}/players",
            headers=_headers(),
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

    results = []
    for entry in data.get("response", []):
        player = entry.get("player", {})
        stats_list = entry.get("statistics", [])
        if not stats_list:
            continue
        stat = stats_list[0]
        league_info = stat.get("league", {})
        team_info = stat.get("team", {})
        results.append(
            {
                "id": player.get("id"),
                "name": player.get("name"),
                "firstname": player.get("firstname"),
                "lastname": player.get("lastname"),
                "nationality": player.get("nationality"),
                "age": player.get("age"),
                "photo": player.get("photo"),
                "team": team_info.get("name"),
                "team_logo": team_info.get("logo"),
                "league": league_info.get("name"),
                "league_id": league_info.get("id"),
                "season": league_info.get("season"),
            }
        )
    return results


async def get_player_stats(player_id: int, league_id: int, season: int = CURRENT_SEASON) -> dict | None:
    """Fetch full statistics for a player in a given league/season."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BASE_URL}/players",
            headers=_headers(),
            params={"id": player_id, "league": league_id, "season": season},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

    entries = data.get("response", [])
    if not entries:
        return None

    entry = entries[0]
    player = entry["player"]
    stats_list = entry.get("statistics", [])

    aggregated = _aggregate_stats(stats_list)
    return {
        "id": player.get("id"),
        "name": player.get("name"),
        "firstname": player.get("firstname"),
        "lastname": player.get("lastname"),
        "nationality": player.get("nationality"),
        "age": player.get("age"),
        "height": player.get("height"),
        "weight": player.get("weight"),
        "photo": player.get("photo"),
        "position": aggregated.get("position"),
        "team": aggregated.get("team"),
        "team_logo": aggregated.get("team_logo"),
        "league": aggregated.get("league"),
        "season": season,
        "stats": aggregated.get("stats"),
    }


def _aggregate_stats(stats_list: list[dict]) -> dict:
    """Sum stats across multiple competition entries for the same player."""
    totals: dict = {
        "appearances": 0,
        "lineups": 0,
        "minutes": 0,
        "goals": 0,
        "assists": 0,
        "shots_total": 0,
        "shots_on": 0,
        "passes_total": 0,
        "passes_key": 0,
        "passes_accuracy": [],
        "dribbles_attempts": 0,
        "dribbles_success": 0,
        "tackles_total": 0,
        "tackles_interceptions": 0,
        "tackles_blocks": 0,
        "duels_total": 0,
        "duels_won": 0,
        "fouls_drawn": 0,
        "fouls_committed": 0,
        "yellow_cards": 0,
        "red_cards": 0,
        "penalty_scored": 0,
        "penalty_missed": 0,
        "rating_values": [],
    }
    position = team = team_logo = league = None

    for stat in stats_list:
        if position is None:
            position = stat.get("games", {}).get("position")
        if team is None and stat.get("team"):
            team = stat["team"].get("name")
            team_logo = stat["team"].get("logo")
        if league is None and stat.get("league"):
            league = stat["league"].get("name")

        g = stat.get("games", {})
        totals["appearances"] += g.get("appearences") or 0
        totals["lineups"] += g.get("lineups") or 0
        totals["minutes"] += g.get("minutes") or 0
        if g.get("rating"):
            try:
                totals["rating_values"].append(float(g["rating"]))
            except (ValueError, TypeError):
                pass

        go = stat.get("goals", {})
        totals["goals"] += go.get("total") or 0
        totals["assists"] += go.get("assists") or 0

        sh = stat.get("shots", {})
        totals["shots_total"] += sh.get("total") or 0
        totals["shots_on"] += sh.get("on") or 0

        pa = stat.get("passes", {})
        totals["passes_total"] += pa.get("total") or 0
        totals["passes_key"] += pa.get("key") or 0
        if pa.get("accuracy"):
            try:
                totals["passes_accuracy"].append(float(pa["accuracy"]))
            except (ValueError, TypeError):
                pass

        dr = stat.get("dribbles", {})
        totals["dribbles_attempts"] += dr.get("attempts") or 0
        totals["dribbles_success"] += dr.get("success") or 0

        ta = stat.get("tackles", {})
        totals["tackles_total"] += ta.get("total") or 0
        totals["tackles_interceptions"] += ta.get("interceptions") or 0
        totals["tackles_blocks"] += ta.get("blocks") or 0

        du = stat.get("duels", {})
        totals["duels_total"] += du.get("total") or 0
        totals["duels_won"] += du.get("won") or 0

        fo = stat.get("fouls", {})
        totals["fouls_drawn"] += fo.get("drawn") or 0
        totals["fouls_committed"] += fo.get("committed") or 0

        ca = stat.get("cards", {})
        totals["yellow_cards"] += ca.get("yellow") or 0
        totals["red_cards"] += ca.get("red") or 0

        pe = stat.get("penalty", {})
        totals["penalty_scored"] += pe.get("scored") or 0
        totals["penalty_missed"] += pe.get("missed") or 0

    avg_rating = (
        round(sum(totals["rating_values"]) / len(totals["rating_values"]), 2)
        if totals["rating_values"]
        else None
    )
    avg_pass_acc = (
        round(sum(totals["passes_accuracy"]) / len(totals["passes_accuracy"]), 1)
        if totals["passes_accuracy"]
        else None
    )
    dribble_pct = (
        round(totals["dribbles_success"] / totals["dribbles_attempts"] * 100, 1)
        if totals["dribbles_attempts"]
        else None
    )
    duel_pct = (
        round(totals["duels_won"] / totals["duels_total"] * 100, 1)
        if totals["duels_total"]
        else None
    )
    shot_acc = (
        round(totals["shots_on"] / totals["shots_total"] * 100, 1)
        if totals["shots_total"]
        else None
    )
    mins_per_goal = (
        round(totals["minutes"] / totals["goals"], 1)
        if totals["goals"]
        else None
    )

    return {
        "position": position,
        "team": team,
        "team_logo": team_logo,
        "league": league,
        "stats": {
            "appearances": totals["appearances"],
            "lineups": totals["lineups"],
            "minutes": totals["minutes"],
            "avg_rating": avg_rating,
            "goals": totals["goals"],
            "assists": totals["assists"],
            "shots_total": totals["shots_total"],
            "shots_on_target": totals["shots_on"],
            "shot_accuracy_pct": shot_acc,
            "mins_per_goal": mins_per_goal,
            "passes_total": totals["passes_total"],
            "passes_key": totals["passes_key"],
            "pass_accuracy_pct": avg_pass_acc,
            "dribbles_attempts": totals["dribbles_attempts"],
            "dribbles_success": totals["dribbles_success"],
            "dribble_success_pct": dribble_pct,
            "tackles": totals["tackles_total"],
            "interceptions": totals["tackles_interceptions"],
            "blocks": totals["tackles_blocks"],
            "duels_total": totals["duels_total"],
            "duels_won": totals["duels_won"],
            "duel_win_pct": duel_pct,
            "fouls_drawn": totals["fouls_drawn"],
            "fouls_committed": totals["fouls_committed"],
            "yellow_cards": totals["yellow_cards"],
            "red_cards": totals["red_cards"],
            "penalties_scored": totals["penalty_scored"],
            "penalties_missed": totals["penalty_missed"],
        },
    }
