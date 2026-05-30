# FdHMH Terminology & Conventions

## Matrix Decomposition Method

**Algorithm:** CUR decomposition with uniform sampling + Moore-Penrose inverse.

**Key terms:**
- **Hadamard transform** (NOT "ADAMAR") — subsampled randomized Hadamard; used to make matrices incoherent
- **Moore-Penrose inverse** — generalized inverse denoted A⁺
- **Incoherent matrix** — matrix satisfying incoherence property; allows uniform sampling to work as well as volume sampling
- **Minimal norm least-squares solution** — used when solving linear systems like A X = R

## Code Implementation

**Language pair:** Julia + Octave (not proprietary MATLAB)
- Julia files: `.jl` extension (modern syntax, scientific computing)
- Octave files: `.m` extension (compatible with MATLAB syntax, open source)
- Both stored in `CodeMH/` directory

## Weekly Meeting Schedule

**Day:** Monday (recurring)  
**Participants:** Markus Hegland (ANU) + Frank de Hoog (deh009, CSIRO)  
**Duration:** ~45 minutes  
**Format:** Zoom call; transcript saved to `transcripts/YYYY-MM-DD_Frank_Zoom.txt`

**Meeting prep workflow:**
1. Save Zoom transcript to `transcripts/`
2. Create `YYYY-MM-DD_ANALYSIS.md` with progress metrics + action items
3. Build algorithm spec incrementally (see "Building Algorithm Specifications" in main skill)
4. All documents git-tracked on `development` branch

## Algorithm Status (as of June 1, 2026)

**Completed:**
- Algorithm definition (input, steps, computation) — see `2026-06-01_MEETING_PREP.md`
- Julia implementation — `CodeMH/cur_approximation.jl`
- Octave implementation — `CodeMH/cur_approximation.m`

**In progress:**
- Error bounds analysis (Hanson-Wright inequality)
- Comparison with Halko-Tropp volume sampling
- Finding "Polish author's lemma" reference

**Next milestones:**
- Formalize 2-line algorithm characterization (PSD case)
- Numerical experiments validating bounds
- Manuscript section draft

## Collaborators

**Frank de Hoog (deh009)**
- CSIRO (Australia)
- Expertise: randomized numerical linear algebra, matrix approximation
- Email: not integrated (use Markus as intermediary for coordination)
- Administrative note: honorary fellowship at risk (budget constraints, May 2026); exploring visiting fellow backup position

**Markus Hegland**
- ANU Canberra (Australian National University)
- Personal email: markus.hegland@gmail.com (integrated)
- Work email: markus.hegland@anu.edu.au (Outlook, not integrated)
