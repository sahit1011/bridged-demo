"""
Simple FastAPI for Bridged Media Assignment
Natural Language to Pinecone Query Agent
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import json

from .agent import SimpleNLAgent
from .pinecone_client import SimplePineconeClient

# Initialize FastAPI app
app = FastAPI(
    title="Bridged Demo - NL to Pinecone Query Agent",
    description="Convert natural language queries into Pinecone-compatible JSON filters",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
agent = SimpleNLAgent()
pinecone_client = SimplePineconeClient()

# Connect to Pinecone on startup
@app.on_event("startup")
async def startup_event():
    """Initialize Pinecone connection on startup."""
    success = pinecone_client.connect()
    if success:
        print("✅ Pinecone connected successfully")
    else:
        print("⚠️ Pinecone connection failed - API will still work for filter generation")

# Request/Response models
class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class QueryResponse(BaseModel):
    query: str
    filter: Dict[str, Any]
    search_results: Optional[Dict[str, Any]] = None
    success: bool = True
    error: Optional[str] = None

class FilterOnlyRequest(BaseModel):
    query: str

class FilterOnlyResponse(BaseModel):
    filter: Dict[str, Any]
    success: bool = True
    error: Optional[str] = None

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Bridged Demo - Natural Language to Pinecone Query Agent",
        "version": "1.0.0",
        "endpoints": {
            "generate_filter": "/filter",
            "query_and_search": "/query",
            "health": "/health",
            "docs": "/docs"
        },
        "assignment": "Convert natural language to Pinecone query filters"
    }

@app.post("/filter", response_model=FilterOnlyResponse)
async def generate_filter(request: FilterOnlyRequest):
    """
    Generate Pinecone filter from natural language query.
    This is the core functionality required by the assignment.
    
    Returns only the JSON filter as specified in the assignment examples.
    """
    try:
        # Generate filter using the agent
        filter_dict = agent.generate_pinecone_filter(request.query)
        
        return FilterOnlyResponse(
            filter=filter_dict,
            success=True
        )
        
    except Exception as e:
        return FilterOnlyResponse(
            filter={},
            success=False,
            error=str(e)
        )

@app.post("/query", response_model=QueryResponse)
async def query_and_search(request: QueryRequest):
    """
    Generate filter AND perform Pinecone search.
    This demonstrates the complete pipeline.
    """
    try:
        # Step 1: Generate filter
        filter_dict = agent.generate_pinecone_filter(request.query)
        
        # Step 2: Search Pinecone (if connected)
        search_results = None
        if pinecone_client.index:
            search_results = pinecone_client.search(
                query=request.query,
                filter_dict=filter_dict,
                top_k=request.top_k
            )
        
        return QueryResponse(
            query=request.query,
            filter=filter_dict,
            search_results=search_results,
            success=True
        )
        
    except Exception as e:
        return QueryResponse(
            query=request.query,
            filter={},
            search_results=None,
            success=False,
            error=str(e)
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    pinecone_status = "connected" if pinecone_client.index else "disconnected"
    
    return {
        "status": "healthy",
        "agent": "initialized",
        "pinecone": pinecone_status,
        "model": agent.model
    }

@app.get("/test")
async def test_assignment_examples():
    """
    Test the agent with the exact examples from the assignment.
    This endpoint demonstrates that the system works as required.
    """
    test_queries = [
        "Show me articles by Alice Zhang from last year about machine learning.",
        "Find posts tagged with 'LLMs' published in June, 2023.",
        "Anything by John Doe on vector search?"
    ]
    
    results = []
    
    for query in test_queries:
        try:
            filter_dict = agent.generate_pinecone_filter(query)
            results.append({
                "query": query,
                "filter": filter_dict,
                "success": True
            })
        except Exception as e:
            results.append({
                "query": query,
                "filter": {},
                "success": False,
                "error": str(e)
            })
    
    return {
        "assignment_examples": results,
        "note": "These are the exact examples from the Bridged Media assignment"
    }

@app.get("/schema")
async def get_schema_info():
    """Get information about the supported metadata schema."""
    return {
        "supported_fields": {
            "author": {
                "type": "string",
                "description": "Author name (exact match)",
                "example": "Alice Zhang"
            },
            "published_date": {
                "type": "string",
                "format": "YYYY-MM-DD",
                "description": "Publication date with MongoDB operators",
                "operators": ["$gte", "$lt", "$eq"],
                "example": {"$gte": "2024-01-01", "$lt": "2025-01-01"}
            },
            "tags": {
                "type": "array",
                "description": "Topic tags with $in operator",
                "example": {"$in": ["machine learning", "AI"]}
            }
        },
        "alternative_date_fields": {
            "published_year": "integer",
            "published_month": "integer", 
            "published_day": "integer"
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Simple Bridged Demo API...")
    print("📍 API will be available at: http://localhost:8000")
    print("📖 Documentation at: http://localhost:8000/docs")
    print("🧪 Test examples at: http://localhost:8000/test")
    print("=" * 50)
    
    uvicorn.run(
        "simple_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
