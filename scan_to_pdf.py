#!/usr/bin/env python3
"""
Scan multiple pages to a single searchable PDF for the DBT project.
Uses Canon LiDE 400 at 300 DPI, OCR via tesseract, merged with ghostscript.

Usage: python3 scan_to_pdf.py output.pdf
"""
import subprocess
import sys
import tempfile
from pathlib import Path

SCANNER = "pixma:04A91912_46F824"
DPI = 300
OUTPUT_DIR = Path.home() / "projects" / "DBT"


def scan_page(page_num: int, tmpdir: str) -> Path:
    out = Path(tmpdir) / f"page_{page_num:03d}.png"
    print(f"  Scanning page {page_num}...", end=" ", flush=True)
    result = subprocess.run([
        "scanimage",
        f"--device={SCANNER}",
        f"--resolution={DPI}",
        "--format=png",
        "--mode=Gray",
        f"--output-file={out}",
    ], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr.strip()}")
        sys.exit(1)
    print("done")
    return out


def ocr_page(img: Path, tmpdir: str) -> Path:
    out_base = Path(tmpdir) / f"ocr_{img.stem}"
    result = subprocess.run([
        "tesseract", str(img), str(out_base), "-l", "eng", "pdf"
    ], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"OCR error: {result.stderr.strip()}")
        sys.exit(1)
    return out_base.with_suffix(".pdf")


def merge_pdfs(pdfs: list[Path], output: Path):
    result = subprocess.run([
        "gs", "-dBATCH", "-dNOPAUSE", "-q",
        "-sDEVICE=pdfwrite", f"-sOutputFile={output}",
    ] + [str(p) for p in pdfs], capture_output=True, text=True)
    if result.returncode != 0:
        subprocess.run(["pdfunite"] + [str(p) for p in pdfs] + [str(output)], check=True)


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "scanned_document.pdf"
    if not name.endswith(".pdf"):
        name += ".pdf"
    output = OUTPUT_DIR / name

    print(f"Scanner: Canon LiDE 400 @ {DPI} DPI")
    print(f"Output:  {output}")
    print("Press Ctrl+C after placing the last page to stop scanning and generate PDF.\n")

    tmpdir = tempfile.mkdtemp()
    pages = []
    page_num = 1

    try:
        while True:
            input(f"Place page {page_num} on scanner and press Enter...")
            img = scan_page(page_num, tmpdir)
            pages.append(img)
            page_num += 1
    except KeyboardInterrupt:
        print(f"\n\nScanning complete — {len(pages)} page(s) captured.")

    if not pages:
        print("No pages scanned. Exiting.")
        sys.exit(0)

    print("\nRunning OCR...")
    pdf_pages = []
    for img in pages:
        print(f"  OCR {img.stem}...", end=" ", flush=True)
        pdf = ocr_page(img, tmpdir)
        pdf_pages.append(pdf)
        print("done")

    print(f"\nMerging into {output.name}...")
    output.parent.mkdir(parents=True, exist_ok=True)
    merge_pdfs(pdf_pages, output)

    print(f"\n✓ Done: {output}")
    print(f"  Pages: {len(pages)}, Size: {output.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
