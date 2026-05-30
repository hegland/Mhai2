---
name: gmail
description: "Search Markus's personal Gmail (markus.hegland@gmail.com). ANU Outlook is NOT integrated."
version: 1.0.0
author: Mhai2
platforms: [linux]
metadata:
  hermes:
    tags: [Email, Gmail, Personal, Communications]
---

# Gmail Search

**Setup required:** Gmail access uses Google Workspace OAuth. See `google-workspace-setup` skill for a step-by-step guided walkthrough.

Only markus.hegland@gmail.com is integrated. ANU Outlook (markus.hegland@anu.edu.au) is NOT accessible.

## After OAuth Setup

Once authenticated via `google-workspace` skill, use:

```bash
GAPI="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/google_api.py"

# Search Gmail
$GAPI gmail search "is:unread" --max 10
$GAPI gmail search "from:magda dropbox" --max 5
$GAPI gmail search "has:attachment newer_than:7d"

# Read full message
$GAPI gmail get MESSAGE_ID

# Send email (confirm with user first)
$GAPI gmail send --to user@example.com --subject "Hello" --body "Message"
```

## Gmail Search Syntax

Use standard Gmail operators:
- `from:` — emails from a specific person
- `to:` — emails sent to someone
- `subject:` — search in subject line
- `is:unread` — unread emails
- `has:attachment` — emails with files
- `newer_than:7d` — last 7 days
- `before:`, `after:` — date ranges
- Combine with `AND`, `OR`, `-` (not)

**Example:** `from:magda dropbox newer_than:30d` finds recent emails from Magda mentioning Dropbox.

## Pasted emails
If Markus pastes an email into the chat, it is automatically saved to:
`~/.openclaw/workspace/knowledge/emails/YYYY-MM-DD_Sender_Subject.md`

To recall a saved email:
```bash
ls ~/.openclaw/workspace/knowledge/emails/ | sort -r | head -10
cat ~/.openclaw/workspace/knowledge/emails/FILENAME.md
```
