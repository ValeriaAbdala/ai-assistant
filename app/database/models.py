from sqlalchemy import Column, String, DateTime, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import json

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    user_id = Column(String(100), nullable=False, default="default_user")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id='{self.id}', title='{self.title}', user='{self.user_id}')>"

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=True)  # Store analysis_type, context_used, etc.
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship with conversation
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id='{self.id}', role='{self.role}', conversation='{self.conversation_id}')>"

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(String, primary_key=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)  # bug, feature, security, performance
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    priority = Column(String(20), nullable=False)
    status = Column(String(30), nullable=False)  # open, in-progress, resolved, closed
    assignee = Column(String(100), nullable=True)
    reporter = Column(String(100), nullable=True)
    sprint = Column(String(100), nullable=True)
    epic = Column(String(200), nullable=True)
    story_points = Column(Integer, nullable=True)
    affected_customers = Column(Integer, nullable=True, default=0)
    revenue_impact = Column(Float, nullable=True, default=0.0)
    business_impact = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Ticket(id='{self.id}', title='{self.title}', severity='{self.severity}')>"

class AnalyticsSession(Base):
    __tablename__ = "analytics_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(100), nullable=False)
    analysis_type = Column(String(50), nullable=False)  # comprehensive, correlation, etc.
    query = Column(Text, nullable=False)
    results = Column(JSON, nullable=True)  # Store analysis results
    rag_context_used = Column(Integer, nullable=True, default=0)
    web_sources_used = Column(Integer, nullable=True, default=0)
    processing_time_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AnalyticsSession(id='{self.id}', type='{self.analysis_type}', user='{self.user_id}')>"

class RAGDocument(Base):
    __tablename__ = "rag_documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(100), nullable=False)  # Original document ID (e.g., ticket ID)
    document_type = Column(String(50), nullable=False)  # ticket, document, etc.
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    doc_metadata = Column(JSON, nullable=True)
    embedding_model = Column(String(100), nullable=False)
    vector_db_id = Column(String(100), nullable=True)  # ChromaDB ID
    indexed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<RAGDocument(id='{self.id}', type='{self.document_type}', title='{self.title[:50]}')>"

class WebScrapingCache(Base):
    __tablename__ = "web_scraping_cache"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    query_hash = Column(String(64), nullable=False, unique=True)  # MD5 hash of query
    original_query = Column(Text, nullable=False)
    analysis_type = Column(String(50), nullable=False)
    results = Column(JSON, nullable=True)
    sources_count = Column(Integer, nullable=True, default=0)
    success = Column(String(10), nullable=False, default="true")  # "true" or "false"
    cached_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<WebScrapingCache(query='{self.original_query[:50]}', cached='{self.cached_at}')>"