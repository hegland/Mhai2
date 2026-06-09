# CLAUDE.md — Mhai2

This file documents Mhai2, a personal AI agent for Markus Hegland built on the Hermes Agent Framework.

## Overview

Mhai2 is a successor to Mhai (`~/projects/agent/`) using the Hermes Agent Framework instead of a custom Telegram bot. Mhai (agent/) is left completely untouched.

- **Hermes install:** `~/.hermes/`
- **Telegram bot:** separate bot from Mhai (token starts with 8922755953)
- **LLM:** Claude Haiku 4.5 via direct Anthropic API (no OpenRouter)
- **Skills:** `~/.hermes/skills/mhai2/`
- **Skill library:** `~/projects/Mhai2/mhai_skills.py`

## Architecture

```
Telegram bot (Hermes native)
    ↓
Hermes Agent Framework (memory, skill learning, agent loop)
    ↓
Claude API — claude-haiku-4-5-20251001 (default)
           — claude-sonnet-4-6 (research queries)
    ↓
mhai_skills.py (Julia, file I/O, git, calendar, search, etc.)
```

## Service Management

```bash
hermes gateway status
hermes gateway start
hermes gateway stop
hermes gateway restart
journalctl --user -u hermes-gateway -f   # live logs
~/.hermes/logs/gateway.log               # full log file
```

Mhai2 sends a Telegram message ("☀️ Good morning — I'm up and ready.") automatically ~8s after the gateway starts. Implemented via a companion systemd service:
- Script: `~/.hermes/hooks/notify_startup.sh`
- Service: `~/.config/systemd/user/hermes-gateway-notify.service` (bound to hermes-gateway, auto-starts with it)

## Configuration

- `~/.hermes/config.yaml` — model, provider, auxiliary models, memory limits
- `~/.hermes/.env` — API keys (Anthropic + Telegram only — NO Gemini key)
- `~/.hermes/SOUL.md` — personality, project list, math formatting rules
- `~/.hermes/memories/MEMORY.md` — agent's persistent notes
- `~/.hermes/memories/USER.md` — user profile

**Important:** Never add `GEMINI_API_KEY` to `~/.hermes/.env` — Hermes auto-detects it and switches to Gemini as the default provider, causing quota errors.

## Projects

Each conversation is locked to one project. Projects:

- VRZM26 — Sphere packing / IAS algorithm (includes sphere_packing code)
- XiChen26honors — Xi Chen honours, neural network approximation theory
- GlebPhD — Gleb Shabernev PhD assessment
- MATH8702 — Course materials
- FdHMH — CUR/RandNLA research with Frank de Hoog
- DBT — DBT workbook / Linehan
- Recipes — Recipe collection
- Personal — Weather, calendar, Gmail, general chat

## Skills

Located at `~/.hermes/skills/mhai2/`:

- `julia/` — Run Julia code in FdHMH/CodeMH workdir
- `project-files/` — Read/save/search files with project isolation; PDF generation
- `git-ops/` — Commit, push, restore files in StudentProjects/VRZM26
- `papers/` — arXiv, Semantic Scholar, CrossRef search; bulk download workflow
- `calendar/` — Google Calendar natural language queries
- `gmail/` — Personal Gmail search
- `backup/` — pCloud backup status
- `whiteboard/` — Research whiteboard append/render/save
- `scan-pages/` — Physical document scanning via Canon LiDE 400 (multi-turn workflow)

```bash
hermes skills list   # see all skills
```

## Scanning Physical Documents (scan-pages v4.0.0, rewritten 2026-06-07)

Uses the Canon CanoScan LiDE 400 (`escl:http://localhost:60000`) via `scanimage`.

Multi-turn workflow — each Telegram message triggers one page scan. The flatbed
scans one physical page per call, so pages are scanned individually into `raw/`,
then OCR-combined into ONE markdown file at the end:

```
/scan-pages Scan pages 65 to 73 from the DBT skills training workbook
→ scans first page immediately, saves state

/scan-pages next   ← repeat for each subsequent page
→ on the LAST page, auto-OCRs all pages into one markdown file
```

**Architecture — one `terminal` command per turn (no orchestration):**
All per-turn logic lives in two scripts under `~/.hermes/skills/mhai2/scan-pages/scripts/`:
- `scan.py` — driver. `scan.py start --title "..." --pages 65-73 --output-dir <dir>`
  scans page 1; `scan.py next` scans the next page and, on the last page, runs the
  combine and deletes state. Mhai2 issues exactly one command per turn.
- `combine_to_markdown.py` — OCRs each `raw/*.pdf` into one combined markdown
  (`<slug>_p<first>-p<last>.md`) with `# title` + `## Page N` headers.

State persists in `~/.hermes/scan_state.json` between turns; deleted when complete.

**Output:**
- Per-page PDFs: `~/projects/DBT/scans/raw/dbt_skills_training_workbook_p065.pdf` etc. (kept)
- Combined markdown: `~/projects/DBT/scans/dbt_skills_training_workbook_p065-p073.md`

**OCR engine:** Tesseract only — plain text, fast (seconds per job). Raw per-page
PDFs are kept in `raw/`, so a job can be re-OCR'd later without re-scanning if a
better tool ever becomes practical. (marker-pdf was trialled 2026-06-07 and
rejected: ~1 hour for 9 pages on this CPU-only machine, no usable quality gain
over Tesseract. Don't reach for it again without a GPU.)

Output-dir mapping (in SKILL.md Step A): DBT → `~/projects/DBT/scans`,
VRZM26 → `~/Desktop/VRZM26/scans`, FdHMH → `~/Desktop/FdHMH/scans`, else ask.

**Why the rewrite (root causes of past stalls):**
- v2/v3 made Mhai2 orchestrate 4–5 tool calls per turn (mkdir + write state +
  scanimage + increment). She routed the increment through `execute_code`, which
  HUNG for minutes and stalled the job. v4 collapses each turn to one `scan.py`
  call via `terminal` — no orchestration surface, and SKILL.md forbids `execute_code`.
- v2 stopped at loose per-page PDFs (no combine); she'd then try to `read_file`
  the image PDFs and wrongly call them "empty." v4 always produces the combined
  markdown, and SKILL.md warns never to read raw image PDFs to "check" them.

**Key lessons:**
- Mhai2 ignores skills that conflict with her training ("I can't scan hardware") — always invoke via `/skill-name`, never rely on conversational requests
- After changing a skill, delete `~/.hermes/.skills_prompt_snapshot.json` and restart the gateway
- Restarting the gateway drops the active Telegram session's project lock — re-send the project name (e.g. `DBT`) afterward before continuing
- SOUL.md now has a CRITICAL block overriding the "no hardware access" belief
- `~/projects/agent/` is read-only (`chmod -R a-w`) — original Mhai, never modify

## PDF Generation (learned 2026-05-30)

Standard workflow for meeting prep documents:

```bash
pandoc file.md --pdf-engine=xelatex -o file.pdf
```

YAML front matter for readable notes:

```yaml
---
mainfont: "DejaVu Serif"
linestretch: 1.8
geometry: margin=1.5cm
header-includes:
  - \usepackage{fontspec}
  - \usepackage{amsmath}
  - \usepackage{listings}
  - \setmainfont[Scale=1.5]{DejaVu Serif}
  - \setmonofont[Scale=1.5]{DejaVu Sans Mono}
  - \lstset{basicstyle=\ttfamily\small, breaklines=true, frame=single}
---
```

To include code files (preserves comments, no markdown interpretation):

```
```{=latex}
\newpage
```

## Section Heading

```{=latex}
\lstinputlisting[language={}]{CodeMH/filename.jl}
```
```

Rules:
- Put `\newpage` before the section heading, not inside `\lstinputlisting`
- Use `language={}` to avoid comment misinterpretation
- Unicode math in body text (∈, ℝ, ⁺) works directly with DejaVu
- Inside `$$...$$` use LaTeX: `\widetilde{M}` not `M̃`

## Session Log

### Skill management
Irrelevant bundled skills are archived (not deleted) in:
- `~/.hermes/skills/.archive/` — user-synced skills
- `~/.hermes/hermes-agent/skills/.archive/` — bundled skills

Hermes excludes `.archive` directories automatically (defined in `agent/skill_utils.py` `EXCLUDED_SKILL_DIRS`).
To re-enable a skill, move it back out of `.archive/` and restart the gateway.
Active skills: 61 (down from 104).

### 2026-05-30
- Installed Hermes Agent Framework (`curl ... | bash`)
- Configured with Anthropic API + new Telegram bot
- Fixed Gemini auto-detection issue (removed GEMINI_API_KEY from .env, set provider: anthropic in config.yaml)
- Set all auxiliary models (compression, vision, etc.) to Claude Haiku
- Wrote `mhai_skills.py` — full skill library extracted from Mhai's bot.py
- Created 8 Hermes skills in `~/.hermes/skills/mhai2/`
- Worked on FdHMH meeting prep PDF (`2026-06-01_MEETING_PREP.md`):
  - Fixed font size via YAML front matter + fontspec Scale
  - Fixed Unicode math rendering with DejaVu Serif
  - Embedded Julia and Octave code files via `\lstinputlisting`
  - Added page breaks before each code section
  - Committed and pushed to FdHMH repo (development branch)
- Fixed arxiv Python API (v4 requires `client.results()` not `search.results()`)
- Added 5s rate limiting between arXiv queries to avoid HTTP 429 bans
- Reduced active Hermes skills from 104 to 61 by archiving irrelevant ones
- Installed `pandoc-include` for embedding code files in markdown PDFs
- Tightened context compression (threshold 30%, hard limit 200 messages)
- Set session auto-reset after 60 min idle and at 4am daily
- Added `project_reset.py` pre_gateway_dispatch hook — auto-resets session on project switch
- Diagnosed cost reporting: only output tokens billed ($4.00/M Haiku); cache tokens free on current plan
- Fixed monitoring skill to include cache_read + cache_write tokens in total input count
- Model name corrected to `claude-haiku-4-5` (unversioned) for pricing table match
- config.yaml wiped twice by `sed -i` — switched to Python/Write tool for file edits
- Mhai2 auto-created skills during sessions: fdhh-weekly-meeting-workflow, papers references, project-files references
- Diagnosed cost reporting — DB only captures partial tokens; auxiliary model calls missing
- Read Anthropic console via browser: Haiku cost $14.93 today (47.1M input, 418K output)
- Correct pricing: 72% of input = cache reads at $0.08/M; 28% uncached at $0.80/M
- Effective average input rate ~$0.28/M; output $4.00/M
- Fixed monitoring skill with correct formula: cost = uncached*0.80 + cache_read*0.08 + cache_write*1.00 + output*4.00 (all /1M)
- Never use `sed -i` on config files — wipes them; use Write tool instead

### 2026-05-31
- Added `scan-pages` skill — physical scanning via Canon LiDE 400 using `scanimage`
- Designed as stateful multi-turn workflow: `/scan-pages <desc>` then `/scan-pages next` per page
- State stored in `~/.hermes/scan_state.json`; deleted when job completes
- Made `~/projects/agent/` read-only (`chmod -R a-w`) — original Mhai, reference only
- Added CRITICAL block to SOUL.md overriding Mhai2's "no hardware access" belief
- Learned: Hermes only injects skill name+description into system prompt; full skill loads only on explicit `/skill-name` invocation; conversational requests won't trigger skills that conflict with training
- Tested and confirmed working end-to-end
- **Cost diagnosis:** $9/day driven by 37 sessions × cache-write cost ($1.00/M per session start)
  - Root cause: `project_reset.py` hook firing on false positives ("frank" → FdHMH, "recipe" → Recipes, "backup" → Personal)
  - Fix: rewrote hook to use word-boundary regex; removed overly generic single-word triggers
  - Idle timeout already at 4h (`session_reset.idle_minutes: 240`), daily reset at 4am (`at_hour: 4`)
  - Cache write pricing: $1.00/M (10× more expensive than cache reads at $0.08/M) — minimising session resets is key
- Added startup Telegram notification: Mhai2 sends "☀️ Good morning — I'm up and ready." on every gateway start
- Added per-session cost reporting: `project_reset.py` hook sends a cost summary to Telegram on `/new` or project switch
  - Format: `📊 <session title>\n<msgs> msgs · $<cost> (in <tokens> / out <tokens>)`

### Post-setup session (same day)
- Mhai2 auto-updated gmail skill to use google-workspace OAuth flow
- Mhai2 transcribed DBT audio file locally using Whisper CLI (`~/.local/bin/whisper`)
  - File: `~/projects/DBT/Group 1, Session 7.6.m4a`
  - Runs on CPU, no API cost, no internet needed
- Command approval prompts kept enabled (yolo: false) — working as intended
- Gmail setup: existing Google OAuth client found in `~/.config/gcalendar/default_v1.dat`
  - `setup_gmail.py` written in Mhai2/ but not yet run (browser auth page looked unofficial)
  - Mhai2 google-workspace skill can guide through proper setup interactively
- DBT project added to Mhai2 — audio transcription via Whisper working

### Cost summary (verified via Anthropic console 2026-05-30)
- Total May spend: $38.00 USD ($22.00 credits remaining)
- Haiku (Mhai2) today: $14.93 — heavy setup day (47.1M input, 418K output)
- Remainder ($23.07): Claude Code / Sonnet / Opus sessions this month
- To see Mhai2-only cost: filter by Model = "Claude Haiku 4.5" on Anthropic console Cost page
- Typical non-setup day expected: $1-3/day with compression tightened
- Cache reads (72% of input) billed at $0.08/M — 10x cheaper than uncached

### 2026-06-01
- Updated Hermes framework (121 new commits) — Telegram retry fixes, compression improvements, security patch (CVE-2026-48710)
- Fixed Ctrl+V keybinding in Claude Code — unbound `chat:imagePaste` to stop popup interrupting terminal paste
- Copy/paste conventions:
  - Claude Code TUI: Shift+drag to select, Ctrl+Shift+C to copy, Ctrl+Shift+V to paste
  - Terminal: Ctrl+Shift+C / Ctrl+Shift+V
  - Telegram app (GUI): Ctrl+C / Ctrl+V
- Added "Response Discipline" section to SOUL.md — Mhai2 must not volunteer unsolicited code in a second language or anticipate unrequested follow-up tasks
- Skill audit: cut active skills from 110 → 40 by archiving unused builtins (creative, gaming, media, mlops, github, etc.)
  - Cache write tokens per session expected to drop ~60% (~190K → ~75K), saving ~$0.10–0.12/session
- Token monitoring via `~/.hermes/state.db` — each API call adds ~60K cache read tokens (system prompt re-read)
- Cost reduction strategy: (1) fewer skills = smaller system prompt; (2) lightweight stateless bot for simple queries (future work)
- SOUL.md now tracked in this repo
- Further skill audit: cut 40 → 35 by archiving minecraft, pokemon, jupyter-live-kernel, openhue, xurl
- All CUR test scripts (Julia + Octave) updated to output markdown tables directly — output can be pasted into markdown without conversion
- randnla-algorithm-testing and julia skills updated with markdown table output rule
- Created `cost_report.py` — shows cost, API calls, upload/download, cache R/W per session in AEST
  - Usage: `python3 ~/projects/Mhai2/cost_report.py [days] [--all]`
  - Includes link to Anthropic console (note: console uses US time): https://platform.claude.com/workspaces/default/cost?model=Claude+Haiku+4.5
- Added `/cost-report` skill — Mhai2 runs cost_report.py directly on request
- Updated monitoring skill and MEMORY.md to use cost_report.py instead of directing to console
- FdHMH: fixed CUR_DiagonalMatrix_Test.md — converted raw Octave output to markdown table, added DejaVu font front matter
- FdHMH: created CUR_DiagonalMatrix_Test_Julia.md with Julia results and matching markdown table
- Today's Anthropic cost (2026-06-01): ~$8.23 Haiku (console); cost_report.py undercounts ~2× due to auxiliary calls not in state.db
- Ran out of Anthropic credits mid-afternoon — prompted switch to Gemini

### 2026-06-03 (continued)

#### Google skills consolidation
- Archived custom `calendar` and `gmail` skills (in `~/.hermes/skills/mhai2/.archive/`) — superseded by official `google-workspace` skill
- OAuth already authenticated: `~/.hermes/google_token.json`
- Created `google-workspace-context` skill (`~/.hermes/skills/mhai2/google-workspace-context/`) with Markus-specific defaults:
  - Gmail: markus.hegland@gmail.com (ANU Outlook is NOT integrated)
  - **Mhai Drive folder:** `1uyJNDlqPTQRcCuAHhLK_3fPJXGunJXK8` — default upload target when no folder specified
  - Drive folder URL: https://drive.google.com/drive/folders/1uyJNDlqPTQRcCuAHhLK_3fPJXGunJXK8

#### save-email skill (2026-06-03)

Skill: `~/.hermes/skills/mhai2/save-email/`
Script: `~/.hermes/skills/mhai2/save-email/scripts/gmail_save.py`

Workflow for getting Outlook emails into a project directory (since ANU Outlook is not integrated):

1. Markus says *"I got an email"* → Mhai2 replies *"Use `/save-email` and I'll walk you through it"*
2. Markus sends `/save-email`
3. Mhai2: *"Forward it to markus.hegland@gmail.com with subject **Mhai**, with attachments. Tell me when done."*
4. Markus forwards and confirms
5. Mhai2 runs `gmail_save.py --search "subject:Mhai newer_than:1h" --output-dir <project_dir>`
6. Script saves body (.txt) + attachments to the project directory
7. Mhai2 checks original sender in email body to confirm correct project directory

**Key lessons:**
- Gemini won't auto-load skills from conversational hints — must use explicit `/save-email`
- SOUL.md rule: when Markus says "I got an email", reply "Use `/save-email`" — never ask to paste content
- `gmail get` doesn't download attachments — `gmail_save.py` handles body + attachments via Gmail API directly
- gmail_save.py tested and working: found forwarded email, saved body + `Nystrom_CUR2.m` attachment
- Known limitation: email currently saved to `CodeMH/` regardless of content type. Future improvement: route code files → CodeMH, general correspondence → FdHMH/emails/

#### Send-file-to-collaborator workflow (tested and working 2026-06-03)

Trigger: "send [filename] to Frank" (or any collaborator)

1. Mhai looks in `~/Desktop/FdHMH/CodeMH/` for the file
2. Uploads to GDrive `Mhai/FdHMH/` folder via `google-workspace` skill
3. Replies: "I've saved it to GDrive: [link]. You can attach it to an Outlook email to Frank de Hoog at Frank.DeHoog@csiro.au"

**Key lesson:** SOUL.md prose instructions are unreliable for file operations. Skills need concrete bash commands with full absolute paths — the fdhh skill now has an explicit "Sending Files to Frank" section with copy-paste commands.

Key collaborators added to SOUL.md:
- Frank de Hoog — Frank.DeHoog@csiro.au — CSIRO, FdHMH RandNLA project — via ANU Outlook (manual)

Outlook workflow rule added to SOUL.md: when sending files to collaborators, save to GDrive and tell Markus to attach via Outlook. Never use Gmail for work correspondence.

**Note:** SOUL.md changes only take effect in new sessions — send `/new` on Telegram after any SOUL.md update.

Active Google skills:
- `google-workspace` (Nous Research) — Gmail, Calendar, Drive, Sheets, Docs, Contacts
- `google-workspace-context` (mhai2) — Markus-specific defaults and Drive folder
- `google-workspace-setup` (builtin) — OAuth setup wizard (keep for token re-auth)

Google Drive folder structure:
- `Mhai/` — `1uyJNDlqPTQRcCuAHhLK_3fPJXGunJXK8` — default root
- `Mhai/FdHMH/` — `17YYxlSTVFYb-vZclqAfvyD3IZbpWoKzy` — FdHMH project files

Upload a project file to Drive:
```bash
GAPI="python3 ${HERMES_HOME:-$HOME/.hermes}/hermes-agent/skills/productivity/google-workspace/scripts/google_api.py"
$GAPI drive upload /path/to/file --parent 17YYxlSTVFYb-vZclqAfvyD3IZbpWoKzy  # FdHMH
$GAPI drive upload /path/to/file --parent 1uyJNDlqPTQRcCuAHhLK_3fPJXGunJXK8  # root
```

## Gemini Setup (2026-06-01)

- Installed `@google/gemini-cli` (v0.44.1) via npm
- Authenticated via `hermes auth add google-gemini-cli` (Google One AI Premium OAuth)
- Switched main model + all auxiliary models from `claude-haiku-4-5` to Gemini
- Model trials and outcomes:
  - `gemini-2.5-flash-lite` (OAuth) — hit rate limits constantly (~10 RPM shared quota)
  - `gemini-2.5-flash` (OAuth) — same rate limit pool, still 429s, slow retries
  - `gemini-3-flash-preview` (OAuth) — 404 not found via cloudcode-pa path + tool call compatibility bug
  - `gemini-3.5-flash` (OAuth) — 404 not found via cloudcode-pa path
  - `gemini-2.5-flash-lite` (AI Studio API key) — **working cleanly, 2-6s responses, no rate limits**
- Root cause of OAuth rate limits: Google One AI Premium quota is shared, ~10 RPM, not separate from AI Studio free tier
- Fix: switched provider from `google-gemini-cli` to `gemini` (AI Studio API key from ~/projects/agent/.env)
- GEMINI_API_KEY stored in `~/.hermes/.env` (not committed to repo)
- Current config: `provider: gemini`, `model: gemini-2.5-flash-lite` for main + all auxiliary models
- `task_completion_guidance: false` — disabled "anything else?" follow-up messages
- `api_max_retries: 6` — increased from 3 to handle transient rate limit backoff
- Monitoring: state.db does not record Gemini token counts; use gateway.log for API call tracking

## Hermes Workspace (installed 2026-06-02)

Community-built web UI for Hermes Agent (not official NousResearch). Installed at `~/hermes-workspace/` (v2.3.0).

- **URL:** http://localhost:3000
- **Install location:** `~/hermes-workspace/`
- **GitHub:** https://github.com/outsourc-e/hermes-workspace
- **Env config:** `~/hermes-workspace/.env`
- **Service:** `hermes-workspace.service` (user systemd, bound to hermes-gateway.service)

```bash
systemctl --user start hermes-workspace
systemctl --user stop hermes-workspace
systemctl --user status hermes-workspace
```

Features: chat interface, terminal, memory editor, 2000+ skills library, file browser, Kanban TaskBoard, multi-agent Swarm Mode, Agent View, MCP, Operations dashboard.

**Three services must all be running for the workspace to work fully:**

| Service | Port | Purpose |
|---------|------|---------|
| `hermes-gateway` | — | Core agent + Telegram |
| `hermes-dashboard` | 9119 | Rich API endpoints (`/api/model/info`, analytics, logs, cron) |
| `hermes-workspace` | 3000 | Web UI |

All three are bound to each other — aggressive gateway restarts kill all three. If the workspace shows "Connection error" or "Active Model Offline":

```bash
systemctl --user start hermes-dashboard hermes-workspace
```

**"Active Model Offline"** means `hermes-dashboard` is down (port 9119 not listening). The workspace fetches `/api/model/info` from the dashboard, not from the API server (8642).

**"Cannot read properties of undefined (reading 'map')"** means the workspace can't connect to the Hermes API server. Check `~/hermes-workspace/.env` has `HERMES_API_KEY` matching `API_SERVER_KEY` in `~/.hermes/.env`.

**API key fix (applied 2026-06-03):** added `HERMES_API_KEY=<value>` to `~/hermes-workspace/.env` — the key must match `API_SERVER_KEY` in `~/.hermes/.env`.

**Tailscale access (configured 2026-06-03):**
- URL: `http://100.101.247.30:3000/` (Tailscale IP)
- Password protected — no username, just the password
- Password stored in `~/hermes-workspace/.env` as `HERMES_PASSWORD`
- `HOST=0.0.0.0` set in `~/hermes-workspace/.env` to bind on all interfaces
- `COOKIE_SECURE=0` set in `~/hermes-workspace/.env` — required for HTTP access (Tailscale is plain HTTP, not HTTPS)
- Requires restart after `.env` changes: `systemctl --user restart hermes-workspace`

**Tailscale login loop fix:** `NODE_ENV=production` enables the `Secure` cookie flag by default. Browsers silently drop `Secure` cookies over plain HTTP, so the session is never stored and login immediately re-appears. Fix: `COOKIE_SECURE=0` in `~/hermes-workspace/.env`.

### 2026-06-03

#### Gateway startup failure (root cause + fixes)
- **Root cause:** Mhai2 switching to the `dbt` project during a session set `~/.hermes/active_profile` to `dbt` persistently. On reboot, `hermes_cli/main.py` reads `active_profile` and overrides `HERMES_HOME` to `~/.hermes/profiles/dbt` even when systemd has set `HERMES_HOME=/home/hegland/.hermes`. The dbt profile directory has no `.env`, so `TELEGRAM_BOT_TOKEN` is never loaded → "No messaging platforms enabled."
- **Fix 1:** Reset `active_profile` to `default` (`echo default > ~/.hermes/active_profile`)
- **Fix 2:** systemd drop-in at `~/.config/systemd/user/hermes-gateway.service.d/override.conf` runs `ExecStartPre` to reset `active_profile` to `default` on every gateway start — survives Hermes auto-updates (Hermes only rewrites the main `.service` file, not the `.d/` override directory)
- **HERMES_HOME override behaviour:** if `HERMES_HOME` points to the hermes root (not a profile dir), `main.py` still reads `active_profile` and overrides it. The root is detected as `Path(HERMES_HOME).parent.name != "profiles"`. Setting `HERMES_HOME` to `/home/hegland/.hermes/profiles/default` would bypass this, but the drop-in approach is simpler.

#### Gateway startup resilience (check_platforms.sh)
- Added `~/.hermes/hooks/check_platforms.sh` — runs via `ExecStartPost`, waits 8s, kills gateway if Telegram didn't load (triggers systemd auto-restart)
- Fixed script to use `--since "9 seconds ago"` so it only checks current-run journal entries, not stale entries from previous failed runs
- Drop-in override also re-adds `ExecStartPost` after Hermes auto-updates wipe the main service file
- **Hermes auto-updates the service file:** `refresh_systemd_unit_if_needed()` is called at every gateway startup and rewrites the systemd unit if it has changed — always use the `.d/` drop-in for custom additions

#### Tavily web search + hermes-docs skill
- Added `TAVILY_API_KEY` to `~/.hermes/.env`; set `search_backend: tavily` in config.yaml
- Created `~/.hermes/skills/mhai2/hermes-docs/` skill — tells Mhai2 where to look for Hermes docs and local source
- Key doc URL: `https://hermes-agent.nousresearch.com/docs/llms.txt` (LLM-optimised index); `/docs/llms-full.txt` for full docs
- Note: `/llms.txt` at root returns 404 — correct path is `/docs/llms.txt`
- Mhai2 must use the browser tool to fetch these URLs, not look for local files

#### Web search toolset missing from Telegram sessions
- **Root cause:** `web_search` and `web_extract` tools belong to the `web` toolset, which was not listed under `platform_toolsets.telegram` in config.yaml — so Mhai2 had no web search capability in Telegram sessions despite Tavily being configured
- **Fix:** added `web` to `platform_toolsets.telegram` in config.yaml alongside `hermes-telegram` and `browser`
- Available search backends: tavily (active), brave-free, ddgs, exa, firecrawl, searxng, parallel, xai
- **Rule:** whenever adding a new tool capability, check `platform_toolsets` in config.yaml — tools in unloaded toolsets are silently unavailable

#### SOUL.md: Hermes knowledge rule
- Added CRITICAL section to `~/.hermes/SOUL.md` — Mhai2 must never answer Hermes questions from memory (Gemini has no training data for Hermes)
- Rule: load `/hermes-docs` skill, fetch `https://hermes-agent.nousresearch.com/docs/llms.txt` via browser, then answer from what is read
- Also documented that "Hermes Workspace" is a real community project (hermes-workspace.com) not an official NousResearch product

### 2026-06-09

#### LLM provider outage + migration to free providers
- **Symptom:** every Telegram message failed with "The model provider has rate limited requests."
- **Root cause (NOT a rate limit):** the pay-as-you-go Gemini API key (`provider: gemini`, AI Studio) ran out of prepaid credit → HTTP 429 `RESOURCE_EXHAUSTED: prepayment credits depleted`. Hermes mislabels that 429 as "rate limited" and burns 6 slow retries per message before failing. The Anthropic fallback was also dead (credit balance too low). So every message dead-ended.
- **Fix — switched to free providers (config.yaml):**
  - Main model: `provider: gemini` → `google-gemini-cli`, `model: gemini-2.5-flash` → `gemini-2.5-flash-lite`. Runs free on Markus's Google One AI Premium OAuth (`~/.gemini/oauth_creds.json`), NOT the dead pay-as-you-go key.
  - Added fallback chain: `copilot` / `gpt-5.4-mini` — free via Markus's GitHub **academic** Copilot Pro. Fires only on primary error (rate-limit/5xx/connection). Manage with `hermes fallback list/add/remove`.
  - Auxiliary slots (vision, web_extract, compression, session_search): set to `provider: auto`, `model: ''`. OAuth providers aren't supported for auxiliary ("OAuth provider google-gemini-cli not directly supported, try 'auto'"); and pinning a gemini model name under `auto` would route back to the dead pay-as-you-go key.
- **Copilot model selection:** initially set fallback to `gpt-4o`, but the Telegram `/model` Copilot picker only surfaces the current-gen list (gpt-5.4, gpt-5.5, gpt-5-mini, gpt-5.4-mini). gpt-4o still works via the token but GitHub is phasing it out — switched fallback to `gpt-5.4-mini`. Full token model list: `curl https://api.githubcopilot.com/models -H "Authorization: Bearer $(gh auth token)" -H "Editor-Version: vscode/1.0" -H "Copilot-Integration-Id: vscode-chat"`.
- **Verified:** gpt-5.4-mini generates AND tool-calls correctly (unguessable-secret test passed); DBT coaching responds well via the live gateway.
- **Cost reality:** both paths are $0/token under subscriptions Markus already holds. The per-token "$/M" shown by Telegram `/model` is the upstream list price from Hermes's model DB, not a real charge. "Mini" Copilot models are included/quota-safe; full gpt-5.4/5.5/Claude/Gemini-via-Copilot consume the monthly premium-request allowance — never set one as daily primary. Check usage at github.com/settings/copilot.
- **Quota/throttling:** Gemini OAuth is the bottleneck (~10 RPM shared); bursts overflow automatically to the Copilot mini fallback at no premium cost. Design intent: cheap/fast Gemini answers everything; Copilot mini only catches failures.
- **Rejected fallback:** local Ollama — extremely slow on this CPU-only box (minutes/response); worse than a clean retry.
- **Telegram usage rules:** lock the project FIRST (e.g. send `DBT`), THEN `/model` — switching projects triggers a session reset that wipes the model override. `/model` is session-only unless `--global`; after `/new`, the 4am reset, or a gateway restart it reverts to Gemini primary + Copilot fallback.
- **Confirming which model answered:** `/model` shows the active primary; successful calls don't log the model name, only failures/fallbacks log a WARNING — so `grep -aiE "fallback|429|RESOURCE_EXHAUSTED" ~/.hermes/logs/gateway.log` empty = selected model handled it.

#### The `/model` picker trap → dead key removed from .env
- **Symptom:** during a DBT coaching session, Mhai2 turned assertive/contradictory — it argued with Markus about which workbook pages were "homework," insisting on its own (wrong) guesses ("Not quite", "wrong again"). Looked like "rebellion."
- **Root cause:** at 10:57 Markus picked Gemini from the Telegram `/model` picker — reported as "Provider: Google", ~$0.10/M. That option routes to the **dead API-key `gemini` provider, NOT the OAuth `google-gemini-cli`.** A manual `/model` pick OVERRIDES the config default. So every message 11:12–11:39 hit the dead key → HTTP 429 → **silently fell back to Copilot gpt-5.4-mini**, which generated all the replies. The assertive tone was gpt-5.4-mini's style coming through the fallback, not Gemini and not deliberate defiance. Confirmed in gateway.log: every `agent.conversation_loop` call in that window = `provider=gemini` 429 depleted.
- **Key lesson:** setting the config-default provider does NOT protect against a manual `/model` selection — the picker still offers the dead API-key Gemini. Kill the dead credential at the source.
- **Fix:** removed `GEMINI_API_KEY` from `~/.hermes/.env` (commented out with a dated note). This makes the dead `gemini` provider disappear from the `/model` picker and from `auto`; all Gemini traffic now goes via OAuth only. Backup at `~/.hermes/.env.bak-2026-06-09`; key also recoverable from `~/projects/agent/.env`. Restarted gateway; verified `GEMINI_API_KEY` is no longer in the process environment.
- **Note — Mhai2 self-corrected correctly:** after Markus explained the course structure, Mhai2 saved the right rule to its own memory (`~/.hermes/memories/MEMORY.md`): *"For DBT course homework, the instructor assigns the homework pages and questions; Mhai should not guess page ranges or infer the homework from the workbook."* No bad-memory cleanup needed.
