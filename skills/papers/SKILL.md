---
name: papers
description: \"Search academic papers on arXiv, Semantic Scholar, and CrossRef. Download and read PDFs. Relevant for FdHMH, VRZM26, and XiChen26honors projects.\"
version: 1.1.0
author: Mhai2
platforms: [linux]
metadata:
  hermes:
    tags: [Research, Papers, ArXiv, Academic, RandNLA, CUR, Neural Networks]
---

# Academic Paper Search & Curation

## Markus's Multi-Step Research Prep Workflow (Project-Locked)

### Complete 4-Step Workflow: Discovery → Guides → Cross-Reference → Data Extraction

**Context:** Markus works in discrete project contexts (VRZM26, FdHMH, XiChen26honors) and expects complete, modular research packages delivered sequentially before analysis. All 4 steps matter; workflow is cumulative. User preferences: terse communication, modular docs, granular git commits, navigation-friendly structure.

#### Step 1: Identify & Download Key Papers

After discovering a key author (3–5 recent papers on your topic), bulk download with **descriptive names** (Author+Year+Topic, not arxiv IDs):

```bash
# Search arXiv for author + keyword
curl -s \"https://export.arxiv.org/api/query?search_query=au:Torquato+AND+packing&max_results=20\" \
  | grep -E \"<title>|<id>http\" | head -10

# Bulk download with descriptive filenames
cd ~/Desktop/VRZM26/lit
curl -s \"https://arxiv.org/pdf/1805.04468\" -o \"Torquato2018_BasicUnderstanding.pdf\"
curl -s \"https://arxiv.org/pdf/2103.14989\" -o \"Torquato2021_HyperuniformityCharacterization.pdf\"
curl -s \"https://arxiv.org/pdf/2204.11345\" -o \"Torquato2022_DisorderedHyperuniformComposites.pdf\"
curl -s \"https://arxiv.org/pdf/2504.16924\" -o \"Torquato2025_UltradenseSpherePacking.pdf\"

# Commit and move forward
git add lit/*.pdf
git commit -m \"Add Torquato 2018, 2021, 2022, 2025 papers on packing and hyperuniformity\"
```

**Pitfall:** Batch naming (`1805.04468.pdf`) is a dead-end. Use human-readable names so you (and Markus) know what each paper contains without opening it.

#### Step 2: Create Access & Reading Guides

**Access guide** (`lit/AUTHOR_ACCESS_GUIDE.md`):
- Tier-rank methods: **FREE** (arXiv) → **INSTITUTIONAL** (ANU Library) → **CONTACT** (email author)
- **Critical insight for Markus:** Clarify that arXiv preprints are scientifically identical to published journal versions (only formatting differs). Fully citable. Unblocks immediate reading without access anxiety.
- Include specific login instructions, email templates, direct DOI links
- See: `references/access-strategies-academic-papers.md` for template

**Reading guide** (`lit/AUTHOR_READING_GUIDE.md`):
- Why read each paper (2–3 lines, project-specific)
- Key sections to focus on
- What to extract (definitions, theorems, formulas)
- Estimated reading hours per paper
- **Implementation checklist** — tie papers directly to your analysis questions (e.g., \"Torquato 2018 explains jamming point φ ≈ 0.64, needed for Question 1\")
- Quick reference formulas (don't make Markus hunt for them)
- See: `references/reading-guide-template.md` for template

**Pitfall — CRITICAL:** Papers without reading plans create debt. Markus will not engage if the roadmap is unclear. Always pair bulk downloads with prioritized guides and explicit implementation checklists.

```bash
git add lit/*_READING_GUIDE.md lit/*_ACCESS_GUIDE.md
git commit -m \"Add reading guide and access strategies for Torquato papers\"
```

#### Step 3: Cross-Reference Theory to Your Existing Analysis

**Create two companion documents:**

1. **Key Insights doc** (e.g., `research/TORQUATO2018_KEY_INSIGHTS.md`):
   - Extract core concepts from papers (definitions, theorems, key results)
   - Translate to your project's notation and language
   - Provide working formulas (not just citations)
   - Example from VRZM26: jamming point φ ≈ 0.64, contact number Z, hyperuniformity structure factor S(k), robustness threshold σ/gap ≈ 0.5

2. **Cross-Reference Map** (e.g., `research/TORQUATO_CROSS_REFERENCE.md`) — **THIS IS THE MOST IMPORTANT DOCUMENT**:
   - **Table:** Your question → Which Torquato paper → Page reference
   - Why each paper matters for your specific work
   - Implementation roadmap (code sketches, methods, next steps)
   - Friday meeting agenda (if meeting is imminent)
   - **Critical insight:** Your existing analysis questions should map directly to theory. If they don't, you're missing foundational papers. This is Markus's \"aha\" moment.

This cross-reference document is where theory **connects to their work** — make it explicit.

```bash
git add research/TORQUATO2018_KEY_INSIGHTS.md
git commit -m \"Add Torquato 2018 analysis: jamming, hyperuniformity, contact networks\"

git add research/TORQUATO_CROSS_REFERENCE.md
git commit -m \"Add Torquato ↔ IAS analysis cross-reference guide for Friday meeting\"
```

#### Step 4: Create Data Extraction & Visualization Roadmap

**Checklist document** (e.g., `BEFORE_FRIDAY_CHECKLIST.md`):
- **Ready-to-run scripts** (Octave/MATLAB/Python) for extracting key metrics from data
- **Visualization code templates** (working examples, not stubs)
- Timeline from now → Friday/next meeting
- Data extraction milestones and deliverables
- Talking points / presentation agenda for meeting
- Example metrics: packing fraction φ, contact number Z̄, distributions P(Z), coordinate evolution

```bash
git add BEFORE_FRIDAY_CHECKLIST.md
git commit -m \"Add detailed checklist for data extraction, visualization, and Friday meeting prep\"
```

#### Delivery Format (Markus-Specific Preferences)

Create **modular, navigation-friendly structure:**

- **INDEX.md** — One-page navigation linking to all new materials + project status
- **SUMMARY.md** — 5-minute read: what's done, what's pending, next steps
- **CHECKLIST.md** — Actionable next steps for this weekend (if meeting is imminent)
- Cross-links between all documents so Markus can jump around without searching

**Tone & Style (Embedded Preference):**
- **No lengthy preambles.** State the result, show options, let him choose.
- **No introductory throat-clearing.** Start with the output, not the process.
- **Bullet points, not prose.** Keep it scannable and direct.
- **Terse communication.** Assume he knows what you're doing and wants the artifact, not the reasoning.

This is Markus's interaction preference. Embed it in your communication style when delivering results.

**Commit Pattern (Granular, Not Batched):**

After each logical sub-step, commit:
```bash
# Papers + initial organization
git commit -m \"Add Torquato 2018, 2021, 2022, 2025 papers on packing\"

# Guides
git commit -m \"Add reading guide and access strategies\"

# Cross-reference
git commit -m \"Add Torquato ↔ IAS cross-reference for Friday\"

# Data extraction roadmap
git commit -m \"Add checklist for data extraction and visualization prep\"

# Navigation
git commit -m \"Add project index for quick navigation\"
```

Granular commits let Markus track which step added which materials and preview changes incrementally.

---

## Extracting Mathematical Content from PDFs (Critical for Theory Papers)

**Context:** When extracting theorems, bounds, formulas, or proofs from academic PDFs, `pdftotext` often mangles mathematical notation, producing broken equations that look plausible but are **wrong**. Don't synthesize — verify visually.

### Correct Workflow for Math-Heavy Content

1. **Never rely on pdftotext alone for formulas.** It converts PDFs to plain text by dropping formatting, which renders mathematics unreadable or incorrect. Example: multi-line bounds get concatenated, fractions become ambiguous, subscripts/superscripts vanish.

2. **Use visual verification (browser_vision) when extracting theorems or bounds:**
   ```bash
   # Step 1: Use pdftotext to find the section number/page
   pdftotext paper.pdf - | grep "Theorem 4" | head -5
   
   # Step 2: Navigate to that page in browser
   # (browser_navigate file://absolute/path/to/paper.pdf)
   
   # Step 3: Use browser_vision to read the formula visually
   # ("Show me Theorem 4 clearly. What is the exact bound formula?")
   ```

3. **When you extract a formula and it looks plausible, verify immediately** — don't assume correctness. Mathematical notation is easy to get wrong from plain-text extraction.

4. **Red flags for broken formula extraction:**
   - Inconsistent parentheses or brackets
   - Terms that don't align dimensionally
   - Exponents/subscripts that appear to be separate lines
   - Fraction bars or division symbols that are ambiguous
   - If you synthesize the formula before checking, you're at high risk of error

### Example (This Session, May 30 2026)

**Wrong (from pdftotext):**
```
E{‖M̃_CUR − M‖_F²} ≤ [(m−r)/(m−k) · (k+1)² + (k+1)] · ‖C_(k+1)(M)‖_F² / ‖C_k(M)‖_F²
```

**Correct (from visual verification):**
```
E{‖M̃_CUR − M‖_F²} ≤ [(m−r)/(m−k) · (k+1)² + (r−k)/(m−k) · (k+1)] · ‖C_(k+1)(M)‖_F² / ‖C_k(M)‖_F²
```

**Key difference:** Second term should be `(r−k)/(m−k) · (k+1)`, not just `(k+1)`. This was missed in the pdftotext version and only caught when visually inspecting the rendered PDF.

### Workflow Pattern

```python
# Workflow for extracting theorem from page N of a PDF
1. pdftotext paper.pdf - | sed -n '/Theorem X/,/^Proof/p'  # Find location
2. browser_navigate(file://path/to/paper.pdf)              # Open PDF
3. [navigate to page N]
4. browser_vision("Show me Theorem X exactly. What is the formula?")  # Visual read
5. Transcribe the formula you see, do NOT synthesize
```

### When to Use This Workflow

- Extracting **theorems, lemmas, main results** from any paper
- Extracting **bounds, inequalities, error expressions** (especially in RandNLA, optimization, numerical analysis)
- Extracting **definitions with precise notation** that must match later use
- ANY formula that will be used in code, analysis docs, or meetings

### When It's Safe to Use pdftotext Alone

- **Literature summaries** (paraphrasing, not quoting formulas)
- **Author names, publication year, abstract text** (plain text content)
- **Section/page navigation** (finding where something is, not what it says precisely)
- **Quotations of prose** (non-mathematical text blocks)

### Pitfall: Plausible-Looking Wrong Formulas

The worst case is synthesizing a formula that:
- Has the right shape and structure
- Passes a quick dimensional check
- But has a critical missing or wrong term (like `(r−k)` vs just `(k+1)`)
- User catches it later in a meeting or detailed review

Always verify mathematical content visually when you extract it. A few seconds of browser_vision saves hours of debugging later.

---

## Classic Bulk Download Pattern (Quicker Version)

**For 3–5 papers by one author on a topic (if not doing full 4-step):**

1. Search arXiv for author + keywords
2. Bulk download with descriptive names
3. Create reading guide — include access methods + why each paper matters
4. Create key insights doc — translate theory to your project notation
5. Create cross-reference map — tie papers to your questions
6. Commit each logical unit separately to git

**Pitfall:** Papers without reading plans create debt. Always pair downloads with guides and implementation checklists.

---

## Quick Search Commands

### Search arXiv

```bash
curl -s \"https://export.arxiv.org/api/query?search_query=au:LASTNAME+AND+keyword&max_results=20\" | grep -E \"<title>|<id>http\"
```

### Search Semantic Scholar (citations of a paper)

```bash
curl -s \"https://api.semanticscholar.org/graph/v1/paper/arXiv:1805.04468/citations?fields=title,authors,year&limit=20\"
```

### Download arXiv PDF

```bash
curl -s \"https://arxiv.org/pdf/ARXIV_ID\" -o \"Author_Year_Topic.pdf\"
```

---

## Access Strategies

**Always tier-rank access methods for paywalled papers:**

1. **FREE:** arXiv preprints (scientifically identical to journal versions)
2. **INSTITUTIONAL:** ANU Library (search via proxy if off-campus)
3. **CONTACT:** Email author directly — most academics freely share preprints
4. **INTERLIBRARY LOAN:** Free for ANU staff (5–7 day turnaround)

**Key insight:** Don't wait for official journal versions if you have arXiv preprints. They're fully citable and 100% scientifically valid.

See: `references/access-strategies-academic-papers.md` for detailed guidance.

---

## Project-Specific Search Tips

- **FdHMH project:** Search for CUR decomposition, RandNLA, SRHT, compound matrices, volume sampling, low-rank approximation
- **VRZM26 project:** Search for sphere packing, jamming, hyperuniformity, amorphous solids, IAS algorithm, contact networks, packing fraction
- **XiChen26honors:** Search for neural network approximation theory, Barron space, DeVore, ReLU networks, depth-width tradeoffs

---

## Support Files (External Templates & Examples)

**Template for reading guides:** `references/reading-guide-template.md`
- Use when curating 3–5 papers
- Includes sections for: why read, key sections, what to extract, hours, checklist, quick formulas

**Worked example from May 2026 VRZM26 session:** `references/torquato-2026-case-study.md`
- Full walkthrough of discovery → bulk download → reading guide → cross-reference → data extraction
- Demonstrates workflow at scale with 4 papers + 5 companion documents
- Shows granular git commits and modular documentation structure

**Access strategies guide:** `references/access-strategies-academic-papers.md`
- Tier-ranked methods for obtaining papers (arXiv → institutional subscriptions → author contact)
- Guidance on preprints vs. published versions
- Email templates for contacting authors
- DOI lookup instructions

## IMPORTANT: arXiv rate limiting
- arXiv enforces minimum 3 seconds between requests. Violations → HTTP 429 → ~5 minute ban.
- Never make multiple arXiv searches in quick succession.
- mhai_skills.py enforces a 5 second minimum interval automatically.
- If you get a 429 error, wait at least 5 minutes before retrying.
- Prefer Semantic Scholar for repeated searches — more lenient rate limits.
- To download by known arXiv ID without searching: fetch_url_tool("https://arxiv.org/pdf/ARXIV_ID")
