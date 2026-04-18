import pandas as pd

def exporter_vers_excel(resultats, chemin_fichier):
    if not resultats:
        return
    
    df = pd.DataFrame(resultats)
    colonnes = {"fichier": "Fichier","fds": "FDS","code_un": "Code UN","ge": "Groupe Emballage","classe": "Classe","lq": "Limite Quantité","ips": "Info premier secours",
                "mci": "Mesures contre incendie","ms": "Manutention et Stockage","nb_pages": "Nombre de pages","est_protege": "PDF protégé","erreur": "Erreur"}
    
    colonnes_existantes = {cle: val for cle, val in colonnes.items() if cle in df.columns}
    df = df.rename(columns=colonnes_existantes)
    df.to_excel(chemin_fichier, index=False)

    return chemin_fichier