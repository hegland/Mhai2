---
name: julia
description: "Run Julia code or scripts in Markus's FdHMH/CodeMH working directory."
version: 1.0.0
author: Mhai2
platforms: [linux]
metadata:
  hermes:
    tags: [Julia, Research, Computation, VRZM26, FdHMH]
---

# Julia Execution

Run Julia code for Markus's research. The working directory is `~/Desktop/FdHMH/CodeMH/`.
Julia is installed via juliaup at `~/.juliaup/bin/julia`.

## Run a code snippet

```bash
cd ~/Desktop/FdHMH/CodeMH && cat > /tmp/mhai2_snippet.jl << 'JULIAEOF'
<code here>
JULIAEOF
~/.juliaup/bin/julia --project=@. /tmp/mhai2_snippet.jl
```

## Run an existing script

```bash
cd ~/Desktop/FdHMH/CodeMH && ~/.juliaup/bin/julia --project=@. ~/Desktop/VRZM26/path/to/script.jl
```

## After running — check for new images

```bash
ls -lt ~/Desktop/FdHMH/CodeMH/*.png ~/Desktop/FdHMH/CodeMH/*.svg 2>/dev/null | head -5
```

Send any new images to Markus using the send_file tool or by reading them.

## Julia Documentation Quirks

**Frobenius norm:** According to LinearAlgebra docs: `norm(A, 2)` on a matrix gives the Frobenius norm (not spectral). Do NOT use `norm(A)` (defaults to spectral) or `norm(A, :fro)` (symbol notation doesn't work for matrices). Always use explicit `norm(A, 2)` for matrix Frobenius norms in your code and documentation.

**Formatted output (@printf):** To use `@printf()` for table formatting, **always** `using Printf` at the top of the script. PITFALL: Forgetting `using Printf` causes `UndefVarError: @printf not defined in Main` at runtime.

**Code format for Telegram:** When sending Julia code to Markus via Telegram, treat it as Unicode text (not file attachment). Include full Unicode symbols (×, ̃, ✓, α, etc.) — Julia handles them natively. If code is needed in a file, ask first or create it in the project directory.

## Output Formatting Rule

**All tabular output must use markdown table syntax**, not raw terminal formatting. This allows output to be pasted directly into markdown documents without conversion.

✓ **Good:**
```julia
println("| k | % of n | Frob. Error (mean) | Frob. Error (std) | Rel. Error (mean) | Rel. Error (std) | Error/Tail (mean) | Error/Tail (std) |")
println("|---:|---:|---:|---:|---:|---:|---:|---:|")
for r in results
    @printf("| %d | %.2f | %.4e | %.2e | %.4f | %.4f | %.4f | %.4f |\n",
            r.k, r.k_percent, r.mean_frob, r.std_frob, r.mean_rel, r.std_rel, r.mean_norm_ratio, r.std_norm_ratio)
end
```

❌ **Bad:**
```julia
println("k    | % of n | Frobenius Error (mean ± std) | ...")
@printf("%4d | %5.2f | %15.4e ± %8.2e | ...\n", ...)
```

## Parametric Testing Pattern

For sweeping a parameter over a range (e.g., sampling sizes k ∈ {2¹, 2², …, 2ⁿ}), use a loop with pre-computed invariants and result collection:

1. **Pre-compute once** before the loop: eigenvalues, matrix norms, or other loop-invariant values
2. **Collect results** in an array of NamedTuples, storing raw values and rounded summaries separately
3. **Format output** after collection using `@printf` with appropriate format strings for scientific/decimal notation
4. **Storage:** Store both full precision (for analysis) and rounded values (for display)

See `references/parametric-sweep-template.jl` for a complete example (powers-of-2 sampling with eigenvalue tail analysis).

## Notes
- Filter precompilation noise from stderr: ignore lines with "Precompiling", "Progress", "✓", "─"
- Timeout: 120 seconds
- If packages are missing, run: `cd ~/Desktop/FdHMH/CodeMH && ~/.juliaup/bin/julia --project=@. -e 'using Pkg; Pkg.instantiate()'`
- For VRZM26 scripts, the workdir may be `~/Desktop/VRZM26/` — check the script's header
