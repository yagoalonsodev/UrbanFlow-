import json
import os
from typing import Annotated, TypedDict

from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import (
    END,
    START,
    StateGraph,
)
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from agent.database import (
    execute_read_only_sql,
    live_database_context,
)


class AgentState(TypedDict):
    messages: Annotated[
        list[BaseMessage],
        add_messages,
    ]

    database_context: str

    provenance: str


SYSTEM_PROMPT = """
Eres el asistente de datos de UrbanFlow.

UrbanFlow es una plataforma de Data Engineering
sobre movilidad urbana de Barcelona.

Tu trabajo es responder preguntas utilizando
los datos disponibles en PostgreSQL.

REGLAS:

1. Responde siempre en español.

2. Cuando la pregunta necesite datos de UrbanFlow,
   debes utilizar la herramienta SQL.

3. Solo puedes ejecutar consultas SELECT.

4. Nunca debes modificar la base de datos.

5. No inventes datos.

6. Si los datos no están disponibles,
   dilo claramente.

7. Las consultas SQL están limitadas a un número
   máximo de filas.

8. Después de utilizar SQL, explica brevemente
   qué información has obtenido.

9. La respuesta debe incluir al final:

   Consulta SQL usada:
   <consulta ejecutada>

10. Si no has ejecutado SQL, indica:

   Consulta SQL usada:
   No se ejecutó ninguna consulta SQL.
"""


@tool
def query_urbanflow_sql(
    query: str,
) -> str:
    """
    Ejecuta una consulta SQL de solo lectura
    sobre PostgreSQL de UrbanFlow.
    """

    return execute_read_only_sql(query)


tools = [
    query_urbanflow_sql,
]


model = ChatOllama(
    model=os.getenv(
        "OLLAMA_MODEL",
        "deepseek-coder:6.7b",
    ),
    base_url=os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434",
    ),
    temperature=0,
)


model_with_tools = model.bind_tools(
    tools
)


def context_node(
    state: AgentState,
) -> dict:

    context = live_database_context()

    return {
        "database_context": context
    }


def assistant_node(
    state: AgentState,
) -> dict:

    context = state.get(
        "database_context",
        "{}",
    )

    messages = [
        SystemMessage(
            content=SYSTEM_PROMPT
        ),
        SystemMessage(
            content=(
                "Contexto actual de la base de datos:\n"
                + context
            )
        ),
        *state["messages"],
    ]

    response = model_with_tools.invoke(
        messages
    )

    return {
        "messages": [response]
    }


def should_use_tools(
    state: AgentState,
) -> str:

    last_message = state[
        "messages"
    ][-1]

    if getattr(
        last_message,
        "tool_calls",
        None,
    ):
        return "tools"

    return "provenance"


def provenance_node(
    state: AgentState,
) -> dict:

    executed_queries = []

    for message in state["messages"]:

        if not isinstance(
            message,
            ToolMessage,
        ):
            continue

        try:
            data = json.loads(
                message.content
            )

            query = data.get(
                "query"
            )

            if query:
                executed_queries.append(
                    query
                )

        except (
            json.JSONDecodeError,
            TypeError,
        ):
            continue

    if executed_queries:

        provenance = (
            "Consulta SQL usada:\n\n"
            + "\n\n".join(
                executed_queries
            )
        )

    else:

        provenance = (
            "Consulta SQL usada:\n\n"
            "No se ejecutó ninguna "
            "consulta SQL."
        )

    return {
        "provenance": provenance
    }


tool_node = ToolNode(
    tools
)


graph = StateGraph(
    AgentState
)


graph.add_node(
    "context",
    context_node,
)

graph.add_node(
    "assistant",
    assistant_node,
)

graph.add_node(
    "tools",
    tool_node,
)

graph.add_node(
    "provenance",
    provenance_node,
)


graph.add_edge(
    START,
    "context",
)

graph.add_edge(
    "context",
    "assistant",
)

graph.add_conditional_edges(
    "assistant",
    should_use_tools,
    {
        "tools": "tools",
        "provenance": "provenance",
    },
)

graph.add_edge(
    "tools",
    "assistant",
)

graph.add_edge(
    "provenance",
    END,
)


app = graph.compile()