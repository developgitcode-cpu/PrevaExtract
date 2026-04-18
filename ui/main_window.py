import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QFileDialog, QListWidget, QTabWidget, QTableWidget, QTableWidgetItem)
from PyQt6.QtGui import ( QShortcut, QKeySequence, QIcon )
from PyQt6.QtCore import Qt

from core.pdf_manager import extraire_texte, nettoyer_texte
from core.fds_extract import extraire_infos
from services.excel_writer import exporter_vers_excel

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 1) Configuration générale de la fenêtre
        self.setWindowTitle("PrevaExtract")
        self.resize(600, 400)
        self.setWindowIcon(QIcon("assets/icon/prevaextract.ico"))

        # --- Données en mémoire ---
        self.resultats_fds = []  # une entrée par PDF
        self.textes_pdfs = {}    # dictionnaire {chemin: texte_nettoye}
        self.logs = []           # liste de messages pour l’onglet Journal
        self.chemins_ouvert = []  # liste des chemins dans l'ordre de la QListWidget

        # --- Layout global ---
        layout_global = QVBoxLayout(self)
        self.setLayout(layout_global)

    
        barre_boutons = QHBoxLayout()

        # 2) Création des widgets
        self.bouton_ouvrir = QPushButton("Ouvrir un fichier (Ctrl+O)")
        #self.bouton_extraire = QPushButton("Lancer l'extraction")
        self.bouton_export = QPushButton("Exporter vers Excel (Ctrl+E)")
        self.bouton_export.setEnabled(False)
        self.texte = QTextEdit()

        barre_boutons.addWidget(self.bouton_ouvrir)
        #barre_boutons.addWidget(self.bouton_extraire)
        barre_boutons.addWidget(self.bouton_export)
        barre_boutons.addStretch()  # pousse les boutons à gauche

        layout_global.addLayout(barre_boutons)

        # 3) Raccourci clavier
        self.raccourci_ouvrir = QShortcut(QKeySequence("Ctrl+O"), self)
        self.raccourci_exporter = QShortcut(QKeySequence("Ctrl+E"), self)

        zone_centrale = QHBoxLayout()
        layout_global.addLayout(zone_centrale, stretch=1)

        self.liste_fichiers = QListWidget()
        zone_centrale.addWidget(self.liste_fichiers, stretch=1)

        self.onglets = QTabWidget()

        self.texte = QTextEdit()
        self.texte.setReadOnly(False)  # tu peux mettre True si tu veux
        self.onglets.addTab(self.texte, "Texte")
        
        self.table_infos = QTableWidget()
        self.table_infos.setColumnCount(8)
        self.table_infos.setHorizontalHeaderLabels([
            "Fichier", "Code UN", "Classe", "GE",
            "LQ", "Pages", "Protégé", "Erreur"
        ])
        self.onglets.addTab(self.table_infos, "Infos extraites")

        self.journal = QTextEdit()
        self.journal.setReadOnly(True)
        self.onglets.addTab(self.journal, "Journal")

        zone_centrale.addWidget(self.onglets, stretch=3)
    
        # 5) Connections
        self.bouton_ouvrir.clicked.connect(self.ouverture_fichier)
        self.raccourci_ouvrir.activated.connect(self.ouverture_fichier)
        self.bouton_export.clicked.connect(self.exporter_excel)
        self.raccourci_exporter.activated.connect(self.exporter_excel) #S'occuper de bloquer le raccourci si bouton Enabled (isEnabed fonctionne bizarrement)
        #self.bouton_extraire.clicked.connect(self.exporter_excel) #Pour la V2
        self.liste_fichiers.currentRowChanged.connect(self.afficher_details_pdf)

        # 6) Information des pdfs
        self.resultats_fds = []
        self.textes_pdfs = {}
        self.logs = []

    def ouverture_fichier(self):
            # 1) Ouvrir la boîte de dialogue
        chemins, _ = QFileDialog.getOpenFileNames(self,"Ouvrir un ou plusieurs fichiers PDF","","Fichiers PDF (*.pdf)")

            # 2) Si aucun fichier sélectionné
        if not chemins:
            self.texte.setPlainText("Aucun fichier sélectionné.")
            return

            # 3) S'l y a 1 ou des chemins
        self.resultats_fds = []
        self.textes_pdfs = {}
        self.chemins_ouvert = []
        self.liste_fichiers.clear()
        self.table_infos.setRowCount(0)
        self.logs = []
        self.journal.clear()
        self.ajouter_log(f"Ouverture de {len(chemins)} fichier(s) PDF.")


        nb_fichiers = len(chemins)
        nb_total_pages = 0
        nb_fichiers_proteges = 0
        nb_fichiers_erreur = 0
        texte_final = ""
        noms = []
        for chemin in chemins:
            nom = os.path.basename(chemin)
            noms.append(nom)
            self.ajouter_log(f"Traitement de : {nom}")
            self.chemins_ouvert.append(chemin)
            self.liste_fichiers.addItem(nom)

            texte_pdf, nb_pages, est_protege, erreur = extraire_texte(chemin)
            texte_nettoye = nettoyer_texte(texte_pdf)
            self.textes_pdfs[chemin] = texte_nettoye

            if est_protege:
                nb_fichiers_proteges += 1
                bloc_resume = f"==== Fichier : {nom} ====\nPDF protégé par mot de passe.\n"
                self.ajouter_log(f"PDF protégé (mot de passe) ignoré : {nom}")            
            if erreur!=None:
                nb_fichiers_erreur += 1
                bloc_resume = f"==== Fichier : {nom} ====\nErreur : {erreur}\n"
                self.ajouter_log(f"Erreur lors de la lecture de {nom} : {erreur} ")            
            else :
                nb_total_pages += nb_pages
                fds, code_un, ge, classe, lq, ips, mci, ms = extraire_infos(texte_nettoye)

                self.resultats_fds.append({"fichier": nom,"fds": fds,"code_un": code_un,"ge": ge,"classe": classe,"lq": lq,
                                       "ips": ips,"mci": mci,"ms": ms,"nb_pages": nb_pages,"est_protege": est_protege,"erreur": erreur,})

                bloc_resume = (f"==== Fichier : {nom} ====\n"
                               f"Code UN : {code_un or 'Non trouvé'}\n"
                               f"Groupe Emballage : {ge or 'Non trouvé'}\n"
                               f"Classe : {classe or 'Non trouvée'}\n"
                               f"LQ : {lq or 'Non trouvée'}\n\n")
                
                self.ajouter_log(f"OK : {nom} | UN={code_un or '-'} | Classe={classe or '-'} | GE={ge or '-'} | LQ={lq or '-'}")
            texte_final += bloc_resume + "\n" + ("_" * 30) + "\n\n"

        synthese = (
        "\n--- Synthèse ---\n"
        f"{nb_fichiers} fichiers ouverts\n"
        f"{nb_total_pages} pages extraites\n"
        f"{nb_fichiers_proteges} fichiers protégés ignorés\n"
        f"{nb_fichiers_erreur} fichiers en erreur\n"
        )

        self.ajouter_log(f"Terminé : {nb_fichiers} fichiers, {nb_total_pages} pages, "
                         f"{nb_fichiers_proteges} protégés, {nb_fichiers_erreur} avec une erreur")

        texte_final += synthese
        self.texte.setPlainText(texte_final)

        self.remplir_table_infos()
        self.bouton_export.setEnabled(bool(self.resultats_fds))

        """if self.liste_fichiers.count()>0:
            self.liste_fichiers.setCurrentRow(0)"""
    
    def exporter_excel(self):
        # 1) Vérifier qu'on a des résultats à exporter
        if not hasattr(self, "resultats_fds") or not self.resultats_fds:
            self.texte.setPlainText(
            "Aucun résultat à exporter.\n"
            "Lance d'abord une extraction sur un ou plusieurs PDF."
            )
        # 2) Demander à l'utilisateur où enregistrer le fichier
        chemin_fichier, _ = QFileDialog.getSaveFileName(self,"Enregistrer le fichier Excel",
                                                        "resultats_extraction.xlsx","Fichiers Excel (*.xlsx)")

        # Si l'utilisateur annule
        if not chemin_fichier:
            return
        
        # 3) Tenter l'export
        try:
            exporter_vers_excel(self.resultats_fds, chemin_fichier)
            self.texte.setPlainText(f"Export terminé.\nFichier enregistré ici :\n{chemin_fichier}")
        except Exception as e:
            self.texte.setPlainText(f"Erreur lors de l'export Excel :\n{e}")

        return
    
    def remplir_table_infos(self):
        lignes = len(self.resultats_fds)
        self.table_infos.setRowCount(lignes)

        for row, res in enumerate(self.resultats_fds):
            chemin = res.get("fichier", "")
            nom = os.path.basename(chemin)

            code_un = res.get("code_un", "")
            classe = res.get("classe", "")
            ge = res.get("ge", "")
            lq = res.get("lq", "")
            nb_pages = res.get("nb_pages", "")
            est_protege = res.get("est_protege", False)
            erreur = res.get("erreur", "")

            valeurs = [nom, code_un or "", classe or "", ge or "", lq or "",
                       str(nb_pages), "Oui" if est_protege else "Non", str(erreur) if erreur else ""]

            for col, valeur in enumerate(valeurs):
                item = QTableWidgetItem(valeur)
                self.table_infos.setItem(row, col, item)

        self.table_infos.resizeColumnsToContents()
        if erreur :
            couleur = Qt.GlobalColor.red
        elif est_protege :
            couleur = Qt.GlobalColor.darkYellow
        else :
            couleur = None
        
        if couleur :
            for col in range(self.table_infos.columnCount()):
                item = self.table_infos.item(row, col)
                if item :
                    item.setForeground(couleur)
    
    def afficher_details_pdf(self, row):
        if row < 0 or row >= len(self.chemins_ouvert):
            return

        chemin = self.chemins_ouvert[row]
        if not chemin:
            return
        texte = self.textes_pdfs.get(chemin, "")

        # On bascule sur l'onglet "Texte" et on affiche
        index_onglet_texte = self.onglets.indexOf(self.texte)
        if index_onglet_texte != -1:
            self.onglets.setCurrentIndex(index_onglet_texte)

        self.texte.setPlainText(texte)
    
    def ajouter_log(self, message: str):
        """Ajoute un message au journal et met à jour l'onglet Journal."""
        self.logs.append(message)
        self.journal.setPlainText("\n".join(self.logs))




