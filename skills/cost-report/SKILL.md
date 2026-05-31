---
name: cost-report
title: "Mhai2 Cost & Data Transfer Report"
description: "Run the cost report to show today's API cost, API calls, and data transfer to/from Anthropic."
tags: ["cost", "monitoring", "billing"]
---

# Cost Report

Run this command and send the output to Markus:

```bash
python3 ~/projects/Mhai2/cost_report.py
```

For other periods:
- Last 2 days: `python3 ~/projects/Mhai2/cost_report.py 2`
- All time: `python3 ~/projects/Mhai2/cost_report.py --all`

Send the full output as-is. Do not summarise or paraphrase it.
