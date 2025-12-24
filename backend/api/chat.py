from fastapi import APIRouter
from schemas.chat import ChatRequest, ChatResponse
from agent.rag_agent import RAGAgent

router = APIRouter()
agent = RAGAgent()

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    answer = agent.answer(req.question, req.selected_text)
    return {"answer": answer}
