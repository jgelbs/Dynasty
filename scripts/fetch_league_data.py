#!/usr/bin/env python3
"""
Pulls current state from the Sleeper API for a single dynasty league and
writes it to /data as JSON files. Designed to be run on a schedule via
GitHub Actions so the repo builds a running history of roster/trade moves.

No auth needed -- Sleeper's API is public read-only.
"""

import json
import os
import time
import urllib.request

LEAGUE_ID = "1312199624605335552"
BASE = "https://api.sleeper.app/v1"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Only keep these fields per player to keep the trimmed file small and
# actually useful for fantasy analysis (position, team, status, etc.)
PLAYER_FIELDS = [
    "player_id", "full_name", "first_name", "last_name",
    "position", "fantasy_positions", "team", "age", "years_exp",
    "status", "injury_status", "injury_body_part", "search_rank",
    "college",
]


def fetch_json(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "sleeper-dynasty-tracker"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"  retry {attempt + 1}/{retries} for {url}: {e}")
            time.sleep(2)
    raise RuntimeError(f"Failed to fetch {url} after {retries} retries")


def write_json(name, obj):
    path = os.path.join(DATA_DIR, name)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
    print(f"wrote {path}")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    print("Fetching league settings...")
    league = fetch_json(f"{BASE}/league/{LEAGUE_ID}")
    write_json("league.json", league)

    print("Fetching rosters...")
    rosters = fetch_json(f"{BASE}/league/{LEAGUE_ID}/rosters")
    write_json("rosters.json", rosters)

    print("Fetching users...")
    users = fetch_json(f"{BASE}/league/{LEAGUE_ID}/users")
    write_json("users.json", users)

    print("Fetching traded picks...")
    traded_picks = fetch_json(f"{BASE}/league/{LEAGUE_ID}/traded_picks")
    write_json("traded_picks.json", traded_picks)

    print("Fetching recent transactions (all weeks 1-18)...")
    all_transactions = []
    for week in range(1, 19):
        try:
            txns = fetch_json(f"{BASE}/league/{LEAGUE_ID}/transactions/{week}")
            all_transactions.extend(txns)
        except Exception as e:
            print(f"  week {week}: {e}")
    write_json("transactions.json", all_transactions)

    print("Fetching full player database (this is the big one, ~5MB)...")
    all_players = fetch_json(f"{BASE}/players/nfl")

    # Collect every player_id that's actually rostered or on waivers/FA
    # relevant to this league (i.e. anyone in any roster's players list).
    relevant_ids = set()
    for roster in rosters:
        for pid in (roster.get("players") or []):
            relevant_ids.add(str(pid))
        for pid in (roster.get("taxi") or []) or []:
            relevant_ids.add(str(pid))
        for pid in (roster.get("reserve") or []) or []:
            relevant_ids.add(str(pid))

    print(f"Trimming player DB from {len(all_players)} to {len(relevant_ids)} rostered players...")
    trimmed_players = {}
    for pid in relevant_ids:
        p = all_players.get(pid)
        if not p:
            continue
        trimmed_players[pid] = {k: p.get(k) for k in PLAYER_FIELDS}

    write_json("players.json", trimmed_players)

    print("Done.")


if __name__ == "__main__":
    main()
