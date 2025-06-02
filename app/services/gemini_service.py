import google.generativeai as genai
from typing import List, Dict, Any, Optional
import asyncio
import json
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")


        
    async def generate_response(
        self, 
        message: str, 
        context: List[Dict] = None,
        analysis_type: str = "general"
    ) -> str:
        """Generate response with Gemini"""
        try:
            prompt = self._build_prompt(message, context, analysis_type)
            
            logger.info(f"Generating response for: {analysis_type}")
            
            # Run in thread pool to avoid blocking
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.model.generate_content(prompt)
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error in Gemini: {str(e)}")
            return f"Error processing request: {str(e)}"
    
    def _build_prompt(
        self, 
        message: str, 
        context: List[Dict] = None, 
        analysis_type: str = "general"
    ) -> str:
        """Build optimized prompt based on analysis type"""
        
        base_context = """
You are an AI assistant specialized for Project Managers and Scrum Masters.
Your goal is to analyze incidents, tickets and their impact on sales to generate valuable insights.
Always respond in English in a clear and concise manner.
"""
        
        if analysis_type == "ticket_analysis":
            prompt = f"""{base_context}

TICKET ANALYSIS:
{self._format_context(context)}

PM QUERY: {message}

Generate analysis focused on:
1. Criticality by business impact
2. Incident patterns
3. Prioritization recommendations
4. Loss/risk estimation
5. Resource suggestions

Keep response concise but valuable."""

        elif analysis_type == "sales_correlation":
            prompt = f"""{base_context}

SALES-INCIDENTS CORRELATION ANALYSIS:
{self._format_context(context)}

QUERY: {message}

Analyze:
1. Direct relationship between incidents and sales drop
2. Temporal patterns
3. ROI of resolving each incident
4. Future impact predictions

Include specific metrics and recommendations."""

        elif analysis_type == "team_optimization":
            prompt = f"""{base_context}

TEAM OPTIMIZATION:
{self._format_context(context)}

QUERY: {message}

Focus on:
1. Optimal work distribution
2. Bottleneck identification
3. Specialization by incident type
4. Process improvement suggestions"""

        else:  # general
            context_str = self._format_context(context) if context else ""
            prompt = f"""{base_context}

{context_str}

QUERY: {message}

Provide relevant analysis for PM/Scrum Master with actionable insights."""

        return prompt
    
    def _format_context(self, context: List[Dict]) -> str:
        """Format context for prompt"""
        if not context:
            return ""
        
        formatted = "RELEVANT CONTEXT:\n"
        for item in context[:5]:  # Limit context
            if isinstance(item, dict):
                formatted += f"- {json.dumps(item, ensure_ascii=False)}\n"
            else:
                formatted += f"- {str(item)}\n"
        
        return formatted

    async def analyze_tickets(self, tickets: List[Dict], query: str) -> Dict[str, Any]:
        """Specialized ticket analysis"""
        try:
            # Format tickets for analysis
            ticket_data = []
            for ticket in tickets:
                ticket_summary = {
                    "id": ticket.get("id"),
                    "title": ticket.get("title"),
                    "severity": ticket.get("severity"),
                    "priority": ticket.get("priority"),
                    "status": ticket.get("status"),
                    "revenue_impact": ticket.get("revenue_impact", 0),
                    "affected_customers": ticket.get("affected_customers", 0),
                    "business_impact": ticket.get("business_impact", "")
                }
                ticket_data.append(ticket_summary)
            
            analysis_prompt = f"""
Analyze these tickets as a PM expert:

TICKETS DATA:
{json.dumps(ticket_data, indent=2)}

ANALYSIS REQUEST: {query}

Provide a JSON response with:
{{
    "critical_tickets": ["list of most critical ticket IDs"],
    "risk_assessment": "overall risk level",
    "revenue_impact_total": "estimated total impact",
    "recommendations": ["list of actionable recommendations"],
    "priority_order": ["ticket IDs in priority order"]
}}
"""
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.model.generate_content(analysis_prompt)
            )
            
            # Try to parse JSON response
            try:
                return json.loads(response.text)
            except:
                # If not JSON, return structured response
                return {
                    "analysis": response.text,
                    "tickets_analyzed": len(tickets),
                    "status": "completed"
                }
                
        except Exception as e:
            logger.error(f"Error in ticket analysis: {str(e)}")
            return {"error": str(e)}