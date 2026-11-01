# JOURNAL

## 2026-11-01 — P2-01 Choix et préparation du jeu de données
- Fait : jeu Tobi-Bueck/customer-support-tickets retenu et justifié dans SPEC.md (10 files, 3 priorités, réponses d'agent, anglais et allemand) ; téléchargement à révision fixée vérifié par SHA-256 ; dédoublonnage ; découpage stratifié par langue et file versionné dans data/splits/ ; statistiques dans docs/donnees.md.
- Chiffre mesuré : 28 587 tickets lus, 15 doublons retirés, découpage 19 998 / 4 287 / 4 287 ; files de 29,3 % (Technical Support) à 1,4 % (General Inquiry) ; anglais 57,1 %, allemand 42,9 %
- Décision technique : garder deux langues réelles (anglais, allemand) plutôt qu'un test français traduit automatiquement : le jeu ne contient pas de français, et une traduction aurait mesuré le traducteur autant que le modèle.
- Visuel disponible : aucun

## 2026-11-01 — Démarrage P2
- Fait : dépôt créé ; CLAUDE.md, SPEC.md (problème, utilisateurs, périmètre, architecture, critères de choix du jeu de données, protocole d'évaluation, Definition of Done) et ROADMAP.md (14 tickets) ; squelette Python 3.12 / uv / FastAPI avec ruff, mypy strict, pytest, Dockerfile et CI GitHub Actions.
- Chiffre mesuré : aucun
- Décision technique : reprendre la stack éprouvée en P1 (Groq derrière LLMProvider, Azure Container Apps avec Terraform Cloud Run prêt) plutôt que la cible initiale (Mistral, Cloud Run), indisponible sans abonnement ni compte de facturation.
- Visuel disponible : aucun
