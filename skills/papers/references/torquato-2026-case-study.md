# Torquato Papers on Sphere Packing & Hyperuniformity — VRZM26 Case Study

**Session:** May 30, 2026  
**Project:** VRZM26 (Sphere packing, IAS algorithm)  
**Goal:** Understand jamming, hyperuniformity, and contact networks for IAS validation

---

## Workflow Summary

1. **Discovery:** Found 4 key Torquato papers on sphere packing/hyperuniformity via arXiv author search
2. **Bulk download:** All 4 PDFs to `~/Desktop/VRZM26/lit/` with descriptive names (21.8 MB total)
3. **Reading guide:** Created `TORQUATO_READING_GUIDE.md` with 4 paper summaries + implementation checklist
4. **Analysis doc:** Created `TORQUATO2018_KEY_INSIGHTS.md` with key concepts + computational methods
5. **Git commit:** All papers + guides committed with clear message

**Result:** Structured pathway from theory → implementation for testing IAS hyperuniformity

---

## Papers Curated

| arXiv | Title | Size | Key Contribution |
|-------|-------|------|-----------------|
| 1805.04468 | Basic Understanding of Condensed Phases | 8.6 MB | Jamming, contact networks, phase diagram |
| 2103.14989 | Structural Characterization of Hyperuniform States | 480 KB | S(k) detection, Fourier methods |
| 2204.11345 | Extraordinary Disordered Hyperuniform Composites | 8.3 MB | Physical properties, robustness |
| 2504.16924 | Ultradense Sphere Packings from Stealthy Hyperuniform | 4.5 MB | Density optimization, latest methods |

---

## Reading Guide Structure (4 Sections)

```
Paper 1 — Foundations
  Why: Establishes terminology (jamming, Z̄, φ, order maps)
  Key sections: Sec. II (definitions), III.A–E (jammed states)
  Extract: Jamming definition, contact number ranges, phase diagram
  Hours: ~2 hours

Paper 2 — Methodology ⚡ CRITICAL
  Why: Provides S(k) computation algorithms
  Key sections: Fourier representation, B/A ratio, hyperuniformity test
  Extract: FFT-based structure factor calculation
  Hours: ~1.5 hours

Paper 3 — Applications
  Why: Shows why hyperuniformity matters physically
  Key sections: Material properties, defect tolerance, robustness
  Extract: Physical implications, how hyperuniformity changes behavior
  Hours: ~1 hour

Paper 4 — Latest
  Why: State-of-the-art approach to dense packings
  Key sections: Stealthy potentials, density results
  Extract: Are IAS outputs similar to stealthy hyperuniform systems?
  Hours: ~1.5 hours

Total: ~5–6 hours (skim) to 8–10 hours (deep)
```

---

## Implementation Checklist (from papers)

Each item maps to a paper section:

- [ ] **Contact Number Analysis** (paper 1, Sec. III.D)
  - [ ] Compute Z̄ distribution in IAS packings
  - [ ] Check if Z̄ → 6 (2D) or 12 (3D) at convergence
  - [ ] Plot histogram of Z per particle

- [ ] **Hyperuniformity Test** (paper 2, Sec. on S(k))
  - [ ] Extract IAS particle coordinates
  - [ ] Compute S(k) via FFT
  - [ ] Fit S(k) ~ k^α for small k
  - [ ] Compare α to known systems (FCC, MRJ, random)
  - [ ] Document α value and conclusion

- [ ] **Packing Fraction Analysis** (paper 1, Sec. III.A)
  - [ ] Compute φ achieved by IAS
  - [ ] Compare to MRJ (0.64) and FCC (0.74)
  - [ ] Plot φ vs. number of spheres (convergence)

- [ ] **Order Characterization** (papers 1, 2)
  - [ ] Compute pair correlation g(r)
  - [ ] Measure correlation length ξ_c
  - [ ] Quantify disorder vs. order on spectrum

- [ ] **Stealthy Connection** (paper 4)
  - [ ] Analyze if IAS resembles stealthy hyperuniform states
  - [ ] Check long-wavelength suppression (low-k behavior in S(k))

---

## Key Formulas Extracted

### Packing Fraction
$$\varphi = \rho v_1 \quad \text{where } \rho = N/V, \, v_1 = \text{particle volume}$$

### Contact Number
$$Z = \text{mean number of contacting neighbors per particle}$$

### Structure Factor
$$S(\mathbf{k}) = 1 + \rho \int e^{i\mathbf{k}\cdot\mathbf{r}} [g(\mathbf{r}) - 1] d\mathbf{r}$$

### Hyperuniformity Condition
$$S(\mathbf{k} \to 0) = 0 \quad \Rightarrow \quad \text{S(k) ~ k^α for α > 0}$$

### Pressure in Hard Spheres (3D)
$$p = 1 + 4 \varphi g_2(D^+) \rho k_B T$$
where $g_2(D^+)$ = contact value of pair correlation

---

## Output Artifacts Created

**From this session:**

1. **Reading Guide:** `~/Desktop/VRZM26/lit/TORQUATO_READING_GUIDE.md`
   - 4 paper summaries + reading timeline
   - Implementation checklist (8 items)
   - Quick formulas
   - Follow-up questions

2. **Theory Analysis:** `~/Desktop/VRZM26/research/TORQUATO2018_KEY_INSIGHTS.md`
   - 10 sections on jamming/packing theory
   - Phase diagrams
   - Hyperuniformity framework
   - Computational methods
   - Questions specific to IAS

3. **Git commits:**
   - `ffd6c72` — Add all 4 Torquato papers
   - `4076bf9` — Add reading guide

---

## Lessons for Future Sessions

1. **Always pair bulk downloads with a reading guide.** A folder of 5 PDFs without prioritization is debt. The guide creates accountability and prevents "I have these papers but haven't read them" freeze.

2. **Reading guides should feed directly into implementation checklists.** Each paper section → extraction task → code task. No abstract "learn stuff" phase.

3. **Use descriptive file names** (`Author2025_Topic.pdf`, not `paper5.pdf`). Makes it easy to reference during reading.

4. **Create a separate analysis/theory document** (TORQUATO2018_KEY_INSIGHTS.md) alongside the reading guide. The guide is "how to read", the theory doc is "what this means for your code".

5. **Commit papers + guides together.** Future you (or Zbigniew) can trace exactly which papers informed which design decisions.

---

## Connection to VRZM26 IAS Work

**Questions you can now answer after reading these papers:**

- Is IAS fundamentally a jamming algorithm? (Yes — 3-contact rule is a jamming constraint)
- Can you test if IAS creates hyperuniform packings? (Yes — compute S(k) via FFT)
- Where does IAS sit on the spectrum (random ↔ crystalline)? (Compute φ, Z̄, order parameters)
- Should you expect IAS to be defect-tolerant? (Yes — if hyperuniform, should be robust)

---

## Status

- ✅ All papers downloaded and organized
- ✅ Reading guide created
- ✅ Implementation checklist written
- ⏭️ Ready for: Implement S(k) structure factor calculation in Julia

---

**This document serves as a template for future paper curation workflows in VRZM26, FdHMH, and XiChen26honors projects.**
