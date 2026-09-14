import os
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from agent.database import execute_read_only_sql, live_database_context


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


@tool
def query_urbanflow_sql(query: str) -> str:
    """Consulta PostgreSQL UrbanFlow en modo estrictamente solo lectura."""

    return execute_read_only_sql(query)


tools = [query_urbanflow_sql]


def context_node(state: AgentState) -> dict[str, list[SystemMessage]]:
    context = live_database_context()
    return {
        "messages": [
            SystemMessage(
                content=(
                    "CONTEXTO VIVO DE URBANFLOW. Úsalo junto con el historial del thread. "
                    "No inventes tablas, columnas, cifras ni snapshots. "
                    f"Estado actual: {context}"
                )
            )
        ]
    }


def assistant_node(state: AgentState) -> dict[str, list[BaseMessage]]:
    model = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0,
    ).bind_tools(tools)
    system = SystemMessage(
        content=(
            "Eres el analista de datos de UrbanFlow. Responde en español. "
            "Solo puedes afirmar datos obtenidos del contexto vivo o de query_urbanflow_sql. "
            "Para cifras actuales, consulta la base de datos. "
            "Usa las tablas dimensionales para analítica histórica cuando sea posible y "
            "realtime_bus_arrivals para llegadas. Nunca generes SQL de escritura. "
            "Si no puedes verificar algo, dilo claramente. Resume la consulta y el snapshot "
            "usados cuando respondas con datos."
        )
    )
    response = model.invoke([system, *state["messages"]])
    return {"messages": [response]}


def route_after_assistant(state: AgentState) -> str:
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"
    return END


builder = StateGraph(AgentState)
builder.add_node("context", context_node)
builder.add_node("assistant", assistant_node)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "context")
builder.add_edge("context", "assistant")
builder.add_conditional_edges("assistant", route_after_assistant)
builder.add_edge("tools", "assistant")

# langgraph dev supplies persistence for thread history and rejects custom
# checkpointers in graph definitions loaded by its API runtime.
graph = builder.compile()