#!/usr/bin/env python3
"""
pre_gateway_dispatch hook: detect project switches and auto-reset session.

When the user's message signals a different project than the current one,
prepend /reset so Hermes starts a fresh context before processing.

Also reports session token cost via Telegram when /new is sent or a
project switch occurs.
"""
import json, sys, re, sqlite3, urllib.request, urllib.parse
from pathlib import Path

STATE_FILE  = Path.home() / ".hermes" / "hooks" / ".current_project"
DB_PATH     = Path.home() / ".hermes" / "state.db"
ENV_FILE    = Path.home() / ".hermes" / ".env"
CONFIG_FILE = Path.home() / ".hermes" / "config.yaml"

PROJECT_DIRS = {
    "VRZM26":         "/home/hegland/Desktop/VRZM26",
    "FdHMH":          "/home/hegland/Desktop/FdHMH",
    "XiChen26honors": "/home/hegland/Desktop/StudentProjects/XiChen26honors",
    "GlebPhD":        "/home/hegland/Desktop/StudentProjects/GlebPhD",
    "MATH8702":       "/home/hegland/Desktop/StudentProjects/MATH8702",
    "DBT":            "/home/hegland/projects/DBT",
    "Recipes":        "/home/hegland",
    "Personal":       "/home/hegland",
}

# Signals are matched as whole words (word boundaries) to avoid false positives.
# Multi-word phrases are matched as substrings (they're specific enough).
PROJECT_SIGNALS = {
    "VRZM26":         [r"\bvrzm\b", r"\bzbigniew\b", r"\bstachurski\b", r"\bias algorithm\b", r"\bamorphous solid\b", "sphere pack", "sphere packing", "ideal amorphous"],
    "XiChen26honors": ["xi chen", "xichen", r"\bhonours\b", r"\bpinn\b", r"\bbarron\b", r"\bdevore\b", "relu approximation", "neural network approximation"],
    "GlebPhD":        [r"\bgleb\b", r"\bshabernev\b", "phd thesis"],
    "MATH8702":       [r"\bmath8702\b", "math 8702", r"\b8702\b"],
    "FdHMH":          [r"\bfrank de hoog\b", r"\bde hoog\b", r"\bfdh\b", "cur decomposition", r"\brandnla\b", r"\bsrht\b", "cur matrix"],
    "DBT":            [r"\bdbt\b", "radical acceptance", r"\blinehan\b", "distress tolerance"],
    "Recipes":        [r"\brecipes\b", r"\bairfryer\b", "air fryer", "cooking recipe"],
    "Personal":       [r"\bgmail\b", r"\bgoogle calendar\b", r"\bmy calendar\b", r"\bpcloud\b", r"\bcalendar\b"],
}

# Commands that should never trigger a project reset
RESET_SKIP_COMMANDS = {"/reset", "/start", "/help", "/stop", "/project", "/projects"}


def detect_project(text: str) -> str | None:
    t = text.lower()
    scores = {}
    for project, signals in PROJECT_SIGNALS.items():
        score = 0
        for sig in signals:
            if sig.startswith(r"\b") or sig.startswith("("):
                if re.search(sig, t):
                    score += 1
            else:
                if sig in t:
                    score += 1
        scores[project] = score
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else None


def load_env() -> dict:
    env = {}
    try:
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"')
    except Exception:
        pass
    return env


def session_cost_summary() -> str | None:
    """Return a short cost string for the most recent session, or None on error."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        cur.execute("""
            SELECT title, message_count,
                   COALESCE(input_tokens,0), COALESCE(output_tokens,0),
                   COALESCE(cache_read_tokens,0), COALESCE(cache_write_tokens,0)
            FROM sessions
            ORDER BY started_at DESC LIMIT 1
        """)
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        title, msgs, inp, out, cr, cw = row
        cost = (inp * 0.80 + cr * 0.08 + cw * 1.00 + out * 4.00) / 1e6
        label = (title or "session")[:40]
        return f"📊 {label}\n{msgs} msgs · ${cost:.3f} (in {inp+cr:,} / out {out:,})"
    except Exception:
        return None


def send_telegram(text: str) -> None:
    env = load_env()
    token = env.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = env.get("TELEGRAM_HOME_CHANNEL", "")
    if not token or not chat_id:
        return
    try:
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage", data=data
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


def set_project_cwd(project: str) -> None:
    """Update terminal.cwd in config.yaml for the detected project."""
    cwd = PROJECT_DIRS.get(project)
    if not cwd:
        return
    try:
        import re
        text = CONFIG_FILE.read_text()
        text = re.sub(r"^(\s*cwd:\s*).*$", f"\\g<1>{cwd}", text, flags=re.MULTILINE)
        CONFIG_FILE.write_text(text)
    except Exception:
        pass


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        print(json.dumps({"action": "allow"}))
        return

    # text is in payload["text"] for direct test calls, or embedded in
    # payload["extra"]["event"] as a serialised MessageEvent string for real gateway calls
    text = payload.get("text", "")
    if not text:
        extra = payload.get("extra", {})
        event_str = str(extra.get("event", ""))
        # Extract from MessageEvent(text='...', ...) string representation
        m = re.search(r"MessageEvent\(text='(.*?)',", event_str)
        if m:
            text = m.group(1)
        elif isinstance(extra.get("event"), dict):
            text = extra["event"].get("text", "")
    text = text.strip()
    cmd = text.split()[0].lower() if text.startswith("/") else ""

    # Tier 1: handle known commands directly without invoking the LLM
    try:
        import sys as _sys
        _sys.path.insert(0, str(Path.home() / ".hermes" / "hooks"))
        from tier1_commands import handle as tier1_handle
        if tier1_handle(text):
            print(json.dumps({"action": "skip", "reason": "tier1"}))
            return
    except Exception as e:
        with open(Path.home() / ".hermes" / "logs" / "tier1_errors.log", "a") as f:
            import traceback
            f.write(f"tier1 error: {e}\ntext: {text}\n{traceback.format_exc()}\n\n")
        pass

    # /new: report cost, clear project state, then allow Hermes to handle the reset
    if cmd == "/new":
        summary = session_cost_summary()
        if summary:
            send_telegram(summary)
        STATE_FILE.unlink(missing_ok=True)
        print(json.dumps({"action": "allow"}))
        return

    # Other skip commands: pass through unchanged
    if cmd in RESET_SKIP_COMMANDS:
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

    # If project changed, report cost then reset
    if current and current != detected:
        summary = session_cost_summary()
        if summary:
            send_telegram(summary)
        print(json.dumps({"action": "rewrite", "text": f"/reset\n{text}"}))
        return

    print(json.dumps({"action": "allow"}))


if __name__ == "__main__":
    main()
