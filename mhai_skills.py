"""
mhai_skills.py — Portable skill library for Mhai2.

All skill functions (file I/O, Julia, git, calendar, search, etc.) extracted
from Mhai's bot.py. Both Mhai2's bot and any future tooling import from here.
Mhai (agent/) is NOT modified.

Error handling: functions raise exceptions; callers decide how to surface them.
"""

import os
import re
import json
import logging
import tempfile
import subprocess
import base64
import urllib.request
import urllib.parse
import ssl
from pathlib import Path
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration / constants
# ---------------------------------------------------------------------------

KNOWLEDGE_DIR = Path(os.environ.get("KNOWLEDGE_DIR", "/home/hegland/.openclaw/workspace/knowledge"))
TRANSCRIPT_DIR = Path(os.environ.get("TRANSCRIPT_DIR", "/home/hegland/Desktop/FdHMH/transcripts"))
WHITEBOARD_FILE = Path(os.environ.get("WHITEBOARD_FILE", "/home/hegland/projects/Mhai2/whiteboard.md"))
XICHEN_DIR = Path(os.environ.get("XICHEN_DIR", "/home/hegland/projects/XiChen26Hnrs"))

JULIA_TIMEOUT = int(os.environ.get("JULIA_TIMEOUT", "120"))
JULIA_WORKDIR = os.environ.get("JULIA_WORKDIR", "/home/hegland/Desktop/FdHMH/CodeMH")

PCLOUD_BACKUP_DIR = Path(os.environ.get("PCLOUD_BACKUP_DIR", "/home/hegland/pCloudDrive/pCloud Backup/homepc"))
HOMEPC_SOURCE = Path(os.environ.get("HOMEPC_SOURCE", "/home/hegland"))
BACKUP_FOLDERS = ["Desktop", "Documents", "Downloads", "Music", "Pictures", "Videos", "Zotero"]

STUDENT_PROJECTS_DIR = Path.home() / "Desktop" / "StudentProjects"
VRZM26_DIR = Path(os.environ.get("VRZM26_DIR", str(Path.home() / "Desktop" / "VRZM26")))
SPHERE_PACKING_DIR = Path(os.environ.get("SPHERE_PACKING_DIR", str(Path.home() / "projects" / "sphere_packing")))
PROJECT_DIRS = [STUDENT_PROJECTS_DIR, VRZM26_DIR, SPHERE_PACKING_DIR]

ALLOWED_SAVE_DIRS = [Path.home() / "Desktop", Path.home() / "Documents"]

GMAIL_TOKEN = Path(os.environ.get("GMAIL_TOKEN", "/home/hegland/.config/mhai/gmail_token.json"))
CALENDAR_TOKEN = Path(os.environ.get("CALENDAR_TOKEN", "/home/hegland/.config/gcalendar/default_v1.dat"))
CALENDAR_IDS = {
    "primary": "markus.hegland@gmail.com",
    "work": "a83e82112b14c229e8cabcf9c0fc589e3320064c066ccbfd0d735596cba568e9@group.calendar.google.com",
    "family": "family08752193323172971998@group.calendar.google.com",
}
CALENDAR_PEOPLE = {
    "xi chen": ["xi chen", "xi"],
    "frank": ["frank", "de hoog", "dehoog"],
    "gleb": ["gleb"],
    "zbigniew": ["zbigniew"],
    "boris": ["boris"],
    "steve": ["steve"],
    "conrad": ["conrad"],
}

CANBERRA_TZ = ZoneInfo("Australia/Sydney")

ANU_EZPROXY_COOKIE = os.environ.get("ANU_EZPROXY_COOKIE", "")
ANU_EZPROXY_HOST = "virtual.anu.edu.au"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

_LAST_SAVED_MD_FILE = Path.home() / ".config" / "mhai2" / "last_saved_md.txt"

EXT_GROUPS = {
    "pdf":        [".pdf"],
    "image":      [".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp"],
    "manuscript": [".md", ".tex", ".docx", ".odt", ".txt"],
    "code":       [".jl", ".py", ".m", ".r", ".ipynb"],
    "data":       [".csv", ".tsv", ".dat", ".npy", ".npz", ".mat", ".h5", ".json"],
    "output":     [".png", ".svg", ".pdf", ".csv", ".txt"],
}
_OUTPUT_EXTS = {".png", ".svg", ".pdf"}
_SKIP_DIRS = {"src", "test", "archive", "legacy", "lib", ".git", "node_modules", "sandbox", "dev"}

EMAILS_DIR = KNOWLEDGE_DIR / "emails"
CHAT_LOG_DIR = STUDENT_PROJECTS_DIR / "chat_logs"

# ---------------------------------------------------------------------------
# Project registry
# ---------------------------------------------------------------------------

PROJECTS = {
    "VRZM26": {
        "path": VRZM26_DIR,
        "desc": "Sphere packing / IAS algorithm — research with Zbigniew Stachurski",
        "knowledge": "research/sphere_packing.md",
        "extra_paths": [SPHERE_PACKING_DIR],  # sphere_packing code merged into VRZM26
    },
    "XiChen26honors": {
        "path": STUDENT_PROJECTS_DIR / "XiChen26honors",
        "desc": "Xi Chen honours project — neural network approximation theory",
        "knowledge": None,
        "extra_paths": [],
    },
    "GlebPhD": {
        "path": STUDENT_PROJECTS_DIR / "GlebPhD",
        "desc": "Gleb Shabernev PhD thesis assessment",
        "knowledge": None,
        "extra_paths": [],
    },
    "MATH8702": {
        "path": STUDENT_PROJECTS_DIR / "MATH8702",
        "desc": "MATH8702 course — machine learning foundations",
        "knowledge": None,
        "extra_paths": [],
    },
    "FdHMH": {
        "path": None,
        "desc": "CUR/RandNLA research with Frank de Hoog (CSIRO)",
        "knowledge": "research/fdhmh.md",
        "extra_paths": [],
    },
    "DBT": {
        "path": None,
        "desc": "DBT workbook / Linehan — personal wellbeing",
        "knowledge": "dbt/radical-acceptance.md",
        "extra_paths": [],
    },
    "Recipes": {
        "path": None,
        "desc": "Recipe collection",
        "knowledge": "recipes/airfryer.md",
        "extra_paths": [],
    },
    "Personal": {
        "path": None,
        "desc": "General personal chat — weather, calendar, Gmail",
        "knowledge": None,
        "extra_paths": [],
    },
}

KNOWLEDGE_KEYWORDS = {
    "dbt/radical-acceptance.md": [
        "dbt", "radical acceptance", "linehan", "distress tolerance", "worksheet 9", "handout 11",
        "point 1", "point 2", "point 3", "point 4", "point 5", "point 6",
        "accepting", "acceptance", "non-acceptance", "turning the mind",
        "willingness", "willfulness", "half-smile", "willing hands",
    ],
    "recipes/airfryer.md": ["airfryer", "air fryer", "air-fryer"],
    "research/fdhmh.md": [
        "cur", "frank", "fdh", "hoog", "randnla", "srht", "hadamard", "manuscript",
        "compound matrix", "volume sampling", "randomized", "sketch", "decomposition",
        "nystrom", "nyström", "incoherence", "mu_k", "r_eff", "effective rank",
        "compound incoherence", "mad", "median", "concentration",
    ],
    "research/transcript_2026-05-11.txt": [
        "may 11", "11 may", "last week", "previous meeting",
        "hadamard inside", "transform inside", "algorithm steps",
    ],
    "research/transcript_2026-05-18.txt": [
        "may 18", "18 may", "last meeting", "most recent meeting",
        "action items", "frank agreed", "two-line",
        "incoherent matrix", "csiro fellowship",
    ],
    "xichen:CLAUDE.md": [
        "xi chen", "xichen", "honours", "honours project", "pinn", "physics-informed",
        "fem", "finite element", "xi chen meeting", "xi chen feedback",
        "barron", "devore", "approximation theory", "sobolev", "besov",
        "neural network approximation", "model class", "approximation class",
        "kalman", "data assimilation", "ridge function", "vc dimension",
    ],
    "xichen:barron_shallow_networks.md": ["barron", "barron space", "barron norm", "monte carlo", "shallow network", "dimension-free"],
    "xichen:relu_upper_bound.md": ["relu", "relu upper bound", "relu approximation"],
    "xichen:abstract_approximation_framework.md": ["abstract approximation", "approximation framework", "jackson", "bernstein inequality"],
    "xichen:devore_hanin_section3.md": ["devore hanin", "section 3", "parallel network", "sequential network", "concatenated network"],
    "xichen:feedback_notes_30apr2026.md": ["feedback", "xi chen feedback", "april feedback", "model class feedback", "theorem 7"],
    "xichen:devore_hanin_2021.txt": [
        "devore hanin", "neural network approximation", "acta numerica 2021",
        "devore 2021", "hanin petrova", "theorem 7.4", "theorem 7.2",
        "section 7", "section 4", "section 5", "section 6",
        "free-knot spline", "besov space", "approximation rate",
    ],
    "xichen:devore_1998_nonlinear.txt": [
        "devore 1998", "nonlinear approximation", "acta numerica 1998",
        "devore nonlinear", "nonlinear approximation theory",
        "jackson inequality", "bernstein inequality", "wavelet",
    ],
    "research/sphere_packing.md": [
        "sphere packing", "sphere_packing", "vrzm", "ias algorithm",
        "amorphous", "cannonball", "hexagonal", "triangular lattice",
        "packing density", "packing ratio", "triplet site", "jitter",
        "crystalline", "fcc", "hcp", "zbigniew", "stachurski",
        "amorphous solid", "molecular dynamics",
    ],
    "research/sphere_packing_report_analysis.md": [
        "sphere packing report", "packing report",
        "317", "367", "layer 1", "layer 2", "layer 3",
        "jitter 0.02", "jitter 0.05", "section 4", "section 6", "section 7", "section 8",
    ],
}

LITERATURE_PDFS = {
    "xichen:devore_hanin_2021.txt": Path("/home/hegland/Desktop/StudentProjects/XiChen26honors/Literature/DeVore.pdf"),
    "xichen:devore_1998_nonlinear.txt": Path("/home/hegland/Desktop/StudentProjects/XiChen26honors/Literature/DeVore1998_NonlinearApproximation.pdf"),
}

RESEARCH_KEYWORDS = [
    "arxiv", "paper", "literature", "search", "find", "reference",
    "cur", "matrix", "decomposition", "srht", "hadamard", "compound",
    "randomized", "randnla", "sketch", "sampling", "volume sampling",
    "conjecture", "proof", "theorem", "lemma", "bound", "convergence",
    "frank", "fdh", "transcript", "meeting", "zoom",
    "minres", "galerkin", "coercive", "condition number", "oversampling",
    "manuscript", "paper", "draft", "research", "maths", "math",
    "julia", "experiment", "eigenvalue", "incoherence", "diagonal",
    "compound", "effective rank", "r_eff", "mu_k", "determinant",
    "nystrom", "nyström", "concentration", "mad", "volume", "uniform sampling",
    "xi chen", "xichen", "honours", "pinn", "physics-informed", "fem", "finite element",
    "neural network", "approximation", "sobolev", "besov", "barron", "devore",
    "relu", "universal approximation", "pde", "laplace", "kalman", "ridge function",
    "vc dimension", "approximation class", "model class",
    "sphere packing", "sphere_packing", "vrzm", "ias algorithm", "amorphous",
    "cannonball", "hexagonal", "triangular lattice", "packing density", "packing ratio",
    "triplet site", "jitter", "disorder", "crystalline", "fcc", "hcp",
    "zbigniew", "stachurski",
]

# ---------------------------------------------------------------------------
# Query classification
# ---------------------------------------------------------------------------

def is_research_query(text: str) -> bool:
    return any(kw in text.lower() for kw in RESEARCH_KEYWORDS)


def detect_project(text: str) -> str | None:
    """Return the project name most strongly signalled by text, or None."""
    t = text.lower()
    project_signals = {
        "VRZM26":         ["vrzm", "zbigniew", "stachurski", "ias", "amorphous", "sphere pack",
                           "sphere_packing", "ideal amorphous", "cannonball", "packing density"],
        "XiChen26honors": ["xi chen", "xichen", "honours", "pinn", "barron", "devore",
                           "relu approximation", "neural network approximation"],
        "GlebPhD":        ["gleb", "shabernev", "thesis", "phd thesis"],
        "MATH8702":       ["math8702", "math 8702", "8702"],
        "FdHMH":          ["frank", "de hoog", "fdh", "cur decomposition", "randnla", "srht",
                           "cur matrix", "compound matrix"],
        "DBT":            ["dbt", "radical acceptance", "linehan", "distress tolerance",
                           "willingness", "willfulness", "half-smile"],
        "Recipes":        ["recipe", "airfryer", "air fryer", "cooking", "bake", "roast"],
        "Personal":       ["weather", "calendar", "schedule", "email", "gmail"],
    }
    scores = {p: sum(1 for s in sigs if s in t) for p, sigs in project_signals.items()}
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else None


# ---------------------------------------------------------------------------
# Knowledge base
# ---------------------------------------------------------------------------

def load_relevant_knowledge(text: str) -> tuple[str, list[Path]]:
    """Return (text snippets joined, list of PDF paths to attach)."""
    text_lower = text.lower()
    snippets = []
    pdf_paths = []
    for key, keywords in KNOWLEDGE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            if key in LITERATURE_PDFS:
                pdf_path = LITERATURE_PDFS[key]
                if pdf_path.exists():
                    pdf_paths.append(pdf_path)
                continue
            path = (XICHEN_DIR / key[len("xichen:"):]) if key.startswith("xichen:") else (KNOWLEDGE_DIR / key)
            if path.exists():
                snippets.append(f"--- {key} ---\n{path.read_text()}")
    return "\n\n".join(snippets), pdf_paths


# ---------------------------------------------------------------------------
# Directory tree helpers
# ---------------------------------------------------------------------------

_STUDENT_PROJECTS_TREE_CACHE: str = ""
_VRZM26_TREE_CACHE: str = ""


def _build_tree(root: Path) -> str:
    if not root.exists():
        return ""
    lines = [f"{root.name}/"]
    for child in sorted(root.iterdir()):
        if child.name.startswith("."):
            continue
        if child.is_dir():
            lines.append(f"  {child.name}/")
            for grandchild in sorted(child.iterdir()):
                if grandchild.name.startswith("."):
                    continue
                if grandchild.is_dir():
                    lines.append(f"    {grandchild.name}/")
                    for ggchild in sorted(grandchild.iterdir()):
                        if not ggchild.name.startswith("."):
                            lines.append(f"      {ggchild.name}")
                else:
                    lines.append(f"    {grandchild.name}")
        else:
            lines.append(f"  {child.name}")
    return "\n".join(lines)


def get_student_projects_tree() -> str:
    global _STUDENT_PROJECTS_TREE_CACHE
    if not _STUDENT_PROJECTS_TREE_CACHE:
        _STUDENT_PROJECTS_TREE_CACHE = _build_tree(STUDENT_PROJECTS_DIR)
    return _STUDENT_PROJECTS_TREE_CACHE


def get_vrzm26_tree() -> str:
    global _VRZM26_TREE_CACHE
    if not _VRZM26_TREE_CACHE:
        _VRZM26_TREE_CACHE = _build_tree(VRZM26_DIR)
    return _VRZM26_TREE_CACHE


def get_sphere_packing_tree() -> str:
    return _build_tree(SPHERE_PACKING_DIR)


def get_julia_context(repo: Path) -> str:
    """Compact summary of Julia scripts and co-located outputs grouped by task directory."""
    if not repo.exists():
        return ""
    groups: dict[Path, dict] = {}
    for jl in sorted(repo.rglob("*.jl")):
        if set(jl.relative_to(repo).parts[:-1]) & _SKIP_DIRS:
            continue
        d = jl.parent
        if d not in groups:
            groups[d] = {"scripts": [], "outputs": []}
        groups[d]["scripts"].append(jl.name)
    for d, v in groups.items():
        for f in sorted(d.iterdir()):
            if f.suffix.lower() in _OUTPUT_EXTS and f.is_file():
                v["outputs"].append(f.name)
    if not groups:
        return ""
    lines = ["Julia scripts and outputs by task directory:"]
    for d in sorted(groups):
        rel = d.relative_to(repo)
        v = groups[d]
        lines.append(f"  {rel}/\n    scripts: {', '.join(v['scripts'])}\n    outputs: {', '.join(v['outputs']) or '—'}")
    return "\n".join(lines)


def projects_summary() -> str:
    lines = ["*Markus's active projects:*\n"]
    for name, info in PROJECTS.items():
        p = info["path"]
        exists = p is None or p.exists()
        status = "" if exists else " _(path not found)_"
        lines.append(f"*{name}*{status}\n  {info['desc']}")
        if p and p.exists():
            try:
                n = sum(1 for _ in p.rglob("*") if _.is_file() and not _.name.startswith("."))
                lines[-1] += f"\n  {n} files in {p}"
            except Exception:
                pass
    lines.append("\nUse /new between projects to keep conversations focused.")
    return "\n\n".join(lines)


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------

def _repo_for_path(target: Path) -> Path | None:
    for d in PROJECT_DIRS:
        if str(target).startswith(str(d.resolve())):
            return d
    return None


def _load_last_saved_md() -> str:
    if _LAST_SAVED_MD_FILE.exists():
        p = _LAST_SAVED_MD_FILE.read_text().strip()
        return p if Path(p).exists() else ""
    return ""


def _store_last_saved_md(path: str):
    _LAST_SAVED_MD_FILE.parent.mkdir(parents=True, exist_ok=True)
    _LAST_SAVED_MD_FILE.write_text(path)


def read_project_file(path: str) -> str:
    """Read a file or list a directory under any project directory."""
    target = Path(path).expanduser()
    if not target.is_absolute():
        rel = str(target)
        for prefix, repo_dir in [
            ("StudentProjects/", STUDENT_PROJECTS_DIR),
            ("VRZM26/", VRZM26_DIR),
            ("sphere_packing/", SPHERE_PACKING_DIR),
        ]:
            if rel.startswith(prefix):
                target = repo_dir / rel[len(prefix):]
                break
        else:
            found = False
            for repo_dir in PROJECT_DIRS:
                candidate = repo_dir / rel
                if candidate.exists():
                    target = candidate
                    found = True
                    break
            if not found:
                target = STUDENT_PROJECTS_DIR / rel
    target = target.resolve()
    if not _repo_for_path(target):
        safe_to_rglob = target.name not in ("CLAUDE.md", "README.md", "Project.toml", "Manifest.toml")
        if safe_to_rglob:
            for repo_dir in PROJECT_DIRS:
                matches = list(repo_dir.rglob(target.name))
                if matches:
                    target = matches[0]
                    break
            else:
                return f"Refused: {path} is outside project directories."
        else:
            return f"File not found: {path} — please use a full path like 'sphere_packing/CLAUDE.md'"
    if not target.exists():
        normalized = target.name.replace("’", "'").replace("‘", "'")
        candidate = target.parent / normalized
        if candidate.exists():
            target = candidate
        else:
            repo_dir = _repo_for_path(target) or STUDENT_PROJECTS_DIR
            matches = list(repo_dir.rglob(target.name))
            if matches:
                target = matches[0]
            else:
                return f"File not found: {target}"
    try:
        if target.is_dir():
            entries = sorted(target.iterdir())
            lines = [f"{target.name}/"]
            for e in entries:
                if e.name.startswith("."):
                    continue
                lines.append(f"  {'  ' if e.is_dir() else ''}{e.name}{'/' if e.is_dir() else ''}")
            return "\n".join(lines)
        if target.suffix.lower() == ".pdf":
            result = subprocess.run(["pdftotext", str(target), "-"],
                                    capture_output=True, text=True, timeout=30)
            return result.stdout.strip() if result.returncode == 0 else f"pdftotext error: {result.stderr.strip()}"
        text = target.read_text(errors="replace")
        if len(text) > 8000:
            text = text[:8000] + "\n...(truncated)"
        return text
    except Exception as e:
        return f"Read error: {e}"


def save_file_tool(path: str, content: str) -> str:
    """Save content to path under an allowed directory; auto-commit if in a project repo."""
    target = Path(path).expanduser().resolve()
    if not any(str(target).startswith(str(d.resolve())) for d in ALLOWED_SAVE_DIRS):
        return f"Refused: {path} is outside allowed directories (~/Desktop, ~/Documents)."
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    if target.suffix == ".md":
        _store_last_saved_md(str(target))
    repo_dir = _repo_for_path(target)
    if repo_dir:
        try:
            subprocess.run(["git", "-C", str(repo_dir), "add", str(target)], capture_output=True)
            subprocess.run(["git", "-C", str(repo_dir), "commit", "-m", f"Auto-save {target.name}"],
                           capture_output=True)
            log.info("Auto-committed: %s", target.name)
        except Exception as e:
            log.warning("Auto-commit failed: %s", e)
    return str(target)


def append_file_tool(path: str, content: str) -> str:
    """Append content to a file (or create it); auto-commit if in StudentProjects."""
    target = Path(path).expanduser().resolve()
    if not any(str(target).startswith(str(d.resolve())) for d in ALLOWED_SAVE_DIRS):
        return f"Refused: {path} is outside allowed directories (~/Desktop, ~/Documents)."
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "a") as f:
        f.write(("\n" if target.exists() and target.stat().st_size > 0 else "") + content)
    if target.suffix == ".md":
        _store_last_saved_md(str(target))
    if str(target).startswith(str(STUDENT_PROJECTS_DIR.resolve())):
        try:
            subprocess.run(["git", "-C", str(STUDENT_PROJECTS_DIR), "add", str(target)], capture_output=True)
            subprocess.run(["git", "-C", str(STUDENT_PROJECTS_DIR), "commit", "-m", f"Auto-append {target.name}"],
                           capture_output=True)
        except Exception as e:
            log.warning("Auto-commit failed: %s", e)
    return str(target)


def convert_to_pdf(md_path: str) -> str:
    """Run pandoc to convert a markdown file to PDF. Returns PDF path or error string."""
    src = Path(md_path).expanduser().resolve()
    if not src.exists():
        return f"File not found: {src}"
    pdf = src.with_suffix(".pdf")
    try:
        subprocess.run(
            ["pandoc", str(src), "--pdf-engine=xelatex",
             "-V", "mainfont=DejaVu Serif",
             f"--resource-path={src.parent}", "-o", str(pdf)],
            check=True, capture_output=True, text=True, cwd=str(src.parent),
        )
        return str(pdf)
    except subprocess.CalledProcessError as e:
        return f"pandoc error: {e.stderr.strip()}"


# ---------------------------------------------------------------------------
# Git operations
# ---------------------------------------------------------------------------

def git_restore_tool(path: str, commit: str = "HEAD") -> str:
    """Restore a file in StudentProjects to a given commit, or list history."""
    target = Path(path).expanduser().resolve()
    if not str(target).startswith(str(STUDENT_PROJECTS_DIR.resolve())):
        return f"Refused: {path} is outside StudentProjects."
    rel = target.relative_to(STUDENT_PROJECTS_DIR.resolve())
    if commit == "list":
        result = subprocess.run(
            ["git", "-C", str(STUDENT_PROJECTS_DIR), "log", "--oneline", "--", str(rel)],
            capture_output=True, text=True)
        return result.stdout.strip() or "No git history found for this file."
    result = subprocess.run(
        ["git", "-C", str(STUDENT_PROJECTS_DIR), "checkout", commit, "--", str(rel)],
        capture_output=True, text=True)
    if result.returncode != 0:
        return f"Git restore failed: {result.stderr.strip()}"
    subprocess.run(["git", "-C", str(STUDENT_PROJECTS_DIR), "add", str(target)], capture_output=True)
    subprocess.run(["git", "-C", str(STUDENT_PROJECTS_DIR), "commit", "-m",
                    f"Restore {target.name} to {commit}"], capture_output=True)
    return f"Restored {target.name} to {commit}."


def git_commit_push(message: str, repo_dir: Path = None) -> str:
    """Stage all changes in a project repo, commit, and push."""
    repo = str(repo_dir or STUDENT_PROJECTS_DIR)
    try:
        subprocess.run(["git", "-C", repo, "add", "-A"], check=True, capture_output=True)
        result = subprocess.run(["git", "-C", repo, "commit", "-m", message],
                                capture_output=True, text=True)
        if result.returncode != 0:
            if "nothing to commit" in result.stdout:
                return "Nothing to commit."
            return f"Commit failed: {result.stderr.strip()}"
        push = subprocess.run(["git", "-C", repo, "push"], capture_output=True, text=True)
        if push.returncode != 0:
            return f"Committed but push failed: {push.stderr.strip()}"
        return "Committed and pushed to GitHub."
    except subprocess.CalledProcessError as e:
        return f"Git error: {e.stderr.strip() if e.stderr else str(e)}"


# ---------------------------------------------------------------------------
# File search
# ---------------------------------------------------------------------------

def search_project_files(query: str, repos: list[Path] = None) -> str:
    """Search project directories for files matching query by name or type."""
    if repos is None:
        repos = PROJECT_DIRS
    query_lower = query.lower().strip()
    wanted_exts: set[str] = set()
    for group, exts in EXT_GROUPS.items():
        if group in query_lower:
            wanted_exts.update(exts)
    for word in re.findall(r'\.\w+', query_lower):
        wanted_exts.add(word)
    stopwords = {
        "find", "search", "list", "show", "me", "all", "the", "in", "files",
        "vrzm", "vrzm26", "student", "projects", "sphere", "packing",
        "pdf", "image", "images", "manuscript", "manuscripts", "code", "output",
        "paper", "papers", "file", "document", "documents", "report", "reports",
    }
    name_keywords = [w for w in re.findall(r'\w+', query_lower)
                     if w not in stopwords and len(w) > 2 and not w.isdigit()]
    results = []
    for repo in repos:
        if not repo.exists():
            continue
        for f in sorted(repo.rglob("*")):
            if not f.is_file() or f.name.startswith("."):
                continue
            if wanted_exts and f.suffix.lower() not in wanted_exts:
                continue
            if name_keywords and not any(kw in f.name.lower() for kw in name_keywords):
                continue
            rel = f.relative_to(repo)
            results.append(f"• {repo.name}/{rel}  ({f.stat().st_size // 1024} KB)")
    if not results:
        return f"No files found matching: {query}"
    body = "\n".join(results[:50])
    if len(results) > 50:
        body += f"\n…and {len(results)-50} more"
    return f"Found {len(results)} file(s):\n{body}"


# ---------------------------------------------------------------------------
# Julia execution
# ---------------------------------------------------------------------------

def run_julia(code: str) -> tuple[str, list[Path]]:
    """Execute Julia code in JULIA_WORKDIR. Returns (text_output, new_image_paths)."""
    with tempfile.NamedTemporaryFile(suffix=".jl", mode="w", delete=False) as f:
        f.write(code)
        tmp = f.name
    workdir = Path(JULIA_WORKDIR)
    before = set(workdir.glob("*.png")) | set(workdir.glob("*.svg"))
    try:
        julia_bin = os.path.expanduser("~/.juliaup/bin/julia")
        result = subprocess.run(
            [julia_bin, "--project=@.", tmp],
            capture_output=True, text=True, timeout=JULIA_TIMEOUT, cwd=JULIA_WORKDIR)
        out = result.stdout.strip()
        err_lines = [l for l in result.stderr.splitlines()
                     if not any(w in l for w in ["Precompiling", "Progress", "✓", "─"])]
        err = "\n".join(err_lines).strip()
        new_images = sorted((set(workdir.glob("*.png")) | set(workdir.glob("*.svg"))) - before)
        if result.returncode != 0:
            return (f"Error:\n{err}" if err else "Julia exited with an error.", [])
        return (out if out else (err if err else "(no output)")), new_images
    except subprocess.TimeoutExpired:
        return f"Timed out after {JULIA_TIMEOUT}s.", []
    finally:
        os.unlink(tmp)


# ---------------------------------------------------------------------------
# Web / URL fetching
# ---------------------------------------------------------------------------

def _ezproxy_url(url: str) -> str:
    p = urllib.parse.urlparse(url)
    proxy_host = p.netloc.replace(".", "-") + "." + ANU_EZPROXY_HOST
    return f"{p.scheme}://{proxy_host}{p.path}" + (f"?{p.query}" if p.query else "")


def fetch_url_tool(url: str, save_path: str = "") -> tuple[str, str]:
    """Download a URL (PDF or HTML), extract text, optionally save PDF.
    Falls back to ANU EZproxy on access denial. Returns (text, saved_path)."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Mhai2/1.0; research bot)"}
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    def _fetch(target_url, extra_headers=None):
        h = {**headers, **(extra_headers or {})}
        req = urllib.request.Request(target_url, headers=h)
        with urllib.request.urlopen(req, timeout=30, context=ssl_ctx) as r:
            return r.headers.get("Content-Type", ""), r.read()

    try:
        content_type, data = _fetch(url)
        is_pdf_url = url.lower().endswith(".pdf") or "pdf" in url.lower()
        if is_pdf_url and b"%PDF" not in data[:16] and len(data) < 50000:
            raise ValueError("Paywall suspected")
    except Exception as direct_err:
        if ANU_EZPROXY_COOKIE:
            try:
                content_type, data = _fetch(_ezproxy_url(url), {"Cookie": f"EZproxy={ANU_EZPROXY_COOKIE}"})
            except Exception as proxy_err:
                return f"Fetch error (direct: {direct_err}; EZproxy: {proxy_err})", ""
        else:
            return f"Fetch error: {direct_err}", ""

    saved = ""
    if "pdf" in content_type.lower() or url.lower().endswith(".pdf") or b"%PDF" in data[:8]:
        if save_path:
            dest = Path(save_path).expanduser().resolve()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            saved = str(dest)
            repo = _repo_for_path(dest)
            if repo:
                subprocess.run(["git", "-C", str(repo), "add", str(dest)], capture_output=True)
                subprocess.run(["git", "-C", str(repo), "commit", "-m", f"Add {dest.name}"], capture_output=True)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        try:
            result = subprocess.run(["pdftotext", tmp_path, "-"],
                                    capture_output=True, text=True, timeout=30)
            text = result.stdout.strip() if result.returncode == 0 else f"pdftotext error: {result.stderr.strip()}"
        finally:
            os.unlink(tmp_path)
    else:
        text = re.sub(r"<[^>]+>", " ", data.decode("utf-8", errors="replace"))
        text = re.sub(r"\s+", " ", text).strip()

    if len(text) > 12000:
        text = text[:12000] + "\n...(truncated)"
    return text, saved


# ---------------------------------------------------------------------------
# Weather
# ---------------------------------------------------------------------------

def get_weather() -> str:
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude=-35.2809&longitude=149.1300"
            "&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m,relative_humidity_2m"
            "&timezone=Australia%2FSydney"
        )
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        c = data["current"]
        codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
            61: "Light rain", 63: "Rain", 65: "Heavy rain", 71: "Light snow", 73: "Snow",
            75: "Heavy snow", 80: "Rain showers", 82: "Heavy showers",
            95: "Thunderstorm", 96: "Thunderstorm+hail", 99: "Thunderstorm+hail",
        }
        desc = codes.get(c["weather_code"], f"Code {c['weather_code']}")
        return (f"Canberra now: {c['temperature_2m']}°C (feels like {c['apparent_temperature']}°C)\n"
                f"{desc} | Humidity {c['relative_humidity_2m']}% | Wind {c['wind_speed_10m']} km/h")
    except Exception as e:
        return f"Weather unavailable: {e}"


# ---------------------------------------------------------------------------
# pCloud backup
# ---------------------------------------------------------------------------

def _newest_mtime(path: Path) -> float:
    best = 0.0
    try:
        best = max(best, path.stat().st_mtime)
        for p in path.iterdir():
            try:
                best = max(best, p.stat().st_mtime)
            except OSError:
                pass
    except OSError:
        pass
    return best


def check_backup() -> str:
    if not PCLOUD_BACKUP_DIR.exists():
        return "pCloudDrive not mounted — backup folder not accessible."
    lines = []
    any_stale = False
    for folder in BACKUP_FOLDERS:
        src = HOMEPC_SOURCE / folder
        dst = PCLOUD_BACKUP_DIR / folder
        if not src.exists():
            continue
        src_time = _newest_mtime(src)
        dst_time = _newest_mtime(dst)
        if src_time == 0:
            lines.append(f"• {folder}: empty")
            continue
        lag = src_time - dst_time
        src_dt = datetime.fromtimestamp(src_time, tz=timezone.utc)
        dst_dt = datetime.fromtimestamp(dst_time, tz=timezone.utc) if dst_time else None
        lag_days, lag_hrs = int(lag / 86400), int((lag % 86400) / 3600)
        if lag <= 3600:
            status = "OK"
        elif lag <= 7 * 86400:
            status = f"behind {lag_days}d {lag_hrs}h"
            any_stale = True
        else:
            status = f"STALE {lag_days}d behind"
            any_stale = True
        src_str = src_dt.strftime("%b %d")
        dst_str = dst_dt.strftime("%b %d") if dst_dt else "never"
        lines.append(f"• {folder}: {status} (local {src_str}, backup {dst_str})")
    overall = "WARNING — some folders behind" if any_stale else "All folders up to date"
    return f"pCloud backup — {overall}\n" + "\n".join(lines)


# ---------------------------------------------------------------------------
# Paper search
# ---------------------------------------------------------------------------

_arxiv_last_query_time: float = 0.0
_ARXIV_MIN_INTERVAL = 5.0

def search_arxiv(query: str, max_results: int = 5, sort_by_date: bool = False) -> str:
    """Search arXiv via direct API. Always uses relevance sorting (date sort ignores filters).
    Set sort_by_date=True to sort results locally by date after fetching."""
    import time, xml.etree.ElementTree as ET
    global _arxiv_last_query_time
    elapsed = time.time() - _arxiv_last_query_time
    if elapsed < _ARXIV_MIN_INTERVAL:
        time.sleep(_ARXIV_MIN_INTERVAL - elapsed)
    try:
        params = urllib.parse.urlencode({
            "search_query": query,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        })
        url = f"https://export.arxiv.org/api/query?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mhai2/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()
        _arxiv_last_query_time = time.time()
        ns = {"a": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(data)
        entries = []
        for entry in root.findall("a:entry", ns):
            title = entry.find("a:title", ns).text.strip().replace("\n", " ")
            arxiv_id = entry.find("a:id", ns).text.strip()
            published = entry.find("a:published", ns).text[:10]
            authors = [a.find("a:name", ns).text for a in entry.findall("a:author", ns)]
            author_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
            entries.append((published, title, author_str, arxiv_id))
        if sort_by_date:
            entries.sort(key=lambda x: x[0], reverse=True)
        results = [f"• {t}\n  {a} ({p[:4]})\n  {i}" for p, t, a, i in entries]
        return "\n\n".join(results) if results else "No results found."
    except Exception as e:
        _arxiv_last_query_time = time.time()
        return f"ArXiv search error: {e}"


def search_semantic_scholar(query: str, max_results: int = 5) -> str:
    try:
        params = urllib.parse.urlencode({"query": query, "limit": max_results,
                                         "fields": "title,authors,year,venue,externalIds,openAccessPdf"})
        req = urllib.request.Request(f"https://api.semanticscholar.org/graph/v1/paper/search?{params}",
                                     headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        papers = data.get("data", [])
        if not papers:
            return "No results found on Semantic Scholar."
        results = []
        for p in papers:
            authors = ", ".join(a["name"] for a in p.get("authors", [])[:3])
            if len(p.get("authors", [])) > 3:
                authors += " et al."
            ext = p.get("externalIds", {})
            link = f"  arxiv.org/abs/{ext['ArXiv']}" if ext.get("ArXiv") else (f"  doi.org/{ext['DOI']}" if ext.get("DOI") else "")
            pdf = p.get("openAccessPdf")
            if pdf and pdf.get("url"):
                link += f"\n  PDF: {pdf['url']}"
            results.append(f"• {p['title']}\n  {authors} ({p.get('year','?')}){chr(10)+link if link else ''}")
        return f"Semantic Scholar ({len(papers)} results):\n\n" + "\n\n".join(results)
    except Exception as e:
        return f"Semantic Scholar error: {e}"


def search_crossref(query: str, max_results: int = 5) -> str:
    try:
        params = urllib.parse.urlencode({"query": query, "rows": max_results,
                                         "select": "title,author,published,container-title,DOI",
                                         "mailto": "markus.hegland@anu.edu.au"})
        req = urllib.request.Request(f"https://api.crossref.org/works?{params}",
                                     headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        items = data.get("message", {}).get("items", [])
        if not items:
            return "No results found on CrossRef."
        results = []
        for item in items:
            title = item.get("title", ["?"])[0]
            authors = ", ".join(f"{a.get('family','')} {a.get('given','')[:1]}".strip()
                                for a in item.get("author", [])[:3])
            if len(item.get("author", [])) > 3:
                authors += " et al."
            pub = item.get("published", {}).get("date-parts", [[None]])[0]
            year = pub[0] if pub else "?"
            journal = item.get("container-title", [""])[0]
            doi = item.get("DOI", "")
            results.append(f"• {title}\n  {authors} ({year}){' — '+journal if journal else ''}{chr(10)+'  doi.org/'+doi if doi else ''}")
        return f"CrossRef ({len(items)} results):\n\n" + "\n\n".join(results)
    except Exception as e:
        return f"CrossRef error: {e}"


def search_papers(query: str) -> str:
    return (f"**arXiv:**\n{search_arxiv(query, 3)}\n\n"
            f"**Semantic Scholar:**\n{search_semantic_scholar(query, 3)}\n\n"
            f"**CrossRef:**\n{search_crossref(query, 3)}")


def search_gemini(query: str) -> str:
    if not GEMINI_API_KEY:
        return "Gemini not configured — add GEMINI_API_KEY to .env"
    try:
        from google import genai as gai
        from google.genai import types as gtypes
        gc = gai.Client(api_key=GEMINI_API_KEY)
        response = gc.models.generate_content(
            model="gemini-2.5-flash",
            contents=query,
            config=gtypes.GenerateContentConfig(
                tools=[gtypes.Tool(google_search=gtypes.GoogleSearch())],
                temperature=0.2,
            ),
        )
        text = response.text
        if not text:
            parts = []
            for candidate in (response.candidates or []):
                for part in (getattr(getattr(candidate, "content", None), "parts", None) or []):
                    t = getattr(part, "text", None)
                    if t:
                        parts.append(t)
            text = "\n".join(parts) if parts else "Gemini returned no results."
        return text or "Gemini returned no results."
    except Exception as e:
        return f"Gemini search error: {e}"


# ---------------------------------------------------------------------------
# Gmail
# ---------------------------------------------------------------------------

def _get_gmail_service():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    if not GMAIL_TOKEN.exists():
        raise RuntimeError("Gmail not set up — run setup_gmail.py first.")
    with open(GMAIL_TOKEN) as f:
        data = json.load(f)
    creds = Credentials(token=data["token"], refresh_token=data["refresh_token"],
                        token_uri=data["token_uri"], client_id=data["client_id"],
                        client_secret=data["client_secret"], scopes=data["scopes"])
    if creds.expired:
        creds.refresh(Request())
        data["token"] = creds.token
        with open(GMAIL_TOKEN, "w") as f:
            json.dump(data, f, indent=2)
    return build("gmail", "v1", credentials=creds)


def search_gmail(query: str, max_results: int = 10) -> str:
    service = _get_gmail_service()
    result = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    messages = result.get("messages", [])
    if not messages:
        return f"No emails found for: {query}"
    summaries = []
    for msg in messages:
        m = service.users().messages().get(userId="me", id=msg["id"], format="metadata",
                                           metadataHeaders=["From", "Subject", "Date"]).execute()
        headers = {h["name"]: h["value"] for h in m.get("payload", {}).get("headers", [])}
        sender = re.sub(r"\s*<.*?>", "", headers.get("From", "?")).strip()
        summaries.append(f"• {headers.get('Date','')[:16]} | {sender}\n  {headers.get('Subject','(no subject)')}\n  {m.get('snippet','')[:120]}…")
    return f"Gmail ({len(messages)} results for: {query})\n\n" + "\n\n".join(summaries)


def parse_gmail_query(text: str) -> str:
    t = text.lower()
    parts = []
    if "unread" in t: parts.append("is:unread")
    if "attachment" in t or "attached" in t: parts.append("has:attachment")
    if "this week" in t: parts.append("newer_than:7d")
    elif "today" in t: parts.append("newer_than:1d")
    elif "this month" in t: parts.append("newer_than:30d")
    subj_m = re.search(r"(?:about|subject|regarding)\s+['\"]?(.+?)['\"]?(?:\s|$)", t)
    if subj_m:
        parts.append(f'subject:"{subj_m.group(1)}"')
    if not parts:
        stopwords = {"email", "emails", "find", "show", "search", "me", "my", "from", "any", "all", "the", "get"}
        words = [w for w in re.findall(r'\w+', t) if w not in stopwords and len(w) > 3]
        if words:
            parts.append(" ".join(words))
    return search_gmail(" ".join(parts) if parts else "newer_than:7d")


# ---------------------------------------------------------------------------
# Google Calendar
# ---------------------------------------------------------------------------

def _get_calendar_service():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    with open(CALENDAR_TOKEN) as f:
        data = json.load(f)
    creds = Credentials(token=data["access_token"], refresh_token=data["refresh_token"],
                        token_uri=data["token_uri"], client_id=data["client_id"],
                        client_secret=data["client_secret"], scopes=data["scopes"])
    if creds.expired:
        creds.refresh(Request())
        data["access_token"] = creds.token
        with open(CALENDAR_TOKEN, "w") as f:
            json.dump(data, f)
    return build("calendar", "v3", credentials=creds)


def _fetch_events(time_min: datetime, time_max: datetime) -> list[dict]:
    service = _get_calendar_service()
    events = []
    for cal_name, cal_id in CALENDAR_IDS.items():
        try:
            result = service.events().list(calendarId=cal_id,
                                           timeMin=time_min.isoformat(), timeMax=time_max.isoformat(),
                                           singleEvents=True, orderBy="startTime", maxResults=50).execute()
            for e in result.get("items", []):
                e["_calendar"] = cal_name
                events.append(e)
        except Exception as ex:
            log.warning("Calendar fetch error (%s): %s", cal_name, ex)
    events.sort(key=lambda e: e.get("start", {}).get("dateTime", e.get("start", {}).get("date", "")))
    return events


def _format_event(e: dict) -> str:
    start = e.get("start", {})
    if "dateTime" in start:
        dt = datetime.fromisoformat(start["dateTime"]).astimezone(CANBERRA_TZ)
        end_dt = datetime.fromisoformat(e["end"]["dateTime"]).astimezone(CANBERRA_TZ)
        time_str = f"{dt.strftime('%a %d %b %H:%M')}–{end_dt.strftime('%H:%M')}"
    else:
        time_str = f"{start.get('date', '?')} (all day)"
    return f"• {time_str}: {e.get('summary', '(no title)')}"


def query_calendar_range(time_min: datetime, time_max: datetime, person: str = "") -> str:
    try:
        events = _fetch_events(time_min, time_max)
        if person:
            keywords = next((v for k, v in CALENDAR_PEOPLE.items() if k in person.lower()), [person.lower()])
            events = [e for e in events if any(kw in e.get("summary", "").lower() for kw in keywords)]
        return "\n".join(_format_event(e) for e in events) if events else "No events found."
    except Exception as ex:
        return f"Calendar error: {ex}"


def parse_calendar_query(text: str) -> str:
    t = text.lower()
    now = datetime.now(CANBERRA_TZ)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    person = next((name for name in CALENDAR_PEOPLE if name in t), "")
    if "today" in t:
        tmin, tmax = today, today + timedelta(days=1)
    elif "tomorrow" in t:
        tmin, tmax = today + timedelta(days=1), today + timedelta(days=2)
    elif "this week" in t:
        monday = today - timedelta(days=today.weekday())
        tmin, tmax = monday, monday + timedelta(days=7)
    elif "next week" in t:
        monday = today - timedelta(days=today.weekday()) + timedelta(weeks=1)
        tmin, tmax = monday, monday + timedelta(days=7)
    elif "next" in t and "days" in t:
        m = re.search(r"next (\d+) days", t)
        days = int(m.group(1)) if m else 7
        tmin, tmax = today, today + timedelta(days=days)
    else:
        tmin, tmax = today, today + timedelta(days=7)
    label = tmin.strftime("%d %b") + ("" if (tmax - tmin).days == 1 else f" – {(tmax - timedelta(days=1)).strftime('%d %b')}")
    return f"Calendar {label}{' — '+person if person else ''}\n{query_calendar_range(tmin, tmax, person)}"


# ---------------------------------------------------------------------------
# Whiteboard
# ---------------------------------------------------------------------------

def whiteboard_append(content: str):
    with open(WHITEBOARD_FILE, "a") as f:
        f.write("\n" + content + "\n")


def whiteboard_save(topic: str) -> str:
    if not WHITEBOARD_FILE.exists():
        return "Whiteboard is empty."
    dest = KNOWLEDGE_DIR / f"research/whiteboard_{topic.replace(' ', '_')}.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(WHITEBOARD_FILE.read_text())
    return f"Saved to knowledge base: {dest.name}"


def whiteboard_render_png() -> list[Path]:
    if not WHITEBOARD_FILE.exists() or not WHITEBOARD_FILE.read_text().strip():
        return []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        pdf = tmp / "whiteboard.pdf"
        subprocess.run(["pandoc", str(WHITEBOARD_FILE), "--pdf-engine=pdflatex", "-o", str(pdf)],
                       check=True, capture_output=True)
        subprocess.run(["pdftoppm", "-png", "-r", "180", str(pdf), str(tmp / "page")],
                       check=True, capture_output=True)
        out_dir = WHITEBOARD_FILE.parent / ".whiteboard_render"
        out_dir.mkdir(exist_ok=True)
        result = []
        for p in sorted(tmp.glob("page-*.png")):
            dest = out_dir / p.name
            dest.write_bytes(p.read_bytes())
            result.append(dest)
        return result


# ---------------------------------------------------------------------------
# Email auto-save
# ---------------------------------------------------------------------------

def detect_and_save_email(text: str) -> str | None:
    """If text looks like a pasted email, save to knowledge/emails/ and return path."""
    if len(re.findall(r'^(From|To|Subject|Date|Sent|CC|BCC)\s*:', text, re.MULTILINE | re.IGNORECASE)) < 2:
        return None
    subj_m = re.search(r'^Subject\s*:\s*(.+)', text, re.MULTILINE | re.IGNORECASE)
    date_m = re.search(r'^(Date|Sent)\s*:\s*(.+)', text, re.MULTILINE | re.IGNORECASE)
    from_m = re.search(r'^From\s*:\s*(.+)', text, re.MULTILINE | re.IGNORECASE)
    subject = re.sub(r'\s+', '_', re.sub(r'[^\w\s-]', '', subj_m.group(1).strip())[:50].strip()) if subj_m else "email"
    date_str = datetime.now().strftime("%Y-%m-%d")
    if date_m:
        for fmt in ("%d %B %Y", "%B %d, %Y", "%Y-%m-%d", "%d/%m/%Y"):
            try:
                date_str = datetime.strptime(date_m.group(2).strip()[:20], fmt).strftime("%Y-%m-%d")
                break
            except ValueError:
                pass
    sender = (re.sub(r'\s+', '_', re.sub(r'[^\w\s-]', '', from_m.group(1).strip())[:30].strip()) + "_") if from_m else ""
    EMAILS_DIR.mkdir(parents=True, exist_ok=True)
    dest = EMAILS_DIR / f"{date_str}_{sender}{subject}.md"
    dest.write_text(f"# Email: {subj_m.group(1).strip() if subj_m else 'untitled'}\nSaved: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{text}")
    log.info("Saved email: %s", dest.name)
    return str(dest)


# ---------------------------------------------------------------------------
# Transcripts
# ---------------------------------------------------------------------------

def list_transcripts() -> str:
    if not TRANSCRIPT_DIR.exists():
        return "Transcript folder not found. Save .vtt or .txt Zoom transcripts to ~/Desktop/FdHMH/transcripts/"
    files = list(TRANSCRIPT_DIR.glob("*.vtt")) + list(TRANSCRIPT_DIR.glob("*.txt"))
    return "\n".join(f"• {f.name}" for f in sorted(files)) if files else "No transcripts found."


def load_transcript(filename: str) -> str:
    path = TRANSCRIPT_DIR / filename
    if not path.exists():
        matches = list(TRANSCRIPT_DIR.glob(f"*{filename}*")) if TRANSCRIPT_DIR.exists() else []
        if not matches:
            return ""
        path = matches[0]
    text = path.read_text(errors="replace")
    if path.suffix == ".vtt":
        lines = [l for l in text.splitlines()
                 if not re.match(r"^\d{2}:\d{2}", l) and not re.match(r"^WEBVTT", l) and l.strip()]
        text = "\n".join(lines)
    return text
