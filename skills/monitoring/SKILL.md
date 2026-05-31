---
name: monitoring
description: "Report Mhai2 cost, API calls, and data transfer — run cost_report.py for full breakdown."
version: 1.1.0
author: Mhai2
platforms: [linux]
metadata:
  hermes:
    tags: [Monitoring, Usage, Cost, Billing, Performance]
---

# Mhai2 Monitoring

## Cost, API calls and data transfer report

Run this to get today's full breakdown:

```bash
python3 ~/projects/Mhai2/cost_report.py
```

Options:
- `python3 ~/projects/Mhai2/cost_report.py 2` — last 2 days
- `python3 ~/projects/Mhai2/cost_report.py --all` — all time

Output columns: Time (AEST) | Cost | API calls | Messages | Upload | Download | Cache reads | Cache writes | Session title

- **Upload** = uncached input + cache writes sent to Anthropic (~4 bytes/token)
- **Download** = output tokens received from Anthropic
- **Cache R** = tokens Anthropic read from their cache (not re-sent by us, billed at $0.08/M)
- **Cache W** = tokens written to Anthropic cache (billed at $1.00/M)

## Pricing reference

- Input uncached: $0.80/M tokens
- Input cache read: $0.08/M tokens
- Input cache write: $1.00/M tokens
- Output: $4.00/M tokens

## Gateway health

```bash
hermes gateway status && tail -3 ~/.hermes/logs/gateway.log
```
