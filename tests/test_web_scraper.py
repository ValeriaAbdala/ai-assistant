import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.web_scraper import GuidedWebScraper

async def test_web_scraper():
    print("Testing Guided Web Scraper...")
    
    scraper = GuidedWebScraper()
    
    # Mock local context (simulating RAG results)
    local_context = [
        {
            "content": "Ticket PROD-001: Checkout payment failure",
            "metadata": {"revenue_impact": 23500, "severity": "critical"}
        }
    ]
    
    # Test different PM intents
    test_cases = [
        {
            "query": "payment gateway issues",
            "intent": "impact_analysis",
            "urgency": "high"
        },
        {
            "query": "how to fix checkout errors", 
            "intent": "technical_solution",
            "urgency": "medium"
        },
        {
            "query": "which bugs to prioritize",
            "intent": "priority_analysis", 
            "urgency": "low"
        }
    ]
    
    for test in test_cases:
        print(f"\n--- Testing {test['intent']} ---")
        
        result = await scraper.scrape_with_guidance(
            query=test["query"],
            local_context=local_context,
            pm_intent=test["intent"],
            urgency=test["urgency"]
        )
        
        print(f"Query: {test['query']}")
        print(f"Intent: {test['intent']}")
        print(f"Knowledge gaps: {result.get('knowledge_gaps_identified', [])}")
        print(f"Queries used: {result.get('queries_used', [])}")
        print(f"Web results: {len(result.get('web_results', []))}")
        
        for i, web_result in enumerate(result.get('web_results', [])[:2]):
            print(f"  Result {i+1}: {web_result.get('content', '')[:100]}...")
    
    await scraper.close()
    print("\nWeb scraper test completed!")

if __name__ == "__main__":
    asyncio.run(test_web_scraper())