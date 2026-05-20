"""SQLAlchemy engine and session management."""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func

from app.config import settings

# Engine: long-lived, manages connection pool
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Test connections before use; survives DB restarts
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Conversation(Base):
    """A chat conversation. Belongs to a tenant (eventually)."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, nullable=False, index=True)  # Placeholder for multi-tenancy
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """A single message in a conversation. Either user or assistant role."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")


def get_db():
    """FastAPI dependency: yields a DB session per request, closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. For dev only — in production use Alembic migrations."""
    Base.metadata.create_all(bind=engine)
