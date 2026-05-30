# VRZM26 Project Structure & Workflows

## Root Directory: ~/Desktop/VRZM26/

### Key Directories

| Path | Purpose |
|------|---------|
| `src/` | IAS algorithm code (Julia) |
| `src/IAS-code/` | Core IAS implementation |
| `research/tasks/` | Experiments (first_shell_investigation, etc.) |
| `research/tasks/first_shell_investigation/experiments/` | Ex1, Ex3, Experiment3 — main test suite |
| `data/` | Input/output data files (MAT format) |
| `lit/` | Literature references (PDFs) |
| `reference/` | Reference implementations (Octave/MATLAB) |
| `dev/` | Development utilities |

### Key Files

| File | Purpose |
|------|---------|
| `Project.toml` / `Manifest.toml` | Julia dependencies (CairoMakie, KernelDensity, MAT) |
| `README.md` | Quick start guide (ex1, ex3 commands) |
| `sphere_packing_report_analysis.md` | Latest analysis (hyperuniformity, boundary effects) |
| `sphere_packing_report_analysis.pdf` | Generated PDF report |

### Quick Start Commands

**Ex1: End-to-end T11→T12 with reference check**
```bash
cd ~/Desktop/VRZM26/research/tasks/first_shell_investigation/experiments
julia --project=. ex1.jl
```

**Ex3: Start T12 after first three spheres from T11, plot radial density**
```bash
cd ~/Desktop/VRZM26/research/tasks/first_shell_investigation/experiments/Experiment3
julia --project=. ex3.jl
# Output: radial_density.png
```

### File Exchange Protocol

- **Julia → Octave:** Write state to `T1_input.mat`
- **Octave → Julia:** Write output to `T1_output.mat`
- **Temporary:** `T11_output.mat` (read and deleted by Julia)

### Key Collaborator

- **Zbigniew Stachurski** (ANU) — sphere packing research lead

### Recent Focus: Hyperuniformity

See `sphere_packing_report_analysis.md` (lines 211–360):
- **Torquato 2026 paper:** `lit/Torquato2026_NatureReviewsPhysics.pdf`
- Test: Compute structure factor S(k) for IAS
- Question: Does 3-contact rule suppress density fluctuations?
- Status: Awaiting Torquato 2026 paper analysis

### Git Workflow

Auto-commits on file save; check recent history:
```bash
cd ~/Desktop/VRZM26 && git log --oneline -10
```
