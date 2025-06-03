from fastapi import APIRouter, HTTPException
from app.services.visualization_service import VisualizationService
from app.services.analytics_service import AnalyticsService
from app.database.connection import SessionLocal
from app.database.models import Ticket
from typing import List, Dict, Any
import logging
import pandas as pd

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
viz_service = VisualizationService()
analytics_service = AnalyticsService()

@router.get("/dashboard")
async def get_real_dashboard():
    """Create dashboard with real tickets from database"""
    try:
        db = SessionLocal()
        tickets = db.query(Ticket).all()
        
        if not tickets:
            raise HTTPException(status_code=404, detail="No tickets found in database")
        
        # Convert to format expected by visualization service
        tickets_data = []
        for ticket in tickets:
            tickets_data.append({
                "id": ticket.id,
                "title": ticket.title,
                "description": ticket.description,
                "type": ticket.type,
                "severity": ticket.severity,
                "priority": ticket.priority,
                "status": ticket.status,
                "assignee": ticket.assignee,
                "reporter": ticket.reporter,
                "sprint": ticket.sprint,
                "affected_customers": ticket.affected_customers or 0,
                "revenue_impact": ticket.revenue_impact or 0.0,
                "business_impact": ticket.business_impact
            })
        
        db.close()
        
        # Generate dashboard
        dashboard = viz_service.create_ticket_dashboard(tickets_data)
        
        return {
            "dashboard": dashboard,
            "data_source": "real_database",
            "tickets_count": len(tickets_data),
            "total_revenue_impact": sum(t["revenue_impact"] for t in tickets_data)
        }
        
    except Exception as e:
        logger.error(f"Error creating real dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts/severity")
async def get_severity_distribution():
    """Get severity distribution chart with real data"""
    try:
        db = SessionLocal()
        tickets = db.query(Ticket).all()
        
        if not tickets:
            raise HTTPException(status_code=404, detail="No tickets found")
        
        tickets_data = [{"severity": ticket.severity} for ticket in tickets]
        df = pd.DataFrame(tickets_data)
        
        chart = viz_service._create_severity_chart(df)
        
        db.close()
        
        return {
            "chart": chart,
            "total_tickets": len(tickets_data)
        }
        
    except Exception as e:
        logger.error(f"Error creating severity chart: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts/revenue-impact")
async def get_revenue_impact():
    """Get revenue impact chart with real data"""
    try:
        db = SessionLocal()
        tickets = db.query(Ticket).filter(Ticket.revenue_impact > 0).all()
        
        if not tickets:
            raise HTTPException(status_code=404, detail="No tickets with revenue impact found")
        
        tickets_data = [
            {
                "id": ticket.id,
                "title": ticket.title,
                "revenue_impact": ticket.revenue_impact
            } 
            for ticket in tickets
        ]
        df = pd.DataFrame(tickets_data)
        
        chart = viz_service._create_revenue_impact_chart(df)
        
        db.close()
        
        return {
            "chart": chart,
            "tickets_with_impact": len(tickets_data),
            "total_impact": sum(t["revenue_impact"] for t in tickets_data)
        }
        
    except Exception as e:
        logger.error(f"Error creating revenue impact chart: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts/team-workload")
async def get_team_workload():
    """Get team workload chart with real data"""
    try:
        db = SessionLocal()
        tickets = db.query(Ticket).filter(Ticket.assignee.isnot(None)).all()
        
        if not tickets:
            raise HTTPException(status_code=404, detail="No tickets with assignees found")
        
        tickets_data = [
            {
                "assignee": ticket.assignee,
                "severity": ticket.severity,
                "status": ticket.status
            }
            for ticket in tickets
        ]
        df = pd.DataFrame(tickets_data)
        
        chart = viz_service._create_team_workload_chart(df)
        
        db.close()
        
        return {
            "chart": chart,
            "team_members": len(set(t["assignee"] for t in tickets_data))
        }
        
    except Exception as e:
        logger.error(f"Error creating team workload chart: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts/priority-matrix")
async def get_priority_matrix():
    """Get priority matrix with real data"""
    try:
        db = SessionLocal()
        tickets = db.query(Ticket).all()
        
        if not tickets:
            raise HTTPException(status_code=404, detail="No tickets found")
        
        tickets_data = [
            {
                "id": ticket.id,
                "severity": ticket.severity,
                "affected_customers": ticket.affected_customers or 0,
                "revenue_impact": ticket.revenue_impact or 0.0
            }
            for ticket in tickets
        ]
        df = pd.DataFrame(tickets_data)
        
        chart = viz_service._create_priority_matrix(df)
        
        db.close()
        
        return {
            "chart": chart,
            "total_tickets": len(tickets_data)
        }
        
    except Exception as e:
        logger.error(f"Error creating priority matrix: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ticket-dashboard")
async def create_ticket_dashboard(tickets_data: Dict[str, List[Dict[str, Any]]]):
    """Create comprehensive ticket dashboard with visualizations"""
    try:
        tickets = tickets_data.get("tickets", [])
        
        if not tickets:
            raise HTTPException(status_code=400, detail="No tickets data provided")
        
        dashboard = viz_service.create_ticket_dashboard(tickets)
        
        return dashboard
        
    except Exception as e:
        logger.error(f"Error creating ticket dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics-charts")
async def create_analytics_charts(analytics_data: Dict[str, Any]):
    """Create charts for analytics results"""
    try:
        charts = viz_service.create_analytics_charts(analytics_data)
        return charts
        
    except Exception as e:
        logger.error(f"Error creating analytics charts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sample-dashboard")
async def get_sample_dashboard():
    """Get sample dashboard with mock data"""
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
                "affected_customers": 150
            },
            {
                "id": "PROD-002", 
                "title": "Search not working",
                "severity": "high",
                "status": "in-progress", 
                "assignee": "Roberto Silva",
                "revenue_impact": 8000,
                "affected_customers": 80
            },
            {
                "id": "SECU-001",
                "title": "XSS vulnerability",
                "severity": "critical",
                "status": "open",
                "assignee": "Alejandro Ruiz", 
                "revenue_impact": 0,
                "affected_customers": 0
            },
            {
                "id": "PROD-007",
                "title": "Cart empties randomly",
                "severity": "high",
                "status": "open",
                "assignee": "Natalia Jiménez",
                "revenue_impact": 34200,
                "affected_customers": 178
            }
        ]
        
        dashboard = viz_service.create_ticket_dashboard(sample_tickets)
        return dashboard
        
    except Exception as e:
        logger.error(f"Error creating sample dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-analytics-viz")
async def test_analytics_visualizations():
    """Test analytics with visualizations"""
    try:
        # Get analytics data
        sample_tickets = [
            {"id": "PROD-001", "severity": "critical", "status": "open", 
             "assignee": "Maria González", "revenue_impact": 25000, "affected_customers": 150},
            {"id": "PROD-002", "severity": "high", "status": "in-progress",
             "assignee": "Roberto Silva", "revenue_impact": 8000, "affected_customers": 80}
        ]
        
        # Run analytics
        analytics_result = await analytics_service.correlation_analysis(sample_tickets)
        
        # Generate charts
        charts = viz_service.create_analytics_charts(analytics_result)
        
        return {
            "analytics": analytics_result,
            "visualizations": charts
        }
        
    except Exception as e:
        logger.error(f"Error in test analytics viz: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))