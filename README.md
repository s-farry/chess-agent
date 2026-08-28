# Chess Club SQL Assistant

A natural-language chat interface for a chess club's database. Ask a question
in plain English ("how many teams are there?", "who won the most games last
season?") and it writes, validates, runs, and explains the SQL for you.

Built with [LangGraph](https://github.com/langchain-ai/langgraph) and a
[Streamlit](https://streamlit.io) chat UI. Works against a local SQLite
database (default target: a Django-based chess club app) and supports Claude,
OpenAI, or a fully local Ollama model as the LLM backend.

## How it works

The agent is a small LangGraph state machine (`graph.py`):

```
schema → generate_sql → validate_sql → execute_sql → generate_insights
                                              │
                                              └─(on invalid SQL)─▶ generate_sql
```

1. **schema** — inspects the database and builds a text description of every table.
2. **generate_sql** — asks the LLM to turn the question into a SQL query.
3. **validate_sql** — asks the LLM to review the query against the schema (correct tables/columns, `SELECT`-only, etc.).
4. **execute_sql** — runs the query. Only `SELECT` statements are allowed; anything else is rejected.
5. If execution fails, the error is fed back into **generate_sql** and it retries (up to 3 attempts) before giving up gracefully.
6. **generate_insights** — turns the question, SQL, and results into a plain-English answer.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```bash
# Which LLM backend to use: ollama | anthropic | openai
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen3-coder:30b        # only needed for LLM_PROVIDER=ollama

# Only needed for the provider you're actually using
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

By default the app points at `~/Sites/chessclub/db.sqlite3` (see
`database.py`) — update that path for your own database.

If using Ollama, make sure the [Ollama](https://ollama.com) service is
running and the model is pulled first: `ollama pull qwen3-coder:30b`.

## Running it

```bash
streamlit run app.py
```

Opens a chat UI at `http://localhost:8501`. Each answer includes an
expandable panel showing the SQL that was run, plus a results table.

## Project layout

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit chat UI |
| `graph.py` | LangGraph state machine wiring the nodes together |
| `nodes.py` | The individual graph steps (schema, generate SQL, validate, execute, insights) |
| `state.py` | Shared state shape passed between graph nodes |
| `tools.py` | DB tools the graph uses: list tables, get schema, run SQL (SELECT-only) |
| `llm.py` | Picks the LLM backend based on `LLM_PROVIDER` |
| `database.py` | SQLAlchemy engine pointing at the SQLite database |
| `prompts.py` | Draft system prompt text (not currently wired into the graph) |

## License

MIT — see [LICENSE](LICENSE).
