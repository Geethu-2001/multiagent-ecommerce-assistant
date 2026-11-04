# Setup checklist

1. Install Python 3.11+, Docker Compose and Ollama.
2. Copy `.env.example` to `.env` and review credentials.
3. Start database: `docker compose up -d postgres`.
4. Install app: `python -m pip install -e '.[dev]'`.
5. Pull model explicitly: `ollama pull granite3.3:8b`; check with `ollama list`.
6. Initialize schema: `python scripts/init_db.py`.
7. Seed fictional data: `python scripts/seed_db.py`.
8. Run `pytest -q`.
9. Launch: `streamlit run app.py`.

Resetting demo data is destructive: run `python scripts/seed_db.py` to truncate and reseed the named demo tables. Never point this script at a real database.
