#!/bin/bash
# Sync the live Hermes SOUL.md into this repo.
# The LIVE file (~/.hermes/SOUL.md) is the source of truth — Mhai reads it.
# The repo copy is a tracked mirror for version history. Always EDIT the live
# file, never the repo copy (the copy is overwritten by this sync).
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIVE="$HOME/.hermes/SOUL.md"
if [[ -f "$LIVE" ]]; then
    if ! cmp -s "$LIVE" "$REPO/SOUL.md"; then
        cp "$LIVE" "$REPO/SOUL.md"
        echo "sync_soul: updated repo SOUL.md from live ~/.hermes/SOUL.md"
    fi
else
    echo "sync_soul: WARNING live $LIVE not found — repo SOUL.md left unchanged" >&2
fi
