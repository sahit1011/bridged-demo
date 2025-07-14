#!/usr/bin/env python3
"""
FastAPI version of the Natural Language to Pinecone Query Agent
Modern, high-performance API with automatic documentation
Enhanced with comprehensive debugging and logging
"""

from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import os
import logging
import time
from datetime import datetime
from simple_agent import SimpleNLAgent
from simple_pinecone import SimplePineconeClient

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def log_separator(title: str, char: str = "=", width: int = 80):
    """Create a visual separator for console output"""
    separator = char * width
    title_line = f" {title} ".center(width, char)
    print(f"\n{separator}")
    print(title_line)
    print(separator)

# Initialize FastAPI app
app = FastAPI(
    title="Natural Language to Pinecone Query Agent",
    description="Convert natural language queries into Pinecone database filters",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize components
agent = SimpleNLAgent()
client = SimplePineconeClient()

# Connect to Pinecone on startup
@app.on_event("startup")
async def startup_event():
    """Initialize Pinecone connection on app startup"""
    if not client.connect():
        raise RuntimeError("Failed to connect to Pinecone database")
    print("✅ Connected to Pinecone database")

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class QueryResponse(BaseModel):
    query: str
    filter: Dict[str, Any]
    search_results: Dict[str, Any]
    processing_time: float

class HealthResponse(BaseModel):
    status: str
    pinecone_connected: bool
    agent_ready: bool

# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    return HTML_TEMPLATE

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    return HealthResponse(
        status="healthy",
        pinecone_connected=client.index is not None,
        agent_ready=True
    )

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process natural language query and return Pinecone filter + results
    Enhanced with comprehensive debugging and performance metrics

    - **query**: Natural language query string
    - **top_k**: Number of results to return (default: 5)
    """
    start_time = time.time()
    request_id = f"req_{int(time.time() * 1000)}"

    try:
        # Validate input
        if not request.query.strip():
            logger.error(f"[{request_id}] Empty query received")
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        log_separator(f"API QUERY PROCESSING - {request_id}", "=", 80)
        print(f"🔍 Query: '{request.query}'")
        print(f"📊 Top K: {request.top_k}")
        print(f"🕐 Started: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        logger.info(f"[{request_id}] Processing query: '{request.query}' (top_k={request.top_k})")

        # Step 1: Generate filter with timing
        filter_start = time.time()
        log_separator("STEP 1: LLM FILTER GENERATION", "-", 60)

        filter_dict = agent.generate_pinecone_filter(request.query)
        filter_time = time.time() - filter_start

        print(f"🎯 Generated Pinecone Filter (took {filter_time:.3f}s):")
        print(json.dumps(filter_dict, indent=2, ensure_ascii=False))
        logger.info(f"[{request_id}] Filter generated in {filter_time:.3f}s: {filter_dict}")

        # Step 2: Execute search with timing
        search_start = time.time()
        log_separator("STEP 2: PINECONE SEARCH EXECUTION", "-", 60)

        search_results = client.search(request.query, filter_dict, top_k=request.top_k)
        search_time = time.time() - search_start

        print(f"🔍 Pinecone search completed in {search_time:.3f}s")
        logger.info(f"[{request_id}] Pinecone search completed in {search_time:.3f}s")

        # Step 3: Process and display results
        log_separator("STEP 3: SEARCH RESULTS ANALYSIS", "-", 60)

        matches = search_results.get('matches', [])
        print(f"📊 Total Results Found: {len(matches)}")

        if matches:
            print(f"📈 Score Range: {matches[0].get('score', 0):.4f} → {matches[-1].get('score', 0):.4f}")

            # Display detailed results
            for i, match in enumerate(matches, 1):
                metadata = match.get('metadata', {})
                print(f"\n📄 Result #{i}:")
                print(f"   🆔 ID: {match.get('id', 'Unknown')}")
                print(f"   📊 Score: {match.get('score', 0):.4f}")
                print(f"   👤 Author: {metadata.get('author', 'Unknown')}")
                print(f"   🏷️ Tags: {metadata.get('tags', 'None')}")
                print(f"   📅 Published: {metadata.get('publishedDate', 'Unknown')}")
                print(f"   🕐 Timestamp: {metadata.get('publishedTimestamp', 'Unknown')}")
                print(f"   🌐 Domain: {metadata.get('url_domain', 'Unknown')}")
                print(f"   📏 Title Length: {metadata.get('title_length', 'Unknown')}")
                print(f"   🏷️ Tag Count: {metadata.get('tag_count', 'Unknown')}")
                print(f"   📝 Record Type: {metadata.get('record_type', 'Unknown')}")
                print(f"   📅 Indexed At: {metadata.get('indexed_at', 'Unknown')}")

                # Log each result for debugging
                logger.info(f"[{request_id}] Result {i}: ID={match.get('id')}, Score={match.get('score', 0):.4f}, Author={metadata.get('author')}")
        else:
            print("❌ No results found matching the criteria")
            logger.warning(f"[{request_id}] No results found for query")

        # Step 4: Performance summary
        total_time = time.time() - start_time
        log_separator("PERFORMANCE SUMMARY", "-", 60)
        print(f"⏱️ Filter Generation: {filter_time:.3f}s ({filter_time/total_time*100:.1f}%)")
        print(f"⏱️ Pinecone Search: {search_time:.3f}s ({search_time/total_time*100:.1f}%)")
        print(f"⏱️ Total Processing: {total_time:.3f}s")
        print(f"🕐 Completed: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

        logger.info(f"[{request_id}] Query completed successfully in {total_time:.3f}s (filter: {filter_time:.3f}s, search: {search_time:.3f}s)")
        log_separator("END OF PROCESSING", "=", 80)

        return QueryResponse(
            query=request.query,
            filter=filter_dict,
            search_results=search_results,
            processing_time=total_time
        )

    except Exception as e:
        error_time = time.time() - start_time
        logger.error(f"[{request_id}] Error after {error_time:.3f}s: {str(e)}")
        print(f"❌ Error processing query after {error_time:.3f}s: {e}")
        log_separator("ERROR END", "=", 80)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/query", response_class=HTMLResponse)
async def web_query(query: str = Form(...)):
    """Web form endpoint for browser interface with enhanced logging"""
    start_time = time.time()
    request_id = f"web_{int(time.time() * 1000)}"

    try:
        log_separator(f"WEB QUERY PROCESSING - {request_id}", "=", 80)
        print(f"🌐 Web Query: '{query}'")
        print(f"🕐 Started: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        logger.info(f"[{request_id}] Web query received: '{query}'")

        # Step 1: Generate filter
        filter_start = time.time()
        filter_dict = agent.generate_pinecone_filter(query)
        filter_time = time.time() - filter_start

        print(f"🎯 Filter generated in {filter_time:.3f}s:")
        print(json.dumps(filter_dict, indent=2, ensure_ascii=False))

        # Step 2: Execute search
        search_start = time.time()
        search_results = client.search(query, filter_dict, top_k=5)
        search_time = time.time() - search_start

        # Log results for web query
        matches = search_results.get('matches', [])
        total_time = time.time() - start_time

        print(f"🔎 Web Query Results: {len(matches)} found in {search_time:.3f}s")
        print(f"⏱️ Total web processing time: {total_time:.3f}s")

        logger.info(f"[{request_id}] Web query completed: {len(matches)} results in {total_time:.3f}s")
        log_separator("WEB QUERY END", "=", 80)

        # Format for display
        result = {
            'query': query,
            'filter': filter_dict,
            'filter_json': json.dumps(filter_dict, indent=2, ensure_ascii=False),
            'search_results': search_results,
            'processing_time': total_time,
            'request_id': request_id
        }

        return render_result_template(result)

    except Exception as e:
        error_time = time.time() - start_time
        logger.error(f"[{request_id}] Web query error after {error_time:.3f}s: {str(e)}")
        print(f"❌ Web Query Error after {error_time:.3f}s: {e}")
        log_separator("WEB ERROR END", "=", 80)
        return f"<h1>Error</h1><p>{str(e)}</p><p>Processing time: {error_time:.3f}s</p>"

# HTML Templates
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Natural Language to Pinecone Query Agent</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .query-form { background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .query-input { width: 70%; padding: 10px; font-size: 16px; border: 1px solid #ddd; border-radius: 5px; }
        .query-button { padding: 10px 20px; font-size: 16px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .result-card { background: white; border: 1px solid #ddd; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
        pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
        .api-docs { background: #e7f3ff; padding: 15px; border-radius: 5px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Natural Language to Pinecone Query Agent</h1>
        <p>Convert natural language queries into precise Pinecone database filters</p>
        <p><strong>FastAPI Version</strong> - Modern, high-performance API with automatic documentation</p>
    </div>
    
    <div class="query-form">
        <h2>🔍 Query Interface</h2>
        <form method="post" action="/query">
            <input type="text" name="query" class="query-input" placeholder="Enter your natural language query..." required>
            <button type="submit" class="query-button">🚀 Process Query</button>
        </form>
    </div>
    
    <div class="api-docs">
        <h3>📚 API Documentation</h3>
        <p><strong>Interactive API Docs:</strong> <a href="/docs" target="_blank">/docs</a> (Swagger UI)</p>
        <p><strong>Alternative Docs:</strong> <a href="/redoc" target="_blank">/redoc</a> (ReDoc)</p>
        <p><strong>Health Check:</strong> <a href="/health" target="_blank">/health</a></p>
        
        <h4>🔗 API Endpoints:</h4>
        <ul>
            <li><code>POST /api/query</code> - Process natural language query (JSON API)</li>
            <li><code>GET /health</code> - System health check</li>
            <li><code>GET /docs</code> - Interactive API documentation</li>
        </ul>
        
        <h4>📝 Example API Usage:</h4>
        <pre>
curl -X POST "http://localhost:8000/api/query" \\
     -H "Content-Type: application/json" \\
     -d '{"query": "posts about Rohit Sharma", "top_k": 5}'
        </pre>
    </div>
    
    <div class="result-card">
        <h3>💡 Example Queries to Try:</h3>
        <ul>
            <li>"posts about Rohit Sharma"</li>
            <li>"articles by Jane Doe about cricket"</li>
            <li>"posts about Rohit Sharma and Shubman Gill"</li>
            <li>"Mumbai Indians posts"</li>
            <li>"articles from 2025"</li>
            <li>"posts not by Jane Doe"</li>
        </ul>
    </div>
</body>
</html>
"""

def render_result_template(result):
    """Render results template"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Query Results</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
            .result-card {{ background: white; border: 1px solid #ddd; border-radius: 10px; padding: 20px; margin-bottom: 20px; }}
            pre {{ background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }}
            .back-button {{ padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎯 Query Results</h1>
            <p>Query: "{result['query']}"</p>
        </div>
        
        <div class="result-card">
            <h3>🎯 Generated Pinecone Filter</h3>
            <pre>{result['filter_json']}</pre>
        </div>
        
        <div class="result-card">
            <h3>🔎 Search Results ({len(result['search_results'].get('matches', []))} found)</h3>
            {render_search_results(result['search_results'])}
        </div>
        
        <a href="/" class="back-button">← Back to Query Interface</a>
    </body>
    </html>
    """

def render_search_results(search_results):
    """Render search results HTML"""
    matches = search_results.get('matches', [])
    if not matches:
        return "<p>No results found.</p>"
    
    html = "<ul>"
    for i, match in enumerate(matches, 1):
        metadata = match.get('metadata', {})
        html += f"""
        <li>
            <strong>Result {i}</strong><br>
            Author: {metadata.get('author', 'Unknown')}<br>
            Tags: {metadata.get('tags', 'None')}<br>
            Score: {match.get('score', 0):.3f}
        </li>
        """
    html += "</ul>"
    return html

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
