---
name: git-ops
description: "Commit, push, and restore files in Markus's project git repos (StudentProjects, VRZM26)."
version: 1.0.0
author: Mhai2
platforms: [linux]
metadata:
  hermes:
    tags: [Git, Projects, StudentProjects, VRZM26, Version Control]
---

# Git Operations

## Project Repos

| Project | Repo Path | Remote |
|---|---|---|
| VRZM26 + sphere_packing | ~/Desktop/VRZM26/ | github.com/hegland/VRZM26 |
| XiChen26honors, GlebPhD, MATH8702, etc. | ~/Desktop/StudentProjects/ | github.com/hegland/StudentProjects |

## Commit and push all changes

```bash
cd ~/Desktop/VRZM26
git add -A
git commit -m "Your commit message"
git push
```

## Check what's changed

```bash
cd ~/Desktop/VRZM26 && git status --short
cd ~/Desktop/StudentProjects && git status --short
```

## List git history for a file

```bash
cd ~/Desktop/StudentProjects && git log --oneline -- XiChen26honors/notes.md
```

## Restore a file to a previous commit

```bash
cd ~/Desktop/StudentProjects
git checkout abc1234 -- XiChen26honors/notes.md
git add XiChen26honors/notes.md
git commit -m "Restore notes.md to abc1234"
```

## Notes
- Always commit to the repo that contains the changed file
- Use short, descriptive commit messages
- Check `git status` before committing to avoid adding unintended files
