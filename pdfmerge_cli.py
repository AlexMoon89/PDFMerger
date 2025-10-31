#!/usr/bin/env python3
r"""
Simple CLI for merging PDFs using the library `pdfmerge.merge_pdfs`.

Examples (PowerShell):

  # Merge two PDFs into out.pdf (prompt or fail if exists)
  python .\pdfmerge_cli.py -o .\out.pdf .\a.pdf .\b.pdf

  # Overwrite if out.pdf exists
  python .\pdfmerge_cli.py -f -o .\out.pdf .\a.pdf .\b.pdf
This tool also accepts common image files (png/jpg/jpeg/bmp/tif/tiff/gif) and
text files (.txt). Non-PDFs are converted to PDF pages automatically.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pdfmerge


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Merge multiple PDF files into a single PDF.")
    p.add_argument("input", nargs="+", help="Input PDF files in the desired order")
    p.add_argument("-o", "--output", required=True, help="Output PDF file path")
    p.add_argument("-f", "--force", action="store_true", help="Overwrite output if it exists")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    out_path = str(Path(args.output))
    try:
        pdfmerge.merge_pdfs(args.input, out_path, overwrite=args.force)
    except FileExistsError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"Merged {len(args.input)} files -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
