"""
PDF merging utilities.

Provides a library-friendly function `merge_pdfs` that merges multiple PDF files
into a single output file, with basic validation and overwrite control.

Also exposes a backward-compatible `merge(self, readFileList, _translate)`
function used by the legacy PyQt UI. New code should prefer `merge_pdfs`.
"""

from __future__ import annotations

import os
from typing import Iterable, List
import tempfile

from pathlib import Path

# Support modern pypdf first; gracefully fall back to PyPDF2
_PdfMerger = None
try:  # Preferred: pypdf (PdfMerger in older versions)
    from pypdf import PdfMerger as _PdfMerger  # type: ignore
except Exception:
    # pypdf>=6 may remove PdfMerger; provide a small compatibility wrapper via PdfWriter
    try:
        from pypdf import PdfWriter as _PdfWriter  # type: ignore

        class _PdfMerger:  # type: ignore[override]
            def __init__(self, *args, **kwargs) -> None:
                self._writer = _PdfWriter()

            def append(self, file_path: str) -> None:
                # PdfWriter.append can take a file path and append all pages
                self._writer.append(file_path)

            def write(self, fh) -> None:
                self._writer.write(fh)

            def close(self) -> None:
                # PdfWriter has no close; nothing to do
                pass

    except Exception:
        # Fall back to PyPDF2 (new/old API names)
        try:
            from PyPDF2 import PdfMerger as _PdfMerger  # type: ignore
        except Exception:
            try:
                from PyPDF2 import PdfFileMerger as _PdfMerger  # type: ignore
            except Exception as _e:  # pragma: no cover
                _PdfMerger = None


class MergeError(Exception):
    """Raised when merging fails for any reason."""


def merge_pdfs(input_files: Iterable[str], output_path: str, overwrite: bool = False) -> str:
    """
    Merge multiple PDF files into a single PDF.

    Args:
        input_files: Iterable of input PDF file paths (in desired order).
        output_path: Destination PDF file path ('.pdf' extension recommended).
        overwrite: If False and output exists, raise FileExistsError. If True, overwrite.

    Returns:
        The absolute path to the written merged PDF file.

    Raises:
        ValueError: If no input files provided or an input path is invalid.
        FileExistsError: If output exists and overwrite is False.
        MergeError: If the underlying PDF merge operation fails.
    """
    if _PdfMerger is None:  # pragma: no cover
        raise MergeError("No PDF merger backend available. Install 'pypdf' or 'PyPDF2'.")

    files: List[str] = [os.fspath(p) for p in input_files if str(p).strip()]
    if not files:
        raise ValueError("No input PDF files provided.")

    # Validate inputs exist
    for f in files:
        if not os.path.isfile(f):
            raise ValueError(f"Input file not found: {f}")

    out_path = os.path.abspath(os.fspath(output_path))
    out_dir = os.path.dirname(out_path) or os.getcwd()
    os.makedirs(out_dir, exist_ok=True)

    if os.path.isdir(out_path):
        raise ValueError("Output path points to a directory, not a file.")

    if os.path.exists(out_path) and not overwrite:
        raise FileExistsError(f"Output file already exists: {out_path}")

    # Prepare temporary conversions for non-PDF inputs
    try:
        # If running as a package (imported), relative import works
        from . import convert as _convert  # type: ignore
    except Exception:
        # If running as a simple module script, fall back to absolute
        import convert as _convert  # type: ignore

    tmpdir_ctx = tempfile.TemporaryDirectory()
    tmpdir = None

    try:
        tmpdir = tmpdir_ctx.__enter__()
        pdf_paths: List[str] = []
        for f in files:
            if Path(f).suffix.lower() == ".pdf":
                pdf_paths.append(f)
            else:
                # Convert supported types to temporary PDFs
                if _convert.is_supported_nonpdf(f):
                    out_pdf = _convert.convert_to_pdf(f, tmp_dir=tmpdir)
                    pdf_paths.append(out_pdf)
                else:
                    raise ValueError(f"Unsupported input type: {f}")

        # Some backends accept strict kwarg; ignore if unsupported.
        try:
            merger = _PdfMerger(strict=False)  # type: ignore[arg-type]
        except TypeError:
            merger = _PdfMerger()  # type: ignore[call-arg]

        for pdf in pdf_paths:
            # For very old backends, append can accept a file path string.
            merger.append(pdf)  # type: ignore[arg-type]

        # Ensure output has .pdf extension (if not provided)
        root, ext = os.path.splitext(out_path)
        if not ext:
            out_path = root + ".pdf"

        with open(out_path, "wb") as fh:
            merger.write(fh)
    except FileExistsError:
        # Bubble up as-is
        raise
    except Exception as e:  # pragma: no cover
        raise MergeError(f"Failed to merge PDFs: {e}") from e
    finally:
        try:
            merger.close()  # type: ignore[attr-defined]
        except Exception:
            pass
        # Cleanup temp dir
        try:
            if tmpdir is not None:
                tmpdir_ctx.__exit__(None, None, None)
        except Exception:
            pass

    return out_path


def merge(self, readFileList, _translate):
    """Backward-compat thin wrapper used by the legacy GUI.

    This uses `self.outputfolder` and `self.outputFile.text()` from the UI to
    construct the output path, then calls `merge_pdfs` with overwrite=True.
    """
    output_name = str(self.outputFile.text()).strip()
    output_dir = str(getattr(self, "outputfolder", "")).strip()
    if not output_name:
        raise ValueError("Output filename is empty.")
    if not output_dir:
        raise ValueError("Output directory is not selected.")

    mergedfile = os.path.join(output_dir, f"{output_name}.pdf")
    # Legacy behavior: force overwrite to avoid secondary prompts here.
    merge_pdfs(readFileList, mergedfile, overwrite=True)
