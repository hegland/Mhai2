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

```bash
hermes skills list   # see all skills
```

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
