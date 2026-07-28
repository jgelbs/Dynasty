# AEPI Dynasty — Sleeper League Tracker

Pulls this league's data from Sleeper's public (no-auth) API on a daily
schedule and commits it to `/data` as JSON. Built so Claude can read the
files directly via raw.githubusercontent.com without needing anything
pasted into chat.

## Setup

1. Create a new GitHub repo (public is simplest — private also works,
   the Action still runs fine).
2. Copy this whole folder structure into the repo root:
   - `scripts/fetch_league_data.py`
   - `.github/workflows/update-league-data.yml`
   - `data/` (starts empty, gets populated on first run)
3. Push to GitHub.
4. Go to the repo's **Actions** tab. If prompted, click "I understand my
   workflows, go ahead and enable them."
5. Manually trigger it once: Actions tab → "Update Sleeper league data" →
   "Run workflow" → Run. This populates `/data` for the first time instead
   of waiting for the next 13:00 UTC run.
6. After that it runs automatically every day. Adjust the cron schedule
   in the workflow file if you want it more/less frequent.

## What's in /data after a run

- `league.json` — settings, scoring, roster format
- `rosters.json` — every team's players by roster_id
- `users.json` — owner display names / team names by user_id
- `players.json` — trimmed player DB (only ~250 players actually
  rostered in this league), with names, positions, teams, injury status
- `transactions.json` — trades, waivers, free agent moves, all weeks
- `traded_picks.json` — future draft pick trades

## Using this with Claude

Once it's live, just give me the raw file URL, e.g.:

```
https://raw.githubusercontent.com/<your-username>/<repo-name>/main/data/rosters.json
```

I can fetch that directly — no copy-pasting JSON into chat needed. Since
it updates daily, each time we talk I can pull a fresh snapshot and
compare against what I remember from last time to flag what changed.
