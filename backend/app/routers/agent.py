import logging

from fastapi import APIRouter
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agent.graph import SYSTEM_PROMPT, build_graph
from app.agent.tools import AgentTools
from app.database import AsyncSessionLocal
from app.redis_client import get_redis
from app.schemas.agent import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Run the LangGraph ReAct agent for one conversational turn."""

    async with AsyncSessionLocal() as db:
        redis = await get_redis()
        tools = AgentTools(db, redis).as_tools()
        agent = build_graph(tools)

        # Build the messages list: system prompt + recent history + current question
        messages = [SystemMessage(content=SYSTEM_PROMPT)]

        # Include at most the last 6 history messages to keep context bounded
        for msg in request.history[-6:]:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(AIMessage(content=msg.content))

        messages.append(HumanMessage(content=request.question))

        logger.info("Agent invoked | question=%r | history_len=%d", request.question, len(request.history))

        result = await agent.ainvoke({"messages": messages})
        all_messages: list = result["messages"]

        # Collect names of every tool the agent called
        tool_calls_made: list[str] = []
        for msg in all_messages:
            for tc in getattr(msg, "tool_calls", []) or []:
                name = tc["name"] if isinstance(tc, dict) else getattr(tc, "name", str(tc))
                tool_calls_made.append(name)

        final = all_messages[-1]
        answer = final.content if hasattr(final, "content") else str(final)

        logger.info(
            "Agent done | tools_called=%s | answer_len=%d",
            tool_calls_made,
            len(answer),
        )

        return ChatResponse(answer=answer, tool_calls_made=tool_calls_made)
