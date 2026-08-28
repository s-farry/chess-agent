from langgraph.graph import StateGraph, START, END

from state import AgentState
from nodes import (
    schema_node,
    sql_node,
    validate_node,
    execute_node,
    insight_node,
)

builder = StateGraph(AgentState)

builder.add_node("schema", schema_node)
builder.add_node("generate_sql", sql_node)
builder.add_node("validate_sql", validate_node)
builder.add_node("execute_sql", execute_node)
builder.add_node("generate_insights", insight_node)

MAX_RETRIES = 3


def route_after_execute(state):
    if state.get("error") and state.get("retries", 0) < MAX_RETRIES:
        return "generate_sql"
    return "generate_insights"


builder.add_edge(START, "schema")
builder.add_edge("schema", "generate_sql")
builder.add_edge("generate_sql", "validate_sql")
builder.add_edge("validate_sql", "execute_sql")
builder.add_conditional_edges(
    "execute_sql",
    route_after_execute,
    {
        "generate_sql": "generate_sql",
        "generate_insights": "generate_insights",
    },
)
builder.add_edge("generate_insights", END)

graph = builder.compile()