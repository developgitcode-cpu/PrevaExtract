from PyPDF2 import PdfReader
import os
import sys

def extraire_texte(chemin):
        try : 
              contenue = PdfReader(chemin)
        except Exception as e:
               return "",0,False,f"Erreur lors de la lecture de {os.path.basename(chemin)} : {e}" 
           
        if contenue.is_encrypted:
                return "",0,True,None
        
        nb_pages = len(contenue.pages)
        texte_pages = []  
        for i in range(nb_pages):
            texte_page = contenue.pages[i].extract_text()
            if texte_page == None :
                texte_page = ""
            texte_pages.append(texte_page)
    
        texte = "\n\n".join(texte_pages)
        return (texte, nb_pages, False,None)
        
def nettoyer_texte(texte):
    derniere_etait_vide = False
    lignes_resultat = []

    texte = texte.replace("\r\n", "\n").replace("\r", "\n")
    lignes = texte.splitlines()

    for ligne in lignes :
        ligne = ligne.strip()
        ligne = " ".join(ligne.split())
        if ligne != "":
           lignes_resultat.append(ligne)
           derniere_etait_vide = False
        else : 
            if not derniere_etait_vide:
                 lignes_resultat.append("")
                 derniere_etait_vide = True  
    texte_nettoye = "\n".join(lignes_resultat)           
    return(texte_nettoye)

