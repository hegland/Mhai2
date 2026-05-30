# Formula Extraction from Academic PDFs: Pitfalls & Best Practices

## Problem Statement

When extracting mathematical theorems, bounds, or formulas from PDF papers:
- **pdftotext + grep** produces plain text that mangles notation
- Multi-line formulas get concatenated or lose structure
- Subscripts, superscripts, fractions become ambiguous
- **Result:** You synthesize a plausible-looking but WRONG formula

## Real Example: deHoog-Hegland 2025 CUR Bound

**Session:** May 30, 2026 (FdHMH project)  
**Task:** Extract Theorem 4 (main interpolation bound for CUR with oversampling)

### What Went Wrong

Used pdftotext → extracted plain text:
```
E ∥CUR − M ∥2F ≤ [(m−r)/(m−k) (k + 1)2 + (k + 1)/(m−k)] · ‖Ck+1 (M )‖2F / ‖Ck (M )‖2F
```

Synthesized this as:
```
E{‖M̃_CUR − M‖_F²} ≤ [(m−r)/(m−k)·(k+1)² + (k+1)] · ‖C_(k+1)(M)‖_F² / ‖C_k(M)‖_F²
```

**User caught error immediately:** "This bound is wrong, please look carefully."

### What Was Actually in the PDF

```
E{‖M̃_CUR − M‖_F²} ≤ [(m−r)/(m−k)·(k+1)² + (r−k)/(m−k)·(k+1)] · ‖C_(k+1)(M)‖_F² / ‖C_k(M)‖_F²
```

**The missing term:** `(r−k)/(m−k)` in the second interpolation factor.

### Why This Matters

The bound's entire behavior depends on the `(r−k)/(m−k)` term:
- At r=k (no oversampling): factor = (k+1)² / (m−k) · [(m−k)(k+1)] = (k+1)²
- At r=m (full oversampling): factor = (k+1)/(m−k) · [(m−k)] = (k+1)
- **Linear interpolation between k and m only works if the second term has (r−k)**

Without it, the bound looks qualitatively wrong.

## Correct Workflow

### For Theorem/Bound Extraction (Every Time)

1. **Locate with pdftotext (text search only):**
   ```bash
   pdftotext paper.pdf - | grep -n "Theorem 4"
   # Output: page 26, line 543
   ```

2. **Open PDF in browser and navigate to exact page:**
   ```bash
   browser_navigate("file:///absolute/path/to/paper.pdf")
   browser_type(page_input_ref, "26")
   browser_press("Enter")
   ```

3. **Use browser_vision to read the formula visually:**
   ```bash
   browser_vision("Show me Theorem 4 clearly. What is the exact bound formula?")
   ```

4. **Transcribe exactly what you see** — don't synthesize or simplify:
   - Copy the formula as it appears
   - Include all terms, all parentheses, all fractions
   - If you're unsure about a symbol, zoom in or ask again
   - Verify dimensions: are both sides of ≤ compatible?

### Example Usage in Code

```python
# In Julia/MATLAB/Python: extract and verify
theorem_4_bound = """
E{‖M̃_CUR − M‖_F²} ≤ [(m−r)/(m−k)·(k+1)² + (r−k)/(m−k)·(k+1)] · ‖C_(k+1)(M)‖_F² / ‖C_k(M)‖_F²
"""

# Check dimensional consistency
# LHS: squared Frobenius norm (scalar, nonnegative)
# RHS: (dimensionless factor) × (squared norms ratio) → scalar ✓

# Check limiting behavior
# At r=k: (k+1)/(m−k) · [(m−k)(k+1)] = (k+1)² ✓
# At r=m: (k+1)/(m−k) · [(m−k)] = (k+1) ✓
```

## Red Flags: When pdftotext Output is Suspicious

- **Incomplete parentheses or mismatched brackets** → formula is broken
- **Terms appearing on separate lines** → might be part of same expression
- **Fractions with / instead of proper fraction bars** → structure unclear
- **Subscripts/superscripts as separate characters** → notation lost
- **Formula "looks right" on first read but violates dimensional analysis** → hidden error (most dangerous)

**Default:** If you extracted a formula and it looks plausible, **verify it visually anyway**. The cost is 10 seconds; the risk of propagating a wrong bound into analysis/code is hours.

## When pdftotext Is Safe

- Finding section/theorem labels ("locate Theorem 4")
- Extracting author names, dates, publication info
- Summarizing abstract or introduction (plain text)
- Finding page references or citations

## When Browser Vision Is Required

- **Any mathematical formula** that will be used in code or analysis
- **Bounds, inequalities, error expressions**
- **Complex notation** with multiple subscripts/superscripts
- **Multi-line structures** (systems, matrices, fractions)
- **Lemmas and theorems** with precise conditions

## Session Context: FdHMH CUR Research

This mistake occurred while preparing for a Monday meeting with Frank de Hoog (CSIRO) on CUR decomposition theory. The bound in Theorem 4 is central to understanding how oversampling improves the interpolation factor. Getting it wrong would have propagated into:
- Meeting notes and talking points
- Analysis documents comparing bounds to empirical results
- Future Julia/Octave validation code

**Lesson:** Mathematical accuracy is non-negotiable in research contexts. Use visual verification, always.

## Implementation: Add to Future Workflows

When loading the `papers` skill for extracting theorems/bounds:
1. Use pdftotext only for navigation (find location)
2. Switch to browser_vision for formula reading
3. Verify dimensional consistency before moving forward
4. Commit extracted content to git with source page numbers
