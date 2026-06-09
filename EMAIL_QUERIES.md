# EMAIL_QUERIES.md — consolidated search/filter cheat-sheet

One place for every collaborator/admin email query across all projects.
Generated from each project's `COLLABORATORS.md`. Full design rationale is in
[`EMAIL_SYNC_PLAN.md`](EMAIL_SYNC_PLAN.md); per-project detail in the
`COLLABORATORS.md` files. Last updated 2026-06-10.

## How to read this

- **Outlook `from:(…)` filter** — for Outlook search / forwarding rules / "Run Rules Now".
- **Plus-address** — where an Outlook rule forwards the mail (`markus.hegland+TAG@gmail.com`).
- **Gmail label** — applied by a Gmail filter on `to:…+TAG@…`; Mhai searches `label:Collab/Name`.
- **Send-to** — the current address to email the person at.
- **Class** — `research-dominant` (blanket forward OK) · `mixed` (selective, mostly
  social) · `admin/scoped` (content-scoped filter; relevant only intersected with a student).

ANU address patterns: staff = `firstname.lastname@anu.edu.au`; students =
`u#######@anu.edu.au`; functional mailboxes (e.g. `hdr.css@anu.edu.au`) are the exception.

---

## Master table — research collaborators

| Project | Person | Class | Outlook `from:(…)` filter | Plus-address | Gmail label | Send-to |
|---------|--------|-------|---------------------------|--------------|-------------|---------|
| VRZM26 | Zbigniew Stachurski | research-dominant | `from:(zh.stachurski OR zbigniew.stachurski OR u9300839)` | `+zbigniew` | `Collab/Zbigniew` | `zh.stachurski@proton.me` |
| VRZM26 | Vanessa Robins | research-dominant | `from:(vanessa.robins OR u9213671)` | `+vanessa` | `Collab/Vanessa` | `vanessa.robins@anu.edu.au` |
| VRZM26 | Conrad Burden | ⚠️ mixed | `from:(conrad.burden OR u1571037)` | `+conrad` | `Collab/Conrad` | `conrad.burden@anu.edu.au` |
| FdHMH | Frank de Hoog | research-dominant | `from:(Frank.Dehoog@data61.csiro.au OR Frank.Dehoog@csiro.au)` | `+frank` | `Collab/Frank` | `Frank.Dehoog@csiro.au` |
| GlebPhD | Gleb Shabernev | research-dominant | `from:(gleb.shabernev)` | `+gleb` | `Collab/Gleb` | `Gleb.Shabernev@anu.edu.au` |
| XiChen26honors | Xi Chen | research-dominant | `from:(u7641463)` | `+xichen` | `Collab/XiChen` | `u7641463@anu.edu.au` |

Notes:
- **Conrad (mixed):** do NOT blanket-forward — mostly social (coffee/lunch). Capture
  research selectively. 2026 research threads: "Sphere packing paper" (30 May),
  "Re: Extension of IAS beyond infinity" (23 Apr).
- **Frank:** switched addresses mid-2026 (data61 → csiro.au) — keep both in the filter.
  Equivalent shorthand: `from:(frank.dehoog)`.

---

## Master table — admin / scoped contacts

These email about **many** students, so they're filtered by sender **AND** the student.
Routed into the student's own bucket. Admin is **program-specific** (HDR ≠ honours).

| Project | Role | Person / mailbox | Content-scoped `from:(…) AND (…)` filter | Routes to |
|---------|------|------------------|------------------------------------------|-----------|
| GlebPhD (HDR/PhD) | Convenor + HDR admin | `James.Tener@anu.edu.au`, `hdr.css@anu.edu.au` | `from:(James.Tener@anu.edu.au OR hdr.css@anu.edu.au) AND (gleb OR shabernev)` | `+gleb` / `Collab/Gleb` |
| XiChen26honors (Honours) | Convener (+ honours-mail contact) | `joan.licata@anu.edu.au` (formal Honours Convener), `galina.levitina@anu.edu.au` (no formal role; appears in honours mail) | `from:(joan.licata OR galina.levitina) AND (xi chen OR chen OR honours)` | `+xichen` / `Collab/XiChen` |

⚠️ James Tener / `hdr.css` are **PhD-only** — they do NOT apply to honours.
⚠️ Bare `chen` is a common surname — keep it paired with the honours-admin sender.

---

## Outlook discovery queries (name-style, for finding mail in Outlook/Copilot)

**Per-person address+profile discovery (run in Outlook Copilot):**
```
find all emails from <Person> (uses multiple emails) in 2026
```

**GlebPhD HDR admin:**
```
gleb AND hdr                          # most focused on admin
gleb AND (hdr OR tener)               # admin + convenor (James Tener)
gleb AND (hdr OR tener OR extension)  # max reliability (also extension threads)
```

**XiChen26honors honours admin:**
```
chen AND (honours OR meeting OR talk)     # Xi Chen's honours mail
honours AND (MSI OR maths)                # general honours activity
(honours AND galina) OR (honours AND chen)  # coordinator + student
```

---

## Mhai / Gmail search equivalents (once filters/labels exist)

```
label:Collab/Zbigniew      label:Collab/Vanessa     label:Collab/Conrad
label:Collab/Frank         label:Collab/Gleb        label:Collab/XiChen
```
Add scope, e.g. `label:Collab/Frank newer_than:30d`, or by plus-address
`to:markus.hegland+frank@gmail.com`.

---

## Build-out checklist (when live forwarding resumes — see EMAIL_SYNC_PLAN.md)

For each research-dominant person:
1. Outlook rule: `from:(…)` → `markus.hegland+TAG@gmail.com`
2. Gmail filter: `to:…+TAG@gmail.com` → label `Collab/Name`

For each admin/scoped pair: Outlook rule `from:(…) AND (<student>…)` → student's `+TAG`.
For mixed (Conrad): no live blanket rule — selective `/save-email` for research mail.
Backfill 2026: research-dominant → "Run Rules Now"; mixed → hand-pick research threads.
