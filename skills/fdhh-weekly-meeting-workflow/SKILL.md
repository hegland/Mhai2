---
name: fdhh-weekly-meeting-workflow
title: "FdHMH Weekly Meeting Workflow (Algorithm Development Cycle)"
description: "Repeatable workflow for Frank de Hoog (CSIRO) Monday meetings: transcript capture, progress analysis, algorithm specification, and implementation testing. Tailored for iterative algorithm development."
tags: ["fdhh", "research", "algorithm-development", "weekly-meeting", "transcript-analysis", "git-workflow"]
---

# FdHMH Weekly Meeting Workflow (Algorithm Development Cycle)

## Overview

Frank de Hoog (deh009, CSIRO) and Markus Hegland meet **every Monday at 10am** to develop randomized numerical linear algebra (RandNLA) algorithms. This skill captures the repeatable workflow for each meeting cycle.

**Project:** CUR/Nyström decompositions with uniform sampling for PSD matrices  
**Scope:** One-week iterations with clear deliverables, status tracking, and git-versioned artifacts

---

## Standard Meeting Cycle (7-Day)

### Day 0: Friday Before Meeting
- (Optional) Send Frank summary bullet points from previous Friday or Monday
- Ensure all git commits are pushed
- Review previous week's analysis document
- **Pre-meeting prep (if new paper/bound to discuss):**
  - Extract main theorems/bounds from recent papers (e.g., newest deHoog-Hegland submission)
  - Create summary document with bound statement, key properties, comparison to prior work
  - Commit to git with descriptive message (e.g., "Extract Theorem 4 from 2025 submission")
  - Prepare talking points: what changed, why it matters, how it affects current work

### Day 1: Monday ~10:00 AM (Meeting)
- 45-60 minute Zoom call with Frank
- Topics: algorithm clarification, error bounds, literature review, infrastructure (laptop, software setup)
- Frank may report blockers (fellowship uncertainty, licensing issues, missing references)

### Day 1+: Monday Evening (Immediate Post-Meeting)
1. **Save transcript** to `transcripts/YYYY-MM-DD_Frank_Zoom.txt`
   - Raw meeting notes or Zoom auto-transcript
   - Format: plain text, markdown-compatible

2. **Create analysis document** `YYYY-MM-DD_ANALYSIS.md` with:
   - Meeting date, participants, next meeting date
   - Frank's progress on action items (✅ completed, ⏳ in progress, ❌ blocked)
   - 5-10 key technical insights from discussion
   - New or revised action items for Frank
   - Action items for Markus (send summaries, clarify concepts, etc.)
   - Administrative alerts (fellowship risk, equipment issues, missing citations)
   - Metrics: week-to-week progress table (algorithm clarity, literature review depth, laptop setup, etc.)
   - Recommended actions before next Monday

3. **Commit both files** with descriptive message:
   ```bash
   git add transcripts/YYYY-MM-DD_Frank_Zoom.txt YYYY-MM-DD_ANALYSIS.md
   git commit -m "Add YYYY-MM-DD meeting transcript and analysis (focus: [topic], Frank status: [summary])"
   ```

### Days 2-6: Week (Async Work)
- **Markus:** Send action item summary bullet points asap (ideally Tuesday)
- **Frank:** Works on algorithm characterization, literature review, error analysis
- **Markus:** (Optional) Iterate on algorithm specification if Frank sends clarifications
- Maintain git log with granular commits (one per section or deliverable)

### Day 7: Friday Before Next Monday
- (Optional) Review Frank's progress and prepare clarifying questions
- Ensure all work is committed and pushed
- Prepare talking points for Monday

---

## Document Checklist per Meeting

### Transcript (`transcripts/YYYY-MM-DD_Frank_Zoom.txt`)
- [ ] Date in filename
- [ ] All speaker turns captured (even partial sentences)
- [ ] Topics discussed labeled or timestamped if available
- [ ] Frank's reported blockers or questions
- [ ] Plain text or markdown format
- [ ] Committed to git

### Analysis (`YYYY-MM-DD_ANALYSIS.md`)

**Header:**
- [ ] Meeting date (Monday, YYYY-MM-DD)
- [ ] Participants: Markus Hegland, Frank de Hoog (deh009)
- [ ] Duration estimate (~45min)
- [ ] Next meeting date (Monday, +7 days)

**Frank's Progress Table:**
- [ ] Algorithm characterization (2-line PSD form) — status
- [ ] Literature review (Halko-Tropp, error bounds) — status  
- [ ] Probability bounds (Hanson-Wright inequality) — status
- [ ] Infrastructure (laptop, LaTeX, Python/Anaconda) — status
- [ ] Other agreed deliverables — status

**Key Insights (5-10 bullets):**
- [ ] Algorithm clarification/breakthrough
- [ ] Literature findings or disagreements
- [ ] New error bound strategy or probability technique
- [ ] Computational or practical concern raised
- [ ] Administrative/structural updates

**Action Items for Frank:**
- [ ] Explicit, numbered list
- [ ] Each with status (⏳ in progress, ❌ blocked, ⚠️ dependency)
- [ ] Due date (e.g., before June 1)

**Action Items for Markus:**
- [ ] Send bullet point summary to Frank (asap)
- [ ] Clarify specific concept(s)
- [ ] Find/cite missing reference
- [ ] Prepare algorithm draft section
- [ ] Review Frank's submission

**Administrative/Risk Alerts:**
- [ ] CSIRO fellowship status (renewed, at risk, applied for backup)
- [ ] Equipment/software blockers (laptop deadline, Anaconda licensing, LaTeX installation)
- [ ] Missing citations or author references
- [ ] Travel or scheduling conflicts

**Progress Metrics:**
- [ ] Week-to-week comparison table (algorithm clarity, literature progress, code readiness, morale)
- [ ] Example:
  ```
  | Aspect | May 25 | June 1 | Trend |
  |--------|--------|--------|-------|
  | Algorithm clarity | 70% | 80% | ↑ |
  | Literature review | 60% | 75% | ↑ |
  | Laptop setup | 30% | 50% | ↑ |
  | Administrative risk | 1 | 2 | ↑ |
  ```

**Recommended Actions (Before Next Monday):**
- [ ] Priority 1: Frank must complete X (e.g., algorithm characterization)
- [ ] Priority 2: Markus should clarify Y (e.g., error conservation)
- [ ] Priority 3: Team research Z (e.g., Polish author reference)

**Timeline/Readiness:**
- [ ] Estimate weeks to algorithm completion
- [ ] Blockers that could slip the timeline
- [ ] Alternative paths if primary blocker materializes

---

## Algorithm Specification Document (When Ready)

Once algorithm clarifies (typically weeks 2-3), create a LONG-FORM spec document:

**File:** `AlgorithmName.md` (e.g., `UniformCUR.md`)

**Structure:**
1. Algorithm definition (input, steps, output)
2. Mathematical notation and key equations
3. Implementation files (references to `CodeMH/*.jl`, `CodeMH/*.m`)
4. Test results and performance metrics
5. Error analysis roadmap

**Format:** Markdown with YAML frontmatter for PDF generation (use `pdf-generation-xelatex-workflow` skill)

**Outputs:**
- `AlgorithmName.md` — source (git-tracked)
- `AlgorithmName.pdf` — generated (optionally git-tracked or .gitignored)

---

## Implementation Artifacts

### Code Files
- **Julia:** `CodeMH/cur_approximation.jl` (or similar)
  - Include docstring with algorithm name, input/output, reference
  - Keep function focused (single responsibility)

- **Octave/MATLAB:** `CodeMH/cur_approximation.m` (or similar)
  - Same signature and docstring as Julia version
  - Use `%` comments (Octave-compatible)

### Test Script
- **Julia:** `CodeMH/test_cur_approximation.jl`
  - Generate random PSD matrix
  - Run algorithm, compute error metrics
  - Print progress + results
  - Runnable standalone: `julia CodeMH/test_cur_approximation.jl`

### Data/Results
- Store outputs in `data/` or session subdirectory
- Commit `.txt` logs of test runs (for reference)
- Do NOT commit large binary matrices unless essential

---

## Git Workflow for FdHMH

**Branch:** Always work on `development` (long-lived feature branch)

**Commit Strategy:**
- Each meeting → transcript + analysis (1 commit)
- Algorithm spec section finalized → 1 commit per section
- Implementation added → 1 commit per file or function
- Test results → 1 commit with test script + output log

**Message Format:**
```
Add YYYY-MM-DD meeting transcript and analysis (focus: error bounds, Frank: algorithm in progress)

Add algorithm specification section: Step 1 (sampling)

Add Julia implementation of CUR approximation with uniform sampling

Add test script: 1024×1024 random PSD matrix, k=64 samples
```

**Push Frequency:** After every meeting or milestone (at least weekly)

---

## Communication Checklist

### Every Monday (After Meeting)
- [ ] Save transcript to `transcripts/`
- [ ] Create analysis document
- [ ] Git commit with descriptive message
- [ ] Send Markus notification (optional: summary of next steps)

### By Tuesday
- [ ] Markus sends Frank bullet-point summary of action items

### By Friday Before Next Monday
- [ ] Review Frank's progress
- [ ] Push all work to git
- [ ] Prepare any clarifying questions for Monday

---

## Pitfalls & Remedies

| Pitfall | Cause | Prevention |
|---------|-------|-----------|
| Transcript lost / not saved | Forgot to download from Zoom | Save as priority #1 after call ends; use standard filename |
| Analysis too long (3+ pages) | Capturing too much detail | Limit to 10 bullets of insight; use metrics table instead of prose |
| Action items unclear for Frank | Vague wording ("fix algorithm") | Number them, make specific, include due date (e.g., "By June 1: write 2-line PSD form") |
| Administrative alerts buried | Too much technical detail | Dedicate **bold alert section** at top if fellowship/blocker exists |
| Git commits forgotten | Distracted by content creation | Commit immediately after closing analysis doc, before moving on |
| Inconsistent metrics | Change progress dimensions week-to-week | Reuse same categories (algorithm clarity, literature depth, code readiness, infrastructure) every week |
| Frank doesn't see action items | Transcript/analysis not shared | Send link to PDF or git commit SHA, or paste bullet summary in email |
| Algorithm spec becomes messy | Edits without structure | Use separate section headings, edit slow (one section per session), regenerate PDF after each section |

---

## Why This Matters (FdHMH Context)

- **Iterative algorithm development** is non-linear; weekly check-ins catch misunderstandings early
- **Frank's job security** (fellowship risk) means administrative visibility is critical
- **Two remote collaborators** (Markus ANU, Frank CSIRO) require async-friendly docs
- **Git tracking** ensures nothing is lost, next session can see full context
- **Repeatable cycle** scales: if the method works, it works week 1 → week 12

---

## Session Template

See **`templates/meeting-analysis-template.md`** for a ready-to-copy analysis skeleton.

---

## Related Skills

- **`pdf-generation-xelatex-workflow`** — For rendering algorithm specs to PDF
- **`git-ops`** (if available) — Commit and push helpers for FdHMH project

## Bound Extraction for Meeting Prep

When a new paper or submission arrives (especially deHoog-Hegland drafts), extract the main theorem(s) and document them before Monday's meeting. See **`references/bound-extraction-workflow.md`** for the process: locate paper → extract bound statement → create summary doc → commit to git. Examples include Theorem 4 from the 2025 submission and Corollary 1 from the Dec 2024 paper.

---

**First applied:** June 2026 — Frank de Hoog CUR/Nyström algorithm development meetings

**Workflow**: Transcript (day 1 evening) → Analysis (day 1 evening) → Algorithm spec (week 2+) → Test/implement (parallel) → Next Monday meeting
