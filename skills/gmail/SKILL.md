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

Only markus.hegland@gmail.com is integrated. ANU Outlook (markus.hegland@anu.edu.au) is NOT accessible.
If Markus mentions a work/research email, ask him to paste it into the chat.

## Search Gmail (natural language)

```bash
cd ~/projects/Mhai2 && python3 -c "
from mhai_skills import parse_gmail_query
print(parse_gmail_query('YOUR QUERY'))
"
```

## Examples

```bash
# Unread emails
python3 -c "from mhai_skills import parse_gmail_query; print(parse_gmail_query('unread emails'))"

# Emails from a person
python3 -c "from mhai_skills import search_gmail; print(search_gmail('from:zbigniew', max_results=5))"

# Emails this week
python3 -c "from mhai_skills import parse_gmail_query; print(parse_gmail_query('emails this week'))"

# Emails with attachment
python3 -c "from mhai_skills import parse_gmail_query; print(parse_gmail_query('emails with attachment'))"
```

## Pasted emails
If Markus pastes an email into the chat, it is automatically saved to:
`~/.openclaw/workspace/knowledge/emails/YYYY-MM-DD_Sender_Subject.md`

To recall a saved email:
```bash
ls ~/.openclaw/workspace/knowledge/emails/ | sort -r | head -10
cat ~/.openclaw/workspace/knowledge/emails/FILENAME.md
```
