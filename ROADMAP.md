# ROADMAP — Routage automatique des tickets de support

Chaque ticket tient en 90 minutes au plus. Version démontrable à mi-parcours : P2-07 (API + interface de file de tickets sur la meilleure approche légère).

## Données et protocole
- [x] P2-01 Choix et préparation du jeu de données — jeu public FR + EN choisi et justifié dans SPEC.md, script de téléchargement à révision fixée, découpage train / validation / test stratifié et versionné, statistiques des classes publiées (fait le 2026-11-01)
- [x] P2-02 Protocole d'évaluation commun — module de métriques (F1 macro catégorie et priorité avec IC bootstrap, matrice de confusion, latence p50/p95, coût pour 1 000 tickets) testé, script qui note n'importe quelle approche sur le même jeu (fait le 2026-11-01)

## Les trois approches
- [x] P2-03 Base TF-IDF + régression logistique — entraînement reproductible, F1 macro mesurés sur la validation et le test, résultats dans eval/results/ (fait le 2026-11-01)
- [x] P2-04 Embeddings multilingues + classifieur — même protocole, comparaison chiffrée avec TF-IDF, choix du modèle léger justifié (fait le 2026-11-01)
- [ ] P2-05 LLM few-shot derrière l'interface LLMProvider — prompt few-shot (exemples tirés de l'entraînement), sortie structurée validée par Pydantic, mesure sur l'échantillon de test fixé, coût pour 1 000 tickets

## Version démontrable
- [ ] P2-06 API de classification — POST /classify (catégorie, priorité, confiance, approche utilisée), modèle chargé au démarrage, tests
- [ ] P2-07 Interface de file de tickets — React + Vite + TypeScript : file des tickets, proposition affichée, accepter / corriger, corrections stockées côté API, tests du front

## Routage hybride et suggestion de réponse
- [ ] P2-08 Routage hybride — modèle léger d'abord, LLM sous un seuil de confiance choisi sur la validation ; courbe qualité / part sans LLM ; mesure sur le test (F1, coût, part sans LLM, latence p95)
- [ ] P2-09 Suggestion de réponse par RAG — tickets résolus similaires de l'entraînement, réponse proposée dans l'API et l'interface, évaluation simple documentée
- [ ] P2-10 Traces Langfuse et protection de la démo — traces des appels au LLM (tokens, latence), limite par IP et quota quotidien, trace réelle vérifiée

## Évaluation continue
- [ ] P2-11 Évaluation en CI — sous-ensemble bloquant sous des seuils fixés à l'avance, évaluation complète sur tag de version

## Livraison
- [ ] P2-12 Déploiement — Terraform + Azure Container Apps (Terraform Cloud Run prêt) + Vercel, URL publique fonctionnelle
- [ ] P2-13 Rapport docs/evaluation.md — protocole, jeu de test, tableau des 3 approches et du routage hybride, analyse des erreurs, limites
- [ ] P2-14 README étude de cas + GIF de démo
