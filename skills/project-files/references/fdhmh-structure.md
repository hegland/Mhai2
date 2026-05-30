# FdHMH Project Structure & Workflows

## Root Directory: ~/Desktop/FdHMH/

### Key Directories

| Path | Purpose |
|------|---------| 
| `CodeMH/` | Julia code for experiments (volume sampling vs. uniform sampling) |
| `CodeMH/plots/` | Output plots from experiments |
| `lit/` | Literature PDFs and research notes |
| `projects/` | Draft PDFs received externally |
| `transcripts/` | Zoom meeting summaries (weekly, one per Monday) |

### Key Files

| File | Purpose |
|------|---------| 
| `FdH2024_Dec16.tex` | Live manuscript (main working document) — error bounds for CUR with SRHT preprocessing |
| `frank_summary.md` | Executive summary of research (248 lines, CUR/Nyström fundamentals) |
| `MONDAY_MEETING_PREP.md` | Meeting prep guide — use before each Monday call with Frank |
| `ALGORITHM_REFERENCE.md` | Quick visual guide to the algorithm (3-step process) |
| `INDEX.md` | Navigation map for the entire project |
| `.git/` | Version control (development branch) |
| `CLAUDE.md` | Code guidelines and workflow documentation |

### Meeting Schedule

- **Frequency:** Weekly Mondays at [time TBD]
- **Duration:** 45 minutes (typical)
- **Collaborator:** Frank de Hoog (CSIRO, deh009) — co-author on CUR/Nyström research
- **Last meeting:** May 18, 2026 (algorithm clarified, Frank tasked with literature review)
- **Next meeting:** May 25, 2026

### The Algorithm (CUR/Nyström with Incoherence)

**Step 1:** Apply Hadamard transform (SRHT) to make matrix incoherent  
**Step 2:** Uniform sampling (not volume sampling) of k rows/columns  
**Step 3:** CUR approximation: C · U⁻¹ · Rᵀ  

**Error bound:** E[‖M − M_approx‖²_F] ≤ C(r,k) · ‖M − M_k‖²_F

**vs. Halko-Tropp:** Uses volume sampling on Gaussian transforms; HH/FdH uses uniform sampling on Hadamard transforms (simpler, cleaner analysis, potentially cheaper).

### Quick Start Commands

**Run Julia experiments:**
```bash
cd ~/Desktop/FdHMH/CodeMH && julia --project=@. volume_vs_uniform.jl
```

**Build manuscript PDF:**
```bash
cd ~/Desktop/FdHMH
pdflatex FdH2024_Dec16.tex
bibtex FdH2024_Dec16
pdflatex FdH2024_Dec16.tex
pdflatex FdH2024_Dec16.tex
```

**Check git history:**
```bash
cd ~/Desktop/FdHMH && git log --oneline -10
```

### Workflow: Monday Meetings

1. **Before:** Read `MONDAY_MEETING_PREP.md` to review previous meeting, check Frank's action items, prepare questions
2. **During:** Use suggested 5 questions; document discussion with meeting notes template
3. **After:** Save Zoom transcript as `transcripts/YYYY-MM-DD_Frank_Zoom.txt`, commit to git

### Key Collaborator

- **Frank de Hoog** (deh009, CSIRO) — co-author; responsible for literature review, error analysis, algorithm characterization
  - Status: New laptop being set up (LaTeX + Python/Anaconda); CSIRO honorary fellowship may not be renewed
  - Action items (May 18): Write algorithm, study Halko-Tropp, review incoherence bounds, set up laptop

### Research Context

**Problem:** Approximate an n × n PSD matrix using only k rows and columns (not the full matrix).

**Solution:** CUR/Nyström method with Hadamard preprocessing to ensure incoherence, then uniform sampling.

**Innovation:** Simpler algorithm than existing methods; tighter error analysis via compound incoherence; potentially faster computation.

**Manuscript status:** In preparation; error bounds and SRHT preprocessing being finalized.

### Git Workflow

- **Branch:** development (primary working branch)
- **Recent commits:** Meeting prep documents + algorithm reference (May 30, 2026)
- **Status:** 2 commits ahead of origin/development
- **Protocol:** Auto-commit after each Monday meeting with summary line "Add notes from [DATE] Monday meeting with Frank"

### Files to Review Before Meetings

- **MONDAY_MEETING_PREP.md** (must-read before Monday call)
- **frank_summary.md** (10-min overview of research)
- **ALGORITHM_REFERENCE.md** (5-min visual guide)
- Recent commits (last 5–10) via `git log --oneline`

### Common Questions

**Q: What are Frank's action items?**  
A: See `MONDAY_MEETING_PREP.md`, "Frank's Action Items" section. Current status as of May 18: algorithm characterization (in progress), Halko-Tropp review (pending), laptop setup (in progress).

**Q: How do I prepare for a Monday meeting?**  
A: (1) Read `MONDAY_MEETING_PREP.md`; (2) review status of Frank's action items; (3) prepare error bound formulas; (4) check Julia code runs.

**Q: Where are experimental results?**  
A: `CodeMH/plots/` and `CodeMH/mhai_test.png` (volume vs. uniform sampling experiments).

**Q: How do I save a meeting transcript?**  
A: Save as `transcripts/YYYY-MM-DD_Frank_Zoom.txt` (see template in `MONDAY_MEETING_PREP.md`), then `git add` and commit with message "Add notes from [DATE] Monday meeting with Frank".

### Next Steps (May 30 → June)

- Check Frank's progress on algorithm characterization, literature review, laptop setup
- Finalize error bound proofs for manuscript
- Run computational experiments (speedup vs. Halko-Tropp)
- Prepare for submission
