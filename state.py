from typing import TypedDict


class AgentState(TypedDict):

    question: str

    schema: str

    sql: str

    results: list

    answer: str

    error: str | None

    retries: int