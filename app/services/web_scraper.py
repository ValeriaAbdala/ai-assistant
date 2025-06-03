import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class GuidedWebScraper:
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(hours=1)
        
        # PM-relevant sources by intent
        self.pm_sources = {
            "impact_analysis": [
                "business_intelligence_reports",
                "financial_analysis_sites",
                "industry_benchmarks"
            ],
            "technical_solution": [
                "stackoverflow.com",
                "github.com",
                "technical_documentation"
            ],
            "priority_analysis": [
                "pm_methodology_sites",
                "agile_frameworks",
                "priority_frameworks"
            ],
            "team_optimization": [
                "hr_resources",
                "management_blogs",
                "team_allocation_guides"
            ],
            "correlation_analysis": [
                "analytics_platforms",
                "industry_reports",
                "trend_analysis_sites"
            ]
        }

    async def scrape_with_guidance(
        self, 
        query: str, 
        local_context: List[Dict],
        pm_intent: str,
        urgency: str = "medium"
    ) -> Dict[str, Any]:
        """Main scraping method guided by PM context"""
        try:
            # 1. Analyze what information is missing
            knowledge_gaps = self._analyze_knowledge_gaps(local_context, pm_intent, query)
            
            # 2. Build targeted search queries
            targeted_queries = self._build_targeted_queries(query, knowledge_gaps, pm_intent)
            
            # 3. Select relevant sources
            relevant_sources = self._select_sources(pm_intent, urgency)
            
            # 4. Perform guided scraping (simulated)
            web_results = await self._intelligent_scrape(targeted_queries, relevant_sources)
            
            # 5. Filter and rank results
            filtered_results = self._filter_pm_relevant_content(web_results, pm_intent, query)
            
            return {
                "web_results": filtered_results,
                "knowledge_gaps_identified": knowledge_gaps,
                "sources_searched": relevant_sources,
                "queries_used": targeted_queries,
                "pm_intent": pm_intent,
                "scraping_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in guided web scraping: {str(e)}")
            return {
                "web_results": [],
                "error": str(e),
                "pm_intent": pm_intent
            }

    def _analyze_knowledge_gaps(self, local_context: List[Dict], pm_intent: str, query: str) -> List[str]:
        """Analyze what information is missing from local context"""
        gaps = []
        
        # Check for business metrics gaps
        has_financial_data = any(
            item.get("metadata", {}).get("revenue_impact", 0) > 0 
            for item in local_context
        )
        
        if pm_intent == "impact_analysis" and not has_financial_data:
            gaps.append("industry_benchmark_revenue_impact")
            gaps.append("competitor_incident_costs")
        
        # Check for solution gaps
        has_technical_solutions = any(
            "solution" in item.get("content", "").lower() or 
            "fix" in item.get("content", "").lower()
            for item in local_context
        )
        
        if pm_intent == "technical_solution" and not has_technical_solutions:
            gaps.append("implementation_best_practices")
            gaps.append("similar_case_solutions")
        
        # Check for priority frameworks
        if pm_intent == "priority_analysis":
            gaps.append("priority_frameworks")
            gaps.append("risk_assessment_methodologies")
        
        # Check for team best practices
        if pm_intent == "team_optimization":
            gaps.append("team_allocation_strategies")
            gaps.append("skill_matching_practices")
        
        # Check for industry patterns
        if pm_intent == "correlation_analysis":
            gaps.append("industry_incident_patterns")
            gaps.append("seasonal_trends")
        
        return gaps

    def _build_targeted_queries(self, original_query: str, gaps: List[str], pm_intent: str) -> List[str]:
        """Build specific search queries to fill knowledge gaps"""
        queries = []
        enhanced_query = original_query
        
        # Intent-specific query modifications
        if pm_intent == "impact_analysis":
            queries.extend([
                f"{enhanced_query} business impact cost analysis",
                f"{enhanced_query} revenue loss industry benchmark",
                f"{enhanced_query} customer satisfaction metrics"
            ])
        
        elif pm_intent == "technical_solution":
            queries.extend([
                f"{enhanced_query} solution implementation guide",
                f"{enhanced_query} best practices resolution",
                f"{enhanced_query} technical documentation fix"
            ])
        
        elif pm_intent == "priority_analysis":
            queries.extend([
                f"{enhanced_query} priority matrix framework",
                f"{enhanced_query} risk assessment methodology",
                f"{enhanced_query} business criticality evaluation"
            ])
        
        elif pm_intent == "team_optimization":
            queries.extend([
                f"{enhanced_query} team allocation strategy",
                f"{enhanced_query} resource optimization",
                f"{enhanced_query} skill matching assignment"
            ])
        
        elif pm_intent == "correlation_analysis":
            queries.extend([
                f"{enhanced_query} industry patterns trends",
                f"{enhanced_query} correlation analysis methodology",
                f"{enhanced_query} comparative benchmarking"
            ])
        
        # Add gap-specific queries
        for gap in gaps:
            if gap == "industry_benchmark_revenue_impact":
                queries.append(f"{enhanced_query} industry average cost impact")
            elif gap == "implementation_best_practices":
                queries.append(f"{enhanced_query} implementation best practices guide")
            elif gap == "priority_frameworks":
                queries.append(f"project management priority framework {enhanced_query}")
        
        return queries[:5]  # Limit to 5 most relevant queries

    def _select_sources(self, pm_intent: str, urgency: str) -> List[str]:
        """Select most relevant sources based on PM intent and urgency"""
        sources = self.pm_sources.get(pm_intent, ["general_pm_sources"])
        
        if urgency == "high":
            return sources[:2]  # Quick sources
        elif urgency == "medium":
            return sources[:4]  # Balanced
        else:
            return sources  # Comprehensive
    
    async def _intelligent_scrape(self, queries: List[str], sources: List[str]) -> List[Dict[str, Any]]:
        """Perform intelligent scraping with rate limiting and caching"""
        results = []
        
        # Simulate scraping results for each query
        for i, query in enumerate(queries[:3]):  # Limit to 3 queries
            for j, source in enumerate(sources[:2]):  # Limit to 2 sources per query
                try:
                    # Check cache first
                    cache_key = f"{query}_{source}"
                    if self._is_cached_valid(cache_key):
                        results.append(self.cache[cache_key])
                        continue
                    
                    # Simulate web scraping
                    mock_result = await self._simulate_scraping(query, source)
                    
                    # Cache result
                    cached_result = {
                        "content": mock_result,
                        "source": source,
                        "query": query,
                        "timestamp": datetime.utcnow(),
                        "relevance_score": 0.8 - (i * 0.1) - (j * 0.05)  # Decreasing relevance
                    }
                    
                    self.cache[cache_key] = cached_result
                    results.append(cached_result)
                    
                    # Simulate rate limiting
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error scraping {source} for {query}: {str(e)}")
                    continue
        
        return results

    async def _simulate_scraping(self, query: str, source: str) -> str:
        """Simulate web scraping results"""
        mock_results = {
            "payment": "Industry best practices for payment gateway implementations show that redundancy and proper error handling are critical for maintaining 99.9% uptime.",
            "security": "Security experts recommend immediate patching protocols with comprehensive testing for vulnerability management.",
            "priority": "PM methodology suggests using RICE framework for prioritization based on Reach, Impact, Confidence, and Effort metrics.",
            "team": "Resource optimization studies indicate that cross-functional team assignment with clear ownership improves delivery by 40%.",
            "business": "Industry benchmarks show that unresolved critical incidents typically affect 2-5% of monthly revenue when left unaddressed for over 48 hours."
        }
        
        # Find most relevant mock result
        query_lower = query.lower()
        for key, result in mock_results.items():
            if key in query_lower:
                return f"[{source}] {result}"
        
        return f"[{source}] External research suggests that {query} requires systematic analysis and stakeholder alignment for optimal PM outcomes."

    def _is_cached_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key].get("timestamp")
        if not cached_time:
            return False
        
        return datetime.utcnow() - cached_time < self.cache_duration

    def _filter_pm_relevant_content(self, results: List[Dict], pm_intent: str, query: str) -> List[Dict[str, Any]]:
        """Filter and rank results by PM relevance"""
        pm_keywords = {
            "impact_analysis": ["revenue", "business", "cost", "financial", "roi", "impact"],
            "technical_solution": ["implementation", "solution", "fix", "best practice", "guide"],
            "priority_analysis": ["priority", "framework", "methodology", "assessment"],
            "team_optimization": ["team", "resource", "allocation", "optimization"],
            "correlation_analysis": ["pattern", "trend", "analysis", "correlation"]
        }
        
        relevant_keywords = pm_keywords.get(pm_intent, [])
        
        for result in results:
            content = result.get("content", "").lower()
            
            # Calculate relevance score
            relevance_score = 0
            for keyword in relevant_keywords:
                if keyword in content:
                    relevance_score += 1
            
            # Query keyword match
            query_words = query.lower().split()
            for word in query_words:
                if word in content:
                    relevance_score += 0.5
            
            result["pm_relevance_score"] = relevance_score
        
        # Filter and sort by relevance
        filtered = [r for r in results if r.get("pm_relevance_score", 0) > 0]
        filtered.sort(key=lambda x: x.get("pm_relevance_score", 0), reverse=True)
        
        return filtered[:5]  # Return top 5 most relevant

    async def close(self):
        """Cleanup method"""
        pass

    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        logger.info("Web scraper cache cleared")