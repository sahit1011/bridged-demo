"""
Simple Flask Frontend for Bridged Media Assignment
Demonstrates the Natural Language to Pinecone Query Agent
"""

from flask import Flask, render_template_string, request, jsonify
import requests
import json
from simple_agent import SimpleNLAgent
from simple_pinecone import SimplePineconeClient

app = Flask(__name__)

# Initialize components
agent = SimpleNLAgent()
pinecone_client = SimplePineconeClient()

# Connect to Pinecone on startup
pinecone_connected = pinecone_client.connect()

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bridged Demo - NL to Pinecone Query Agent</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 30px;
            font-style: italic;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #34495e;
        }
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
            resize: vertical;
            min-height: 80px;
        }
        textarea:focus {
            border-color: #3498db;
            outline: none;
        }
        button {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
        }
        .examples {
            margin-top: 20px;
        }
        .example-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .example-card {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .example-card:hover {
            border-color: #3498db;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(52, 152, 219, 0.2);
        }
        .example-card h4 {
            margin: 0 0 8px 0;
            color: #2c3e50;
        }
        .example-card p {
            margin: 0;
            color: #7f8c8d;
            font-style: italic;
        }
        .result-section {
            margin-top: 30px;
        }
        .result-card {
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 0 8px 8px 0;
        }
        .result-card h3 {
            margin-top: 0;
            color: #2c3e50;
        }
        pre {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 14px;
            line-height: 1.4;
        }
        .search-result {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            transition: all 0.3s;
        }
        .search-result:hover {
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .search-result h4 {
            margin: 0 0 10px 0;
            color: #2c3e50;
        }
        .search-meta {
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 5px;
        }
        .search-score {
            background: #e3f2fd;
            color: #1976d2;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            float: right;
        }
        .status {
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.warning {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 Bridged Demo</h1>
        <p class="subtitle">Natural Language to Pinecone Query Agent</p>
        
        {% if pinecone_status %}
        <div class="status {{ 'success' if pinecone_status == 'connected' else 'warning' }}">
            📡 Pinecone Status: {{ pinecone_status.title() }}
            {% if pinecone_status == 'connected' %}
                - Full search functionality available
            {% else %}
                - Filter generation only (search disabled)
            {% endif %}
        </div>
        {% endif %}
        
        <form method="POST" action="/">
            <div class="form-group">
                <label for="query">🔍 Enter your natural language query:</label>
                <textarea name="query" id="query" 
                         placeholder="e.g., Show me articles by Alice Zhang from last year about machine learning" 
                         required>{{ request.form.get('query', '') }}</textarea>
            </div>
            
            <button type="submit">🚀 Generate Filter & Search</button>
        </form>
        
        <div class="examples">
            <h3>💡 Try these assignment examples:</h3>
            <div class="example-grid">
                <div class="example-card" onclick="fillQuery('Show me articles by Alice Zhang from last year about machine learning.')">
                    <h4>📚 Example 1</h4>
                    <p>Author + Date + Topic search</p>
                </div>
                <div class="example-card" onclick="fillQuery('Find posts tagged with \\'LLMs\\' published in June, 2023.')">
                    <h4>🏷️ Example 2</h4>
                    <p>Tags + Specific date search</p>
                </div>
                <div class="example-card" onclick="fillQuery('Anything by John Doe on vector search?')">
                    <h4>👤 Example 3</h4>
                    <p>Author + Topic search</p>
                </div>
            </div>
        </div>
    </div>

    {% if result %}
    <div class="container result-section">
        <h2>📊 Results</h2>
        
        <div class="result-card">
            <h3>🎯 Generated Pinecone Filter (Assignment Output)</h3>
            <pre>{{ result.filter_json | safe }}</pre>
        </div>

        {% if result.search_results %}
        <div class="result-card">
            <h3>🔍 Pinecone Search Results ({{ result.search_results.total_count }} found)</h3>
            {% if result.search_results.matches %}
                {% for match in result.search_results.matches %}
                <div class="search-result">
                    <span class="search-score">{{ "%.1f" | format(match.score * 100) }}%</span>
                    <h4>{{ match.metadata.title or 'Untitled Article' }}</h4>
                    <div class="search-meta">
                        <strong>Author:</strong> {{ match.metadata.author or 'Unknown' }} | 
                        <strong>Published:</strong> {{ match.metadata.publishedDate or match.metadata.published_date or 'Unknown' }}
                    </div>
                    <div class="search-meta">
                        <strong>Tags:</strong> 
                        {% if match.metadata.tags %}
                            {% if match.metadata.tags is string %}
                                {{ match.metadata.tags }}
                            {% else %}
                                {{ match.metadata.tags | join(', ') }}
                            {% endif %}
                        {% else %}
                            None
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p>No matching articles found with the generated filter.</p>
            {% endif %}
        </div>
        {% endif %}
    </div>
    {% endif %}

    {% if error %}
    <div class="container">
        <div class="status error">
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
    pinecone_status = "connected" if pinecone_connected else "disconnected"
    
    if request.method == 'GET':
        return render_template_string(HTML_TEMPLATE, pinecone_status=pinecone_status)

    # Handle POST request
    query = request.form.get('query', '').strip()
    
    if not query:
        return render_template_string(HTML_TEMPLATE, 
                                    error="Please enter a query", 
                                    pinecone_status=pinecone_status)

    try:
        # Step 1: Generate filter using the agent
        print(f"🔍 Processing query: {query}")
        filter_dict = agent.generate_pinecone_filter(query)
        
        # Step 2: Search Pinecone if connected
        search_results = None
        if pinecone_connected:
            print(f"🔍 Searching Pinecone with filter: {filter_dict}")
            search_results = pinecone_client.search(query, filter_dict, top_k=5)
        
        # Prepare result with properly formatted JSON
        import json
        result = {
            'filter': filter_dict,
            'filter_json': json.dumps(filter_dict, indent=2, ensure_ascii=False),
            'search_results': search_results
        }

        print(f"✅ Generated filter with {len(search_results.get('matches', []) if search_results else [])} search results")
        return render_template_string(HTML_TEMPLATE,
                                    result=result,
                                    pinecone_status=pinecone_status)

    except Exception as e:
        print(f"❌ Error: {e}")
        return render_template_string(HTML_TEMPLATE, 
                                    error=f"An error occurred: {str(e)}", 
                                    pinecone_status=pinecone_status)

@app.route('/api/filter', methods=['POST'])
def api_filter():
    """API endpoint that returns only the filter (as required by assignment)."""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        filter_dict = agent.generate_pinecone_filter(query)
        return jsonify(filter_dict)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "agent": "initialized",
        "pinecone": "connected" if pinecone_connected else "disconnected",
        "model": agent.model
    })

if __name__ == '__main__':
    print("🚀 Starting Simple Bridged Demo Frontend...")
    print("📍 Frontend available at: http://localhost:5000")
    print("🔗 API endpoint: http://localhost:5000/api/filter")
    print("🗄️ Pinecone status:", "Connected" if pinecone_connected else "Disconnected")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
