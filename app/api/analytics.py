from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalyticsRequest, AnalyticsResponse, TicketAnalysisRequest, TicketAnalysisResponse
from app.services.analytics_service import AnalyticsService
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize analytics service
analytics_service = AnalyticsService()

@router.post("/comprehensive-analysis", response_model=AnalyticsResponse)
async def comprehensive_analysis(request: AnalyticsRequest):
    """Perform comprehensive analysis with RAG + Web + AI"""
    try:
        result = await analytics_service.comprehensive_analysis(
            query=request.query,
            analysis_type="auto",
            include_web=True,
            urgency="medium"
        )
        
        return AnalyticsResponse(
            insights=result.get("analysis_summary", ""),
            charts=[],  # Charts would be generated here
            recommendations=result.get("recommendations", []),
            timestamp=result.get("timestamp", "")
        )
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/correlation-analysis")
async def correlation_analysis(request: TicketAnalysisRequest):
    """Analyze correlations between tickets and business metrics"""
    try:
        # Convert Pydantic models to dicts
        tickets_data = [ticket.dict() for ticket in request.tickets]
        
        result = await analytics_service.correlation_analysis(
            tickets=tickets_data,
            sales_data=None  # Could be added later
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in correlation analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/impact-prediction")
async def impact_prediction(request: TicketAnalysisRequest):
    """Predict impact if tickets remain unresolved"""
    try:
        tickets_data = [ticket.dict() for ticket in request.tickets]
        
        result = await analytics_service.impact_prediction(
            tickets=tickets_data,
            time_horizon="7_days"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in impact prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/team-optimization")
async def team_optimization(request: TicketAnalysisRequest):
    """Analyze team workload and suggest optimizations"""
    try:
        tickets_data = [ticket.dict() for ticket in request.tickets]
        
        result = await analytics_service.team_optimization_analysis(
            tickets=tickets_data,
            team_data=None
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in team optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-analytics")
async def test_analytics():
    """Test analytics with sample data"""
    try:
        # Sample ticket data
        sample_tickets = [
            {
                "id": "PROD-001",
                "title": "Payment gateway failure",
                "severity": "critical",
                "status": "open",
                "assignee": "Maria González",
                "revenue_impact": 25000,
                "affected_customers": 150,
                "components": ["payment", "gateway"]
            },
            {
                "id": "PROD-002",
                "title": "Search not working",
                "severity": "high", 
                "status": "in-progress",
                "assignee": "Roberto Silva",
                "revenue_impact": 8000,
                "affected_customers": 80,
                "components": ["search", "frontend"]
            }
        ]
        
        result = await analytics_service.correlation_analysis(sample_tickets)
        return result
        
    except Exception as e:
        logger.error(f"Error in test analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))