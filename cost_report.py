#!/usr/bin/env python3
"""
Mhai2 cost and data transfer report.
Usage: python3 cost_report.py [days=1] [--all]
"""

import sqlite3, os, sys, datetime

DB = os.path.expanduser("~/.hermes/state.db")
BYTES_PER_TOKEN = 4  # rough estimate: ~4 chars/token

def fmt_bytes(b):
    if b < 1024: return f"{b}B"
    if b < 1024**2: return f"{b/1024:.1f}KB"
    return f"{b/1024**2:.2f}MB"

def fmt_tokens(t):
    if t < 1000: return str(t)
    return f"{t/1000:.1f}K"

def report(days=1):
    con = sqlite3.connect(DB)
    cur = con.cursor()

    if days == 0:
        # All time
        cur.execute('''SELECT title, api_call_count, message_count,
                              input_tokens, output_tokens, cache_read_tokens, cache_write_tokens,
                              estimated_cost_usd, started_at
                       FROM sessions ORDER BY rowid ASC''')
        label = "All time"
    else:
        start = (datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                 - datetime.timedelta(days=days-1)).timestamp()
        cur.execute('''SELECT title, api_call_count, message_count,
                              input_tokens, output_tokens, cache_read_tokens, cache_write_tokens,
                              estimated_cost_usd, started_at
                       FROM sessions WHERE started_at > ? ORDER BY rowid ASC''', (start,))
        label = f"Today ({datetime.date.today().strftime('%d %b %Y')} AEST)" if days == 1 else f"Last {days} days"

    rows = cur.fetchall()
    if not rows:
        print(f"No sessions found for: {label}")
        return

    print(f"\n{'='*90}")
    print(f"  Mhai2 Cost & Data Transfer Report — {label}")
    print(f"{'='*90}")
    print(f"{'Time':6} {'Cost':>7} {'API':>4} {'Msgs':>5} {'Upload':>8} {'Download':>9} {'Cache R':>8} {'Cache W':>8}  Session")
    print(f"{'-'*90}")

    totals = dict(cost=0, api=0, msgs=0, upload=0, download=0, cr=0, cw=0)

    for r in rows:
        title, api, msgs, inp, out, cr, cw, cost, ts = r
        cost = cost or 0
        inp = inp or 0; out = out or 0; cr = cr or 0; cw = cw or 0; api = api or 0; msgs = msgs or 0

        # Upload = uncached input + cache writes sent to API
        upload_tokens = inp + cw
        # Download = output tokens received
        download_tokens = out
        # Cache reads = data Anthropic reads from their cache on our behalf
        upload_bytes = upload_tokens * BYTES_PER_TOKEN
        download_bytes = download_tokens * BYTES_PER_TOKEN

        totals['cost'] += cost
        totals['api'] += api
        totals['msgs'] += msgs
        totals['upload'] += upload_bytes
        totals['download'] += download_bytes
        totals['cr'] += cr
        totals['cw'] += cw

        t = datetime.datetime.fromtimestamp(ts).strftime('%H:%M')
        title_short = title[:30] if title else "—"
        print(f"{t:6} ${cost:>6.4f} {api:>4} {msgs:>5} {fmt_bytes(upload_bytes):>8} {fmt_bytes(download_bytes):>9} "
              f"{fmt_tokens(cr):>8} {fmt_tokens(cw):>8}  {title_short}")

    print(f"{'-'*90}")
    print(f"{'TOTAL':6} ${totals['cost']:>6.4f} {totals['api']:>4} {totals['msgs']:>5} "
          f"{fmt_bytes(totals['upload']):>8} {fmt_bytes(totals['download']):>9} "
          f"{fmt_tokens(totals['cr']):>8} {fmt_tokens(totals['cw']):>8}")
    print(f"\n  Upload   = uncached input + cache writes sent to Anthropic")
    print(f"  Download = output tokens received from Anthropic")
    print(f"  Cache R  = tokens Anthropic read from cache (not re-sent by us)")
    print(f"  Cache W  = tokens written to Anthropic cache this session")
    print(f"  Token→bytes estimate: {BYTES_PER_TOKEN} bytes/token")
    print(f"{'='*90}\n")

if __name__ == "__main__":
    days = 1
    if "--all" in sys.argv:
        days = 0
    elif len(sys.argv) > 1:
        try: days = int(sys.argv[1])
        except: pass
    report(days)
