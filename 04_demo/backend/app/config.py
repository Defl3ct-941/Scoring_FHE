"""
Modele de scoring financier utilise dans toute la demo.

Le score est volontairement LINEAIRE (une simple somme ponderee) car c'est
l'operation que les trois briques cryptographiques presentees (classique,
Paillier, FHE/CKKS) doivent toutes pouvoir "recevoir" en entree. C'est aussi
exactement le modele decrit dans le plan du memoire (section 3 : "score
lineaire pondere") avant d'envisager une regression logistique complete.

score = biais + w_revenu * (revenu - 2500)
              + w_endettement * ratio_endettement
              + w_incidents * incidents
"""

FEATURES = [
    {
        "key": "revenu",
        "label": "Revenu mensuel net",
        "unit": "EUR",
        "min": 1000,
        "max": 8000,
        "step": 50,
        "default": 2500,
        "help": "Plus le revenu est eleve, plus le score augmente.",
    },
    {
        "key": "ratio_endettement",
        "label": "Taux d'endettement",
        "unit": "%",
        "min": 0,
        "max": 60,
        "step": 1,
        "default": 20,
        "help": "Part des revenus deja engagee dans des remboursements.",
    },
    {
        "key": "incidents",
        "label": "Incidents de paiement (12 derniers mois)",
        "unit": "",
        "min": 0,
        "max": 5,
        "step": 1,
        "default": 0,
        "help": "Nombre de retards ou impayes recents.",
    },
]

BIAS = 50.0
WEIGHT_REVENU = 0.005          # points par euro au-dessus/en-dessous de 2500 EUR
WEIGHT_ENDETTEMENT = -0.9      # points par point de pourcentage de ratio
WEIGHT_INCIDENTS = -10.0       # points par incident

# Vecteur de poids public, connu du "serveur" -> jamais secret. C'est
# precisement pourquoi le calcul peut se faire en clair COTE SERVEUR sur
# les poids, et en chiffre cote donnees client.
WEIGHTS_VECTOR = [WEIGHT_REVENU, WEIGHT_ENDETTEMENT, WEIGHT_INCIDENTS]


def centered_features(revenu: float, ratio_endettement: float, incidents: float):
    """Renvoie le vecteur de features exactement dans l'ordre de WEIGHTS_VECTOR."""
    return [float(revenu) - 2500.0, float(ratio_endettement), float(incidents)]


def plaintext_score(revenu: float, ratio_endettement: float, incidents: float) -> float:
    x = centered_features(revenu, ratio_endettement, incidents)
    return BIAS + sum(w * v for w, v in zip(WEIGHTS_VECTOR, x))
