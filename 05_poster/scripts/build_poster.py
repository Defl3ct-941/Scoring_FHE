"""
Construit le poster A0 à partir de la source éditable 05_poster/poster.html.

  1. recopie data/mesures.json dans le bloc <script id="mesures"> du poster ;
  2. imprime le poster en PDF vectoriel A0 (841 x 1189 mm, polices Roboto embarquées) ;
  3. produit un aperçu PNG basse définition (poster_apercu.png).

Prérequis :
    pip install playwright pypdf && python -m playwright install chromium
Usage (depuis la racine du dépôt) :
    python 05_poster/scripts/benchmark.py     # facultatif : refaire les mesures
    python 05_poster/scripts/build_poster.py
Variable facultative CHROMIUM_PATH : chemin d'un Chromium déjà installé.
"""

import json
import os
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

POSTER_DIR = Path(__file__).resolve().parents[1]
HTML = POSTER_DIR / "poster.html"
DATA = POSTER_DIR / "data" / "mesures.json"
PDF = POSTER_DIR / "poster_FYC_scoring_FHE_A0.pdf"
PNG = POSTER_DIR / "poster_apercu.png"

MM_TO_PX = 96 / 25.4


def inject_measures() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    html = HTML.read_text(encoding="utf-8")
    block = json.dumps(data, indent=2, ensure_ascii=False)
    new, n = re.subn(
        r'(<script id="mesures" type="application/json">)(.*?)(</script>)',
        lambda m: f"{m.group(1)}\n{block}\n{m.group(3)}",
        html,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit("Bloc <script id=\"mesures\"> introuvable dans poster.html")
    HTML.write_text(new, encoding="utf-8")


def render() -> None:
    launch = {}
    if os.environ.get("CHROMIUM_PATH"):
        launch["executable_path"] = os.environ["CHROMIUM_PATH"]
    with sync_playwright() as p:
        browser = p.chromium.launch(**launch)
        page = browser.new_page(
            viewport={"width": round(841 * MM_TO_PX), "height": round(1189 * MM_TO_PX)},
            device_scale_factor=0.5,
        )
        page.goto(HTML.as_uri())
        page.evaluate("document.fonts.ready")
        page.wait_for_load_state("networkidle")
        overflow = page.evaluate(
            """() => [...document.querySelectorAll('.col')].map(c => {
                   const last = c.lastElementChild.getBoundingClientRect().bottom;
                   return Math.round(last - c.getBoundingClientRect().bottom);
               })"""
        )
        print("Marge restante par colonne (px, négatif = place libre) :", overflow)
        page.screenshot(path=str(PNG), full_page=False)
        page.pdf(path=str(PDF), width="841mm", height="1189mm", print_background=True,
                 prefer_css_page_size=True)
        browser.close()
    set_metadata()
    print("PDF  :", PDF)
    print("PNG  :", PNG)


def set_metadata() -> None:
    """Auteurs et titre dans les propriétés du PDF (pypdf, facultatif)."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        print("pypdf absent : métadonnées du PDF non renseignées (pip install pypdf)")
        return
    writer = PdfWriter(clone_from=PdfReader(PDF))
    writer.add_metadata({
        "/Title": "Scoring financier sur données chiffrées (FHE) : poster FYC",
        "/Author": "Ravin THILAGARASA, Thomas GRUNDSZTEJN",
        "/Subject": "Poster scientifique, projet FYC ESGI 2026-2027",
        "/Keywords": "FHE, chiffrement homomorphe, scoring, Paillier, CKKS",
    })
    with open(PDF, "wb") as fh:
        writer.write(fh)


if __name__ == "__main__":
    inject_measures()
    render()
