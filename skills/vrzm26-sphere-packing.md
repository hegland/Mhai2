---
name: vrzm26-sphere-packing
title: VRZM26 — Sphere Packing & IAS Algorithm Research
description: |
  Research project on sphere packing and IAS algorithm analysis.
  Collaboration with Zbigniew Stachurski (ANU). Workdir: ~/Desktop/VRZM26/
trigger: ["VRZM26", "sphere packing", "IAS algorithm", "Voronoi cluster", "local density", "coordination number"]
---

# VRZM26 — Sphere Packing & IAS Algorithm

**Project:** Sphere packing optimisation via the IAS (Iterative Adaptive Sphere) algorithm  
**Collaborator:** Zbigniew Stachurski (ANU, Canberra) — zh.stachurski@proton.me  
**Markus role:** Primary researcher  
**Project root:** `~/Desktop/VRZM26/`  
**Deadline:** Friday 2026-06-06 — results to Zbigniew

---

## RULE: New code goes in the new directory only

All new code for Zbigniew's request goes in:

```
~/Desktop/VRZM26/research/tasks/cluster_volume/
```

Existing scripts elsewhere are **read-only**. Do not modify them. Do not move them. Do not touch them.

---

## Directory Map (actual structure on disk)

```
~/Desktop/VRZM26/
├── data/
│   ├── IAS_packing_100.mat          ← SMALL TEST DATA (use this first)
│   ├── IAS_packing_1000.mat
│   ├── IAS_packing_2000.mat
│   ├── IAS_packing_5000.mat
│   ├── IAS_packing_10000.mat
│   ├── IAS_packing_100000.mat
│   └── IAS_packing_200000.mat
├── src/
│   ├── main_IAS.jl                  ← IAS simulation runner (DO NOT MODIFY)
│   └── IAS-code/                    ← original Octave/MATLAB source (DO NOT MODIFY)
├── research/
│   └── tasks/
│       ├── density_investigation/
│       │   ├── local_density.jl     ← KEY: Voronoi cell volume computation
│       │   └── coordination_number.jl (in shell_dependence/)
│       ├── shell_dependence/
│       │   ├── coordination_number.jl  ← KEY: coordination numbers + shell grouping
│       │   └── coord_hist_by_shell.jl  ← KEY: template for shell-grouped plots
│       └── cluster_volume/          ← NEW WORK GOES HERE
│           ├── session_state_2026-06-03.md  ← prior session context
│           └── discussion_notes.md
├── emails/
│   └── email_Wed,3Jun_Markus_Hegland_Markus.Hegland@.txt  ← Zbigniew's request
└── cluster_volume.jl                ← earlier attempt at root level (reference only)
```

---

## RULE: Voronoi computation — use DirectQhull only

The VRZM26 Julia project uses `DirectQhull.jl` for Voronoi tessellation. It is installed and working.

**Never use `VoronoiCells.jl`, `Qhull.jl`, or any other Voronoi package.** They are not installed and will fail.

The exact working pattern, taken from `local_density.jl`:

```julia
using DirectQhull

vor = Voronoi(Matrix(transpose(points)))  # points is (N,3); Voronoi expects (3,N)

for i in 1:N
    region_idx = vor.point_region[i]
    vertex_indices = vor.regions[region_idx]
    if 0 ∉ vertex_indices          # 0 = infinite cell — skip boundary points
        verts = hcat([vor.vertices[:, v] for v in vertex_indices]...)
        hull = ConvexHull(verts)
        volume = hull.volume        # Voronoi cell volume for point i
    end
end
```

Copy this pattern. Do not modify it. Do not substitute another package.

Similarly for coordination numbers, use `NearestNeighbors.jl` (KDTree) exactly as in `coordination_number.jl` — it is installed and working.

To run a Julia script in the VRZM26 project environment:
```bash
cd ~/Desktop/VRZM26 && julia --project=. path/to/script.jl
```

## Code Summary — Key Existing Julia Scripts

| File | Reads | Computes | Outputs |
|------|-------|----------|---------|
| `research/tasks/density_investigation/local_density.jl` | .mat → `S_coord` | Voronoi cell volumes via DirectQhull; density = (4π/3)/cell_vol | volumes[], dist_to_origin[]; plots density vs distance |
| `research/tasks/shell_dependence/coordination_number.jl` | .mat → `S_coord`, `S_shell` | KDTree neighbours within cutoff 2.0+ε; coordination number per ball | coordination_numbers[]; plots by shell |
| `research/tasks/shell_dependence/coord_hist_by_shell.jl` | .mat → `S_coord`, `S_shell` | 2D histogram: coord number × shell | stacked bar chart by shell |

**Data structure in .mat files:**
```
IAS_packing [struct 1x1]
  └── S_coord    — (N,3) sphere centres
  └── S_shell    — (N,1) shell index per sphere
  └── S_r        — radii (check if present; code assumes radius=1 if absent)
  └── number_of_sphere, S_num, ...
```
Read with Octave: `bash ~/.hermes/skills/mhai2/project-files/scripts/read_mat.sh <file.mat>`

---

## Small Test Dataset

Always develop and test on the small dataset first. Use files that contain **both** `S_coord` and `S_shell` — the `data/` directory files do NOT have shell index.

```
research/tasks/new IAS algorithm/data/IAS_packing69_sim5.mat    (69 spheres, has S_shell)
research/tasks/new IAS algorithm/data/IAS_packing391_sim6.mat   (391 spheres, has S_shell)
research/tasks/shell_dependence/IAS_packing2669_sim7.mat        (2669 spheres, has S_shell)
```

Files in `~/Desktop/VRZM26/data/` only have `S_coord` — no shell index — do not use them for shell-dependent analysis.

Run new code on the 69-sphere file first. Verify output looks reasonable. Then scale up.

---

## Workflow: Claude Code writes, Mhai runs

All new Julia code for VRZM26 is written and tested by Markus using Claude Code.
Mhai's role is to **run existing scripts and report results**.

When asked to do something requiring new code: say "I can't write new code reliably —
develop it with Claude Code first, then I'll run it."

When asked to run a script: use the exact command from CODE_SUMMARY.md in the task directory.

## Completed work — cluster_volume task (2026-06-04)

Scripts in `research/tasks/cluster_volume/` — read CODE_SUMMARY.md there for full details.

To rerun the full analysis:
```
cd ~/Desktop/VRZM26 && julia --project=. research/tasks/cluster_volume/stage3.jl
```
Produces three plots in `research/tasks/cluster_volume/`. Runtime ~5 minutes.

## Current Task: Zbigniew's Request (2026-06-03 email)

**Request:** Extend analysis to include Voronoi volume of each cluster type, to complement Figure 2(b) (coordination number histogram by shell).

**Definitions:**
- Cluster for ball i = ball i + all balls touching it
- Cluster Voronoi volume = sum of Voronoi cell volumes for all balls in the cluster
- Local density of ball i = (4π/3) / Voronoi cell volume of ball i

### Three-stage plan (approved)

**Stage 1 — Per-ball data table** (cut-and-paste from existing scripts, no debugging expected)

Build a table with one row per ball:
- Point index i
- Shell index (from S_shell)
- Local density = (4π/3) / Voronoi_cell_volume_i
- Coordination number (touching neighbours, cutoff = 2.0 + 1e-8)
- List of neighbour indices

Source: `local_density.jl` (Voronoi) + `coordination_number.jl` (KDTree neighbours).  
Output: save as `research/tasks/cluster_volume/per_ball_data_100.csv` (for small set).  
Validation: compare local density values against `local_density.jl` output on same file.

**Stage 2 — Touching neighbourhood per ball** (also cut-and-paste)

For each ball, store: degree (= coordination number) and the sorted list of neighbour indices.  
This is already computed as a side-effect of Stage 1.  
Output: save as `research/tasks/cluster_volume/neighbours_100.csv`.  
Validation: compare degree column against Stage 1 coordination numbers — must match exactly.

**Stage 3 — Cluster Voronoi volume**

For each ball i:
- cluster_voronoi_vol[i] = sum of Voronoi_cell_volume[j] for j in {i} ∪ neighbours[i]

Group by coordination number. Compute mean and std per group, optionally per shell.  
Plot: mean cluster Voronoi volume vs coordination number, style similar to coord_hist_by_shell.jl.  
Output: plot saved to `research/tasks/cluster_volume/cluster_vol_vs_coord.png`.

---

## Checkpoint Protocol for This Task

After each stage completes:
1. Append a brief status update to `research/tasks/cluster_volume/session_state_<date>.md`
2. `git add research/tasks/cluster_volume/ && git commit -m "cluster_volume: stage N complete"`
3. Report to Markus with one-line summary and any output values

---

## Starting a Session

The project root is always: `/home/hegland/Desktop/VRZM26/`
Never use `~` — always use the full path above.

First thing every session:
```bash
ls /home/hegland/Desktop/VRZM26/research/tasks/
cat /home/hegland/Desktop/VRZM26/research/tasks/cluster_volume/CODE_SUMMARY.md
```

---

## See Also

- **project-files** — Read/search VRZM26 files
- **git-ops** — Commit and push results
- **julia** — Run Julia scripts in working directory
