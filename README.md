# Routage automatique des tickets de support

Classer chaque ticket de support (catégorie et priorité) avec un modèle léger, et n'appeler un LLM que lorsque la confiance est insuffisante. Objectif mesuré : la qualité du routage, son coût pour 1 000 tickets et la part de tickets traités sans LLM.

**État : en construction** (démarré le 01/11/2026). Aucun résultat n'est publié avant d'être mesuré.

- Spécification : [SPEC.md](SPEC.md)
- Plan : [ROADMAP.md](ROADMAP.md)
- Journal de bord : [JOURNAL.md](JOURNAL.md)

## Lancer en local
```bash
uv sync
uv run pytest
uv run uvicorn support_ticket_routing.api:app
```
