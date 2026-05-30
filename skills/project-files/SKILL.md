---
name: project-files
description: "Read, save, search, and list files across Markus's research projects. Each conversation is locked to one project — never mix files between projects."
version: 1.0.0
author: Mhai2
platforms: [linux]
metadata:
  hermes:
    tags: [Files, Projects, Research, StudentProjects, VRZM26]
---

# Project File Operations

## Project Directories

| Project | Primary Path | Extra Paths |
|---|---|---|
| VRZM26 | ~/Desktop/VRZM26/ | ~/projects/sphere_packing/ |
| FdHMH | ~/Desktop/FdHMH/ | ~/Desktop/FdHMH/CodeMH/ (Julia code) |
| XiChen26honors | ~/Desktop/StudentProjects/XiChen26honors/ | — |
| GlebPhD | ~/Desktop/StudentProjects/GlebPhD/ | — |
| MATH8702 | ~/Desktop/StudentProjects/MATH8702/ | — |
| DBT | ~/projects/DBT/ | Session chunks, CLAUDE.md (MCP Gmail/Drive tasks) |
| Recipes | knowledge base only | — |
| Personal | no filesystem path | — |

Knowledge base root: `~/.openclaw/workspace/knowledge/`

## CRITICAL: Project Isolation
Only access files within the active project's directories. Never read or write files from another project.

## Read a file

```bash
cat ~/Desktop/VRZM26/path/to/file.jl
```

For PDFs:
```bash
pdftotext ~/Desktop/VRZM26/paper.pdf -
```

## List a directory

```bash
ls -la ~/Desktop/VRZM26/research/tasks/
```

## Search for files within a project

```bash
find ~/Desktop/VRZM26/ -name "*.jl" -o -name "*.md" | sort
find ~/Desktop/StudentProjects/XiChen26honors/ -name "*.pdf" | sort
```

## Save a file (auto-commit if in git repo)

```bash
cat > ~/Desktop/VRZM26/path/to/file.md << 'EOF'
<content>
EOF

# Auto-commit if in a git repo
cd ~/Desktop/VRZM26 && git add path/to/file.md && git commit -m "Auto-save file.md"
```

## Append to a file

```bash
cat >> ~/Desktop/VRZM26/path/to/file.md << 'EOF'

<content to append>
EOF
```

## Convert markdown to PDF

Standard command:
```bash
pandoc file.md --pdf-engine=xelatex -o file.pdf
```

For meeting prep / readable notes with large font and embedded code files:
```bash
pandoc file.md --pdf-engine=xelatex -o file.pdf
```

Use this YAML front matter in the markdown for proper font size and Unicode support:
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

- Scale=1.5 gives ~15pt font. Adjust as needed (2.0 = ~20pt).
- `\lstinputlisting` includes code files correctly (preserves comments, no markdown interpretation):
```
```{=latex}
\newpage
```

## Section heading

```{=latex}
\lstinputlisting[language={}]{CodeMH/filename.jl}
```
```
- Put `\newpage` before the section heading, not inside the lstinputlisting block.
- Use `language={}` to avoid comment misinterpretation.
- For math symbols in body text (∈, ℝ, ⁺ etc.) use Unicode directly — DejaVu Serif supports them.
- Inside `$$...$$` math blocks use LaTeX: `\widetilde{M}` not `M̃`, `\backslash` not `\`.

Then send the PDF to Markus.

## Load knowledge base file

```bash
cat ~/.openclaw/workspace/knowledge/research/fdhmh.md
cat ~/.openclaw/workspace/knowledge/dbt/radical-acceptance.md
cat ~/.openclaw/workspace/knowledge/recipes/airfryer.md
```

## Python skill helper (for complex operations)

For fuzzy path matching or project-aware operations, use:
```bash
cd ~/projects/Mhai2 && python3 -c "\
from mhai_skills import read_project_file, save_file_tool, search_project_files
print(read_project_file('VRZM26/research/sphere_packing.md'))
"
```

## Verify project isolation

Check for misfiled content (e.g., astrophysics papers in sphere-packing project):
```bash
python scripts/verify_project.py ~/Desktop/VRZM26 sphere_packing
```

See `scripts/verify_project.py` for implementation.

## Markus's Project Workflow Conventions

1. **Project isolation:** Each conversation is locked to ONE project. Check the context for active project at start.
2. **Terse interaction:** Markus prefers concise responses, minimal explanation. Lead with artifacts and options, not reasoning.
3. **Quick artifact delivery:** Provide files/PDFs/scripts FIRST. Explanation second (if at all).
4. **Check existing state:** Always verify available materials before asking questions. Load project-files skill first.
5. **Git integration:** All research files auto-commit to git on save. Review recent commits to understand project history.
6. **Meeting prep:** Research projects support weekly meetings. Structure all analysis as meeting-prep docs before code/data work.

## Building Algorithm Specifications (FdHMH Weekly Pattern)

**Workflow:** When building markdown documents for Markus's Monday algorithm meetings (e.g., FdHMH), use **incremental display pattern**:

1. Create file with just `# Heading` or minimal content
2. Add ONE section at a time via patch; after each patch, DISPLAY ONLY THAT SECTION (not the whole file)
3. Wait for Markus's feedback/approval before moving to next section
4. When done, save and commit to git

**Why:** Markus prefers slow, deliberate building. He corrects as you go. Shows work-in-progress, not draft dumps.

**Example pattern:**
```
You: "Here's Step 1..."
[show just Step 1 content]
Markus: "Good. Now add Step 2."
You: [patch in Step 2, show only Step 2 with new context]
```

## Implementation File Referencing

**Pattern:** When creating markdown that documents code (algorithms, functions):
- Write implementation files separately (`.jl`, `.m`, `.py` etc.)
- In markdown, REFERENCE the files via `See file: CodeMH/cur_approximation.jl` instead of embedding code blocks inline
- Commit implementation files to git independently
- Benefits: keeps markdown readable, implementations testable, easy to update without re-doing markdown

## PDF Generation for Notes

**Use case:** Markdown meetings docs need to be readable PDFs for sharing/printing.

**Command (readable note style):**
```bash
pandoc document.md -o document.pdf \
  --pdf-engine=xelatex \
  -V papersize=a4 \
  -V margin-left=1.5cm -V margin-right=1.5cm \
  -V margin-top=1.5cm -V margin-bottom=1.5cm \
  -V fontsize=16pt
```

**Parameters:**
- `xelatex`: handles Unicode math symbols (∈, ℝ, ⁺, etc.) better than pdflatex
- `fontsize=16pt`: ~2× default (12pt) — makes it look like notes, not a paper
- Margins `1.5cm`: smaller than default, fits more content while staying readable

**Note:** xelatex may warn about missing Unicode chars (∈, ℝ, superscripts) — warnings are harmless; PDF still renders correctly.

## Project-Specific References

- **VRZM26:** See `references/vrzm26-structure.md` for directory map, quick-start commands, file exchange protocol, and hyperuniformity status.
- **FdHMH:** 
  - `references/fdhmh-structure.md` — manuscript layout, Monday meeting schedule, algorithm reference, collaboration with Frank de Hoog (CSIRO)
  - `references/fdhmh-terminology.md` — matrix decomposition terminology, code language pair (Julia + Octave), algorithm status (June 2026)
- **DBT:**
  - `references/dbt-session-learning-workflow.md` — workflow for extracting, summarizing, and learning from session transcripts; key patterns in DBT teaching (attachment, nervous system, bottom-up regulation)
