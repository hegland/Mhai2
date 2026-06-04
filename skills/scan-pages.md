---
name: scan-pages
description: "Scan physical document pages one at a time using the Canon LiDE 400 scanner. Stateful multi-turn workflow — each /scan-pages next triggers the next page scan."
version: 2.0.0
author: Mhai2
platforms: [linux]
metadata:
  hermes:
    tags: [Scan, Documents, DBT, Files, Canon]
---

# Page Scanning Workflow

## How it works

This is a multi-turn workflow. Mhai2 scans one page per turn:
1. User invokes `/scan-pages <description>` → Mhai2 sets up state, scans page 1, asks user to place next page
2. User places next page, sends `/scan-pages next` → Mhai2 scans the next page
3. Repeat until done

State is stored in `~/.hermes/scan_state.json` between turns.

## Scanner device
Canon CanoScan LiDE 400. Always use this device string:
```
escl:http://localhost:60000
```

## Scan command
```bash
scanimage --device-name 'escl:http://localhost:60000' \
  --format=pdf \
  --mode Color \
  --resolution 300 \
  -o OUTPUT_PATH
```

---

## Step A — Starting a new scan job

**Triggered by:** `/scan-pages <document description and page range>`

Example: `/scan-pages Scan pages 55 to 64 from the DBT skills training workbook`

1. Parse document title and page range from the request.

2. Determine output directory:
   - DBT documents → `~/projects/DBT/scans/`
   - VRZM26 documents → `~/Desktop/VRZM26/scans/`
   - Other → ask the user

3. Create output directory:
   ```bash
   mkdir -p ~/projects/DBT/scans/
   ```

4. Write state file `~/.hermes/scan_state.json`:
   ```bash
   cat > ~/.hermes/scan_state.json << 'EOF'
   {
     "doc_title": "DBT skills training workbook",
     "doc_slug": "dbt_skills_workbook",
     "output_dir": "/home/hegland/projects/DBT/scans",
     "pages": [55, 56, 57, 58, 59, 60, 61, 62, 63, 64],
     "next_index": 0
   }
   EOF
   ```

5. Read the state file to get the first page number.

6. Scan page 1 immediately (don't wait — Markus has already placed it):
   ```bash
   scanimage --device-name 'escl:http://localhost:60000' \
     --format=pdf --mode Color --resolution 300 \
     -o ~/projects/DBT/scans/dbt_skills_workbook_p055.pdf
   ```

7. Update `next_index` to 1 in the state file.

8. Tell Markus:
   "✓ Page 55 scanned → dbt_skills_workbook_p055.pdf
   Place page 56 on the scanner, then send: /scan-pages next"

---

## Step B — Scanning the next page

**Triggered by:** `/scan-pages next`

1. Read `~/.hermes/scan_state.json`:
   ```bash
   cat ~/.hermes/scan_state.json
   ```

2. If file doesn't exist: "No scan job in progress. Start one with /scan-pages <description>."

3. Get `pages[next_index]` — this is the page number to scan now.

4. Run scan command with the correct output path.

5. Increment `next_index` in the state file:
   ```bash
   python3 -c "
   import json
   with open('/home/hegland/.hermes/scan_state.json') as f:
       s = json.load(f)
   s['next_index'] += 1
   with open('/home/hegland/.hermes/scan_state.json', 'w') as f:
       json.dump(s, f, indent=2)
   "
   ```

6. If more pages remain, tell Markus:
   "✓ Page N scanned → filename.pdf
   Place page M on the scanner, then send: /scan-pages next"

7. If all pages done, delete the state file and tell Markus:
   "✓ All pages scanned! Files saved to <output_dir>"
   ```bash
   rm ~/.hermes/scan_state.json
   ```

---

## File naming convention

- Document slug: lowercase, underscores, no special chars
  - "DBT skills training workbook" → `dbt_skills_workbook`
- Page number: zero-padded to 3 digits → `p055`, `p007`
- Full example: `~/projects/DBT/scans/dbt_skills_workbook_p055.pdf`

## Notes & Pitfalls
- Scan takes ~10–20 seconds per page at 300 DPI.
- No OCR — use `ocr-and-documents` skill separately if needed.
- If the scan fails: `scanimage -L` to check the scanner is connected.
- Use 150 DPI for faster scans of plain text pages without diagrams.

### Pitfall: Internal Tool Availability Misunderstanding
On occasion, the agent may incorrectly assert that it lacks the `scan_pages` tool, even when this skill is active and explicitly provides the `scanimage` command. If the `scan-pages` skill is loaded and the user requests a scan, *always* attempt to execute the `scanimage` command as specified in the skill, rather than stating an inability to scan. The capability is provided by this skill's explicit instructions and the `terminal` tool, not a separate internal tool named `scan_pages`. Do not refuse to scan.

### Pitfall: State file increment timing
After scanning a page, **always increment `next_index` in the state file AFTER the scan completes**, before prompting for the next page. This keeps the state file in sync with what has actually been scanned. If you read `next_index` before incrementing, you'll read stale state and risk confusion about which page comes next.
