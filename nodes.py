from langchain_core.messages import HumanMessage

from llm import get_llm
from tools import (
    list_tables,
    get_schema,
    run_sql,
)

llm = get_llm()


def sql_node(state):

    retry_context = ""
    if state.get("error"):
        retry_context = f"""

Your previous SQL was rejected:

{state['sql']}

Error:

{state['error']}

Fix the SQL to address this error.
"""

    prompt = f"""
Schema:

{state['schema']}

Question:

{state['question']}
{retry_context}
Return ONLY SQL.
"""

    sql = llm.invoke(prompt).content

    return {
        "sql": sql
    }

def execute_node(state):

    try:
        rows = run_sql.invoke({
            "query": state["sql"]
        })
    except Exception as exc:
        return {
            "error": str(exc),
            "retries": state.get("retries", 0) + 1,
        }

    return {
        "results": rows,
        "error": None,
    }

def insight_node(state):

    if state.get("error"):
        return {
            "answer": (
                f"I couldn't produce a valid SQL query after "
                f"{state.get('retries', 0)} attempt(s).\n\n"
                f"Last error: {state['error']}\n\n"
                f"Last SQL attempted:\n{state['sql']}"
            )
        }

    prompt = f"""
Question:

{state['question']}

SQL:

{state['sql']}

Results:

{state['results']}

Explain the findings.
"""

    answer = llm.invoke(prompt).content

    return {
        "answer": answer
    }

def schema_node(state):

    tables = list_tables.invoke({})

    schema_text = "\n\n".join(
        f"Table: {table}\n{get_schema.invoke({'table_name': table})}"
        for table in tables
    )

    return {
        "schema": schema_text
    }


def validate_node(state):

    prompt = f"""
You are an expert SQL reviewer.

Schema:
{state["schema"]}

Review the SQL below.

Rules:
- Check that all tables exist.
- Check that all columns exist.
- Check GROUP BY clauses.
- Check JOIN conditions.
- Check aggregate functions.
- Ensure only SELECT statements are used.
- If the SQL is correct, return it unchanged.
- Return ONLY the SQL.

SQL:
{state["sql"]}
"""

    sql = llm.invoke([HumanMessage(content=prompt)]).content

    return {
        "sql": sql
    }
