# Configuration

All settings are read from environment variables or `.env` via Pydantic Settings.

| Variable | Purpose | Default |
|---|---|---|
| `LLM_PROVIDER` | LLM runtime (currently Ollama only) | `ollama` |
| `OLLAMA_BASE_URL` | Ollama local API | `http://localhost:11434` |
| `OLLAMA_MODEL` | Pulled model name | `granite3.3:8b` |
| `DATABASE_URL` | Read-only SQLAlchemy PostgreSQL URL for agent queries | local `ecommerce_db` / `agent_reader` |
| `OWNER_DATABASE_URL` | Schema and seed script connection | local `ecommerce_db` / `app_user` |
| `APP_MAX_WEB_BYTES` | Max HTTP response bytes | `1500000` |
| `APP_MAX_WEB_CHARS` | Max extracted text characters | `18000` |
| `APP_HTTP_TIMEOUT` | HTTP request timeout, seconds | `12` |
| `APP_SQL_TIMEOUT_MS` | PostgreSQL statement timeout | `5000` |
| `APP_SQL_MAX_ROWS` | Maximum fetched rows | `100` |

The default database URL format is `postgresql+psycopg://USER:PASSWORD@HOST:5432/ecommerce_db`.
