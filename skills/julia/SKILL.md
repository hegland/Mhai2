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

## Notes
- Filter precompilation noise from stderr: ignore lines with "Precompiling", "Progress", "✓", "─"
- Timeout: 120 seconds
- If packages are missing, run: `cd ~/Desktop/FdHMH/CodeMH && ~/.juliaup/bin/julia --project=@. -e 'using Pkg; Pkg.instantiate()'`
- For VRZM26 scripts, the workdir may be `~/Desktop/VRZM26/` — check the script's header
