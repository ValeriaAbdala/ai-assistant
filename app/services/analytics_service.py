from typing import Dict, List, Any, Optional
from app.services.rag_service import LocalRAGService
from app.services.web_scraper import GuidedWebScraper
from app.services.prompt_optimizer import PromptOptimizer
from app.services.gemini_service import GeminiService
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.rag_service = LocalRAGService()
        self.web_scraper = GuidedWebScraper()
        self.prompt_optimizer = PromptOptimizer()
        self.gemini_service = GeminiService()

    async def comprehensive_analysis(
        self,
        query: str,
        analysis_type: str = "auto",
        include_web: bool = True,
        urgency: str = "medium"
    ) -> Dict[str, Any]:
        """Perform comprehensive analysis combining RAG + Web + AI"""
        try:
            # 1. Optimize query and detect intent
            optimization = await self.prompt_optimizer.optimize_query(query, analysis_type)
            detected_intent = optimization["detected_intent"]
            
            # 2. Search local knowledge base (RAG)
            local_results = await self.rag_service.search_tickets(
                query=optimization["optimized_prompt"],
                max_results=5
            )
            
            # 3. Web scraping if requested
            web_results = []
            if include_web:
                web_data = await self.web_scraper.scrape_with_guidance(
                    query=query,
                    local_context=local_results,
                    pm_intent=detected_intent,
                    urgency=urgency
                )
                web_results = web_data.get("web_results", [])
            
            # 4. Generate comprehensive insights
            insights = await self._generate_comprehensive_insights(
                query=query,
                local_context=local_results,
                web_context=web_results,
                intent=detected_intent
            )
            
            # 5. Create recommendations
            recommendations = await self._generate_recommendations(
                local_results, web_results, detected_intent, query
            )
            
            # 6. Calculate metrics
            metrics = self._calculate_pm_metrics(local_results, web_results)
            
            return {
                "analysis_summary": insights,
                "recommendations": recommendations,
                "metrics": metrics,
                "local_results_count": len(local_results),
                "web_results_count": len(web_results),
                "detected_intent": detected_intent,
                "query_optimization": optimization,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {str(e)}")
            return {"error": str(e), "query": query}

    async def correlation_analysis(
        self,
        tickets: List[Dict[str, Any]],
        sales_data: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Analyze correlations between tickets and business metrics"""
        try:
            # Group tickets by severity and impact
            critical_tickets = [t for t in tickets if t.get("severity") == "critical"]
            high_impact_tickets = [t for t in tickets if t.get("revenue_impact", 0) > 10000]
            
            # Calculate correlation metrics
            total_revenue_impact = sum(t.get("revenue_impact", 0) for t in tickets)
            total_customers_affected = sum(t.get("affected_customers", 0) for t in tickets)
            
            # Generate correlation insights with Gemini
            correlation_prompt = f"""
            Analyze ticket correlations:
            - Total tickets: {len(tickets)}
            - Critical tickets: {len(critical_tickets)}
            - High impact tickets: {len(high_impact_tickets)}
            - Total revenue impact: ${total_revenue_impact:,.2f}
            - Customers affected: {total_customers_affected}
            
            Provide PM insights on patterns and correlations.
            """
            
            correlation_insights = await self.gemini_service.generate_response(
                message=correlation_prompt,
                analysis_type="correlation_analysis"
            )
            
            return {
                "correlation_insights": correlation_insights,
                "metrics": {
                    "total_tickets": len(tickets),
                    "critical_tickets": len(critical_tickets),
                    "high_impact_tickets": len(high_impact_tickets),
                    "total_revenue_impact": total_revenue_impact,
                    "customers_affected": total_customers_affected,
                    "avg_revenue_per_ticket": total_revenue_impact / len(tickets) if tickets else 0
                },
                "patterns": self._identify_patterns(tickets),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in correlation analysis: {str(e)}")
            return {"error": str(e)}

    async def impact_prediction(
        self,
        tickets: List[Dict[str, Any]],
        time_horizon: str = "7_days"
    ) -> Dict[str, Any]:
        """Predict impact if tickets remain unresolved"""
        try:
            predictions = []
            
            for ticket in tickets:
                if ticket.get("status") in ["open", "in-progress"]:
                    daily_impact = ticket.get("revenue_impact", 0) / 30  # Monthly to daily
                    
                    if time_horizon == "7_days":
                        predicted_loss = daily_impact * 7
                    elif time_horizon == "30_days":
                        predicted_loss = daily_impact * 30
                    else:
                        predicted_loss = daily_impact * 1
                    
                    predictions.append({
                        "ticket_id": ticket.get("id"),
                        "current_impact": ticket.get("revenue_impact", 0),
                        "predicted_additional_loss": predicted_loss,
                        "urgency_multiplier": self._calculate_urgency_multiplier(ticket),
                        "recommendation": self._get_urgency_recommendation(ticket, predicted_loss)
                    })
            
            # Generate AI insights
            prediction_summary = await self._generate_prediction_insights(predictions, time_horizon)
            
            return {
                "predictions": predictions,
                "prediction_summary": prediction_summary,
                "time_horizon": time_horizon,
                "total_predicted_loss": sum(p["predicted_additional_loss"] for p in predictions),
                "highest_risk_tickets": sorted(predictions, key=lambda x: x["predicted_additional_loss"], reverse=True)[:3],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in impact prediction: {str(e)}")
            return {"error": str(e)}

    async def team_optimization_analysis(
        self,
        tickets: List[Dict[str, Any]],
        team_data: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Analyze team workload and suggest optimizations"""
        try:
            # Group tickets by assignee
            assignee_workload = {}
            unassigned_tickets = []
            
            for ticket in tickets:
                assignee = ticket.get("assignee", "Unassigned")
                if assignee == "Unassigned":
                    unassigned_tickets.append(ticket)
                else:
                    if assignee not in assignee_workload:
                        assignee_workload[assignee] = []
                    assignee_workload[assignee].append(ticket)
            
            # Calculate workload metrics
            workload_analysis = {}
            for assignee, assigned_tickets in assignee_workload.items():
                critical_count = len([t for t in assigned_tickets if t.get("severity") == "critical"])
                total_impact = sum(t.get("revenue_impact", 0) for t in assigned_tickets)
                
                workload_analysis[assignee] = {
                    "ticket_count": len(assigned_tickets),
                    "critical_tickets": critical_count,
                    "total_revenue_impact": total_impact,
                    "workload_score": len(assigned_tickets) + (critical_count * 2)  # Weight critical tickets
                }
            
            # Generate optimization recommendations
            optimization_prompt = f"""
            Team workload analysis:
            {json.dumps(workload_analysis, indent=2)}
            
            Unassigned tickets: {len(unassigned_tickets)}
            
            Provide team optimization recommendations for PM.
            """
            
            optimization_insights = await self.gemini_service.generate_response(
                message=optimization_prompt,
                analysis_type="team_optimization"
            )
            
            return {
                "workload_analysis": workload_analysis,
                "optimization_insights": optimization_insights,
                "unassigned_tickets": len(unassigned_tickets),
                "team_recommendations": self._generate_team_recommendations(workload_analysis),
                "bottlenecks": self._identify_bottlenecks(workload_analysis),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in team optimization: {str(e)}")
            return {"error": str(e)}

    async def _generate_comprehensive_insights(
        self,
        query: str,
        local_context: List[Dict],
        web_context: List[Dict],
        intent: str
    ) -> str:
        """Generate comprehensive insights using all available context"""
        
        # Prepare context summary
        local_summary = f"Local tickets found: {len(local_context)} relevant items"
        if local_context:
            high_impact = [t for t in local_context if t.get("metadata", {}).get("revenue_impact", 0) > 10000]
            local_summary += f", {len(high_impact)} with high revenue impact"
        
        web_summary = f"External insights: {len(web_context)} relevant sources"
        if web_context:
            avg_relevance = sum(w.get("pm_relevance_score", 0) for w in web_context) / len(web_context)
            web_summary += f", average relevance score: {avg_relevance:.2f}"
        
        comprehensive_prompt = f"""
        PM Analysis Request: {query}
        Intent: {intent}
        
        Local Context: {local_summary}
        External Context: {web_summary}
        
        Based on both internal tickets and external industry insights, provide:
        1. Key findings and patterns
        2. Business impact assessment  
        3. Risk analysis
        4. Strategic recommendations
        
        Focus on actionable insights for PM decision-making.
        """
        
        return await self.gemini_service.generate_response(
            message=comprehensive_prompt,
            context=local_context + web_context,
            analysis_type=intent
        )

    async def _generate_recommendations(
        self,
        local_results: List[Dict],
        web_results: List[Dict],
        intent: str,
        query: str
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Intent-specific recommendations
        if intent == "impact_analysis":
            if local_results:
                high_impact_tickets = [t for t in local_results if t.get("metadata", {}).get("revenue_impact", 0) > 5000]
                if high_impact_tickets:
                    recommendations.append(f"Prioritize {len(high_impact_tickets)} high-impact tickets immediately")
            
            recommendations.append("Establish revenue impact tracking for all critical incidents")
            recommendations.append("Implement automated alerting for tickets exceeding $10K impact")
        
        elif intent == "technical_solution":
            recommendations.append("Document solution patterns for faster future resolution")
            recommendations.append("Consider implementing automated testing for similar issues")
            recommendations.append("Create knowledge base articles for common fixes")
        
        elif intent == "priority_analysis":
            recommendations.append("Use RICE framework for systematic prioritization")
            recommendations.append("Review and update priority criteria quarterly")
            recommendations.append("Implement escalation paths for critical items")
        
        elif intent == "team_optimization":
            recommendations.append("Balance workload across team members")
            recommendations.append("Cross-train team on critical system components")
            recommendations.append("Implement pair programming for complex issues")
        
        # Add web-informed recommendations
        if web_results:
            recommendations.append("Consider industry best practices from external research")
            if any("benchmark" in w.get("content", "").lower() for w in web_results):
                recommendations.append("Compare current metrics against industry benchmarks")
        
        return recommendations

    def _calculate_pm_metrics(self, local_results: List[Dict], web_results: List[Dict]) -> Dict[str, Any]:
        """Calculate PM-relevant metrics"""
        metrics = {
            "knowledge_coverage": len(local_results) / 10,  # Assume 10 is good coverage
            "external_validation": len(web_results) > 0,
            "confidence_score": 0.7  # Base confidence
        }
        
        # Adjust confidence based on data quality
        if local_results:
            has_financial_data = any(r.get("metadata", {}).get("revenue_impact", 0) > 0 for r in local_results)
            if has_financial_data:
                metrics["confidence_score"] += 0.2
        
        if web_results:
            avg_relevance = sum(w.get("pm_relevance_score", 0) for w in web_results) / len(web_results)
            metrics["confidence_score"] += min(avg_relevance / 10, 0.1)  # Cap at 0.1 bonus
        
        return metrics

    def _identify_patterns(self, tickets: List[Dict]) -> List[str]:
        """Identify patterns in ticket data"""
        patterns = []
        
        # Severity patterns
        severities = [t.get("severity") for t in tickets]
        critical_ratio = severities.count("critical") / len(severities) if severities else 0
        if critical_ratio > 0.3:
            patterns.append(f"High critical ticket ratio: {critical_ratio:.1%}")
        
        # Component patterns
        components = []
        for ticket in tickets:
            ticket_components = ticket.get("components", [])
            components.extend(ticket_components)
        
        if components:
            from collections import Counter
            component_counts = Counter(components)
            most_common = component_counts.most_common(1)
            if most_common:
                patterns.append(f"Most affected component: {most_common[0][0]} ({most_common[0][1]} tickets)")
        
        return patterns

    def _calculate_urgency_multiplier(self, ticket: Dict) -> float:
        """Calculate urgency multiplier based on ticket properties"""
        multiplier = 1.0
        
        if ticket.get("severity") == "critical":
            multiplier *= 2.0
        elif ticket.get("severity") == "high":
            multiplier *= 1.5
        
        if ticket.get("affected_customers", 0) > 100:
            multiplier *= 1.3
        
        return multiplier

    def _get_urgency_recommendation(self, ticket: Dict, predicted_loss: float) -> str:
        """Get urgency recommendation based on predicted impact"""
        if predicted_loss > 50000:
            return "IMMEDIATE ACTION REQUIRED - Significant revenue at risk"
        elif predicted_loss > 10000:
            return "HIGH PRIORITY - Schedule resolution within 24h"
        elif predicted_loss > 1000:
            return "MEDIUM PRIORITY - Address within current sprint"
        else:
            return "LOW PRIORITY - Include in backlog planning"

    async def _generate_prediction_insights(self, predictions: List[Dict], time_horizon: str) -> str:
        """Generate AI insights about predictions"""
        total_predicted = sum(p["predicted_additional_loss"] for p in predictions)
        high_risk_count = len([p for p in predictions if p["predicted_additional_loss"] > 10000])
        
        prediction_prompt = f"""
        Impact prediction analysis for {time_horizon}:
        - Total predicted additional loss: ${total_predicted:,.2f}
        - High-risk tickets: {high_risk_count}
        - Total tickets analyzed: {len(predictions)}
        
        Provide PM insights on risk mitigation and resource allocation.
        """
        
        return await self.gemini_service.generate_response(
            message=prediction_prompt,
            analysis_type="impact_analysis"
        )

    def _generate_team_recommendations(self, workload_analysis: Dict) -> List[str]:
        """Generate team-specific recommendations"""
        recommendations = []
        
        if not workload_analysis:
            return ["No team data available for analysis"]
        
        # Find overloaded team members
        workloads = [(name, data["workload_score"]) for name, data in workload_analysis.items()]
        workloads.sort(key=lambda x: x[1], reverse=True)
        
        if len(workloads) > 1:
            highest_load = workloads[0][1]
            lowest_load = workloads[-1][1]
            
            if highest_load > lowest_load * 2:
                recommendations.append(f"Rebalance workload: {workloads[0][0]} has {highest_load} vs {workloads[-1][0]} with {lowest_load}")
        
        # Critical ticket distribution
        critical_distribution = {name: data["critical_tickets"] for name, data in workload_analysis.items()}
        max_critical = max(critical_distribution.values()) if critical_distribution else 0
        
        if max_critical > 3:
            overloaded_member = max(critical_distribution, key=critical_distribution.get)
            recommendations.append(f"Consider redistributing critical tickets from {overloaded_member}")
        
        return recommendations

    def _identify_bottlenecks(self, workload_analysis: Dict) -> List[str]:
        """Identify team bottlenecks"""
        bottlenecks = []
        
        if not workload_analysis:
            return bottlenecks
        
        for assignee, data in workload_analysis.items():
            if data["workload_score"] > 10:  # Arbitrary threshold
                bottlenecks.append({
                    "assignee": assignee,
                    "workload_score": data["workload_score"],
                    "type": "overload"
                })
        
        return bottlenecks

    async def close(self):
        """Cleanup all services"""
        await self.web_scraper.close()