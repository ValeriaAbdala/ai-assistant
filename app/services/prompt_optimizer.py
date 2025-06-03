import re
from typing import Dict, List, Tuple
from app.services.gemini_service import GeminiService
import logging

logger = logging.getLogger(__name__)

class PromptOptimizer:
    def __init__(self):
        self.gemini_service = GeminiService()
        
        # PM intent patterns
        self.intent_patterns = {
            "impact_analysis": [
                "impact", "revenue", "sales", "business", "cost", "loss", "financial",
                "customers affected", "business impact", "roi", "profit", "income"
            ],
            "technical_solution": [
                "how to fix", "solution", "resolve", "implement", "code", "technical",
                "bug fix", "implementation", "troubleshoot", "solve", "repair", "debug"
            ],
            "priority_analysis": [
                "priority", "urgent", "critical", "important", "prioritize",
                "order", "sequence", "first", "next", "rank", "which should"
            ],
            "team_optimization": [
                "team", "assign", "workload", "resource", "capacity", "developer",
                "allocation", "distribute", "who should", "staff", "personnel"
            ],
            "correlation_analysis": [
                "correlation", "relationship", "pattern", "trend", "compare",
                "related", "similar", "connection", "analyze", "overview"
            ]
        }
        
        # Common PM query improvements
        self.query_enhancements = {
            "tickets": "incidents and tickets",
            "bugs": "bugs and defects with business impact",
            "issues": "issues affecting operations and revenue",
            "problems": "problems impacting customers and sales",
            "critical": "critical severity items requiring immediate attention",
            "sales": "sales performance and revenue metrics",
            "customers": "customer satisfaction and affected users"
        }

    def auto_detect_analysis_type(self, query: str) -> str:
        """Auto-detect analysis type from user query"""
        query_lower = query.lower()
        
        # Priority scoring for each analysis type
        type_scores = {
            "impact_analysis": 0,
            "technical_solution": 0, 
            "priority_analysis": 0,
            "team_optimization": 0,
            "correlation_analysis": 0
        }
        
        # Impact analysis keywords (weighted higher)
        impact_keywords = [
            "revenue", "sales", "money", "cost", "financial", "business impact",
            "customers affected", "loss", "profit", "income", "earnings", "roi"
        ]
        
        # Technical solution keywords  
        technical_keywords = [
            "how to fix", "solution", "resolve", "implement", "bug", "error",
            "fix", "solve", "repair", "debug", "troubleshoot", "code"
        ]
        
        # Priority analysis keywords
        priority_keywords = [
            "priority", "urgent", "critical", "important", "first", "next",
            "order", "sequence", "prioritize", "rank", "which should"
        ]
        
        # Team optimization keywords
        team_keywords = [
            "team", "assign", "developer", "resource", "capacity", "workload",
            "allocation", "who should", "distribute", "staff", "personnel"
        ]
        
        # Correlation analysis keywords
        correlation_keywords = [
            "pattern", "trend", "relationship", "correlation", "compare",
            "similar", "related", "connection", "analyze", "overview", "what"
        ]
        
        # Score each type based on keyword presence
        for keyword in impact_keywords:
            if keyword in query_lower:
                type_scores["impact_analysis"] += 2
        
        for keyword in technical_keywords:
            if keyword in query_lower:
                type_scores["technical_solution"] += 2
                
        for keyword in priority_keywords:
            if keyword in query_lower:
                type_scores["priority_analysis"] += 2
                
        for keyword in team_keywords:
            if keyword in query_lower:
                type_scores["team_optimization"] += 2
                
        for keyword in correlation_keywords:
            if keyword in query_lower:
                type_scores["correlation_analysis"] += 1
        
        # Question pattern analysis (bonus points)
        if "what" in query_lower and ("affecting" in query_lower or "impact" in query_lower):
            type_scores["impact_analysis"] += 3
            
        if "how" in query_lower and ("fix" in query_lower or "solve" in query_lower):
            type_scores["technical_solution"] += 3
            
        if "which" in query_lower and ("priority" in query_lower or "first" in query_lower):
            type_scores["priority_analysis"] += 3
            
        if "who" in query_lower and ("should" in query_lower or "assign" in query_lower):
            type_scores["team_optimization"] += 3
            
        # Financial/business indicators
        if any(term in query_lower for term in ["$", "revenue", "sales", "cost", "business"]):
            type_scores["impact_analysis"] += 2
        
        # Return highest scoring type, default to correlation_analysis
        max_score = max(type_scores.values())
        if max_score == 0:
            return "correlation_analysis"  # Default for general queries
            
        return max(type_scores, key=type_scores.get)

    async def optimize_query(self, raw_query: str, context_type: str = "auto") -> Dict[str, str]:
        """Optimize and enhance user query for better RAG results"""
        try:
            # 1. Auto-detect intent if context_type is "auto"
            if context_type == "auto":
                detected_intent = self.auto_detect_analysis_type(raw_query)
            else:
                detected_intent = context_type
            
            # 2. Clean and enhance query
            enhanced_query = self._enhance_query(raw_query)
            
            # 3. Build context-specific prompt
            optimized_prompt = self._build_optimized_prompt(
                enhanced_query, 
                detected_intent, 
                context_type
            )
            
            # 4. Use Gemini to further refine if needed
            if self._needs_gemini_refinement(raw_query):
                refined_prompt = await self._gemini_refine_prompt(
                    optimized_prompt, 
                    detected_intent
                )
            else:
                refined_prompt = optimized_prompt
            
            return {
                "original_query": raw_query,
                "enhanced_query": enhanced_query,
                "optimized_prompt": refined_prompt,
                "detected_intent": detected_intent,
                "context_type": context_type,
                "auto_detected": context_type == "auto"
            }
            
        except Exception as e:
            logger.error(f"Error optimizing prompt: {str(e)}")
            # Fallback to enhanced query
            return {
                "original_query": raw_query,
                "enhanced_query": self._enhance_query(raw_query),
                "optimized_prompt": self._enhance_query(raw_query),
                "detected_intent": "general",
                "context_type": context_type,
                "auto_detected": True
            }

    def _enhance_query(self, query: str) -> str:
        """Enhance query with PM-specific terminology"""
        enhanced = query.lower()
        
        # Replace common terms with PM-specific ones
        for original, enhanced_term in self.query_enhancements.items():
            enhanced = re.sub(r'\b' + original + r'\b', enhanced_term, enhanced)
        
        # Add PM context keywords based on detected patterns
        pm_keywords = []
        if any(word in enhanced for word in ["revenue", "sales", "financial"]):
            pm_keywords.append("business impact analysis")
        if any(word in enhanced for word in ["critical", "urgent", "high"]):
            pm_keywords.append("priority assessment")
        if any(word in enhanced for word in ["team", "assign", "resource"]):
            pm_keywords.append("resource allocation")
        
        if pm_keywords:
            enhanced += " focusing on " + " and ".join(pm_keywords)
        
        return enhanced.strip()

    def _build_optimized_prompt(self, query: str, intent: str, context_type: str) -> str:
        """Build optimized prompt based on intent and context"""
        
        intent_contexts = {
            "impact_analysis": f"Analyze the business impact and revenue implications of {query}. Focus on customer satisfaction, financial effects, and business metrics. Provide quantifiable insights where possible.",
            
            "technical_solution": f"Provide technical analysis and actionable solution recommendations for {query}. Include implementation approaches, technical considerations, and best practices for resolution.",
            
            "priority_analysis": f"Evaluate {query} for business criticality, urgency, and impact severity. Provide clear prioritization recommendations with reasoning based on business value and risk assessment.",
            
            "team_optimization": f"Analyze {query} from team capacity, skill requirements, and workload distribution perspectives. Suggest optimal resource allocation and team assignment strategies.",
            
            "correlation_analysis": f"Identify patterns, relationships, and trends in {query}. Look for correlations between incidents, business metrics, and operational dependencies. Provide comprehensive overview with insights.",
            
            "general": f"Provide comprehensive PM analysis of {query} including business impact, technical considerations, and actionable recommendations for project management decisions."
        }
        
        return intent_contexts.get(intent, f"Analyze {query} from a project management perspective")

    def _needs_gemini_refinement(self, query: str) -> bool:
        """Determine if query needs Gemini-based refinement"""
        complexity_indicators = [
            len(query.split()) > 12,  # Very long queries
            query.count("?") > 1,  # Multiple questions
            any(word in query.lower() for word in ["complex", "detailed", "comprehensive", "analyze thoroughly"]),
            any(phrase in query.lower() for phrase in ["explain how", "walk me through", "break down"])
        ]
        
        return any(complexity_indicators)

    async def _gemini_refine_prompt(self, prompt: str, intent: str) -> str:
        """Use Gemini to refine complex prompts"""
        try:
            refinement_prompt = f"""
Refine this PM analysis prompt to be more specific and actionable:

Original prompt: {prompt}
Analysis intent: {intent}

Requirements:
1. Make it specific to PM/Scrum Master needs
2. Focus on actionable business insights
3. Include relevant metrics and KPIs
4. Keep concise but comprehensive
5. Emphasize practical recommendations

Refined prompt:"""
            
            response = await self.gemini_service.generate_response(
                message=refinement_prompt,
                analysis_type="general"
            )
            
            # Extract the refined prompt from response
            lines = response.strip().split('\n')
            for line in lines:
                if line.strip() and not line.startswith('Refined prompt:'):
                    return line.strip()
            
            return prompt  # Fallback to original
            
        except Exception as e:
            logger.error(f"Error in Gemini refinement: {str(e)}")
            return prompt

    async def get_search_keywords(self, query: str) -> List[str]:
        """Extract key search terms for RAG"""
        try:
            optimization = await self.optimize_query(query)
            enhanced_query = optimization["enhanced_query"]
            
            # Extract keywords
            keywords = []
            words = enhanced_query.split()
            
            # Remove common stop words but keep PM-specific terms
            pm_stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
            pm_important_words = {"critical", "high", "urgent", "revenue", "impact", "customers", "business", "priority"}
            
            for word in words:
                if word.lower() not in pm_stop_words or word.lower() in pm_important_words:
                    keywords.append(word)
            
            return keywords[:10]  # Limit to 10 most important keywords
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return query.split()[:5]  # Fallback to first 5 words