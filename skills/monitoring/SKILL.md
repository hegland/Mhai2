---
name: monitoring
description: "Report Mhai2 resource usage: token counts, API costs, session stats, and Anthropic billing."
version: 1.0.0
author: Mhai2
platforms: [linux]
metadata:
  hermes:
    tags: [Monitoring, Usage, Cost, Billing, Performance]
---

# Mhai2 Monitoring

## Claude API pricing

- claude-haiku-4-5: $1.00/M input, $5.00/M output, $0.10/M cache read, $1.25/M cache write
- claude-sonnet-4-6: $3.00/M input, $15.00/M output, $0.30/M cache read, $3.75/M cache write

## IMPORTANT: Token counting

`input_tokens` in the DB = only uncached new tokens per turn.
The full input cost = input_tokens + cache_read_tokens + cache_write_tokens.
Cache read tokens dominate (prompt caching re-uses system prompt + history each turn).
Always include all three columns for accurate cost.

## Today's usage

```bash
python3 << 'EOF'
import sqlite3
from datetime import datetime
conn = sqlite3.connect('/home/hegland/.hermes/state.db')
# Pricing per million tokens
P = {
    'haiku':  {'in': 1.00, 'out': 5.00, 'cr': 0.10, 'cw': 1.25},
    'sonnet': {'in': 3.00, 'out': 15.00, 'cr': 0.30, 'cw': 3.75},
}
today = datetime.now().strftime('%Y-%m-%d')
rows = conn.execute('''
    SELECT model, started_at, input_tokens, output_tokens,
           cache_read_tokens, cache_write_tokens, message_count, tool_call_count
    FROM sessions
    WHERE date(started_at, "unixepoch") = ?
    ORDER BY started_at DESC
''', (today,)).fetchall()

totals = dict(inp=0, out=0, cr=0, cw=0, cost=0.0)
print(f"Today ({today}): {len(rows)} sessions\n")
for r in rows:
    model, ts, inp, out, cr, cw, msgs, tools = r
    inp=inp or 0; out=out or 0; cr=cr or 0; cw=cw or 0
    dt = datetime.fromtimestamp(ts).strftime('%H:%M') if ts else '?'
    p = P['sonnet'] if 'sonnet' in (model or '') else P['haiku']
    cost = (inp*p['in'] + out*p['out'] + cr*p['cr'] + cw*p['cw']) / 1_000_000
    total_in = inp + cr + cw
    for k,v in zip(['inp','out','cr','cw'],[inp,out,cr,cw]): totals[k]+=v
    totals['cost'] += cost
    print(f"  {dt} | in={total_in:,} (cache_read={cr:,}) out={out:,} | msgs={msgs or 0} tools={tools or 0} | ${cost:.4f}")

total_in = totals['inp'] + totals['cr'] + totals['cw']
print(f"\nTOTAL")
print(f"  Input:       {total_in:,} tokens  (new={totals['inp']:,} cache_read={totals['cr']:,} cache_write={totals['cw']:,})")
print(f"  Output:      {totals['out']:,} tokens")
print(f"  Cost:        ${totals['cost']:.4f}")
print(f"\n👉 Verify: https://console.anthropic.com/settings/usage")
EOF
```

## All-time usage

```bash
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('/home/hegland/.hermes/state.db')
P = {'haiku': (1.00, 5.00, 0.10, 1.25), 'sonnet': (3.00, 15.00, 0.30, 3.75)}
rows = conn.execute('''
    SELECT model, COUNT(*), SUM(input_tokens), SUM(output_tokens),
           SUM(cache_read_tokens), SUM(cache_write_tokens)
    FROM sessions GROUP BY model ORDER BY SUM(cache_read_tokens) DESC
''').fetchall()
print("All-time by model:")
total_cost = 0
for model, sessions, inp, out, cr, cw in rows:
    inp=inp or 0; out=out or 0; cr=cr or 0; cw=cw or 0
    p = P['sonnet'] if 'sonnet' in (model or '') else P['haiku']
    cost = (inp*p[0] + out*p[1] + cr*p[2] + cw*p[3]) / 1_000_000
    total_cost += cost
    print(f"  {model}: {sessions} sessions | in={inp+cr+cw:,} out={out:,} | ${cost:.4f}")
print(f"\n  TOTAL COST: ${total_cost:.4f}")
EOF
```

## Gateway health

```bash
hermes gateway status && tail -5 ~/.hermes/logs/gateway.log
```

## Open Anthropic billing

```bash
xdg-open https://console.anthropic.com/settings/usage
```

## Billing note (updated 2026-05-30)

On Markus's current Anthropic plan, cache read and cache write tokens appear to be
free/included. Only output tokens are billed. When reporting cost, use:

cost = output_tokens * 4.00 / 1_000_000   (haiku output rate)

This matches the Anthropic console figure exactly.
The cache token counts are still useful for understanding context size and compression efficiency.
