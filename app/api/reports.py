from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import FileResponse
from app.services.pdf_report_service import PDFReportService
from app.services.visualization_service import VisualizationService
from app.services.gemini_service import GeminiService
from app.services.rag_service import LocalRAGService
from app.database.connection import SessionLocal
from app.database.models import Ticket
from typing import List, Dict, Any, Optional
import tempfile
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
pdf_service = PDFReportService()
viz_service = VisualizationService()
gemini_service = GeminiService()
rag_service = LocalRAGService()

@router.get("/executive")
async def generate_executive_report(
    ticket_ids: Optional[List[str]] = Query(None, description="Specific ticket IDs to include"),
    include_analysis: bool = Query(True, description="Include AI analysis in report"),
    format: str = Query("pdf", description="Output format: pdf, base64")
):
    """Generate executive summary report PDF"""
    try:
        # Get tickets from database
        db = SessionLocal()
        
        if ticket_ids:
            tickets = db.query(Ticket).filter(Ticket.id.in_(ticket_ids)).all()
        else:
            tickets = db.query(Ticket).all()
        
        if not tickets:
            raise HTTPException(status_code=404, detail="No tickets found")
        
        # Convert to dict format
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
        
        # Generate dashboard data for metrics
        dashboard_data = viz_service.create_ticket_dashboard(tickets_data)
        
        # Generate AI analysis if requested
        analysis_result = ""
        if include_analysis:
            try:
                # Create analysis query
                query = f"Analyze these {len(tickets_data)} tickets for executive summary. Focus on business impact, revenue implications, and strategic recommendations."
                
                # Use RAG for context
                rag_results = await rag_service.search_tickets(query, max_results=len(tickets_data))
                
                # Generate analysis with Gemini
                analysis_result = await gemini_service.generate_response(
                    message=query,
                    context=rag_results,
                    analysis_type="impact_analysis"
                )
                
            except Exception as e:
                logger.warning(f"Could not generate AI analysis: {str(e)}")
                analysis_result = "AI analysis unavailable. Manual review recommended."
        
        # Generate PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = pdf_service.generate_executive_report(
                tickets_data=tickets_data,
                analysis_result=analysis_result,
                dashboard_data=dashboard_data,
                output_path=tmp_file.name
            )
        
        if format == "base64":
            # Return base64 encoded PDF
            pdf_base64 = pdf_service.export_base64_pdf(pdf_path)
            os.unlink(pdf_path)  # Clean up
            
            return {
                "report_type": "executive",
                "format": "base64",
                "pdf_data": pdf_base64,
                "tickets_included": len(tickets_data),
                "generated_at": datetime.utcnow().isoformat(),
                "filename": f"executive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        else:
            # Return file response
            response = FileResponse(
                path=pdf_path,
                media_type='application/pdf',
                filename=f"executive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            
            # Schedule cleanup (in production, use proper cleanup mechanism)
            return response
            
    except Exception as e:
        logger.error(f"Error generating executive report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/technical")
async def generate_technical_report(
    ticket_ids: Optional[List[str]] = Query(None, description="Specific ticket IDs to include"),
    include_details: bool = Query(True, description="Include detailed technical analysis"),
    format: str = Query("pdf", description="Output format: pdf, base64")
):
    """Generate detailed technical report PDF"""
    try:
        # Get tickets from database
        db = SessionLocal()
        
        if ticket_ids:
            tickets = db.query(Ticket).filter(Ticket.id.in_(ticket_ids)).all()
        else:
            tickets = db.query(Ticket).all()
        
        if not tickets:
            raise HTTPException(status_code=404, detail="No tickets found")
        
        # Convert to dict format
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
        
        # Generate dashboard data for metrics
        dashboard_data = viz_service.create_ticket_dashboard(tickets_data)
        
        # Generate PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = pdf_service.generate_technical_report(
                tickets_data=tickets_data,
                dashboard_data=dashboard_data,
                output_path=tmp_file.name
            )
        
        if format == "base64":
            # Return base64 encoded PDF
            pdf_base64 = pdf_service.export_base64_pdf(pdf_path)
            os.unlink(pdf_path)  # Clean up
            
            return {
                "report_type": "technical",
                "format": "base64", 
                "pdf_data": pdf_base64,
                "tickets_included": len(tickets_data),
                "generated_at": datetime.utcnow().isoformat(),
                "filename": f"technical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        else:
            # Return file response
            response = FileResponse(
                path=pdf_path,
                media_type='application/pdf',
                filename=f"technical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            
            return response
            
    except Exception as e:
        logger.error(f"Error generating technical report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/custom")
async def generate_custom_report(
    title: str = Query("Custom Report", description="Report title"),
    ticket_ids: Optional[List[str]] = Query(None, description="Specific ticket IDs to include"),
    severity_filter: Optional[str] = Query(None, description="Filter by severity"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    include_analysis: bool = Query(True, description="Include AI analysis"),
    include_charts: bool = Query(False, description="Include visual charts"),
    analysis_type: str = Query("impact_analysis", description="Type of AI analysis"),
    format: str = Query("pdf", description="Output format: pdf, base64")
):
    """Generate custom report with specified filters and options"""
    try:
        # Get tickets from database with filters
        db = SessionLocal()
        query = db.query(Ticket)
        
        if ticket_ids:
            query = query.filter(Ticket.id.in_(ticket_ids))
        
        if severity_filter:
            query = query.filter(Ticket.severity == severity_filter)
            
        if status_filter:
            query = query.filter(Ticket.status == status_filter)
        
        tickets = query.all()
        
        if not tickets:
            raise HTTPException(status_code=404, detail="No tickets found matching criteria")
        
        # Convert to dict format
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
        
        # Generate dashboard data
        dashboard_data = viz_service.create_ticket_dashboard(tickets_data)
        
        # Generate AI analysis if requested
        analysis_result = ""
        if include_analysis:
            try:
                query_text = f"Analyze tickets with focus on {analysis_type}. Filters applied: severity={severity_filter}, status={status_filter}"
                
                rag_results = await rag_service.search_tickets(query_text, max_results=len(tickets_data))
                
                analysis_result = await gemini_service.generate_response(
                    message=query_text,
                    context=rag_results,
                    analysis_type=analysis_type
                )
                
            except Exception as e:
                logger.warning(f"Could not generate AI analysis: {str(e)}")
                analysis_result = "AI analysis unavailable."
        
        # For now, use executive report template (can be extended)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = pdf_service.generate_executive_report(
                tickets_data=tickets_data,
                analysis_result=analysis_result,
                dashboard_data=dashboard_data,
                output_path=tmp_file.name
            )
        
        if format == "base64":
            pdf_base64 = pdf_service.export_base64_pdf(pdf_path)
            os.unlink(pdf_path)
            
            return {
                "report_type": "custom",
                "title": title,
                "format": "base64",
                "pdf_data": pdf_base64,
                "tickets_included": len(tickets_data),
                "filters_applied": {
                    "severity": severity_filter,
                    "status": status_filter,
                    "ticket_ids": ticket_ids
                },
                "generated_at": datetime.utcnow().isoformat(),
                "filename": f"custom_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        else:
            response = FileResponse(
                path=pdf_path,
                media_type='application/pdf',
                filename=f"custom_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            
            return response
            
    except Exception as e:
        logger.error(f"Error generating custom report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quick-summary")
async def generate_quick_summary(
    format: str = Query("pdf", description="Output format: pdf, base64")
):
    """Generate quick summary report of all tickets"""
    try:
        # Get all tickets
        db = SessionLocal()
        tickets = db.query(Ticket).all()
        
        if not tickets:
            raise HTTPException(status_code=404, detail="No tickets found")
        
        tickets_data = []
        for ticket in tickets:
            tickets_data.append({
                "id": ticket.id,
                "title": ticket.title,
                "severity": ticket.severity,
                "status": ticket.status,
                "assignee": ticket.assignee,
                "revenue_impact": ticket.revenue_impact or 0.0,
                "affected_customers": ticket.affected_customers or 0
            })
        
        db.close()
        
        # Generate dashboard data
        dashboard_data = viz_service.create_ticket_dashboard(tickets_data)
        
        # Quick analysis
        analysis_result = f"""
        Quick Summary Analysis:
        
        Total Tickets: {len(tickets_data)}
        Critical Issues: {len([t for t in tickets_data if t['severity'] == 'critical'])}
        Total Revenue at Risk: ${sum(t['revenue_impact'] for t in tickets_data):,.2f}
        
        Immediate Actions Required:
        - Review all critical tickets
        - Prioritize high-revenue-impact issues
        - Ensure proper resource allocation
        """
        
        # Generate PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = pdf_service.generate_executive_report(
                tickets_data=tickets_data,
                analysis_result=analysis_result,
                dashboard_data=dashboard_data,
                output_path=tmp_file.name
            )
        
        if format == "base64":
            pdf_base64 = pdf_service.export_base64_pdf(pdf_path)
            os.unlink(pdf_path)
            
            return {
                "report_type": "quick_summary",
                "format": "base64",
                "pdf_data": pdf_base64,
                "tickets_included": len(tickets_data),
                "generated_at": datetime.utcnow().isoformat(),
                "filename": f"quick_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        else:
            response = FileResponse(
                path=pdf_path,
                media_type='application/pdf',
                filename=f"quick_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            
            return response
            
    except Exception as e:
        logger.error(f"Error generating quick summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available-templates")
async def get_available_templates():
    """Get list of available report templates"""
    return {
        "templates": [
            {
                "name": "executive",
                "title": "Executive Summary Report",
                "description": "High-level overview for stakeholders with key metrics and recommendations",
                "endpoint": "/api/reports/executive"
            },
            {
                "name": "technical",
                "title": "Technical Analysis Report", 
                "description": "Detailed technical breakdown for development teams",
                "endpoint": "/api/reports/technical"
            },
            {
                "name": "custom",
                "title": "Custom Report",
                "description": "Configurable report with filters and options",
                "endpoint": "/api/reports/custom"
            },
            {
                "name": "quick_summary",
                "title": "Quick Summary",
                "description": "Fast overview of current status",
                "endpoint": "/api/reports/quick-summary"
            }
        ],
        "formats": ["pdf", "base64"],
        "filters": {
            "severity": ["critical", "high", "medium", "low"],
            "status": ["open", "in-progress", "resolved", "closed"],
            "analysis_types": ["impact_analysis", "technical", "priority", "team", "correlation"]
        }
    }