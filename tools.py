import re

from langchain.tools import tool
from sqlalchemy import inspect, text

from database import engine


@tool
def list_tables() -> list[str]:
    """Return available tables."""

    inspector = inspect(engine)
    return inspector.get_table_names()


@tool
def get_schema(table_name: str) -> str:
    """Return schema for a table."""

    inspector = inspect(engine)

    cols = inspector.get_columns(table_name)

    return "\n".join(
        f"{c['name']} : {c['type']}"
        for c in cols
    )


def _strip_sql_fences(query: str) -> str:
    match = re.search(r"```(?:sql)?\s*(.*?)```", query, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else query.strip()


@tool
def run_sql(query: str) -> list[dict]:
    """Execute a SELECT statement."""

    query = _strip_sql_fences(query)

    if not query.upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries allowed")

    with engine.connect() as conn:

        rows = conn.execute(text(query))

        return [
            dict(row._mapping)
            for row in rows.fetchmany(100)
        ]