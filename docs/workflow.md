# System Workflow

## 🔄 Complete Processing Pipeline

This document outlines the step-by-step workflow from natural language input to Pinecone search results.

## 📝 Phase 1: Query Input & Preprocessing

### **Step 1.1: User Input**
```
User enters natural language query:
"Show me articles by Jane Doe about cricket from 2025"
```

### **Step 1.2: Input Validation**
- Sanitize input string
- Check for minimum length
- Remove potentially harmful characters
- Normalize whitespace

### **Step 1.3: Query Analysis**
- Identify query components (author, date, tags)
- Determine query complexity
- Select processing strategy

## 🧠 Phase 2: Natural Language Processing

### **Step 2.1: LLM Network Processing**

```python
Sequential Fallback Chain:
1. google/gemma-3n-e4b-it:free
2. sarvamai/sarvam-m:free  
3. qwen/qwen3-8b:free
4. deepseek/deepseek-r1-0528:free
5. Rule-based fallback
```

**Process:**
1. Send query to first available LLM
2. Parse JSON response
3. If fails, try next LLM
4. Continue until success or exhaustion

### **Step 2.2: LLM Prompt Structure**

```
You are an expert at converting natural language queries into Pinecone database filters.

REAL DATABASE SCHEMA:
- author: string (e.g., "Jane Doe", "Mary Poppins")
- tags: string containing array format (e.g., "['#RohitSharma', '#DRS']")
- published_year: int, published_month: int, published_day: int

SUPPORTED OPERATORS:
- Equality: $eq, $ne
- Comparison: $gt, $gte, $lt, $lte  
- Arrays: $in, $nin
- Logic: $and, $or

Convert: "Show me articles by Jane Doe about cricket from 2025"

JSON filter:
```

### **Step 2.3: Response Parsing**

```python
Raw LLM Response:
'{"$and": [{"author": "Jane Doe"}, {"tags": "#Cricket"}, {"published_year": {"$eq": 2025}}]}'

Parsed Filter:
{
  "$and": [
    {"author": "Jane Doe"},
    {"tags": "#Cricket"}, 
    {"published_year": {"$eq": 2025}}
  ]
}
```

### **Step 2.4: Rule-Based Fallback**

If all LLMs fail, use pattern matching:

```python
def rule_based_extraction(query):
    filter_dict = {}
    
    # Extract authors
    if "by " in query.lower():
        author = extract_author_pattern(query)
        filter_dict["author"] = author
    
    # Extract players/tags
    player_tags = []
    if "rohit sharma" in query.lower():
        player_tags.append("#RohitSharma")
    if "cricket" in query.lower():
        player_tags.append("#Cricket")
    
    if len(player_tags) > 1:
        filter_dict["tags"] = {"$or": player_tags}
    elif len(player_tags) == 1:
        filter_dict["tags"] = player_tags[0]
    
    # Extract dates
    if "2025" in query:
        filter_dict["published_year"] = {"$eq": 2025}
    
    return filter_dict
```

## ✅ Phase 3: Filter Validation & Optimization

### **Step 3.1: Structure Validation**

```python
def validate_filter(filter_dict):
    # Handle root-level logical operators
    if "$and" in filter_dict or "$or" in filter_dict:
        return filter_dict
    
    validated = {}
    
    # Validate author field
    if "author" in filter_dict:
        if isinstance(filter_dict["author"], dict):
            validated["author"] = filter_dict["author"]  # With operators
        else:
            validated["author"] = str(filter_dict["author"])  # Simple string
    
    # Validate tags field
    if "tags" in filter_dict:
        tags_value = filter_dict["tags"]
        if isinstance(tags_value, dict):
            # Support $in, $nin, $or, $and, $eq, $ne
            validated["tags"] = tags_value
        elif isinstance(tags_value, str):
            validated["tags"] = tags_value
    
    # Validate date fields
    date_fields = ["published_year", "published_month", "published_day", 
                   "publishedDate", "publishedTimestamp"]
    for field in date_fields:
        if field in filter_dict:
            validated[field] = filter_dict[field]
    
    return validated
```

### **Step 3.2: Operator Optimization**

- Convert simple equality to optimized format
- Combine redundant conditions
- Optimize date range queries
- Validate operator compatibility

## 🔍 Phase 4: Search Execution

### **Step 4.1: Embedding Generation**

```python
Embedding Fallback Chain:
1. OpenAI text-embedding-ada-002 (primary)
   - Dimension: 1536
   - High quality embeddings
   
2. Sentence Transformers (fallback)
   - Model: all-MiniLM-L6-v2
   - Dimension: 384 → padded to 1536
   - Free, local processing
```

### **Step 4.2: Filter Conversion**

Convert tag filters for string-based storage:

```python
def convert_tag_filter(filter_dict):
    # Original filter
    {"tags": "#RohitSharma"}
    
    # Database storage format
    "['#RohitSharma', '#DRS', '#RRvsMI']"
    
    # Search strategy: Remove tag filter, do broader search
    # Post-process results to match tags
    return converted_filter
```

### **Step 4.3: Pinecone Query Execution**

```python
search_results = index.query(
    vector=query_embedding,
    top_k=5,
    include_metadata=True,
    filter=converted_filter  # Author, date filters only
)
```

### **Step 4.4: Post-Processing Filter**

```python
def filter_by_tags(matches, tag_filter):
    filtered_matches = []
    
    for match in matches:
        tags_str = match.metadata.get("tags", "")
        
        if isinstance(tag_filter, str):
            if tag_filter in tags_str:
                filtered_matches.append(match)
        elif isinstance(tag_filter, dict) and "$or" in tag_filter:
            for tag in tag_filter["$or"]:
                if tag in tags_str:
                    filtered_matches.append(match)
                    break
    
    return filtered_matches
```

## 📊 Phase 5: Result Processing & Response

### **Step 5.1: Result Formatting**

```python
formatted_results = {
    "matches": [
        {
            "id": match.id,
            "score": match.score,
            "metadata": {
                "author": match.metadata.get("author"),
                "tags": match.metadata.get("tags"),
                "publishedDate": match.metadata.get("publishedDate")
            }
        }
        for match in filtered_matches
    ],
    "total_count": len(filtered_matches),
    "filter_applied": original_filter
}
```

### **Step 5.2: Frontend Display**

```python
# JSON filter display
filter_json = json.dumps(filter_dict, indent=2, ensure_ascii=False)

# Results display
for i, match in enumerate(results["matches"], 1):
    print(f"{i}. Author: {match['metadata']['author']}")
    print(f"   Tags: {match['metadata']['tags']}")
    print(f"   Score: {match['score']:.3f}")
```

## ⚡ Performance Optimizations

### **Caching Strategy**
- Cache LLM responses for identical queries
- Cache embeddings for repeated searches
- Cache Pinecone results for common filters

### **Parallel Processing**
- Embedding generation while filter processing
- Concurrent LLM requests (when rate limits allow)
- Asynchronous result formatting

### **Error Recovery**
- Graceful degradation at each step
- Meaningful error messages to users
- Automatic retry with exponential backoff

## 📈 Success Metrics

- **LLM Success Rate**: 95%+
- **Overall Pipeline Success**: 99%+
- **Average Response Time**: 2-6 seconds
- **User Satisfaction**: High-quality, relevant results

This workflow ensures robust, reliable natural language to database query translation with multiple fallback mechanisms and optimization strategies.
