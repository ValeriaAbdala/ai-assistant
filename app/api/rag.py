from fastapi import APIRouter, HTTPException
from app.models.schemas import RAGSearchRequest, RAGSearchResponse
from app.services.rag_service import LocalRAGService
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize RAG service
rag_service = LocalRAGService()

@router.post("/search", response_model=RAGSearchResponse)
async def search_knowledge_base(request: RAGSearchRequest):
    """Search in local knowledge base"""
    try:
        results = await rag_service.search_tickets(
            query=request.query,
            max_results=request.max_results
        )
        
        return RAGSearchResponse(
            results=results,
            query=request.query,
            total_results=len(results)
        )
        
    except Exception as e:
        logger.error(f"Error in RAG search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/critical")
async def search_critical_tickets(request: RAGSearchRequest):
    """Search only critical tickets"""
    try:
        results = await rag_service.search_critical_tickets(request.query)
        
        return RAGSearchResponse(
            results=results,
            query=request.query,
            total_results=len(results)
        )
        
    except Exception as e:
        logger.error(f"Error searching critical tickets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/business-impact") 
async def search_high_impact_tickets(
    request: RAGSearchRequest,
    min_revenue: float = 1000,
    min_customers: int = 10
):
    """Search tickets with significant business impact"""
    try:
        results = await rag_service.search_by_business_impact(
            query=request.query,
            min_revenue_impact=min_revenue,
            min_customers=min_customers
        )
        
        return RAGSearchResponse(
            results=results,
            query=request.query,
            total_results=len(results)
        )
        
    except Exception as e:
        logger.error(f"Error searching business impact tickets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_rag_statistics():
    """Get RAG system statistics"""
    try:
        stats = await rag_service.get_rag_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting RAG stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/load-tickets")
async def load_tickets_to_rag(tickets_data: Dict[str, Any]):
    """Load tickets into RAG system"""
    try:
        tickets = tickets_data.get("tickets", [])
        result = await rag_service.add_tickets_to_rag(tickets)
        return result
    except Exception as e:
        logger.error(f"Error loading tickets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))