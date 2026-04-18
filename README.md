# PrevaExtract

### *Solution Python de génération automatisée de tableaux Excel à partir de documents PDF hétérogènes*

## 🏦**Contexte du projet**

Prevarisk est une entreprise indépendante spécialisée dans l’audit, le conseil et la formation en matière de prévention des risques professionnels.

L’entreprise doit gérer un grand volume de fiches produits dangereux, fournies par différents clients et sous des formats PDF variés et non standardisés.

Problématique : 

Retrouver et exploiter rapidement des informations clés (ex. code UN, dénomination du produit, classe de danger, etc.) dans ces documents est difficile et chronophage.

## 🎯 **Objectif du projet**

Concevoir une application Python capable de :

- Lire automatiquement un ensemble de fichiers PDF,
- Extraire les informations clés définies par Prevarisk,
- Générer un fichier Excel structuré, avec une ligne par produit et des colonnes correspondant aux champs d’intérêt (ex. code UN, danger principal, fabricant, etc.),
- Offrir une interface graphique intuitive (PyQt6) pour simplifier l’utilisation par des non-techniciens.

L’objectif final est que l’outil soit utilisé au quotidien par Prevarisk pour automatiser une partie du traitement documentaire.

## ⚙️ **Technologies et outils**

- **Langage :** Python
- **Interface utilisateur :** PyQt6 (widgets, signaux/slots, layouts)
- **Extraction PDF :** PyPDF2 & pdfplumber
- **Analyse du texte :** Expressions régulières (`re` )
- **Packaging :** PyInstaller (création d’un exécutable autonome)
- **Outils de planification à venir :** Kanban / méthode Agile légère (Notion board)

## 🧠 **Défis techniques rencontrés**

L’un des principaux défis du projet réside dans :

- La structure incohérente des fichiers PDF, entraînant un désordre dans le texte extrait :
    
    certaines données côte à côte visuellement finissent très éloignées lors de la lecture par PyPDF2.
    
- La nécessité de concevoir des règles robustes d’extraction (regex) pour identifier correctement les champs malgré ces incohérences.

Ce problème structurel a conduit à repenser l’architecture du code et à envisager des traitements plus fins (par zone, ou via pdfplumber).

## 🧩 **Organisation et gestion de projet**

- **Autonomie complète :** conception, développement et tests menés seul.
- Communication directe avec la dirigeante de Prevarisk pour valider les fonctionnalités et les besoins.
- **Approche agile à mettre en place :**
    - Découpage du projet en itérations (sprints courts de 1 à 2 semaines).
    - Tableau de suivi sur Notion.
    - Points hebdomadaires d’avancement.
- **Documentation prévue :**
    - **Technique :** architecture du code, dépendances, guide d’installation.
    - **Utilisateur :** guide d’usage de l’interface graphique.

## 🧪 **État d’avancement**

- ✅ Prototype fonctionnel sans interface (lecture PDF → extraction → export Excel) validé par Prevarisk.
- 🔄 Refonte en cours avec interface PyQt6 pour une utilisation quotidienne.
- 🧩 Étape actuelle : conception de l’UI et intégration avec la logique d’extraction existante.

## 💡 **Compétences développées**

**Techniques :**

- Extraction et traitement automatisé de texte (PDF, regex)
- Développement d’interface graphique (PyQt6)
- Packaging et déploiement d’applications Python
- Architecture logicielle et gestion des exceptions

**Gestion de projet :**

- Recueil et formalisation du besoin client
- Suivi d’avancement et communication avec le commanditaire
- Mise en place d’une démarche Agile adaptée à un projet individuel

## 🚀 **Prochaines étapes**

1. Finaliser l’interface graphique (PyQt6)
2. Intégrer les modules d’extraction et de génération Excel
3. Mettre en place un mini Kanban sur Notion pour le suivi Agile
4. Rédiger la documentation technique et utilisateur
5. Livraison du prototype complet à Prevarisk