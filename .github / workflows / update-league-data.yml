name: Update Sleeper league data

on:
  schedule:
    # Runs daily at 13:00 UTC (~9am ET / 6am PT). Adjust as you like.
    - cron: "0 13 * * *"
  workflow_dispatch: {}  # lets you trigger it manually from the Actions tab

permissions:
  contents: write

jobs:
  update-data:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Fetch latest league data
        run: python scripts/fetch_league_data.py

      - name: Commit and push if changed
        run: |
          git config user.name "league-data-bot"
          git config user.email "actions@users.noreply.github.com"
          git add data/
          if git diff --cached --quiet; then
            echo "No changes to commit."
          else
            git commit -m "Update league data $(date -u +'%Y-%m-%d %H:%M UTC')"
            git push
          fi
