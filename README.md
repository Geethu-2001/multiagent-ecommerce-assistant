# Multi-Agent E-commerce Research Assistant

A runnable Python application using **LangGraph**, **Ollama**, **PostgreSQL**, **SQLAlchemy**, HTTPX, BeautifulSoup and Streamlit. It contains one supervisor and three reusable specialized components: a web scraper, a database connector, and a summarizer. The combined workflow runs web and database retrieval concurrently.

> The project is designed as a local demo/reference implementation. Review the security notes before exposing it to untrusted users or production data.

## Features

- Chat-style Streamlit UI, independent session IDs, answer styles, source/result expanders and optional workflow traces.
- Ollama is the default local model runtime; no paid API key is needed.
- PostgreSQL `ecommerce_db` schema with seven tables: `users`, `categories`, `products`, `orders`, `order_items`, `payments`, `shipments`.
- Repeatable fictional seed data: 32 users, 45 products, 60 orders, multiple items per order, payments, shipments and deliberately un-ordered products/customers.
- LangGraph parent graph and separately compiled web, database and summarizer subgraphs.
- Read-only SQL validation, PostgreSQL read-only transactions, statement timeout and row limit.
- URL validation, HTTP timeout/size limits, redirect checks and HTML content extraction.
- Tests for routing, SQL safety, URL validation and the summarizer's empty-input behavior.

## Prerequisites

- Python 3.11+
- Docker and Docker Compose
- [Ollama](https://ollama.com/download)
- A model with tool/structured generation support; the default example is `granite3.3:8b`. Check current Ollama availability and model capabilities for your machine before choosing a model.

## Setup

### 1. Start PostgreSQL

```bash
cp .env.example .env
docker compose up -d postgres
docker compose ps
```

Compose initializes `ecommerce_db` with owner/setup user `app_user` (`change_me`) and a restricted `agent_reader` role (`reader_change_me`). The application uses `DATABASE_URL` as `agent_reader`; only schema/seed scripts use `OWNER_DATABASE_URL`. Change both passwords in `docker-compose.yml`, `scripts/init-postgres.sql`, and `.env` before use beyond a local demo. The reader role receives SELECT privileges on tables created by the owner.

### 2. Create Python environment and install

```bash
python3.11 -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e '.[dev]'
```

### 3. Install and verify Ollama model

Install Ollama from its official download page and ensure its service is running. Then:

```bash
ollama pull granite3.3:8b
ollama list
curl http://localhost:11434/api/tags
```

If that model is too large or does not reliably draft valid SQL on your hardware, choose a currently supported Ollama model and update `OLLAMA_MODEL` in `.env`. Do not assume every text model supports tool calling. The app does not silently download models; it checks whether Ollama and the configured model are available in the sidebar.

### 4. Initialize schema and seed data

Run from the repository root with the virtual environment active:

```bash
python scripts/init_db.py
python scripts/seed_db.py
```

Seeding clears and recreates rows in the known demo tables, so it is repeatable but destructive to data in those tables. Use only on this demo database. Verify the connection:

```bash
python -c "from multiagent.agents.database import get_engine; c=get_engine().connect(); print(c.exec_driver_sql('SELECT COUNT(*) FROM products').scalar()); c.close()"
```

### 5. Launch Streamlit

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit. Configure `DATABASE_URL`, `OLLAMA_BASE_URL`, and `OLLAMA_MODEL` in `.env` if needed. The application does not silently switch database or model provider if one is unavailable.

## Example questions

**Database**

- `Show the five most expensive active products in our e-commerce database.`
- `Show products with stock below their reorder level.`
- `Which customers have never placed an order?`
- `Show orders for customer id 3.`
- `Find the top five products by quantity sold.`
- `Calculate revenue by product category.`
- `Show pending shipments.`
- `Show orders with failed or unpaid payments.`
- `Show the products included in order ORD-1001.`

**Web retrieval**

- `Fetch the product details from https://example.com/` (replace with a public HTML page you are allowed to access).

**Direct summarization**

- `Summarize this: [paste your text here]`

**Combined**

- `Compare this product with our database and sales history: https://example.com/product`

## Tests and checks

```bash
pytest -q
ruff check .
```

Tests use deterministic routing and security checks and do not require an LLM call. The end-to-end app does require a running PostgreSQL instance and Ollama model. A public website workflow also requires internet access to a permitted public page. Do not report an end-to-end scenario as verified unless you have run it locally.

## Project layout

```text
app.py
scripts/                    # PostgreSQL schema + deterministic seed
src/multiagent/
  config.py                  # environment settings
  llm.py                     # Ollama setup and health check
  state.py                   # shared LangGraph state contract
  supervisor.py              # initial routing
  graph.py                   # parent orchestration graph
  agents/web_scraper.py      # bounded HTTP + HTML extraction
  agents/web_agent.py        # web subgraph
  agents/database.py         # SQL validation, query generation/execution
  agents/db_agent.py         # database subgraph
  agents/summarizer.py       # shared summarization subgraph
  tools/web_security.py      # public URL validation
  tests/                     # pytest tests
  docs/                      # architecture and setup notes
```

## Limitations and production hardening

- The supervisor uses deterministic routing rather than an LLM classifier to reduce latency and avoid fragile routing. Add explicit routing tests when extending keywords/intents.
- Common database questions use deterministic SQL templates. Other questions use Ollama to draft SQL, followed by validation. Generated SQL may be rejected if unsupported or invalid; refine the question or add a tested template.
- Application SQL validation is defense in depth, not a security boundary. Create a separate database role with SELECT grants only on the approved tables and configure the agent connection with that role for production.
- The sample schema includes fictional addresses and synthetic payment/tracking references only. No real card data is stored.
- SSRF defenses check host resolution and each redirect, but DNS rebinding and hostile network paths need network-level egress controls in production.
- This version uses in-memory Streamlit session history and accepts a `thread_id`; durable LangGraph checkpointing is not configured. For persistence across restarts, add a supported PostgreSQL checkpointer and define retention/access controls.
- The optional OpenAI-compatible provider from the original generic prompt is not implemented here: Ollama is the required default and the only provider wired in this repository.

## Troubleshooting

- **Ollama unavailable:** start the Ollama service, run `ollama list`, check `OLLAMA_BASE_URL`, and verify `curl http://localhost:11434/api/tags`.
- **Model missing:** run `ollama pull "$OLLAMA_MODEL"` (substitute the actual value if shell expansion is not configured) and reload the UI.
- **PostgreSQL unavailable:** `docker compose up -d postgres`, inspect `docker compose logs postgres`, and confirm `DATABASE_URL` matches the compose credentials.
- **Schema missing:** run `python scripts/init_db.py`, then `python scripts/seed_db.py`.
- **SQL rejected:** the agent intentionally rejects non-SELECT, multiple statements and system catalog access. Rephrase the request or add a tested deterministic query template.
- **No page content:** the scraper only supports public HTML pages; it does not bypass logins, CAPTCHAs, paywalls or site access controls.
