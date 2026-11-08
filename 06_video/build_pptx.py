"""
Genere video/PPT_CAS_PRATIQUE_FHE.pptx : le support de presentation utilise
pendant les parties de la video ou l'on n'est PAS sur une page web (04_demo/
ou 03_cas_pratiques/atelier-web/).

Reprend le theme visuel de BASE_template_video_scoring_fhe.pptx (couleurs,
polices, icones) SANS jamais modifier ce fichier : on l'ouvre, on retire ses
diapositives d'exemple ("Lorem Ipsum"), et on enregistre sous un nouveau nom.

Usage :
    python build_pptx.py
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Pt

HERE = Path(__file__).parent
BASE_PPTX = HERE / "BASE_template_video_scoring_fhe.pptx"
OUTPUT_PPTX = HERE / "PPT_CAS_PRATIQUE_FHE.pptx"

MEDIA_DIR = HERE / "_icons_extracted"

# ---------------------------------------------------------------------------
# Palette et typographies reprises du template BASE (voir BASE_...pptx)
# ---------------------------------------------------------------------------
NAVY = RGBColor(0x0B, 0x13, 0x2B)      # fond des diapos "sombres" (couverture, cloture)
NAVY_2 = RGBColor(0x1C, 0x25, 0x41)    # fond des diapos de transition ("chapitres")
LIGHT_BG = RGBColor(0xF4, 0xF6, 0xF8)  # fond des diapos de contenu
TEAL = RGBColor(0x5B, 0xC0, 0xBE)      # accent
GRAY = RGBColor(0x6B, 0x7A, 0x8F)      # texte secondaire
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK_TEXT = NAVY

TITLE_FONT = "Cambria"
BODY_FONT = "Calibri"

PRESENTER_NAME = "Clément Ruault"
SESSION_LABEL = "Cas pratique : support de présentation"

ICON_LOCK = str(MEDIA_DIR / "icon_lock.png")
ICON_KEY = str(MEDIA_DIR / "icon_key.png")
ICON_SHIELD = str(MEDIA_DIR / "icon_shield.png")
ICON_DATABASE = str(MEDIA_DIR / "icon_database.png")
ICON_CHIP = str(MEDIA_DIR / "icon_chip.png")
ICON_NETWORK = str(MEDIA_DIR / "icon_network.png")
ICON_QUESTION = str(MEDIA_DIR / "icon_question.png")


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------

def set_background(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def add_shape(slide, shape_type, x, y, w, h, color, line=False):
    shp = slide.shapes.add_shape(shape_type, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    if not line:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = color
    shp.shadow.inherit = False
    return shp


def add_rect(slide, x, y, w, h, color):
    return add_shape(slide, MSO_SHAPE.RECTANGLE, x, y, w, h, color)


def add_circle(slide, x, y, d, color):
    return add_shape(slide, MSO_SHAPE.OVAL, x, y, d, d, color)


def add_rounded_rect(slide, x, y, w, h, color):
    shp = add_shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, color)
    try:
        shp.adjustments[0] = 0.06
    except Exception:
        pass
    return shp


def add_textbox(slide, x, y, w, h, text, size, color, bold=False, font=BODY_FONT,
                 align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line_spacing=1.0, italic=False):
    tb = slide.shapes.add_textbox(Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.name = font
        r.font.color.rgb = color
    return tb


def add_dot_grid(slide, x0, y0, cols, rows, step=146304, size=82296, color=TEAL):
    for row in range(rows):
        for col in range(cols):
            add_rect(slide, x0 + col * step, y0 + row * step, size, size, color)


def add_kicker(slide, dark: bool):
    """Marque de marque en haut a gauche : rond teal + icone + libelle."""
    text_color = WHITE if dark else NAVY
    add_circle(slide, 457200, 320040, 310896, TEAL)
    slide.shapes.add_picture(ICON_LOCK, Emu(457200 + 88000), Emu(320040 + 88000), Emu(134896), Emu(134896))
    add_textbox(
        slide, 868680, 320040, 5114800, 310896,
        "SCORING FINANCIER · FHE", 10, text_color, bold=True,
        anchor=MSO_ANCHOR.MIDDLE,
    )


def new_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[0])


# ---------------------------------------------------------------------------
# Diapositives
# ---------------------------------------------------------------------------

def slide_cover(prs):
    """01 - Page de titre (fond sombre)."""
    s = new_slide(prs)
    set_background(s, NAVY)
    add_dot_grid(s, 10561320, 5806440, 8, 5)
    add_kicker(s, dark=True)

    add_textbox(s, 640080, 2200000, 10911840, 1600000,
                "Scoring financier sur données chiffrées via FHE",
                40, WHITE, bold=True, font=TITLE_FONT, line_spacing=1.05)
    add_textbox(s, 658368, 3900000, 9875520, 500000,
                "Prototype et limites : cas pratique",
                16, TEAL, bold=False, font=BODY_FONT)

    add_textbox(s, 640080, 6126480, 7315200, 320040,
                PRESENTER_NAME, 12, WHITE, font=BODY_FONT)
    add_textbox(s, 640080, 6419088, 6572000, 274320,
                SESSION_LABEL, 11, GRAY, font=BODY_FONT)
    return s


def slide_divider(prs, number, title, subtitle):
    """Diapositive de transition / chapitre (fond sombre, gros numero)."""
    s = new_slide(prs)
    set_background(s, NAVY_2)
    add_kicker(s, dark=True)

    add_circle(s, 10424160, 685800, 822960, TEAL)
    s.shapes.add_picture(ICON_LOCK, Emu(10424160 + 205740), Emu(685800 + 205740), Emu(411480), Emu(411480))

    add_dot_grid(s, 502920, 6035040, 10, 3)

    add_textbox(s, 640080, 2286000, 2926080, 2011680, number, 120, TEAL, bold=True, font=TITLE_FONT)
    add_textbox(s, 3749040, 2697480, 7680960, 1005840, title, 34, WHITE, bold=True, font=TITLE_FONT)
    add_textbox(s, 3767328, 3620440, 7315200, 548640, subtitle, 15, GRAY, font=BODY_FONT)
    return s


def slide_content_header(s, title):
    add_kicker(s, dark=False)
    add_textbox(s, 640080, 914400, 10058400, 640080, title, 32, DARK_TEXT, bold=True, font=TITLE_FONT)


def slide_icon_list(prs, title, items):
    """3 items avec icone ronde + titre + description (fond clair)."""
    s = new_slide(prs)
    set_background(s, LIGHT_BG)
    slide_content_header(s, title)

    y_positions = [1965960, 3383280, 4800600]
    for (icon, item_title, item_desc), y in zip(items, y_positions):
        add_circle(s, 640080, y, 685800, TEAL)
        s.shapes.add_picture(icon, Emu(640080 + 171450), Emu(y + 171450), Emu(342900), Emu(342900))
        add_textbox(s, 1600200, y - 27432, 9326880, 384048, item_title, 18, DARK_TEXT, bold=True)
        add_textbox(s, 1600200, y + 365760, 9326880, 548640, item_desc, 14, GRAY)
    return s


def slide_scenario_diagram(prs, title, bullets):
    """Puces a gauche + petit pipeline visuel a droite (fond clair)."""
    s = new_slide(prs)
    set_background(s, LIGHT_BG)
    slide_content_header(s, title)

    y0 = 1856232
    step = 960000
    for text in bullets:
        add_rect(s, 658368, y0 + 91440, 109728, 109728, TEAL)
        add_textbox(s, 960120, y0, 4937760, 800000, text, 14.5, DARK_TEXT, line_spacing=1.1)
        y0 += step

    # Carte blanche a droite avec le pipeline client -> serveur -> client
    card_x, card_y, card_w, card_h = 6309360, 1783080, 5212080, 4206240
    add_rounded_rect(s, card_x, card_y, card_w, card_h, WHITE)

    box_w = card_w - 900000
    box_h = 700000
    box_x = card_x + (card_w - box_w) // 2
    gap = 260000

    steps = [
        ("🔒  Client chiffre ses données", TEAL),
        ("🖥️  Serveur calcule (sans déchiffrer)", NAVY),
        ("🔓  Client déchiffre le résultat", TEAL),
    ]
    y = card_y + 260000
    for i, (label, color) in enumerate(steps):
        rect = add_rounded_rect(s, box_x, y, box_w, box_h, color)
        tf = rect.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = label
        r.font.size = Pt(13.5)
        r.font.bold = True
        r.font.name = BODY_FONT
        r.font.color.rgb = WHITE if color != TEAL else NAVY
        if i < 2:
            arrow_y = y + box_h + (gap - 260000) // 2 + 40000
            add_shape(s, MSO_SHAPE.DOWN_ARROW, box_x + box_w // 2 - 60000, y + box_h + 20000, 120000, gap - 40000, GRAY)
        y += box_h + gap
    return s


def slide_stats(prs, title, stats):
    """3 chiffres cles cote a cote (fond clair)."""
    s = new_slide(prs)
    set_background(s, LIGHT_BG)
    slide_content_header(s, title)

    xs = [640080, 4251960, 7863840]
    for (value, label), x in zip(stats, xs):
        add_rounded_rect(s, x, 2377440, 3291840, 2926080, WHITE)
        add_textbox(s, x + 182880, 2834640, 2926080, 1005840, value, 40, TEAL, bold=True, font=TITLE_FONT)
        add_textbox(s, x + 320040, 3977640, 2651760, 1005840, label, 13, GRAY)
    return s


def slide_bullets(prs, title, bullets):
    """Liste a puces simple (fond clair) pour la conclusion."""
    s = new_slide(prs)
    set_background(s, LIGHT_BG)
    slide_content_header(s, title)

    y0 = 1965960
    for text in bullets:
        add_rect(s, 658368, y0 + 91440, 109728, 109728, TEAL)
        add_textbox(s, 960120, y0, 9700000, 700000, text, 15, DARK_TEXT, line_spacing=1.15)
        y0 += 820000
    return s


def slide_closing(prs):
    """Diapositive finale (fond sombre)."""
    s = new_slide(prs)
    set_background(s, NAVY)
    add_kicker(s, dark=True)
    add_dot_grid(s, 502920, 822960, 6, 3)

    add_circle(s, 5641848, 1920240, 914400, TEAL)
    s.shapes.add_picture(ICON_QUESTION, Emu(5641848 + 228600), Emu(1920240 + 228600), Emu(457200), Emu(457200))

    add_textbox(s, 1371600, 3063240, 9445752, 731520, "Merci de votre attention", 32, WHITE, bold=True,
                font=TITLE_FONT, align=PP_ALIGN.CENTER)
    add_textbox(s, 1371600, 3794760, 9445752, 457200, "Des questions ?", 18, TEAL, align=PP_ALIGN.CENTER)

    add_textbox(s, 1371600, 6126480, 9445752, 320040, f"{PRESENTER_NAME} · {SESSION_LABEL}", 12, GRAY,
                align=PP_ALIGN.CENTER)
    return s


# ---------------------------------------------------------------------------
# Construction du deck
# ---------------------------------------------------------------------------

def build():
    prs = Presentation(str(BASE_PPTX))

    # On retire les diapositives d'exemple ("Lorem Ipsum") du template de base
    # SANS toucher au fichier BASE_ sur le disque : on travaille en memoire et
    # on enregistrera sous un nouveau nom.
    sld_id_lst = prs.slides._sldIdLst
    for sld in list(sld_id_lst):
        prs.part.drop_rel(sld.rId)
        sld_id_lst.remove(sld)

    # 1. Couverture
    slide_cover(prs)

    # 2. Chapitre : la problematique
    slide_divider(
        prs, "01", "La problématique",
        "Scoring de crédit, données sensibles et RGPD : peut-on calculer sans jamais voir ?",
    )

    # 3. Les 3 niveaux de chiffrement (rappel theorique express)
    slide_icon_list(
        prs,
        "Trois niveaux de chiffrement",
        [
            (ICON_SHIELD, "Chiffrement classique (AES)",
             "Protège la donnée au repos et en transit, mais aucun calcul possible sur le chiffré."),
            (ICON_KEY, "Chiffrement homomorphe partiel (Paillier)",
             "Addition entre chiffrés et multiplication par un nombre public : suffisant pour un score linéaire."),
            (ICON_CHIP, "FHE complet (CKKS, TFHE...)",
             "Addition ET multiplication entre deux chiffrés, sur des réels : des modèles bien plus riches, au prix du coût de calcul."),
        ],
    )

    # 4. Le scenario du projet
    slide_scenario_diagram(
        prs,
        "Le scénario : un score de crédit sans jamais montrer les données",
        [
            "Trois données sensibles : revenu, taux d'endettement, incidents de paiement.",
            "Score linéaire pondéré : biais + somme des poids × features.",
            "Les poids sont publics (connus du serveur) ; seules les données du client restent secrètes.",
        ],
    )

    # 5. Chapitre : demonstration en direct
    slide_divider(
        prs, "02", "Démonstration en direct",
        "Application web pédagogique (localhost:8000) puis atelier d'exercices corrigés (localhost:8100).",
    )

    # [ICI : bascule vers le navigateur, hors PowerPoint]

    # 6. Chapitre : limites
    slide_divider(
        prs, "03", "Limites & regard critique",
        "Ce que la démo met en évidence, au-delà de la théorie.",
    )

    # 7. Les limites reelles du FHE
    slide_icon_list(
        prs,
        "Les limites réelles du FHE aujourd'hui",
        [
            (ICON_CHIP, "Surcoût computationnel",
             "Un calcul homomorphe peut être des centaines de fois plus lent qu'en clair."),
            (ICON_DATABASE, "Expansion des données",
             "Un chiffré CKKS peut peser des milliers de fois plus que la donnée brute."),
            (ICON_KEY, "Comparaisons et bootstrapping",
             "Pas de \"if score > seuil\" simple sur du chiffré ; le bootstrapping reste le principal verrou de performance."),
        ],
    )

    # 8. Chiffres mesures dans la demo
    slide_stats(
        prs,
        "Ce que la démo mesure concrètement",
        [
            ("exact", "Résultat Paillier vs score en clair"),
            ("×13 900", "Facteur d'expansion des données (CKKS)"),
            ("≈380 ms", "Temps de calcul total (CKKS, bout en bout)"),
        ],
    )

    # 9. Conclusion & perspectives
    slide_bullets(
        prs,
        "Conclusion & perspectives",
        [
            "Le FHE fonctionne : prototype réel, pas seulement théorique (Paillier exact, CKKS approché).",
            "Mais il reste aujourd'hui coûteux et complexe pour un vrai système bancaire en production.",
            "Pistes : accélération matérielle (GPU/FPGA), progrès sur le bootstrapping, standardisation (NIST, HomomorphicEncryption.org).",
        ],
    )

    # 10. Cloture
    slide_closing(prs)

    prs.save(str(OUTPUT_PPTX))
    print(f"OK -> {OUTPUT_PPTX} ({len(prs.slides._sldIdLst)} slides)")


if __name__ == "__main__":
    build()
