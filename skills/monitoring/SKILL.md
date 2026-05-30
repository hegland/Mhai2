---
name: monitoring
description: "Report Mhai2 cost by reading the Anthropic console — the only reliable source."
version: 1.0.0
author: Mhai2
platforms: [linux]
metadata:
  hermes:
    tags: [Monitoring, Usage, Cost, Billing, Performance]
---

# Mhai2 Monitoring

## CRITICAL: DB figures are unreliable — always use the Anthropic console

The local state DB severely underreports usage. Hermes insights are also unreliable.
The ONLY authoritative source is the Anthropic console Cost page.

## How to answer "how much have I spent today?"

1. Open the browser and navigate to:
   https://platform.claude.com/workspaces/default/cost?model=Claude+Haiku+4.5&range=today

2. Read the "Total token cost" figure shown.

3. Report that number. Do not calculate from DB or estimate from token counts.

## To open in browser

```bash
xdg-open "https://platform.claude.com/workspaces/default/cost?model=Claude+Haiku+4.5&range=today"
```

## Verified costs

- 2026-05-30: $13.79 USD (Claude Haiku 4.5, today only) — heavy setup day
- Credits remaining: $21.92 USD

## Pricing reference (for information only — do not use for cost reporting)

- Input uncached: $0.80/M
- Input cache read: $0.08/M (~72% of input in practice)
- Input cache write: $1.00/M
- Output: $4.00/M

## Gateway health

```bash
hermes gateway status && tail -3 ~/.hermes/logs/gateway.log
```
