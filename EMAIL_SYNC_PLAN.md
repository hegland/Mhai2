# Email Sync Plan — collaborator mail from ANU Outlook → Gmail

Status: **design + data-gathering phase** (live build-out ON HOLD).
Cross-project record. Per-collaborator address records live in each project's
`COLLABORATORS.md` (VRZM26, FdHMH, …). Running notes in Mhai2 memory
`project_email_sync.md`.

## Goal

Systematically manage research email from key collaborators. ANU Outlook is not
integrated with Mhai, so we bridge to personal Gmail. **End goal: labels-only in
Gmail** (searchable by Mhai) — not files on disk.

## Architecture (server-side, nothing runs on Markus's machine)

1. **Outlook rule per person** → forward to a distinct Gmail **plus-address**
   (e.g. `markus.hegland+frank@gmail.com`).
2. **Gmail filter per plus-address** → apply a per-person label (`Collab/Frank`).
   Plus-addressing is used because forwarded mail's `From` header is rewritten, so
   filtering on `to:…+tag@gmail.com` is reliable and survives the rewrite. It also
   means **all of a person's sender addresses land in one bucket** regardless of
   which they used.
3. Mhai searches by label (`label:Collab/Frank`).

Verified 2026-06-10: ANU **allows** external auto-forwarding (FWDTEST reached
`markus.hegland+test@gmail.com`). Confirmed the forward rewrites `From` to Markus
but preserves the plus-address in `To:`.

Constraint: the Mhai OAuth token has `gmail.modify`/`send` but **not
`gmail.settings.basic`**, so Mhai cannot create Gmail filters — they're made once
by hand in the Gmail web UI (no re-auth). Mhai can create/apply labels.

## Working workflow: discovering addresses & profiles via Outlook Copilot

Claude **cannot** interact with Outlook Copilot directly (no API; ANU mailbox
unreachable; browser automation possible but fragile and not worth it). So:

1. Markus runs in Outlook Copilot:
   `find all emails from <Person> (uses multiple emails) in 2026`
2. Markus pastes the full Copilot response to Claude.
3. Claude extracts and records, in the project's `COLLABORATORS.md`:
   - **Addresses** — preferred/current send-to + all variants → a `from:(…)` filter
   - **Profile** — *research-dominant* vs *mixed* (from Copilot's content analysis)
   - **Research threads** — for mixed contacts, the specific threads to hand-pick
     for the backfill

Tip: phrase the query exactly like that — it returns both the address list AND a
content breakdown (which is what reveals research-dominant vs mixed).

### Research-only scope & the two collaborator classes

Projects care about **research email only**, not social/logistics (coffee, lunches,
"not coming tomorrow").

- **research-dominant** (e.g. Zbigniew, Vanessa, Frank) — blanket `from:(…)`
  forward is fine; almost all their mail belongs in the bucket.
- **mixed** (e.g. Conrad — mostly social) — **no live blanket rule**; hand-pick
  research threads for the backfill, and capture future research mail ad hoc via
  `/save-email`.
- **admin / scoped** (e.g. a PhD convenor or HDR administrator) — these people email
  about **many** students, so a sender-only filter would flood the bucket with
  unrelated HDR business. Use a **content-scoped** filter that intersects the sender
  with the student:
  `from:(<admin-person>) AND (<Student> OR <Surname> OR <student-ID>)`.
  Each student project (GlebPhD, XiChen26honors, …) typically has a convenor + HDR
  admin in this class. Discovery pattern: `<student> AND (hdr OR <convenor-surname>
  OR extension)`. Route the matching mail into the *student's own* bucket (e.g.
  admin-about-Gleb → `+gleb` → `Collab/Gleb`); the content scope keeps other
  students out. Worked example (GlebPhD): convenor `James.Tener@anu.edu.au` + HDR
  functional mailbox `hdr.css@anu.edu.au`, scoped with `(gleb OR shabernev)`.

### Gotchas learned
- People use **several addresses**; each `from:(…)` filter needs an OR-list of
  local-parts. Some **switch addresses mid-year** (Frank: data61.csiro.au →
  csiro.au) — include both or lose half the history.
- **Short recycled subjects** ("Meeting today?", "RE:") make subject-filtering
  useless (esp. Frank) — `from:(…)` is the only reliable catch.
- **Plus-tag typos misroute silently.** Gmail delivers *any* `+anything` to the base
  inbox, so a mistyped tag (observed 2026-06-10: `+VRZM25` for `+VRZM26`, and the
  content was actually FdHMH) still "arrives" but won't match the intended filter —
  it sits unlabelled with no bounce or warning. Double-check the tag when sending;
  periodically sweep for stray `+tags` that match no known project. Also check the
  tag matches the *content's* project (Frank = `+FdHMH`, not a VRZM tag).
- **Backfill ≠ live rule.** Outlook rules act only on *incoming* mail; for historical
  2026 mail use desktop Outlook **"Run Rules Now"** on a folder, or select-all →
  forward. Forwarded mail also gets **today's** Gmail timestamp (true date only in
  the body) — fine for search/test, not a dated archive.

## Per-collaborator status (2026-06-10)

| Project | Person | Profile | Status |
|---------|--------|---------|--------|
| VRZM26 | Zbigniew Stachurski | research-dominant | ✅ recorded |
| VRZM26 | Vanessa Robins | research-dominant | ✅ recorded |
| VRZM26 | Conrad Burden | mixed (mostly social) | ✅ recorded |
| FdHMH | Frank de Hoog | research-dominant (~203/yr) | ✅ recorded |
| GlebPhD | Gleb Shabernev | research-dominant (assumed) | ✅ recorded — profile TBC via Copilot |
| XiChen26honors | Xi Chen | research-dominant (assumed) | ✅ recorded |

## Roadmap

1. **Record addresses + profiles** (in progress — see table).
2. **One-off 2026 backfill** — research-dominant: blanket forward (Run Rules Now);
   mixed: hand-pick research threads.
3. **Resume live build-out** (below) once data is complete.

### Live build-out (ON HOLD — ready to execute)

- **Part A — Outlook:** one forwarding rule per person, `from:(…)` → their
  plus-address (`+gleb`, `+xichen`, `+zbigniew`, `+vanessa`, `+conrad`, `+frank`).
- **Part B — Gmail:** one filter per plus-address (`to:…+tag` → label `Collab/Name`),
  created by hand in the Gmail web UI.
- Then add concise send-defaults to SOUL.md collaborators (name + current address +
  project); full variant lists stay in each `COLLABORATORS.md`.

## Open idea (R&D — not yet feasible as literally stated)

**Markus's idea:** "send an email to my ANU address → have an Outlook rule (filter)
that lands a specific email *into Copilot*" so Copilot processes it.

**Reality check:** Outlook Copilot is **not a mailbox destination** — there's no
Copilot address a rule can deliver to. Copilot is an assistant you query in the
M365 UI; it already reads the whole mailbox. So a rule can't "deliver into Copilot."

**What *is* possible (the real adjacencies):**
- **Just ask Copilot.** Since it reads the mailbox, to have it process a specific
  email you ask it directly ("summarise the email with subject X from Frank") — no
  rule needed.
- **Rule → folder, then point Copilot at the folder.** A rule can move matching mail
  to a dedicated folder; you then ask Copilot to work over "the <folder> folder."
  (Copilot doesn't auto-trigger on folder arrival — you still invoke it.)
- **Email-triggered automation via Power Automate / Copilot Studio.** A flow can
  trigger *on email arrival* and run an AI/Copilot action automatically. This is the
  genuine "email lands → Copilot processes it" path — but it needs Power Automate /
  Copilot Studio, subject to ANU M365 licensing/permissions (to be checked).

**Open questions:**
- Does ANU's M365 tenant allow Power Automate flows + Copilot/AI Builder actions?
- What would the trigger be — a dedicated subject tag, or delivery to a folder a
  rule populates?
- What should the Copilot action produce (summary, extraction, a Gmail forward)?
