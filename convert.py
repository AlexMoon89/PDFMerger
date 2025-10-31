"""
Converters for non-PDF inputs to temporary PDF files for merging.

Supported out of the box:
- Images: .png, .jpg, .jpeg, .bmp, .tif, .tiff, .gif (via img2pdf)
- Text: .txt (via reportlab platypus)

Optional (if dependencies available on system):
- DOCX: .docx (via docx2pdf on Windows w/ Microsoft Word)
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional

# Optional docx conversion
try:  # pragma: no cover - optional
    import docx2pdf  # type: ignore
    _HAS_DOCX2PDF = True
except Exception:  # pragma: no cover - optional
    _HAS_DOCX2PDF = False

# Required converters
import img2pdf  # type: ignore
from reportlab.lib.pagesizes import A4  # type: ignore
from reportlab.lib.styles import getSampleStyleSheet  # type: ignore
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer  # type: ignore
from reportlab.lib.units import inch  # type: ignore

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".gif"}
TEXT_EXTS = {".txt"}
DOCX_EXTS = {".docx"}


def is_supported_nonpdf(path: str) -> bool:
    ext = Path(path).suffix.lower()
    return (ext in IMAGE_EXTS) or (ext in TEXT_EXTS) or (ext in DOCX_EXTS and _HAS_DOCX2PDF)


def convert_to_pdf(input_path: str, tmp_dir: Optional[str] = None) -> str:
    """
    Convert a supported non-PDF file into a temporary PDF file, and return its path.

    The returned file resides in the given temp directory (or a new one) and will
    be suitable for merging with pypdf/PyPDF2.

    Raises ValueError for unsupported types or when a required converter is missing.
    """
    in_path = os.path.abspath(os.fspath(input_path))
    if not os.path.isfile(in_path):
        raise ValueError(f"Input not found: {in_path}")

    ext = Path(in_path).suffix.lower()
    if tmp_dir is None:
        tmp_dir = tempfile.gettempdir()

    if ext in IMAGE_EXTS:
        out = os.path.join(tmp_dir, f"img_{Path(in_path).stem}.pdf")
        _image_to_pdf(in_path, out, tmp_dir)
        return out

    if ext in TEXT_EXTS:
        out = os.path.join(tmp_dir, f"txt_{Path(in_path).stem}.pdf")
        _text_to_pdf(in_path, out)
        return out

    if ext in DOCX_EXTS:
        if not _HAS_DOCX2PDF:
            raise ValueError(".docx support requires 'docx2pdf' and Microsoft Word on Windows.")
        out = os.path.join(tmp_dir, f"docx_{Path(in_path).stem}.pdf")
        # docx2pdf handles in->out conversion via Word COM on Windows
        docx2pdf.convert(in_path, out)  # type: ignore[attr-defined]
        return out

    raise ValueError(f"Unsupported file type for conversion: {ext}")


def _text_to_pdf(txt_path: str, out_pdf: str) -> None:
    """Render plain text into a simple paginated PDF using ReportLab."""
    styles = getSampleStyleSheet()
    story = []

    with open(txt_path, "r", encoding="utf-8", errors="ignore") as fh:
        content = fh.read()

    # Simple paragraph per line; could be enhanced to wrap long lines
    for line in content.splitlines():
        if line.strip():
            story.append(Paragraph(_escape_xml(line), styles["BodyText"]))
        else:
            story.append(Spacer(1, 0.2 * inch))

    doc = SimpleDocTemplate(out_pdf, pagesize=A4, leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            topMargin=0.75 * inch, bottomMargin=0.75 * inch, title=Path(txt_path).name)
    doc.build(story)


def _escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
    )


def _image_to_pdf(img_path: str, out_pdf: str, tmp_dir: str) -> None:
    """
    Convert an image to PDF with robust handling of invalid EXIF rotation.

    Uses img2pdf with rotation=ifvalid and auto_orient=True when available.
    Falls back to fixing orientation with Pillow and re-encoding to PNG if needed.
    """
    # First attempt: rely on img2pdf with safe rotation handling
    kwargs = {"auto_orient": True}
    try:
        # img2pdf.Rotation.ifvalid is available in newer versions
        kwargs["rotation"] = img2pdf.Rotation.ifvalid  # type: ignore[attr-defined]
    except Exception:
        pass

    try:
        with open(out_pdf, "wb") as f:
            f.write(img2pdf.convert(img_path, **kwargs))
        return
    except Exception as e:
        msg = str(e).lower()
        if "invalid rotation" not in msg and "rotation" not in msg:
            # Some other error, re-raise
            raise

    # Fallback: normalize orientation using Pillow and remove EXIF orientation tag
    try:
        from PIL import Image, ImageOps  # type: ignore

        with Image.open(img_path) as im:
            fixed = ImageOps.exif_transpose(im)
            tmp_fixed = os.path.join(tmp_dir, f"fixed_{Path(img_path).stem}.png")
            fixed.save(tmp_fixed, format="PNG")

        with open(out_pdf, "wb") as f:
            # After transposing, disable auto_orient to avoid further changes
            f.write(img2pdf.convert(tmp_fixed, auto_orient=False))
    except Exception:
        # As a last resort, re-run original attempt without rotation kwarg
        with open(out_pdf, "wb") as f:
            f.write(img2pdf.convert(img_path))
