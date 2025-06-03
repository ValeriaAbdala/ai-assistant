from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Chat Schemas
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default_user"
    analysis_type: Optional[str] = "auto"  # auto, impact_analysis, technical_solution, priority_analysis, team_optimization, correlation_analysis

class ChatResponse(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    timestamp: str
    context_used: int
    analysis_type: str

# Conversation Schemas
class ConversationCreate(BaseModel):
    title: Optional[str] = None
    user_id: str = "default_user"

class ConversationResponse(BaseModel):
    id: str
    title: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int

# Ticket Schemas
class TicketBase(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    type: str  # bug, feature, security, performance
    severity: str  # critical, high, medium, low
    priority: str
    status: str  # open, in-progress, resolved, closed
    assignee: Optional[str] = None
    reporter: Optional[str] = None
    sprint: Optional[str] = None
    epic: Optional[str] = None
    story_points: Optional[int] = None
    affected_customers: Optional[int] = 0
    revenue_impact: Optional[float] = 0.0
    business_impact: Optional[str] = None

class TicketAnalysisRequest(BaseModel):
    tickets: List[TicketBase]
    analysis_type: str = "criticality"  # criticality, correlation, team_optimization

class TicketAnalysisResponse(BaseModel):
    insights: List[Dict[str, Any]]
    recommendations: List[str]
    metrics: Dict[str, Any]
    timestamp: str

# Analytics Schemas
class AnalyticsRequest(BaseModel):
    query: str
    data_sources: List[str] = ["tickets", "sales"]  # tickets, sales, team
    time_period: Optional[str] = "last_7_days"

class AnalyticsResponse(BaseModel):
    insights: List[Dict[str, Any]]
    charts: List[Dict[str, Any]]
    recommendations: List[str]
    timestamp: str

# RAG Schemas
class RAGSearchRequest(BaseModel):
    query: str
    context_type: str = "all"  # all, tickets, documents
    max_results: int = 5

class RAGSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    query: str
    total_results: int