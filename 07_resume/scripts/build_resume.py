"""Construit le résumé personnel (docx + PDF) à partir de resume_brouillon.md.

Usage : python 07_resume/scripts/build_resume.py
Prérequis : pandoc, python-docx, LibreOffice (soffice) pour le PDF.
La police Roboto du poster (05_poster/assets/fonts) est installée pour
l'utilisateur sous Linux afin que le PDF l'embarque.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "07_resume" / "resume_brouillon.md"
OUT_DOCX = ROOT / "07_resume" / "Resume_personnel_BROUILLON_v0.docx"
FONTS = ROOT / "05_poster" / "assets" / "fonts"

BLEU_NUIT = RGBColor(0x00, 0x1B, 0x40)
AUTEURS = "Ravin THILAGARASA; Thomas GRUNDSZTEJN"
MENTION = "BROUILLON DE TRAVAIL v0 — à réécrire par les auteurs avant dépôt Compilatio"


def install_fonts() -> None:
    if not sys.platform.startswith("linux"):
        return
    dest = Path.home() / ".fonts"
    dest.mkdir(exist_ok=True)
    for f in FONTS.glob("*.ttf"):
        shutil.copy(f, dest / f.name)
    subprocess.run(["fc-cache", "-f"], check=False, capture_output=True)


def set_font(style, size: float | None = None, bold: bool | None = None, color=None) -> None:
    style.font.name = "Roboto"
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), "Roboto")
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        rfonts.attrib.pop(qn(attr), None)
    if size:
        style.font.size = Pt(size)
    if bold is not None:
        style.font.bold = bold
    if color is not None:
        style.font.color.rgb = color


def make_reference(path: Path) -> None:
    data = subprocess.run(
        ["pandoc", "--print-default-data-file", "reference.docx"],
        check=True, capture_output=True,
    ).stdout
    path.write_bytes(data)
    doc = Document(path)
    styles = {s.name: s for s in doc.styles}

    class _St(dict):
        def __getitem__(self, k):
            return styles[k]

    st = _St()
    for name in ("Normal", "Body Text", "First Paragraph", "Compact", "Block Text"):
        if name in styles:
            set_font(st[name], 10.5)
            pf = st[name].paragraph_format
            pf.space_after = Pt(5)
            pf.line_spacing = 1.1
            if name in ("Body Text", "First Paragraph"):
                pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    set_font(st["Title"], 20, True, BLEU_NUIT)
    set_font(st["Subtitle"], 12, False, RGBColor(0xC0, 0x00, 0x00))
    for name in ("Author", "Date"):
        set_font(st[name], 11, False, BLEU_NUIT)
    set_font(st["Heading 1"], 14, True, BLEU_NUIT)
    set_font(st["Heading 2"], 12, True, BLEU_NUIT)
    st["Heading 1"].paragraph_format.space_before = Pt(12)
    st["Heading 2"].paragraph_format.space_before = Pt(8)
    doc.save(path)


def add_page_number(paragraph) -> None:
    run = paragraph.add_run()
    for kind, text in (("begin", None), (None, "PAGE"), ("end", None)):
        if kind:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = text
        run._r.append(el)


def postprocess(path: Path) -> None:
    doc = Document(path)
    for section in doc.sections:
        section.page_height, section.page_width = Cm(29.7), Cm(21.0)
        section.top_margin = section.bottom_margin = Cm(2.2)
        section.left_margin = section.right_margin = Cm(2.3)
        head = section.header.paragraphs[0]
        head.text = MENTION
        head.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in head.runs:
            r.font.name, r.font.size, r.font.bold = "Roboto", Pt(8), True
            r.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
        foot = section.footer.paragraphs[0]
        foot.text = "Ravin THILAGARASA · Thomas GRUNDSZTEJN — ESGI FYC 2026-2027 — page "
        foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_page_number(foot)
        for r in foot.runs:
            r.font.name, r.font.size = "Roboto", Pt(8)
    # Tableaux : police compacte et bordures simples
    for table in doc.tables:
        table.style = doc.styles["Table"] if "Table" in [s.name for s in doc.styles] else None
        tbl_pr = table._tbl.tblPr
        borders = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            b = OxmlElement(f"w:{edge}")
            b.set(qn("w:val"), "single")
            b.set(qn("w:sz"), "4")
            b.set(qn("w:color"), "8090A0")
            borders.append(b)
        tbl_pr.append(borders)
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    for r in p.runs:
                        r.font.size = Pt(9)
    cp = doc.core_properties
    cp.author = AUTEURS
    cp.last_modified_by = AUTEURS
    cp.title = "Scoring financier sur données chiffrées via FHE — résumé personnel (brouillon)"
    cp.comments = MENTION
    doc.save(path)


def main() -> None:
    install_fonts()
    with tempfile.TemporaryDirectory() as tmp:
        ref = Path(tmp) / "reference.docx"
        make_reference(ref)
        subprocess.run(
            ["pandoc", str(SRC), "-o", str(OUT_DOCX), f"--reference-doc={ref}"],
            check=True,
        )
    postprocess(OUT_DOCX)
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice:
        subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir",
             str(OUT_DOCX.parent), str(OUT_DOCX)],
            check=True, capture_output=True,
        )
        print("PDF :", OUT_DOCX.with_suffix(".pdf"))
    else:
        print("LibreOffice introuvable : PDF non généré.")
    print("DOCX :", OUT_DOCX)


if __name__ == "__main__":
    main()
