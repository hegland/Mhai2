---
name: monitoring
description: "Report Mhai2 resource usage and cost estimate."
version: 1.0.0
author: Mhai2
platforms: [linux]
metadata:
  hermes:
    tags: [Monitoring, Usage, Cost, Billing, Performance]
---

# Mhai2 Monitoring

## Pricing (claude-haiku-4-5, Anthropic 2026)

- Input (uncached): $0.80/M
- Output:           $4.00/M
- Cache read:       $0.08/M
- Cache write:      $1.00/M

## Cost estimate (today)

```bash
python3 << 'EOF'
import sqlite3
from datetime import datetime
conn = sqlite3.connect('/home/hegland/.hermes/state.db')
today = datetime.now().strftime('%Y-%m-%d')
rows = conn.execute('''
    SELECT started_at, input_tokens, output_tokens, cache_read_tokens, cache_write_tokens,
           message_count, tool_call_count
    FROM sessions WHERE date(started_at, "unixepoch") = ?
    ORDER BY started_at DESC
''', (today,)).fetchall()
ti=to=tcr=tcw=0
print(f"Today ({today}): {len(rows)} sessions\n")
for ts, inp, out, cr, cw, msgs, tools in rows:
    inp=inp or 0; out=out or 0; cr=cr or 0; cw=cw or 0
    cost = (inp*0.80 + out*4.00 + cr*0.08 + cw*1.00) / 1_000_000
    dt = datetime.fromtimestamp(ts).strftime('%H:%M') if ts else '?'
    ti+=inp; to+=out; tcr+=cr; tcw+=cw
    print(f"  {dt} out={out:,} cache_read={cr:,} ${cost:.4f}")
total = (ti*0.80 + to*4.00 + tcr*0.08 + tcw*1.00) / 1_000_000
print(f"\nTOTAL: out={to:,} cache_read={tcr:,} cache_write={tcw:,}")
print(f"COST:  ${total:.2f}  (lower bound — auxiliary model calls not included)")
print(f"\n👉 https://console.anthropic.com/settings/usage")
EOF
```

## All-time cost

```bash
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('/home/hegland/.hermes/state.db')
r = conn.execute('SELECT SUM(input_tokens), SUM(output_tokens), SUM(cache_read_tokens), SUM(cache_write_tokens) FROM sessions').fetchone()
inp,out,cr,cw = [x or 0 for x in r]
cost = (inp*0.80 + out*4.00 + cr*0.08 + cw*1.00) / 1_000_000
print(f"All-time: out={out:,} cache_read={cr:,} → ${cost:.2f} (lower bound)")
EOF
```

## Gateway health

```bash
hermes gateway status && tail -3 ~/.hermes/logs/gateway.log
```

## Anthropic console (authoritative)

```bash
xdg-open https://console.anthropic.com/settings/usage
```

## Verified billing (2026-05-30)

- Month-to-date cost: $38.00 USD (all of May 2026)
- Credits remaining: $22.00 USD
- Includes both Mhai2 and Claude Code sessions
- No web search, code execution, or session runtime costs

## Haiku-specific cost (Mhai2 only)

Filter by Model = "Claude Haiku 4.5" on the Cost page for Mhai2-only figures.
Verified 2026-05-30: $14.93 for Haiku month-to-date (almost entirely today's setup session).

## Correct cost formula (verified 2026-05-30)

Anthropic bills cache read tokens at $0.08/M, not $0.80/M.
Typical session: ~72% cache reads, ~28% uncached input.

Accurate formula:
  cost = uncached_input * 0.80/1M + cache_read * 0.08/1M + cache_write * 1.00/1M + output * 4.00/1M

Verified: 47.15M input (13.2M uncached + 34.0M cache read) + 418K output = $14.93
