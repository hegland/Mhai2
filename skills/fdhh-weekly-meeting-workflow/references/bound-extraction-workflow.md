# Bound Extraction Workflow for FdHMH Meeting Prep

## Trigger
When a new paper arrives (especially from Frank or Markus's own submissions) and contains key theorems/bounds to discuss on Monday.

## Process

### 1. Locate Paper
- Check `~/Desktop/FdH2025/submission/main.pdf` (Markus's drafts)
- Check `~/Desktop/FdH2026/` (if available)
- Check `~/Desktop/FdHMH/lit/` (reference literature)
- Check `~/Desktop/FdHMH/projects/` (working drafts)

### 2. Extract Main Bound
```bash
pdftotext <paper.pdf> - | grep -A 30 "Theorem\|Main result"
```

Target the key theorem(s):
- Look for **Theorem N** or **Main Result** headers
- Capture statement, assumptions, and key properties
- Note any remarks about special cases (e.g., symmetric PD matrices)

### 3. Document in Markdown
Create file: `MAIN_BOUND_<Authors>_<Year>.md`

**Template:**
```markdown
# Main Bound: <Authors> <Year>

## Theorem N (Descriptive Name)

**Statement:** [LaTeX-style math, using Unicode only for Telegram]

**Key properties:**
- Behavior as k varies
- Behavior as r (oversampling) varies
- Special cases (SPD, rank, etc.)

## Comparison to Prior Work
- How does this improve/change previous bounds?
- Which earlier result does it extend?

## Key Insight
- Why does this bound matter?
- What was previously unknown?
- What does oversampling achieve?

## Submitted/Published
- Date, venue, preprint status
- Authors and affiliations
```

### 4. Create Summary Talking Points
Add section to meeting prep or standalone bullet list:
- **What changed?** vs. Corollary 1 (FdH2024) or previous draft
- **Why?** new technique (determinants, volume sampling, compound matrices, etc.)
- **Effect on current work:** Does it clarify algorithm? Does it affect error analysis roadmap?
- **Questions for Frank:** Does this align with his April 2026 draft? Should we cite it?

### 5. Commit
```bash
git add MAIN_BOUND_<Authors>_<Year>.md
git commit -m "Extract main bound (<Theorem N>) from <Authors> <Year>: <one-line description>"
```

## Examples

### deHoog-Hegland 2025 Submission
- **File:** `deHoog-Hegland-2025-CUR-concentration-bounds.pdf`
- **Main theorem:** Theorem 4 (Interpolation Error Bound for Oversampling)
- **Key insight:** Bound decreases linearly from (k+1)² to (k+1) as r goes from k to m
- **Document created:** `MAIN_BOUND_deHoog_Hegland_2025.md`
- **Commit:** "Extract Theorem 4 from deHoog-Hegland 2025: interpolation error bound for CUR with oversampling"

### FdH2024 Paper (Corollary 1)
- **File:** `FdH2024_Dec16.pdf` (already in project)
- **Main theorem:** Corollary 1 (Expected error bound for uniform sampling)
- **Key structure:** Two factors — absolute (k+1)² term and relative term times SVD error
- **Document:** `THEORETICAL_BOUND_r_equals_k.md`, `BOUND_AS_FACTOR_TIMES_SVD.md` (already created)

## Pitfalls

| Pitfall | Fix |
|---------|-----|
| PDF has no pdftotext support (scanned, security) | Use vision tool to manually read theorem statement |
| Multiple theorems, unclear which is "main" | Read abstract and conclusion; ask "which bound is the paper claiming?" |
| Math notation too complex to extract | Take screenshot of PDF, paste into doc, then manually rewrite in Unicode for Telegram |
| Bound statement spans 3+ pages | Capture the core inequality; reference page number in document for full context |
| Created doc but forgot to commit | Add to git immediately before session ends (or before Monday meeting) |

## Related
- **`pdf-generation-xelatex-workflow`** — If bound doc needs to become a polished PDF for the meeting
- **`fdhh-weekly-meeting-workflow`** — Main workflow; this is the pre-meeting prep sub-task
