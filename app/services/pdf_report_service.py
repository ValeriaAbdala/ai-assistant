from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.lib.colors import HexColor
import plotly.graph_objects as go
import plotly.io as pio
from typing import Dict, List, Any, Optional
import io
import base64
import tempfile
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PDFReportService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # Center alignment
        ))
        
        self.styles.add(ParagraphStyle(
            name='ExecutiveSummary',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            leftIndent=20,
            rightIndent=20,
            backColor=colors.lightgrey
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=colors.darkred,
            alignment=1,
            spaceAfter=6
        ))

    def generate_executive_report(
        self, 
        tickets_data: List[Dict[str, Any]], 
        analysis_result: str,
        dashboard_data: Dict[str, Any],
        output_path: str = None
    ) -> str:
        """Generate executive summary report PDF"""
        try:
            if not output_path:
                output_path = f"executive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Title
            title = Paragraph("Executive Summary Report", self.styles['CustomTitle'])
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Date and metadata
            date_para = Paragraph(
                f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
                self.styles['Normal']
            )
            story.append(date_para)
            story.append(Spacer(1, 20))
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", self.styles['Heading2']))
            
            # Key metrics
            metrics = dashboard_data.get('metrics', {})
            key_metrics_data = [
                ['Metric', 'Value', 'Impact'],
                ['Total Tickets', str(metrics.get('total_tickets', 0)), 'Current workload'],
                ['Critical Tickets', str(metrics.get('critical_tickets', 0)), 'Immediate attention required'],
                ['Revenue Impact', f"${metrics.get('total_revenue_impact', 0):,.2f}", 'Direct financial exposure'],
                ['Completion Rate', f"{metrics.get('completion_rate', 0):.1f}%", 'Team efficiency'],
                ['Customers Affected', f"{metrics.get('avg_customers_affected', 0):.0f} avg", 'Customer satisfaction risk']
            ]
            
            key_metrics_table = Table(key_metrics_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
            key_metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(key_metrics_table)
            story.append(Spacer(1, 20))
            
            # Critical Issues Section
            story.append(Paragraph("Critical Issues Requiring Immediate Attention", self.styles['Heading2']))
            
            critical_tickets = [t for t in tickets_data if t.get('severity') == 'critical']
            
            if critical_tickets:
                for ticket in critical_tickets:
                    story.append(Paragraph(f"<b>{ticket['id']}: {ticket['title']}</b>", self.styles['Normal']))
                    story.append(Paragraph(f"Revenue Impact: ${ticket.get('revenue_impact', 0):,.2f}", self.styles['Normal']))
                    story.append(Paragraph(f"Customers Affected: {ticket.get('affected_customers', 0)}", self.styles['Normal']))
                    story.append(Paragraph(f"Assignee: {ticket.get('assignee', 'Unassigned')}", self.styles['Normal']))
                    story.append(Spacer(1, 10))
            else:
                story.append(Paragraph("No critical issues identified.", self.styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            # AI Analysis Summary
            story.append(Paragraph("AI Analysis Summary", self.styles['Heading2']))
            
            # Clean and format the analysis result
            analysis_lines = analysis_result.split('\n')
            for line in analysis_lines:
                if line.strip():
                    if line.startswith('**') and line.endswith(':**'):
                        # Header
                        clean_line = line.replace('**', '').replace(':', '')
                        story.append(Paragraph(f"<b>{clean_line}</b>", self.styles['Heading3']))
                    elif line.startswith('*'):
                        # Bullet point
                        clean_line = line.replace('*', '').strip()
                        story.append(Paragraph(f"• {clean_line}", self.styles['Normal']))
                    else:
                        story.append(Paragraph(line, self.styles['Normal']))
                    story.append(Spacer(1, 6))
            
            story.append(PageBreak())
            
            # Detailed Ticket Analysis
            story.append(Paragraph("Detailed Ticket Analysis", self.styles['Heading2']))
            
            # Create ticket details table
            ticket_details_data = [['ID', 'Title', 'Severity', 'Status', 'Revenue Impact', 'Assignee']]
            
            for ticket in tickets_data:
                ticket_details_data.append([
                    ticket.get('id', ''),
                    ticket.get('title', '')[:40] + ('...' if len(ticket.get('title', '')) > 40 else ''),
                    ticket.get('severity', ''),
                    ticket.get('status', ''),
                    f"${ticket.get('revenue_impact', 0):,.0f}",
                    ticket.get('assignee', 'Unassigned')[:15] + ('...' if len(ticket.get('assignee', '')) > 15 else '')
                ])
            
            ticket_table = Table(ticket_details_data, colWidths=[0.8*inch, 2.2*inch, 0.8*inch, 1*inch, 1*inch, 1.2*inch])
            ticket_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            
            story.append(ticket_table)
            story.append(Spacer(1, 20))
            
            # Recommendations Section
            story.append(Paragraph("Recommended Actions", self.styles['Heading2']))
            
            recommendations = [
                "Prioritize resolution of high-revenue-impact tickets (PROD-007, PROD-001)",
                "Allocate additional resources to critical security issues (SECU-001)",
                "Implement monitoring for payment gateway stability",
                "Review session management implementation",
                "Establish customer communication plan for affected users",
                "Schedule post-incident review meeting within 48 hours"
            ]
            
            for i, rec in enumerate(recommendations, 1):
                story.append(Paragraph(f"{i}. {rec}", self.styles['Normal']))
                story.append(Spacer(1, 8))
            
            # Footer
            story.append(Spacer(1, 40))
            footer = Paragraph(
                f"Report generated by PM AI Assistant | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                self.styles['Normal']
            )
            story.append(footer)
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"Executive report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating executive report: {str(e)}")
            raise

    def generate_technical_report(
        self,
        tickets_data: List[Dict[str, Any]],
        dashboard_data: Dict[str, Any],
        output_path: str = None
    ) -> str:
        """Generate detailed technical report PDF"""
        try:
            if not output_path:
                output_path = f"technical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Title
            title = Paragraph("Technical Analysis Report", self.styles['CustomTitle'])
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Metadata
            date_para = Paragraph(
                f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
                self.styles['Normal']
            )
            story.append(date_para)
            story.append(Spacer(1, 20))
            
            # Technical Summary
            story.append(Paragraph("Technical Overview", self.styles['Heading2']))
            
            # System Health Metrics
            metrics = dashboard_data.get('metrics', {})
            total_tickets = metrics.get('total_tickets', 0)
            critical_tickets = metrics.get('critical_tickets', 0)
            
            health_data = [
                ['System Health Indicator', 'Value', 'Status'],
                ['Critical Issue Ratio', f"{(critical_tickets/total_tickets*100) if total_tickets > 0 else 0:.1f}%", 
                 'HIGH RISK' if critical_tickets/total_tickets > 0.3 else 'MODERATE'],
                ['Average Resolution Time', 'N/A (No resolved tickets)', 'ATTENTION NEEDED'],
                ['Security Incidents', str(len([t for t in tickets_data if t.get('type') == 'security'])), 
                 'CRITICAL' if any(t.get('type') == 'security' for t in tickets_data) else 'OK'],
                ['Revenue at Risk', f"${metrics.get('total_revenue_impact', 0):,.2f}", 
                 'HIGH' if metrics.get('total_revenue_impact', 0) > 50000 else 'MODERATE']
            ]
            
            health_table = Table(health_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            health_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(health_table)
            story.append(Spacer(1, 30))
            
            # Detailed Issue Analysis
            story.append(Paragraph("Detailed Issue Analysis", self.styles['Heading2']))
            
            for ticket in tickets_data:
                story.append(Paragraph(f"Ticket: {ticket['id']}", self.styles['Heading3']))
                
                details_data = [
                    ['Field', 'Value'],
                    ['Title', ticket.get('title', '')],
                    ['Type', ticket.get('type', '')],
                    ['Severity', ticket.get('severity', '')],
                    ['Status', ticket.get('status', '')],
                    ['Assignee', ticket.get('assignee', 'Unassigned')],
                    ['Reporter', ticket.get('reporter', '')],
                    ['Sprint', ticket.get('sprint', '')],
                    ['Revenue Impact', f"${ticket.get('revenue_impact', 0):,.2f}"],
                    ['Customers Affected', str(ticket.get('affected_customers', 0))],
                    ['Business Impact', ticket.get('business_impact', '')[:100] + ('...' if len(ticket.get('business_impact', '')) > 100 else '')]
                ]
                
                details_table = Table(details_data, colWidths=[1.5*inch, 4*inch])
                details_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]))
                
                story.append(details_table)
                story.append(Spacer(1, 15))
                
                # Description
                if ticket.get('description'):
                    story.append(Paragraph("Description:", self.styles['Heading4']))
                    story.append(Paragraph(ticket['description'], self.styles['Normal']))
                    story.append(Spacer(1, 10))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"Technical report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating technical report: {str(e)}")
            raise

    def add_charts_to_report(self, story: List, dashboard_data: Dict[str, Any]):
        """Add charts to report story (placeholder for chart integration)"""
        try:
            # This would integrate with your visualization service
            # For now, we'll add chart placeholders
            
            story.append(Paragraph("Visual Analytics", self.styles['Heading2']))
            story.append(Spacer(1, 10))
            
            # Chart placeholders
            charts_info = [
                "Severity Distribution Chart - Shows breakdown of ticket severities",
                "Revenue Impact Analysis - Displays financial impact by ticket",
                "Team Workload Distribution - Shows ticket assignment balance",
                "Priority Matrix - Correlates revenue impact vs customer impact"
            ]
            
            for chart_info in charts_info:
                story.append(Paragraph(f"• {chart_info}", self.styles['Normal']))
                story.append(Spacer(1, 6))
            
            story.append(Spacer(1, 20))
            
        except Exception as e:
            logger.error(f"Error adding charts to report: {str(e)}")

    def export_base64_pdf(self, pdf_path: str) -> str:
        """Convert PDF to base64 string for API responses"""
        try:
            with open(pdf_path, 'rb') as pdf_file:
                pdf_bytes = pdf_file.read()
                pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
                return pdf_base64
        except Exception as e:
            logger.error(f"Error converting PDF to base64: {str(e)}")
            return None