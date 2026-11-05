# OrientClin

Prototype académique explorant un parcours d’orientation clinique assistée par IA, avec interface React et services Python. Le dépôt contient des écrans de saisie, de questions, de revue et de rapport ainsi que des composants d’orchestration et une API.

> **Projet expérimental, non validé pour un usage médical.** Ne pas utiliser pour poser un diagnostic, prendre une décision de soins ou traiter des données réelles de patients.

## Contenu

- `App.js` et les fichiers `*Screen.js` : interface React et étapes du parcours.
- `api.py`, `graph.py` et `state.py` : API et composants du flux.
- `server.py` : service expérimental de suggestions par mots-clés.
- `icd10_hints.json` et `care_pathways.json` : exemples de données locales.
- `requirements.txt` et `package.json` : dépendances Python et JavaScript.

## Technologies

Python · FastAPI · LangGraph · React · JavaScript

## État du projet

Le dépôt est un prototype à compléter avant toute démonstration reproductible. En particulier, `server.py` cherche ses données dans un dossier `data/`, tandis que les fichiers JSON sont actuellement à la racine. L’organisation de l’interface et la configuration des services doivent aussi être vérifiées avant lancement. Les instructions d’installation et les résultats restent à valider dans un environnement neuf.

## Pistes d’amélioration

Documenter les prérequis et les variables de configuration, ajouter des tests et des exemples fictifs, puis vérifier la confidentialité et la sécurité. Toute évaluation clinique nécessiterait un protocole et une validation indépendants.
