# JOURNAL

## 2026-11-01 — P2-04 Embeddings multilingues + classifieur
- Fait : approche embeddings multilingues gelés (fastembed) + régression logistique, file et priorité ; trois modèles légers examinés (mpnet écarté pour sa lenteur, MiniLM et potion réglés) ; cache des vecteurs ; réglage sur la validation, grille étendue quand l'optimum tombait au bord ; mesure unique sur le test.
- Chiffre mesuré : test MiniLM (C = 256) : F1 macro file 0,344 (IC 0,322–0,363) et priorité 0,419 (IC 0,403–0,432), contre 0,588 et 0,615 pour TF-IDF ; latence p95 31 ms contre 2,5 ms ; 18,5 % des tickets de test dépassent les 128 jetons lus par MiniLM
- Décision technique : TF-IDF reste le modèle léger du routage hybride : meilleur sur toutes les files, environ 12 fois plus rapide au p95 et sans modèle de 220 Mo dans l'image ; les embeddings gelés ne sont pas retenus pour la classification.
- Visuel disponible : aucun

## 2026-11-01 — P2-03 Base TF-IDF + régression logistique
- Fait : base TF-IDF + régression logistique (un modèle pour la file, un pour la priorité, probabilité de la file comme confiance) ; réglage de C et de la pondération des classes sur la validation seulement (scripts/tune_tfidf.py) ; mesure unique sur le test.
- Chiffre mesuré : test : F1 macro file 0,588 (IC 0,565–0,606) et priorité 0,615 (IC 0,600–0,629), contre 0,045 et 0,195 pour la référence « majorité » ; latence p95 2,5 ms par ticket sur CPU, coût LLM nul
- Décision technique : réglage choisi sur la validation (C = 64, classes pondérées) et test lu une seule fois : le score publié reste légèrement sous celui de la validation (0,588 contre 0,609), mais il n'est pas optimiste.
- Visuel disponible : aucun

## 2026-11-01 — P2-02 Protocole d'évaluation commun
- Fait : module evaluation.py commun à toutes les approches (F1 macro file et priorité avec IC bootstrap, exactitude, F1 par file, matrices de confusion, latence p50/p95, coût pour 1 000 tickets, part sans LLM) ; interface Classifier / Prediction ; script scripts/evaluate.py ; référence triviale « majorité » ; 8 tests sur des valeurs calculées à la main.
- Chiffre mesuré : référence « majorité » sur la validation : exactitude file 29,3 % mais F1 macro file 0,045 (IC 0,044–0,047), F1 macro priorité 0,194 (IC 0,189–0,199) ; test : 0,045 et 0,195
- Décision technique : métriques écrites à la main et testées plutôt que sklearn.metrics : quelques lignes explicables, aucune dépendance ajoutée, et toutes les approches notées par le même code.
- Visuel disponible : aucun

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
