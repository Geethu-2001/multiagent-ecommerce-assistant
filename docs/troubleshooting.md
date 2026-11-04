# Troubleshooting

- `Cannot reach Ollama`: start Ollama and verify `OLLAMA_BASE_URL` with `/api/tags`.
- `Model is not present`: pull the exact configured model name explicitly.
- PostgreSQL connection refused: check `docker compose ps`, `docker compose logs postgres`, and `DATABASE_URL`.
- `relation does not exist`: run `python scripts/init_db.py` then `python scripts/seed_db.py`.
- SQL generation errors: use a supported example query, inspect the safe returned error, or add a tested deterministic query template.
- Website blocked: only public HTTP(S) HTML is supported; local URLs and restricted pages are intentionally blocked.
