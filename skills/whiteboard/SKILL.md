---
name: whiteboard
description: "Append notes to the research whiteboard, show contents, or render it as a PDF/PNG."
version: 1.0.0
author: Mhai2
platforms: [linux]
metadata:
  hermes:
    tags: [Research, Whiteboard, Notes, FdHMH, VRZM26]
---

# Research Whiteboard

The whiteboard is a markdown file at `~/projects/Mhai2/whiteboard.md`.
It is for accumulating research notes, conjectures, and mathematical observations during a session.
Use proper LaTeX inside the whiteboard (it is rendered with pandoc, not displayed in Telegram).

## Append to whiteboard

```bash
cat >> ~/projects/Mhai2/whiteboard.md << 'EOF'

## Topic or date

Content here. Use LaTeX: $\|M - M_{CUR}\|_F^2 \leq C(r,k) \|M - M_k\|_F^2$

EOF
```

Or via Python:
```bash
cd ~/projects/Mhai2 && python3 -c "
from mhai_skills import whiteboard_append
whiteboard_append('''## New note\n\nContent here.\n''')
"
```

## Show whiteboard contents

```bash
cat ~/projects/Mhai2/whiteboard.md
```

## Render to PDF and send

```bash
cd ~/projects/Mhai2 && python3 -c "
from mhai_skills import whiteboard_render_png
pages = whiteboard_render_png()
for p in pages:
    print(p)
"
```
Then send the resulting PNG files to Markus.

## Save whiteboard to knowledge base

```bash
cd ~/projects/Mhai2 && python3 -c "
from mhai_skills import whiteboard_save
print(whiteboard_save('sphere_packing_session'))
"
```

## Clear whiteboard

```bash
echo -n > ~/projects/Mhai2/whiteboard.md && echo "Whiteboard cleared."
```

## Notes
- Trigger phrases: "add to whiteboard", "note that", "put that on the whiteboard"
- Inside whiteboard content, use LaTeX (e.g. \$\\|M\\|_F\$) — it renders via pandoc
- In Telegram chat, always use Unicode math instead of LaTeX
