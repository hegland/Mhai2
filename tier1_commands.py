#!/usr/bin/env python3
"""
Tier 1 command handler — executes shell commands directly via Telegram
without invoking the LLM. Called from project_reset.py pre_gateway_dispatch hook.

Commands handled:
  /ls [path]            — list directory
  /cat <path>           — show file contents
  /pwd                  — show current project directory
  /run <script>         — run a named script from project dir
  /send <path>          — send file to Telegram
  /plots                — send latest PNG files from current project
  /scan-pages <desc>    — start a scan job
  /scan-pages next      — scan next page
  /scan-pages status    — show scan job status
"""

import json
import os
import re
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

HERMES_HOME  = Path.home() / ".hermes"
STATE_FILE   = HERMES_HOME / "hooks" / ".current_project"
SCAN_STATE   = HERMES_HOME / "scan_state.json"
ENV_FILE     = HERMES_HOME / ".env"

PROJECT_DIRS = {
    "VRZM26":         Path.home() / "Desktop/VRZM26",
    "FdHMH":          Path.home() / "Desktop/FdHMH",
    "XiChen26honors": Path.home() / "Desktop/StudentProjects/XiChen26honors",
    "GlebPhD":        Path.home() / "Desktop/StudentProjects/GlebPhD",
    "MATH8702":       Path.home() / "Desktop/StudentProjects/MATH8702",
    "DBT":            Path.home() / "projects/DBT",
    "Personal":       Path.home(),
    "Recipes":        Path.home(),
}

# Named runnable scripts per project
PROJECT_SCRIPTS = {
    "VRZM26": {
        "stage3":  "julia --project=. research/tasks/cluster_volume/stage3.jl",
        "stage1":  "julia --project=. research/tasks/cluster_volume/stage1.jl",
    },
}


# ============================================================================
# Telegram helpers
# ============================================================================

def _load_env() -> dict:
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


def _telegram_creds() -> tuple[str, str]:
    env = _load_env()
    return env.get("TELEGRAM_BOT_TOKEN", ""), env.get("TELEGRAM_HOME_CHANNEL", "")


def send_text(text: str) -> None:
    token, chat_id = _telegram_creds()
    if not token or not chat_id:
        return
    # Telegram message limit is 4096 chars
    for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
        try:
            data = urllib.parse.urlencode({"chat_id": chat_id, "text": chunk}).encode()
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{token}/sendMessage", data=data)
            urllib.request.urlopen(req, timeout=10)
        except Exception:
            pass


def send_file(path: Path) -> None:
    token, chat_id = _telegram_creds()
    if not token or not chat_id:
        return
    suffix = path.suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".gif"}:
        method = "sendPhoto"
        field  = "photo"
    else:
        method = "sendDocument"
        field  = "document"
    try:
        import mimetypes
        boundary = "----HermesBoundary"
        mime     = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        body  = f"--{boundary}\r\n"
        body += f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'
        body += f"--{boundary}\r\n"
        body += f'Content-Disposition: form-data; name="{field}"; filename="{path.name}"\r\n'
        body += f"Content-Type: {mime}\r\n\r\n"
        body_bytes = body.encode() + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/{method}",
            data=body_bytes,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        urllib.request.urlopen(req, timeout=30)
    except Exception as e:
        send_text(f"Failed to send {path.name}: {e}")


# ============================================================================
# Project helpers
# ============================================================================

def current_project() -> str | None:
    try:
        return STATE_FILE.read_text().strip() or None
    except Exception:
        return None


def current_project_dir() -> Path | None:
    p = current_project()
    return PROJECT_DIRS.get(p) if p else None


def resolve_path(arg: str) -> Path:
    """Resolve a path argument relative to the current project dir."""
    p = Path(arg.replace("~", str(Path.home())))
    if p.is_absolute():
        return p
    project_dir = current_project_dir()
    if project_dir:
        return project_dir / p
    return Path.home() / p


# ============================================================================
# Command handlers
# ============================================================================

def cmd_pwd(args: str) -> None:
    project = current_project()
    project_dir = current_project_dir()
    if project and project_dir:
        send_text(f"Project: {project}\nDirectory: {project_dir}")
    elif project:
        send_text(f"Project: {project} (no directory configured)")
    else:
        send_text("No project set. Name a project to switch to it.")


def cmd_ls(args: str) -> None:
    if args.strip():
        path = resolve_path(args.strip())
    else:
        path = current_project_dir() or Path.home()

    if not path.exists():
        send_text(f"Path not found: {path}")
        return

    try:
        entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
        dirs  = [f"📁 {e.name}/" for e in entries if e.is_dir()]
        files = [f"📄 {e.name}" for e in entries if e.is_file()]
        lines = dirs + files
        send_text(f"{path}\n" + "\n".join(lines) if lines else f"{path}\n(empty)")
    except Exception as e:
        send_text(f"Error listing {path}: {e}")


def cmd_cat(args: str) -> None:
    if not args.strip():
        send_text("Usage: /cat <path>")
        return
    path = resolve_path(args.strip())
    if not path.exists():
        send_text(f"File not found: {path}")
        return
    try:
        content = path.read_text()
        send_text(f"{path.name}:\n\n{content}")
    except Exception as e:
        send_text(f"Error reading {path}: {e}")


def cmd_send(args: str) -> None:
    if not args.strip():
        send_text("Usage: /send <path>")
        return
    path = resolve_path(args.strip())
    if not path.exists():
        send_text(f"File not found: {path}")
        return
    send_text(f"Sending {path.name}...")
    send_file(path)


def cmd_plots(args: str) -> None:
    project_dir = current_project_dir()
    if not project_dir:
        send_text("No project set.")
        return
    pngs = sorted(project_dir.rglob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not pngs:
        send_text(f"No PNG files found in {project_dir}")
        return
    recent = pngs[:5]
    send_text(f"Sending {len(recent)} most recent plots...")
    for png in recent:
        send_file(png)


def cmd_run(args: str) -> None:
    if not args.strip():
        send_text("Usage: /run <script-name>")
        return
    project = current_project()
    project_dir = current_project_dir()
    if not project or not project_dir:
        send_text("No project set.")
        return

    scripts = PROJECT_SCRIPTS.get(project, {})
    script_name = args.strip().lower()

    if script_name in scripts:
        command = scripts[script_name]
    else:
        available = ", ".join(scripts.keys()) if scripts else "none"
        send_text(f"Unknown script '{script_name}' for {project}. Available: {available}")
        return

    send_text(f"Running {script_name}...")
    try:
        result = subprocess.run(
            command, shell=True, cwd=str(project_dir),
            capture_output=True, text=True, timeout=600)
        output = result.stdout + result.stderr
        output = output.strip() or "(no output)"
        send_text(f"✓ {script_name} complete:\n\n{output[:3500]}")
    except subprocess.TimeoutExpired:
        send_text(f"⏱ {script_name} timed out after 10 minutes.")
    except Exception as e:
        send_text(f"Error running {script_name}: {e}")


def _ocr_pdf_to_markdown(pdf_path: Path) -> str:
    """OCR a (possibly multi-page) PDF to markdown text using pdftoppm + tesseract."""
    import tempfile
    md_parts = []
    with tempfile.TemporaryDirectory() as tmp:
        prefix = os.path.join(tmp, "page")
        # Convert each PDF page to a PNG at 300 DPI
        subprocess.run(
            ["pdftoppm", "-r", "300", "-png", str(pdf_path), prefix],
            capture_output=True, timeout=120)
        pngs = sorted(Path(tmp).glob("page*.png"))
        for i, png in enumerate(pngs, 1):
            result = subprocess.run(
                ["tesseract", str(png), "stdout"],
                capture_output=True, text=True, timeout=120)
            text = result.stdout.strip()
            # Light cleanup: normalise smart quotes and common artefacts
            text = (text.replace("“", '"').replace("”", '"')
                        .replace("‘", "'").replace("’", "'")
                        .replace("—", "--"))
            if len(pngs) > 1:
                md_parts.append(f"## Page {i}\n\n{text}")
            else:
                md_parts.append(text)
    return "\n\n---\n\n".join(md_parts)


def cmd_ocr(args: str) -> None:
    """OCR scanned PDF(s) to markdown. Tier 1 — local tesseract, no LLM.

    !ocr <file.pdf>  — OCR one PDF
    !ocr             — OCR all PDFs in the current project's scans/ dir lacking a .md
    """
    targets = []
    if args.strip():
        p = resolve_path(args.strip())
        if not p.exists():
            send_text(f"File not found: {p}")
            return
        targets = [p]
    else:
        project_dir = current_project_dir()
        if not project_dir:
            send_text("No project set. Use: !ocr <path-to-pdf>")
            return
        scans_dir = project_dir / "scans"
        if not scans_dir.exists():
            send_text(f"No scans directory in {project_dir}")
            return
        # all PDFs without a matching .md
        targets = [p for p in sorted(scans_dir.glob("*.pdf"))
                   if not p.with_suffix(".md").exists()]
        if not targets:
            send_text(f"No un-OCR'd PDFs in {scans_dir}")
            return

    send_text(f"OCR'ing {len(targets)} PDF(s) with tesseract (no LLM)...")
    for pdf in targets:
        try:
            md = _ocr_pdf_to_markdown(pdf)
            md_path = pdf.with_suffix(".md")
            md_path.write_text(f"# {pdf.stem}\n\n{md}\n")
            send_text(f"✓ {pdf.name} → {md_path.name} ({len(md)} chars)")
        except subprocess.TimeoutExpired:
            send_text(f"⏱ OCR timed out on {pdf.name}")
        except Exception as e:
            send_text(f"Error OCR'ing {pdf.name}: {e}")


def cmd_member_status(args: str) -> None:
    """Check ACT Swiss Club membership status. Searches membership CSV.

    !member-status           — check your own status
    !member-status <name>    — check someone else's status
    """
    import csv
    from datetime import datetime

    # Find membership CSV in ACT-Swiss-Club
    membership_csv = Path.home() / "projects" / "ACT-Swiss-Club" / "data" / "MASTER - Canberra Swiss Club Membership - CURRENT.csv"
    if not membership_csv.exists():
        send_text(f"Membership file not found: {membership_csv}")
        return

    # If no args, search for Markus Hegland
    search_term = args.strip() if args.strip() else "Markus"

    try:
        with open(membership_csv, newline='', encoding='utf-8-sig') as f:
            # Skip metadata rows (first 3 lines) — header is on line 4
            for _ in range(3):
                f.readline()
            reader = csv.DictReader(f)
            found = False
            for row in reader:
                surname = row.get('Surname', '').strip()
                name = row.get('Name', '').strip()
                full_name_fwd = f"{surname} {name}".strip()   # Hegland Markus
                full_name_rev = f"{name} {surname}".strip()   # Markus Hegland

                # Match: search term in surname, name, or either full name order
                search_lower = search_term.lower()
                if (search_lower == surname.lower() or
                    search_lower == name.lower() or
                    search_lower in full_name_fwd.lower() or
                    search_lower in full_name_rev.lower()):
                    found = True
                    mem_year = row.get('MemYear', '?').strip()
                    mem_type = row.get('Membership Type', '?').strip()
                    class_mem = row.get('Class of Membership', '?').strip()
                    send_to = row.get('Send updates and Newsletters to - those marked with an option have up todate memberships.', '?').strip()
                    date_joined = row.get('Date Joined', '').strip()
                    date_ended = row.get('Date Ended', '').strip()
                    email = row.get('Email', '').strip()

                    # Determine financial status
                    current_year = datetime.now().year
                    is_financial = mem_year in (str(current_year), str(current_year - 1)) and send_to
                    status_emoji = "✓" if is_financial else "✗"

                    msg = f"{status_emoji} **{full_name_fwd}**\n"
                    msg += f"Membership year: {mem_year}\n"
                    msg += f"Type: {mem_type}\n"
                    msg += f"Class: {class_mem}\n"
                    msg += f"Status: {'✓ Current/Paid' if is_financial else '✗ Not current'}\n"
                    if date_joined:
                        msg += f"Joined: {date_joined}\n"
                    if date_ended:
                        msg += f"Ended: {date_ended}\n"
                    if email:
                        msg += f"Email: {email}"

                    send_text(msg)
                    return

            if not found:
                send_text(f"Not found in membership list: {search_term}")

    except Exception as e:
        send_text(f"Error reading membership file: {e}")


def cmd_scan_pages(args: str) -> None:
    args = args.strip()

    if args.lower() == "next":
        _scan_next()
    elif args.lower() == "status":
        _scan_status()
    elif args.lower() in {"", "stop", "cancel"}:
        if SCAN_STATE.exists():
            SCAN_STATE.unlink()
            send_text("Scan job cancelled.")
        else:
            send_text("No scan job in progress.")
    else:
        _scan_start(args)


def _scan_start(description: str) -> None:
    # Parse page range: "pages 55 to 64" or "page 55"
    range_match  = re.search(r"pages?\s+(\d+)\s+to\s+(\d+)", description, re.IGNORECASE)
    single_match = re.search(r"pages?\s+(\d+)", description, re.IGNORECASE)
    if range_match:
        start, end = int(range_match.group(1)), int(range_match.group(2))
        pages = list(range(start, end + 1))
    elif single_match:
        pages = [int(single_match.group(1))]
    else:
        pages = [1]
        send_text("No page number found — scanning page 1. Use 'page N' or 'pages N to M'.")

    # Determine output dir from description
    desc_lower = description.lower()
    if "dbt" in desc_lower:
        output_dir = Path.home() / "projects/DBT/scans"
        doc_slug = "dbt_workbook"
    elif "vrzm" in desc_lower or "sphere" in desc_lower:
        output_dir = Path.home() / "Desktop/VRZM26/scans"
        doc_slug = "vrzm26_scan"
    else:
        project_dir = current_project_dir() or Path.home()
        output_dir = project_dir / "scans"
        doc_slug = re.sub(r"[^a-z0-9]+", "_", desc_lower)[:30].strip("_")

    output_dir.mkdir(parents=True, exist_ok=True)

    state = {
        "description": description,
        "doc_slug": doc_slug,
        "output_dir": str(output_dir),
        "pages": pages,
        "next_index": 0,
    }
    SCAN_STATE.write_text(json.dumps(state, indent=2))

    # Scan first page immediately
    _do_scan(state)


def _scan_next() -> None:
    if not SCAN_STATE.exists():
        send_text("No scan job in progress. Start one with /scan-pages <description>")
        return
    state = json.loads(SCAN_STATE.read_text())
    _do_scan(state)


def _do_scan(state: dict) -> None:
    pages     = state["pages"]
    idx       = state["next_index"]
    doc_slug  = state["doc_slug"]
    output_dir = Path(state["output_dir"])

    if idx >= len(pages):
        SCAN_STATE.unlink(missing_ok=True)
        send_text("All pages already scanned.")
        return

    page_num  = pages[idx]
    out_path  = output_dir / f"{doc_slug}_p{page_num:03d}.pdf"

    send_text(f"Scanning page {page_num}...")
    try:
        result = subprocess.run(
            ["scanimage",
             "--device-name", "escl:http://localhost:60000",
             "--format=pdf", "--mode", "Color", "--resolution", "300",
             "-o", str(out_path)],
            capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            send_text(f"Scan failed:\n{result.stderr}")
            return
    except FileNotFoundError:
        send_text("scanimage not found — is the scanner connected?")
        return
    except subprocess.TimeoutExpired:
        send_text("Scan timed out after 60s.")
        return
    except Exception as e:
        send_text(f"Scan error: {e}")
        return

    # Update state
    state["next_index"] = idx + 1
    SCAN_STATE.write_text(json.dumps(state, indent=2))

    remaining = len(pages) - (idx + 1)
    if remaining > 0:
        next_page = pages[idx + 1]
        send_text(
            f"✓ Page {page_num} scanned → {out_path.name}\n"
            f"Place page {next_page} on the scanner, then send: /scan-pages next\n"
            f"({remaining} pages remaining)")
    else:
        SCAN_STATE.unlink(missing_ok=True)
        send_text(f"✓ Page {page_num} scanned → {out_path.name}\n✓ All pages done! Saved to {output_dir}")


def _scan_status() -> None:
    if not SCAN_STATE.exists():
        send_text("No scan job in progress.")
        return
    state = json.loads(SCAN_STATE.read_text())
    idx   = state["next_index"]
    pages = state["pages"]
    done  = pages[:idx]
    remaining = pages[idx:]
    send_text(
        f"Scan job: {state['description']}\n"
        f"Done: {done}\n"
        f"Remaining: {remaining}\n"
        f"Output: {state['output_dir']}")


# ============================================================================
# Main dispatcher
# ============================================================================

TIER1_COMMANDS = {
    "pwd":           cmd_pwd,
    "ls":            cmd_ls,
    "cat":           cmd_cat,
    "send":          cmd_send,
    "plots":         cmd_plots,
    "run":           cmd_run,
    "sc":            cmd_scan_pages,      # !sc — scan pages
    "ocr":           cmd_ocr,             # !ocr — OCR scanned PDFs to markdown (tesseract, no LLM)
    "member-status": cmd_member_status,   # !member-status — check ACT Swiss Club membership status
}


def handle(text: str) -> bool:
    """
    Try to handle text as a Tier 1 command.
    Returns True if handled (caller should return skip), False otherwise.

    Uses '!' prefix to avoid Hermes slash-command interception.
    Examples: !ls, !pwd, !cat path/to/file, !sc pages 1 to 3

    Long-running commands (scan) run in a background thread so the hook
    returns skip immediately before the gateway timeout fires.
    """
    text = text.strip()
    if not text.startswith("!"):
        return False

    parts = text[1:].split(None, 1)
    cmd   = parts[0].lower()
    args  = parts[1] if len(parts) > 1 else ""

    if cmd not in TIER1_COMMANDS:
        return False

    # Long-running commands: spawn detached subprocess, return skip immediately
    LONG_RUNNING = {"sc", "run", "ocr"}
    if cmd in LONG_RUNNING:
        script = (
            f"import sys; sys.path.insert(0,'/home/hegland/.hermes/hooks'); "
            f"from tier1_commands import TIER1_COMMANDS; "
            f"TIER1_COMMANDS[{cmd!r}]({args!r})"
        )
        subprocess.Popen(
            ["python3", "-c", script],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        TIER1_COMMANDS[cmd](args)

    return True
