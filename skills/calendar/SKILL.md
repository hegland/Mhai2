---
name: calendar
description: "Query Markus's Google Calendar — upcoming events, meetings with collaborators, weekly schedule."
version: 1.0.0
author: Mhai2
platforms: [linux]
metadata:
  hermes:
    tags: [Calendar, Google, Schedule, Meetings, Personal]
---

# Google Calendar

## Query calendar (natural language)

```bash
cd ~/projects/Mhai2 && python3 -c "
from mhai_skills import parse_calendar_query
print(parse_calendar_query('THIS WEEK'))
"
```

## Examples

```bash
# This week
python3 -c "from mhai_skills import parse_calendar_query; print(parse_calendar_query('this week'))"

# Next week
python3 -c "from mhai_skills import parse_calendar_query; print(parse_calendar_query('next week'))"

# Meetings with a specific person
python3 -c "from mhai_skills import parse_calendar_query; print(parse_calendar_query('next week with Frank'))"

# Today only
python3 -c "from mhai_skills import parse_calendar_query; print(parse_calendar_query('today'))"
```

## Known people
frank, xi chen, gleb, zbigniew, boris, steve, conrad

## Calendars included
- primary (markus.hegland@gmail.com)
- work calendar
- family calendar

## Notes
- Work/research emails from markus.hegland@anu.edu.au are NOT integrated
- All times displayed in Canberra timezone (Australia/Sydney)
- Run from ~/projects/Mhai2 so mhai_skills imports correctly
