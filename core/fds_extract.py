import re

def raccourcir_texte(texte, code, longueur):
    if not code:  # If code is empty
        return texte
    debut_texte = texte.find(code)
    if debut_texte == -1:
        return texte
    fin_texte = min(debut_texte + longueur, len(texte))
    return texte[debut_texte:fin_texte]

def extraire_code_un(texte):
    pattern_un = r'UN\s*\d{4}'
    
    match = re.search(pattern_un, texte, re.IGNORECASE)
    if match:
        #return match.group().replace(' ', '').upper()
        return match.group().upper()
    
    return None

def extraire_GE(texte: str):
    # 1) On se limite à la rubrique transport 
    zone = extraire_info_transport(texte)

    # 2) Motif principal : autour de "Groupe d’emballage"
    pattern_groupe = r"Groupe d[’']emballage.*?\b(I{1,3})\b"
    match = re.search(pattern_groupe, zone, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1)  # "I", "II" ou "III"

    # 3) Motifs secondaires : ADR / IMDG / IATA
    patterns_modes = [
        r"\bADR[^I\n]{0,80}\b(I{1,3})\b",
        r"\bIMDG[^I\n]{0,80}\b(I{1,3})\b",
        r"\bIATA[^I\n]{0,80}\b(I{1,3})\b",
    ]
    for pat in patterns_modes:
        match = re.search(pat, zone, flags=re.IGNORECASE)
        if match:
            return match.group(1)

    # 4) Motif "Règlement type" avec UN, classe, GE
    pattern_reglement = r"Règlement type[^I\n]{0,120}\b(I{1,3})\b"
    match = re.search(pattern_reglement, zone, flags=re.IGNORECASE)
    if match:
        return match.group(1)

    return None

def extraire_LQ(texte: str):
    """
    Extrait la limite de quantité (LQ) depuis la zone Transport (rubrique 14).

    Règles métier :
    - Valeurs possibles : 0, 1, 5, 100, 500
    - Pour 100 ou 500, l'unité est forcément mL
    """

    # 1) Limiter la recherche à la zone transport si possible
    zone = extraire_info_transport(texte)
    if zone is None:
        zone = texte

    # 2) Normalisation légère
    zone = zone.replace("ml", "mL").replace("Ml", "mL").replace("ML", "mL")

    # 3) Pattern principal : formes explicites "Quantités limitées (LQ) ..."
    pattern_principal = (
        r"(Quantités limitées|Limited quantities)\s*\(LQ\)\s*"
        r"(0|1|5|100|500)\s*(L|mL|kg)"
    )
    match = re.search(pattern_principal, zone, flags=re.IGNORECASE)
    if match:
        quantite = match.group(2)
        unite = match.group(3)
        # Règle métier : 100 ou 500 => mL
        if quantite in ("100", "500"):
            unite = "mL"
        return f"{quantite} {unite}"

    # 4) Pattern secondaire : "LQ 5L", "LQ : 1 kg", etc.
    pattern_LQ_simple = r"LQ\s*[:\-]?\s*(0|1|5|100|500)\s*(L|mL|kg)"
    match = re.search(pattern_LQ_simple, zone, flags=re.IGNORECASE)
    if match:
        quantite = match.group(1)
        unite = match.group(2)
        if quantite in ("100", "500"):
            unite = "mL"
        return f"{quantite} {unite}"

    # 5) Fallback : petite fenêtre autour de "LQ"
    index = zone.find("LQ")
    if index != -1:
        extrait = zone[index:index + 50]
        pattern_fallback = r"(0|1|5|100|500)\s*(L|mL|kg)"
        match = re.search(pattern_fallback, extrait, flags=re.IGNORECASE)
        if match:
            quantite = match.group(1)
            unite = match.group(2)
            if quantite in ("100", "500"):
                unite = "mL"
            return f"{quantite} {unite}"

    # Rien trouvé ou valeur hors des règles métier
    return None


def extraire_classe(texte: str):
    """Extrait la classe de danger pour le transport (1, 2, 3, 4.1, ... 9)
    en se basant principalement sur la rubrique 14."""

    # 1) On se limite à la zone transport si possible
    zone = extraire_info_transport(texte)  # ou extraire_zone_transport(texte)
    if zone is None:
        zone = texte

    # 2) Motif principal : "Classe(s) de danger pour le transport"
    pattern_principal = (
        r"Classe[s]?\s+de\s+danger\s+pour\s+le\s+transport"
        r".*?\b(1|2|3|4\.1|4\.2|4\.3|5\.1|5\.2|6\.1|6\.2|7|8|9)\b"
    )
    match = re.search(pattern_principal, zone, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1)

    # 3) Motifs secondaires : "Classe 8", "Class 8"
    patterns_secondaires = [
        r"\bClasse[s]?\s*[:\-]?\s*(1|2|3|4\.1|4\.2|4\.3|5\.1|5\.2|6\.1|6\.2|7|8|9)\b",
        r"\bClass\s*[:\-]?\s*(1|2|3|4\.1|4\.2|4\.3|5\.1|5\.2|6\.1|6\.2|7|8|9)\b",
    ]
    for pat in patterns_secondaires:
        match = re.search(pat, zone, flags=re.IGNORECASE)
        if match:
            return match.group(1)

    # 4) Fallback : ancienne logique "balayage" autour de 'Classe' / 'Class'
    pattern_classe = r'\b(1|2|3|4\.1|4\.2|4\.3|5\.1|5\.2|6\.1|6\.2|7|8|9)\b'
    mots_cles = ["Classe", "Class"]

    for code in mots_cles:
        index = 0
        while True:
            index = zone.find(code, index)
            if index == -1:
                break

            extrait = zone[index:index + 60]  # petite fenêtre après le mot
            match = re.search(pattern_classe, extrait)
            if match:
                return match.group(1)

            index += len(code)

    return None

def extraire_FDS(texte):
    index_debut = texte.find("Nom du produit")
    index_fin = texte.find("Emploi de la substance", index_debut)
    if index_debut == -1 or index_fin == -1:
        return None
    texte_FDS = texte[index_debut+14:index_fin].strip()

    return texte_FDS

def extraire_paragraphe(texte, code_debut, code_fin):
    index_debut = texte.find(code_debut)
    index_fin = texte.find(code_fin, index_debut)
    
    if index_debut == -1 or index_fin == -1:
        return None

    return texte[index_debut + 12 :index_fin]

def extraire_info_transport(texte):
    zone = extraire_paragraphe(texte, "RUBRIQUE 14", "RUBRIQUE 15")
    if zone is None:
        return texte  # fallback : on cherche dans tout le texte
    return zone


def extraire_infos(texte):
    fds = extraire_FDS(texte)
    code_un = extraire_code_un(texte)
    texte_raccourci = raccourcir_texte(texte, code_un, 2000)
    ge = extraire_GE(texte)
    classe = extraire_classe(texte)
    lq = extraire_LQ(texte)
    ips = extraire_paragraphe(texte, "RUBRIQUE 4", "RUBRIQUE 5")
    mci = extraire_paragraphe(texte, "RUBRIQUE 5", "RUBRIQUE 6")
    ms = extraire_paragraphe(texte, "RUBRIQUE 7", "RUBRIQUE 8")

    return(fds,code_un,ge,classe,lq,ips,mci,ms)


