# DBT Session Learning Workflow

## Context
Markus is working through Dialectical Behaviour Therapy (DBT) group sessions. Each session produces:
- Audio recording (.m4a)
- Transcript (.txt)
- Chunked session breakdowns (in subdirectories by session number)

## Workflow: Extract & Summarize a Session for Learning

### 1. Locate the Session
```bash
ls ~/projects/DBT/ | grep "Session"
# Output: Group 1, Session 1.6.txt, Group 1, Session 2.6.txt, etc.
```

### 2. Read the Full Transcript
Use `mcp_read_file` with pagination if transcript exceeds 500 lines:
```bash
read_file("~/projects/DBT/Group 1, Session 5.6.txt", offset=1, limit=500)
# If truncated, continue with offset=501
```

### 3. Structure the Learning Summary

Create a markdown file with these sections:

#### A. Session Header
- Session number, date, topic
- Key facilitator announcements (e.g., "last teaching session")

#### B. Core Framework (if applicable)
- Name the skill/technique being taught
- List all components (e.g., 5 Crisis Survival Skills)
- Table format for easy reference

#### C. Foundational Theory
- The "why" behind the skill
- Brain science / attachment theory / nervous system concepts
- Common patterns and triggers

#### D. Detailed Techniques
- Step-by-step instructions
- Sensory/body-based approaches (DBT emphasizes bottom-up regulation)
- Examples from the session

#### E. Practice Strategies
- How to apply the skill in real situations
- Self-assessment questions for reflection

#### F. Homework & Next Steps
- Book page references (Linehan workbook)
- Specific exercises assigned
- Materials to bring next week

### 4. Save the File
Name it descriptively:
```bash
~/projects/DBT/Session_N_Learning_Notes.md
```

Commit to git if the repo is initialized.

### 5. Optional: Create a PDF
For readability or sharing:
```bash
pandoc ~/projects/DBT/Session_N_Learning_Notes.md \
  --pdf-engine=xelatex \
  -o ~/projects/DBT/Session_N_Learning_Notes.pdf
```

## Key Patterns in DBT Sessions

### Attachment & Nervous System Focus
DBT group teaching emphasizes:
- **Attunement, mirror neurons, imprinting** — how childhood attachment shapes adult distress
- **Vagus nerve activation** — bottom-up regulation (body → brain, not brain → body)
- **Sensory gateways** — vision, smell, taste, touch, hearing as fastest routes to calming

### Terminology
- **Self-soothe** ≠ avoidance. Self-soothing is active nervous-system regulation; avoidance is escaping without healing.
- **Validation** vs. **reassurance seeking** — anxious attachment constantly seeks reassurance; secure attachment seeks periodic validation.
- **Bottom-up regulation** — activate the body (vagus nerve, bilateral stimulation, vibration) to signal the brain it's safe.

### Session Structure Pattern
1. Recap of prior skills
2. Introduction of new skill + theory
3. In-session practice exercise (often breathing, visualization, or movement)
4. Facilitator draws out insights from the group's experience
5. Homework assignment (pages in the workbook + practical exercises)

### What to Flag in Your Summary
- **Shifts in facilitator role** (e.g., "last teaching session")
- **Practical exercises done in-group** — capture participant feedback and observed effects
- **Common participant questions** — these reveal confusion points worth clarifying
- **Handouts promised but not yet provided** — note the timeline (e.g., "handout next week")

## Example: Session 5 (May 17, 2026)
See `Session_5_Learning_Notes.md` for a completed example.
