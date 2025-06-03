import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any, Optional
import json
import os
from pathlib import Path
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class LocalRAGService:
    def __init__(self):
        # Initialize ChromaDB (local persistent)
        self.chroma_client = chromadb.PersistentClient(path=settings.vector_db_path)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(settings.embeddings_model)
        
        # Collections
        self.tickets_collection = self.chroma_client.get_or_create_collection(
            name="tickets",
            metadata={"description": "PM ticket analysis collection"}
        )
        
        self.conversations_collection = self.chroma_client.get_or_create_collection(
            name="conversations", 
            metadata={"description": "Conversation history for context"}
        )
        
        logger.info(f"RAG Service initialized with model: {settings.embeddings_model}")
    
    async def add_tickets_to_rag(self, tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add tickets to RAG knowledge base"""
        try:
            documents = []
            metadatas = []
            ids = []
            
            for ticket in tickets:
                # Create comprehensive text representation
                text_content = self._create_ticket_text(ticket)
                documents.append(text_content)
                
                # Rich metadata for filtering and analysis
                metadata = {
                    "type": "ticket",
                    "ticket_id": ticket["id"],
                    "severity": ticket.get("severity", ""),
                    "priority": ticket.get("priority", ""),
                    "status": ticket.get("status", ""),
                    "assignee": ticket.get("assignee", ""),
                    "sprint": ticket.get("sprint", ""),
                    "revenue_impact": float(ticket.get("revenue_impact", 0)),
                    "affected_customers": int(ticket.get("affected_customers", 0)),
                    "business_impact": ticket.get("business_impact", ""),
                    "created_date": ticket.get("created_date", ""),
                    "ticket_type": ticket.get("type", "")
                }
                metadatas.append(metadata)
                ids.append(f"ticket_{ticket['id']}")
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(documents).tolist()
            
            # Add to ChromaDB
            self.tickets_collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Successfully added {len(tickets)} tickets to RAG")
            
            return {
                "status": "success",
                "tickets_added": len(tickets),
                "collection_total": self.tickets_collection.count()
            }
            
        except Exception as e:
            logger.error(f"Error adding tickets to RAG: {str(e)}")
            raise
    
    async def search_tickets(
        self, 
        query: str, 
        max_results: int = None,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Search tickets with semantic similarity"""
        try:
            max_results = max_results or settings.max_chunks_retrieval
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Build ChromaDB where clause for filtering
            where_clause = {}
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        where_clause[key] = value
            
            # Search in ChromaDB
            search_kwargs = {
                "query_embeddings": [query_embedding],
                "n_results": max_results,
                "include": ["documents", "metadatas", "distances"]
            }
            
            if where_clause:
                search_kwargs["where"] = where_clause
            
            results = self.tickets_collection.query(**search_kwargs)
            
            # Format results
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i],
                        "similarity": 1 - results["distances"][0][i],
                        "source": "local_tickets"
                    })
            
            logger.info(f"Found {len(formatted_results)} relevant tickets for query: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in ticket search: {str(e)}")
            return []
    
    async def search_by_business_impact(
        self, 
        query: str, 
        min_revenue_impact: float = 1000,
        min_customers: int = 10
    ) -> List[Dict[str, Any]]:
        """Search tickets with significant business impact"""
        filters = {
            "revenue_impact": {"$gte": min_revenue_impact},
            "affected_customers": {"$gte": min_customers}
        }
        
        return await self.search_tickets(query, filters=filters)
    
    async def search_critical_tickets(self, query: str) -> List[Dict[str, Any]]:
        """Search only critical/high severity tickets"""
        filters = {
            "severity": {"$in": ["critical", "high"]}
        }
        
        return await self.search_tickets(query, filters=filters)
    
    def _create_ticket_text(self, ticket: Dict[str, Any]) -> str:
        """Create comprehensive text representation of ticket"""
        text_parts = [
            f"Ticket ID: {ticket['id']}",
            f"Title: {ticket['title']}",
            f"Description: {ticket.get('description', '')}",
            f"Type: {ticket.get('type', '')} ticket",
            f"Severity: {ticket.get('severity', '')} priority",
            f"Current Status: {ticket.get('status', '')}",
            f"Assigned to: {ticket.get('assignee', 'Unassigned')}",
            f"Sprint: {ticket.get('sprint', 'No sprint')}",
            f"Revenue Impact: ${ticket.get('revenue_impact', 0):,.2f}",
            f"Customers Affected: {ticket.get('affected_customers', 0)} users",
            f"Business Impact: {ticket.get('business_impact', 'Not specified')}"
        ]
        
        # Add labels/tags if available
        if ticket.get('labels'):
            text_parts.append(f"Tags: {', '.join(ticket['labels'])}")
        
        # Add customer feedback if available
        if ticket.get('customer_feedback'):
            feedback_texts = []
            for feedback in ticket['customer_feedback']:
                if feedback.get('message'):
                    feedback_texts.append(feedback['message'])
            if feedback_texts:
                text_parts.append(f"Customer Feedback: {' '.join(feedback_texts)}")
        
        return "\n".join(text_parts)
    
    async def get_rag_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        try:
            tickets_count = self.tickets_collection.count()
            conversations_count = self.conversations_collection.count()
            
            return {
                "tickets_indexed": tickets_count,
                "conversations_stored": conversations_count,
                "embedding_model": settings.embeddings_model,
                "vector_db_path": settings.vector_db_path,
                "status": "healthy"
            }
        except Exception as e:
            logger.error(f"Error getting RAG stats: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def clear_collection(self, collection_name: str) -> bool:
        """Clear a specific collection (for testing)"""
        try:
            if collection_name == "tickets":
                self.chroma_client.delete_collection("tickets")
                self.tickets_collection = self.chroma_client.get_or_create_collection("tickets")
            elif collection_name == "conversations":
                self.chroma_client.delete_collection("conversations") 
                self.conversations_collection = self.chroma_client.get_or_create_collection("conversations")
            
            logger.info(f"Cleared collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection {collection_name}: {str(e)}")
            return False