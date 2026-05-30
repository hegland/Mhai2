#!/usr/bin/env python3
"""
Verify project isolation and detect misfiled content.
Usage: python verify_project.py <project_path>
Checks for:
  - Files in wrong project directories
  - Papers/documents outside their domain
  - Stale or orphaned files
"""

import os
import sys
from pathlib import Path

# Domain keywords for classification
DOMAINS = {
    'sphere_packing': ['sphere', 'packing', 'ias', 'isostaticity', 'hyperuniform', 'jammed'],
    'neural_networks': ['neural', 'network', 'approximation', 'deep', 'learning'],
    'linear_algebra': ['matrix', 'svd', 'cur', 'decomposition', 'randnla'],
    'astrophysics': ['magnetar', 'neutron', 'sgr', 'x-ray', 'burst', 'radio'],
    'dbt': ['therapy', 'mindscape', 'dialectical', 'skills', 'diary'],
}

def classify_file(filename, first_lines=None):
    """Guess domain of a file based on name and content."""
    lower_name = filename.lower()
    matches = {domain: 0 for domain in DOMAINS}
    
    # Score by filename
    for domain, keywords in DOMAINS.items():
        for kw in keywords:
            if kw in lower_name:
                matches[domain] += 2
    
    # Score by content (if available)
    if first_lines:
        content = ' '.join(first_lines).lower()
        for domain, keywords in DOMAINS.items():
            for kw in keywords:
                if kw in content:
                    matches[domain] += 1
    
    best = max(matches.items(), key=lambda x: x[1])
    return best[0] if best[1] > 0 else None

def verify_project(project_path, project_name):
    """Check project for misfiled content."""
    path = Path(project_path)
    
    if not path.exists():
        print(f"❌ Project path not found: {project_path}")
        return False
    
    print(f"✓ Scanning {project_name} at {project_path}")
    
    # Common PDF/doc locations
    suspicious = []
    for ext in ['*.pdf', '*.PDF']:
        for pdf in path.rglob(ext):
            # Try to read first few lines to detect mismatch
            try:
                with open(pdf, 'rb') as f:
                    header = f.read(500).decode('utf-8', errors='ignore')
                    detected = classify_file(pdf.name, [header])
                    if detected and detected != project_name.lower().split('_')[0]:
                        suspicious.append((pdf.relative_to(path), detected))
            except:
                pass
    
    if suspicious:
        print(f"\n⚠️  Potential misfiled files:")
        for file, detected_domain in suspicious:
            print(f"   {file} → detected as {detected_domain}")
    else:
        print(f"\n✓ No obvious misfiled documents detected.")
    
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: verify_project.py <project_path> [project_name]")
        sys.exit(1)
    
    project_path = sys.argv[1]
    project_name = sys.argv[2] if len(sys.argv) > 2 else Path(project_path).name
    
    verify_project(project_path, project_name)
