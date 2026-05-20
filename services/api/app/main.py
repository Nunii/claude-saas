"""claude-saas API. Multi-tenant LLM chatbot service."""
import logging

from anthropic import Anthropic
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.db import Conversation, Message, get_db, init_db

logging.basicConfig(level=settings.log_level)
log = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, version="0.1.0")

# Anthropic client — lazy initialized so the app can start without an API key
_anthropic_client: Anthropic | None = None


def get_anthropic() -> Anthropic | None:
    """Lazy-init the Anthropic client. Returns None if no API key (stub mode)."""
    global _anthropic_client
    if _anthropic_client is None and settings.anthropic_api_key:
        _anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
    return _anthropic_client


# --- Request/Response models ---
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: int | None = None
    tenant_id: str = Field(default="default")  # placeholder until proper auth


class ChatResponse(BaseModel):
    conversation_id: int
    message: str


# --- Endpoints ---
@app.on_event("startup")
def on_startup():
    log.info("Starting %s", settings.app_name)
    init_db()
    log.info("Database initialized")


@app.get("/healthz")
def healthz():
    """Liveness probe target. Kubernetes will hit this."""
    return {"status": "ok"}


@app.get("/readyz")
def readyz(db: Session = Depends(get_db)):
    """Readiness probe target. Returns 503 if DB is unreachable."""
    try:
        db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DB not ready: {e}")


@app.post("/v1/chat", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    anthropic: Anthropic = Depends(get_anthropic),
):
    """
    Send a message, get an AI response. Persists the conversation history.
    """
    # Get or create conversation
    if req.conversation_id is None:
        conv = Conversation(tenant_id=req.tenant_id)
        db.add(conv)
        db.flush()  # populates conv.id without committing
    else:
        conv = db.query(Conversation).filter_by(
            id=req.conversation_id, tenant_id=req.tenant_id
        ).first()
        if conv is None:
            raise HTTPException(status_code=404, detail="Conversation not found")

    # Append user message
    user_msg = Message(conversation_id=conv.id, role="user", content=req.message)
    db.add(user_msg)
    db.flush()

    # Load history (for multi-turn conversations)
    history = [
        {"role": m.role, "content": m.content}
        for m in db.query(Message)
        .filter_by(conversation_id=conv.id)
        .order_by(Message.created_at)
        .all()
    ]

    # Call Claude (or stub if no API key configured)
    if anthropic is None:
        log.warning("ANTHROPIC_API_KEY not set — returning stub response")
        assistant_text = (
            f"[STUB RESPONSE] You said: '{req.message}'. "
            f"Set ANTHROPIC_API_KEY in .env for real responses."
        )
    else:
        try:
            response = anthropic.messages.create(
                model=settings.anthropic_model,
                max_tokens=1024,
                messages=history,
            )
            assistant_text = response.content[0].text
        except Exception as e:
            log.exception("Anthropic API call failed")
            raise HTTPException(status_code=502, detail=f"Upstream LLM error: {e}")

    # Persist assistant reply
    assistant_msg = Message(conversation_id=conv.id, role="assistant", content=assistant_text)
    db.add(assistant_msg)
    db.commit()

    return ChatResponse(conversation_id=conv.id, message=assistant_text)
