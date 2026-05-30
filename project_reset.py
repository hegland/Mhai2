#!/usr/bin/env python3
"""
pre_gateway_dispatch hook: detect project switches and auto-reset session.

When the user's message signals a different project than the current one,
prepend /reset so Hermes starts a fresh context before processing.
"""
import json, sys, re
from pathlib import Path

STATE_FILE = Path.home() / ".hermes" / "hooks" / ".current_project"

PROJECT_SIGNALS = {
    "VRZM26":         ["vrzm", "zbigniew", "stachurski", "ias", "amorphous", "sphere pack", "sphere packing", "ideal amorphous"],
    "XiChen26honors": ["xi chen", "xichen", "honours", "pinn", "barron", "devore", "relu approximation", "neural network approximation"],
    "GlebPhD":        ["gleb", "shabernev", "phd thesis"],
    "MATH8702":       ["math8702", "math 8702", "8702"],
    "FdHMH":          ["frank", "de hoog", "fdh", "cur decomposition", "randnla", "srht", "cur matrix"],
    "DBT":            ["dbt", "radical acceptance", "linehan", "distress tolerance"],
    "Recipes":        ["recipe", "airfryer", "air fryer", "cooking"],
    "Personal":       ["weather", "calendar", "gmail", "backup"],
}

# Commands that should never trigger a reset
SKIP_COMMANDS = {"/reset", "/new", "/start", "/help", "/stop", "/project", "/projects"}

def detect_project(text: str) -> str | None:
    t = text.lower()
    scores = {p: sum(1 for s in sigs if s in t) for p, sigs in PROJECT_SIGNALS.items()}
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else None

def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        print(json.dumps({"action": "allow"}))
        return

    text = payload.get("text", "").strip()

    # Don't interfere with commands
    if text.startswith("/") and text.split()[0].lower() in SKIP_COMMANDS:
        print(json.dumps({"action": "allow"}))
        return

    # Detect project from message
    detected = detect_project(text)
    if not detected:
        print(json.dumps({"action": "allow"}))
        return

    # Read current project from state
    current = STATE_FILE.read_text().strip() if STATE_FILE.exists() else None

    # Update state
    STATE_FILE.write_text(detected)

    # If project changed, prepend /reset
    if current and current != detected:
        new_text = f"/reset\n{text}"
        print(json.dumps({
            "action": "rewrite",
            "text": new_text,
        }))
        return

    print(json.dumps({"action": "allow"}))

if __name__ == "__main__":
    main()
