---
name: backup
description: "Check pCloud backup status for Markus's home folders."
version: 1.0.0
author: Mhai2
platforms: [linux]
metadata:
  hermes:
    tags: [Backup, pCloud, Storage, Personal]
---

# pCloud Backup Status

pCloudDrive is mounted at `/home/hegland/pCloudDrive` (500GB FUSE mount).
Backup of homepc lives at `/home/hegland/pCloudDrive/pCloud Backup/homepc/`.
Folders monitored: Desktop, Documents, Downloads, Music, Pictures, Videos, Zotero.

## Check backup status

```bash
cd ~/projects/Mhai2 && python3 -c "
from mhai_skills import check_backup
print(check_backup())
"
```

## Manual check (if pCloudDrive is mounted)

```bash
ls "/home/hegland/pCloudDrive/pCloud Backup/homepc/" 2>/dev/null || echo "pCloudDrive not mounted"
```

## Notes
- `rglob` does NOT work on the pCloudDrive FUSE mount — use `iterdir` only
- `~/Desktop/wordpress-docker/` is excluded (root-owned Docker MySQL files)
- Status: OK = synced within 1h, "behind Xd Yh" = lagging, STALE = more than 7 days behind
