"""
LangGraph ReAct agent graph.

Pattern: agent_node → (tool_calls?) → ToolNode → agent_node → … → END

`build_graph(tools)` is called once per request so each request gets its own
ToolNode bound to that request's db/redis session.  Graph compilation is
cheap (pure Python DAG construction); the expensive part is the LLM call.
"""

import logging
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are TransitTwin AI, an expert assistant for HSL public \
transport in the Helsinki metropolitan area (Helsinki, Espoo, Vantaa).

You have access to real-time data tools. Always use them to ground your answers \
in actual live data — never fabricate route IDs, stop names, or passenger figures.

Guidelines:
- For disruption / alert questions → call get_active_disruptions first.
- For fleet / delay questions → call get_vehicle_summary.
- For simulation / impact questions → use find_stop if you need an ID, then simulate_disruption.
- Be concise and factual. Lead with key numbers and actionable recommendations.
- Stay focused on HSL transport in the Helsinki region. Politely decline off-topic questions.
"""


# ── Minimal MessagesState (avoids version-specific imports) ───────────────────

class MessagesState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# ── Graph factory ─────────────────────────────────────────────────────────────

def build_graph(tools: list):
    """Build and compile a ReAct agent graph for the given tools list."""

    llm = ChatGroq(
        model="qwen/qwen3-32b",
        api_key=settings.GROQ_API_KEY,
        temperature=0,
        max_retries=2,
    )
    llm_with_tools = llm.bind_tools(tools)

    async def agent_node(state: MessagesState) -> dict:
        logger.debug("agent_node: %d messages in state", len(state["messages"]))
        response = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}

    def should_continue(state: MessagesState) -> str:
        last = state["messages"][-1]
        if getattr(last, "tool_calls", None):
            return "tools"
        return END

    tool_node = ToolNode(tools)

    graph: StateGraph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", END: END},
    )
    graph.add_edge("tools", "agent")

    return graph.compile()
