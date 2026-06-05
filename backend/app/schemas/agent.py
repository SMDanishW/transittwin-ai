from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str       # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    question: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    answer: str
    tool_calls_made: list[str] = []
