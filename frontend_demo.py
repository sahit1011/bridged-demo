"""
Enhanced Flask Frontend Demo for Bridged Media Assignment
Tests the Natural Language to Pinecone Query Agent with real Pinecone integration
"""

from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import requests
import json
import asyncio
from datetime import datetime
from src.utils.enhanced_search import EnhancedSearchEngine
from src.agents.custom_agent import CustomAgent
from src.models.schemas import QueryRequest

app = Flask(__name__)

# FastAPI backend URL
BACKEND_URL = "http://localhost:8000"

# Initialize search components
search_engine = EnhancedSearchEngine(use_mock=False)  # Use real Pinecone
custom_agent = CustomAgent()

# Connect to Pinecone on startup
def initialize_pinecone():
    """Initialize Pinecone connection."""
    try:
        search_engine.connect()  # This is a sync method, not async
        print("✅ Connected to Pinecone successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Pinecone: {e}")
        return False

# Initialize on startup
pinecone_connected = initialize_pinecone()

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bridged Demo - NL to Pinecone Query</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        textarea, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        textarea {
            height: 80px;
            resize: vertical;
        }
        .form-row {
            display: flex;
            gap: 20px;
        }
        .form-row .form-group {
            flex: 1;
        }
        button {
            background: #007bff;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
        }
        button:hover {
            background: #0056b3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .result-section {
            margin-top: 30px;
        }
        .result-card {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .result-card h3 {
            margin-top: 0;
            color: #495057;
        }
        pre {
            background: #2d3748;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 14px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .info-item {
            background: white;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }
        .info-label {
            font-weight: bold;
            color: #555;
        }
        .info-value {
            color: #333;
        }
        .search-result {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 10px;
        }
        .search-result h4 {
            margin: 0 0 10px 0;
            color: #495057;
        }
        .search-meta {
            font-size: 14px;
            color: #6c757d;
            margin-bottom: 5px;
        }
        .search-score {
            background: #e3f2fd;
            color: #1976d2;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #f5c6cb;
        }
        .examples {
            margin-top: 20px;
        }
        .example-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .example-card {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .example-card:hover {
            border-color: #007bff;
            transform: translateY(-2px);
        }
        .example-card h4 {
            margin: 0 0 10px 0;
            color: #495057;
        }
        .example-card p {
            margin: 0;
            color: #6c757d;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 Bridged Demo</h1>
        <p class="subtitle">Natural Language to Pinecone Query Agent</p>
        
        <form method="POST" action="/">
            <div class="form-group">
                <label for="query">Natural Language Query:</label>
                <textarea name="query" id="query" placeholder="e.g., Find articles by John Smith from last year about machine learning" required>{{ request.form.get('query', '') }}</textarea>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="agent_type">Agent Type:</label>
                    <select name="agent_type" id="agent_type">
                        <option value="auto" {{ 'selected' if request.form.get('agent_type') == 'auto' else '' }}>Auto (Best Result)</option>
                        <option value="custom" {{ 'selected' if request.form.get('agent_type') == 'custom' else '' }}>Custom Agent</option>
                        <option value="langchain" {{ 'selected' if request.form.get('agent_type') == 'langchain' else '' }}>LangChain Agent</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="date_schema">Date Schema:</label>
                    <select name="date_schema" id="date_schema">
                        <option value="unified" {{ 'selected' if request.form.get('date_schema') == 'unified' else '' }}>Unified Date</option>
                        <option value="separate" {{ 'selected' if request.form.get('date_schema') == 'separate' else '' }}>Separate Date Fields</option>
                    </select>
                </div>
            </div>
            
            <button type="submit">🚀 Generate Query & Search Results</button>
        </form>
        
        <div class="examples">
            <h3>💡 Example Queries (Click to use):</h3>
            <div class="example-grid">
                <div class="example-card" onclick="fillQuery('Find articles about IPL 2025')">
                    <h4>IPL Content Search</h4>
                    <p>"Find articles about IPL 2025"</p>
                </div>
                <div class="example-card" onclick="fillQuery('Show me posts about Mumbai Indians')">
                    <h4>Team-specific Search</h4>
                    <p>"Show me posts about Mumbai Indians"</p>
                </div>
                <div class="example-card" onclick="fillQuery('Articles by Jane Doe about cricket')">
                    <h4>Author & Topic Search</h4>
                    <p>"Articles by Jane Doe about cricket"</p>
                </div>
                <div class="example-card" onclick="fillQuery('Posts about Vaibhav Suryavanshi from 2025')">
                    <h4>Player & Date Search</h4>
                    <p>"Posts about Vaibhav Suryavanshi from 2025"</p>
                </div>
            </div>
        </div>
    </div>

    {% if result %}
    <div class="container result-section">
        <h2>📊 Query Analysis & Results</h2>
        
        <div class="result-card">
            <h3>🔍 Generated Pinecone Query</h3>
            <pre>{{ result.filter | tojson(indent=2) }}</pre>
        </div>

        <div class="result-card">
            <h3>🏷️ Extracted Metadata Filters</h3>
            <pre>{{ result.metadata_filters | tojson(indent=2) }}</pre>
        </div>

        <div class="result-card">
            <h3>🤖 Agent Information</h3>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Agent Used:</div>
                    <div class="info-value">{{ result.agent_used }}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Confidence Score:</div>
                    <div class="info-value">{{ "%.1f" | format(result.confidence * 100) }}%</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Processing Time:</div>
                    <div class="info-value">{{ "%.3f" | format(result.processing_time) }}s</div>
                </div>
            </div>
        </div>

        <div class="result-card">
            <h3>📚 Pinecone Search Results</h3>
            {% if result.search_results and result.search_results.matches %}
                {% for match in result.search_results.matches %}
                <div class="search-result">
                    <h4>{{ match.metadata.title or 'Untitled' }}</h4>
                    <div class="search-meta">
                        <strong>Author:</strong> {{ match.metadata.author or 'Unknown' }} | 
                        <strong>Published:</strong> {{ match.metadata.publishedDate or match.metadata.published_date or 'Unknown' }} |
                        <strong>Domain:</strong> {{ match.metadata.url_domain or 'Unknown' }}
                        <span class="search-score">Score: {{ "%.1f" | format(match.score * 100) }}%</span>
                    </div>
                    <div class="search-meta">
                        <strong>Tags:</strong> {{ match.metadata.tags | join(', ') if match.metadata.tags is iterable and match.metadata.tags is not string else (match.metadata.tags or 'None') }}
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p>No search results found</p>
            {% endif %}
        </div>
    </div>
    {% endif %}

    {% if error %}
    <div class="container">
        <div class="error">
            <h3>❌ Error</h3>
            <p>{{ error }}</p>
        </div>
    </div>
    {% endif %}

    <script>
        function fillQuery(query) {
            document.getElementById('query').value = query;
            document.getElementById('query').focus();
        }
    </script>
</body>
</html>
"""


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template_string(HTML_TEMPLATE)

    # Handle POST request
    query = request.form.get('query', '').strip()
    agent_type = request.form.get('agent_type', 'auto')
    date_schema = request.form.get('date_schema', 'unified')

    if not query:
        return render_template_string(HTML_TEMPLATE, error="Please enter a query")

    try:
        # Step 1: Parse natural language query using custom agent
        print(f"🔍 Processing query: {query}")
        req = QueryRequest(query=query, agent_type=agent_type, date_format=date_schema)

        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Parse query to get filter
            query_result = loop.run_until_complete(custom_agent.process_query(req))

            # Step 2: Search Pinecone with real data
            print(f"🔍 Searching Pinecone with filter: {query_result.filter}")
            if pinecone_connected:
                search_results = loop.run_until_complete(search_engine.search(query, top_k=5))
            else:
                # Fallback to empty results if Pinecone not connected
                search_results = {"matches": [], "total_count": 0}
                print("⚠️ Pinecone not connected, showing query parsing results only")

        finally:
            loop.close()

        # Step 3: Extract metadata filters for display
        metadata_filters = extract_metadata_filters(query_result.filter)

        # Prepare result data
        result = {
            'filter': query_result.filter,
            'metadata_filters': metadata_filters,
            'agent_used': query_result.agent_used,
            'confidence': query_result.confidence,
            'processing_time': query_result.processing_time,
            'search_results': search_results
        }

        print(f"✅ Found {len(search_results.get('matches', []))} results")
        return render_template_string(HTML_TEMPLATE, result=result)

    except Exception as e:
        print(f"❌ Error: {e}")
        return render_template_string(HTML_TEMPLATE, error=f"An error occurred: {str(e)}")


def extract_metadata_filters(filter_dict):
    """Extract metadata filters from the generated query filter."""
    metadata = {}

    # Handle nested $and filters
    if '$and' in filter_dict:
        for condition in filter_dict['$and']:
            metadata.update(extract_metadata_filters(condition))
        return metadata

    if 'author' in filter_dict:
        metadata['author'] = filter_dict['author']

    if 'tags' in filter_dict:
        metadata['tags'] = filter_dict['tags']

    # Handle various date field formats
    date_fields = ['publishedDate', 'published_date', 'publishedTimestamp', 'publishedYear', 'publishedMonth']
    for field in date_fields:
        if field in filter_dict:
            metadata['date_filters'] = {field: filter_dict[field]}
            break

    return metadata


# Mock search results function removed - now using real Pinecone search


@app.route('/health')
def health():
    """Health check endpoint."""
    try:
        # Check if backend is accessible
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        backend_status = "healthy" if response.ok else "unhealthy"
    except:
        backend_status = "unreachable"

    # Check Pinecone connectivity
    try:
        pinecone_status = "healthy" if search_engine else "not_initialized"
    except:
        pinecone_status = "error"

    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "backend_status": backend_status,
        "pinecone_status": pinecone_status,
        "components": {
            "custom_agent": "initialized" if custom_agent else "not_initialized",
            "search_engine": "initialized" if search_engine else "not_initialized"
        }
    })


if __name__ == '__main__':
    print("🚀 Starting Enhanced Flask Frontend with Real Pinecone Integration...")
    print("📍 Frontend will be available at: http://localhost:5000")
    print("🔗 FastAPI backend (optional): http://localhost:8000")
    print("🗄️ Using real Pinecone index: bridged-demo-articles")
    print("🤖 Custom agent with fallback extraction enabled")
    print("=" * 70)

    app.run(debug=True, host='0.0.0.0', port=5000)
