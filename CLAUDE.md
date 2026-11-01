# CLAUDE.md — règles du dépôt (campagne Stage 2027)

## Contexte
Projet de portfolio de Francis Itoua, construit pour décrocher un stage Ingénieur IA appliquée & MLOps. Francis doit pouvoir expliquer chaque ligne en entretien : la clarté prime sur l'astuce.
Spécification : SPEC.md · Plan : ROADMAP.md · Journal : JOURNAL.md
### Contexte propre au projet (P2 — Routage automatique des tickets de support)
- Problème : sur un service desk (infogérance, TMA, DSI), les tickets mal catégorisés ou mal priorisés sont réaffectés plusieurs fois, les SLA sont ratés et du temps d'ingénieur est perdu.
- Données : jeu PUBLIC de tickets de support (Hugging Face ou Kaggle) avec catégorie ou file, et priorité ; on garde le français et l'anglais. Le jeu est choisi et justifié dans SPEC.md au ticket P2-01 ; les données ne sont jamais versionnées (`data/raw/`), seul le script qui les télécharge l'est, avec un découpage train / validation / test figé.
- Évaluation : F1 macro (catégorie, priorité) avec intervalles de confiance, coût pour 1 000 tickets, latence p95, part des tickets traités sans LLM ; tableau comparatif des 3 approches (TF-IDF + régression logistique, embeddings + classifieur, LLM few-shot) et du routage hybride, sur le même jeu de test. Aucune décision ne se prend sur le jeu de test : seuils et réglages sont choisis sur la validation.
- Hors périmètre : Kubernetes, ArgoCD, authentification, intégration à un vrai outil de ticketing (ServiceNow, Jira).
- Definition of Done : celle de 06_PROJETS.md (README étude de cas, tests et CI verts avec évaluation en CI, API déployée via Terraform + front Vercel, docs/evaluation.md, une fiche par ticket, entrée « LIVRÉ » avec 3 chiffres et l'URL de démo).

## Stack imposée
Python 3.12, uv, FastAPI, Pydantic v2, pytest, ruff, mypy · React + Vite + TypeScript (Vercel) · Docker · GitHub Actions · Terraform → Azure Container Apps (France Centre ; Terraform Cloud Run europe-west9 prêt, faute de compte de facturation Google) · LLM Groq (offre gratuite) derrière l'interface LLMProvider, comme en P1 · Langfuse · secrets dans GitHub Secrets / .env non versionné.

## Workflow de chaque session
1. Lis SPEC.md, ROADMAP.md et les 3 dernières entrées de JOURNAL.md.
2. Prends le premier ticket « [ ] » de ROADMAP.md. Un ticket par session ; deux si le premier a pris moins de 30 minutes.
3. Implémente avec ses tests. Lance pytest, ruff et mypy --strict sur src/ jusqu'au vert.
4. Coche le ticket « [x] » avec la date.
5. Écris docs/explications/<ticket>.md : ce qui a été fait, pourquoi ce choix plutôt que l'alternative la plus courante, schéma si utile, 5 questions d'entretien avec leurs réponses.
6. Ajoute une entrée en haut de JOURNAL.md (format ci-dessous).
7. Commit au format Conventional Commits, push sur main, vérifie que la CI passe.
8. Termine par : résumé en 5 lignes, « Prochaine session : <ticket suivant> », et les 2 questions de la fiche que Francis doit savoir répondre à voix haute.

## Format JOURNAL.md — lu automatiquement par l'agent LinkedIn : n'invente jamais rien
## AAAA-MM-JJ — <ticket>
- Fait : …
- Chiffre mesuré : … (ou « aucun »)
- Décision technique : … (le compromis en une phrase)
- Visuel disponible : <chemin d'une capture ou d'un GIF dans docs/media/> (ou « aucun »)
Jour de livraison : entrée « ## AAAA-MM-JJ — LIVRÉ » avec les 3 chiffres clés et l'URL de démo.

## Interdits
Secret dans le dépôt · chiffre non mesuré dans README ou JOURNAL · dépendance non justifiée · test désactivé pour faire passer la CI.
