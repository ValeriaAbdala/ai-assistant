import asyncio
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rag_service import LocalRAGService

async def test_rag():
    print("Testing RAG Service...")
    
    # Initialize RAG
    rag = LocalRAGService()
    
    # Load sample tickets
    try:
        with open('data/tickets/sample_tickets.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: sample_tickets.json not found")
        return
    
    # Add tickets to RAG
    print("Adding tickets to RAG...")
    result = await rag.add_tickets_to_rag(data['tickets'])
    print(f"Result: {result}")
    
    # Test search
    print("\nTesting search...")
    results = await rag.search_tickets("payment checkout critical issues")
    
    for i, result in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(f"Similarity: {result['similarity']:.3f}")
        print(f"Ticket: {result['metadata']['ticket_id']}")
        print(f"Revenue Impact: ${result['metadata']['revenue_impact']}")
        print(f"Customers: {result['metadata']['affected_customers']}")
    
    # Get stats
    stats = await rag.get_rag_stats()
    print(f"\nRAG Stats: {stats}")

if __name__ == "__main__":
    asyncio.run(test_rag())