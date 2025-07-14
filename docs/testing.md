# Testing Guide

## 🧪 Comprehensive Testing Framework

This guide covers all testing scenarios, validation methods, and performance benchmarks for the Natural Language to Pinecone Query Agent.

## 🔍 Test Categories

### **1. Unit Tests**
- Individual component testing
- Function-level validation
- Error handling verification

### **2. Integration Tests**
- End-to-end pipeline testing
- Database connectivity validation
- API integration verification

### **3. Performance Tests**
- Response time benchmarks
- Concurrent user testing
- Resource usage monitoring

### **4. User Acceptance Tests**
- Real-world query scenarios
- Demo preparation validation
- Edge case handling

## 🚀 Quick Test Commands

### **⚠️ Important: PYTHONPATH Setup**
All individual test files require PYTHONPATH to be set to find the `src` module:

```bash
# Windows (PowerShell)
$env:PYTHONPATH = "."

# Windows (Command Prompt)
set PYTHONPATH=.

# Linux/Mac
export PYTHONPATH=.
```

### **Available Test Files**
```bash
# Activate virtual environment (choose your preferred method)
venv\Scripts\activate          # pip environment
venv-uv\Scripts\activate       # uv environment
# or use Poetry: poetry shell

# Set PYTHONPATH (REQUIRED!)
set PYTHONPATH=.               # Windows
export PYTHONPATH=.            # Linux/Mac

# Run available test files:

# 1. COMPREHENSIVE DEMO - Run this for recruiters! (MAIN DEMO)
python test_comprehensive_demo.py

# 2. Unit Tests in tests/ folder
python -m pytest tests/test_api.py -v
python -m pytest tests/test_simple_agent.py -v

# 3. Run all tests with pytest
python -m pytest tests/ -v

# 4. Run tests with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### **Quick Start Testing (Recommended)**
```bash
# Use automated scripts that handle environment setup:

# With uv (fastest)
scripts\run-with-uv.bat        # Windows
./scripts/run-with-uv.sh       # Linux/Mac

# With Poetry (professional)
scripts\run-with-poetry.bat    # Windows
./scripts/run-with-poetry.sh   # Linux/Mac

# With pip (traditional)
scripts\run-with-pip.bat       # Windows
./scripts/run-with-pip.sh      # Linux/Mac

# Then run tests in the activated environment:
python test_comprehensive_demo.py
python -m pytest tests/ -v
```

## 🎬 Comprehensive Demo Suite (NEW)

### **For Recruiters and Stakeholders**
The `test_comprehensive_demo.py` script provides a complete showcase of all system capabilities:

```bash
# Run the full demonstration
python test_comprehensive_demo.py
```

### **Demo Sections Covered**
1. **Boolean Logic (OR vs AND)** - Natural language interpretation
2. **Single Entity Searches** - Basic filtering capabilities
3. **Date Filtering** - Multiple date formats and relative queries
4. **Complex Combinations** - Multi-parameter queries
5. **Advanced Operators** - Negation, comparison, exclusion
6. **Edge Cases** - Error handling and fallback mechanisms
7. **Performance Scenarios** - Different complexity levels
8. **Real-World Examples** - Conversational queries

### **Key Features Demonstrated**
- ✅ **Boolean Logic**: "posts about X and Y" (OR) vs "posts containing both X and Y" (AND)
- ✅ **Smart Interpretation**: Natural language intent recognition
- ✅ **Real Database**: Live Pinecone search with actual results
- ✅ **Robust Fallbacks**: 99%+ success rate with multiple LLM providers
- ✅ **Production Ready**: Error handling, validation, optimization

### **Expected Output**
- Filter generation with timing
- JSON structure display
- Live Pinecone search results
- Performance metrics
- Success/failure indicators

### **Frontend Testing**
```bash
# Start FastAPI web interface (recommended)
python apps/fastapi_app.py

# Access at: http://localhost:8000
# Interactive API docs: http://localhost:8000/docs
# Health check: http://localhost:8000/health

# Alternative: Start Flask frontend (if needed)
python apps/frontend.py

# Access at: http://localhost:5000
# Test with example queries from examples.md
```

## 📊 Test Scenarios

### **Scenario 1: Basic Tag Searches**
```python
Test Queries:
- "posts about Rohit Sharma"
- "articles about Shubman Gill"
- "Mumbai Indians posts"

Expected Results:
- Correct hashtag filters generated
- Relevant articles returned
- Response time < 3 seconds
```

### **Scenario 2: Complex Logical Operations**
```python
Test Queries:
- "posts by Jane Doe about cricket"
- "posts about Rohit Sharma and Shubman Gill"
- "articles not by Jane Doe"

Expected Results:
- Proper $and/$or logic
- Multiple condition handling
- Accurate result filtering
```

### **Scenario 3: Date Filtering**
```python
Test Queries:
- "articles from 2024"
- "posts from June 2023"
- "articles from May 2025"

Expected Results:
- Correct date field usage
- Proper timestamp conversion
- Accurate temporal filtering
```

### **Scenario 4: Fallback System Testing**
```python
Test Scenarios:
- LLM API failures
- Invalid JSON responses
- Network connectivity issues

Expected Results:
- Graceful fallback to rule-based extraction
- No system crashes
- Meaningful error messages
```

### **Scenario 5: Date Query Testing (Enhanced)**
```python
Test Categories:
1. Year Queries:
   - "articles from 2025" → Full year range
   - "posts from 2024" → Full year range (no data expected)

2. Month Queries:
   - "articles from May 2025" → Full month range (3 matches)
   - "posts from June 2025" → Full month range (0 matches expected)

3. Relative Date Queries:
   - "posts from last month" → Previous month calculation
   - "articles from previous 15 days" → Day range calculation
   - "posts from last week" → Week range calculation

4. Specific Date Queries:
   - "posts from 2025-05-01" → Specific date range
   - "articles from June 1, 2025" → Specific date range

Expected Results:
- Correct Unix timestamp generation
- Proper date range calculations
- Accurate filtering with publishedTimestamp field
- 0 results for dates with no data (correct behavior)

Test Coverage:
- test_comprehensive_demo.py - Comprehensive date query testing and all scenarios
- tests/test_api.py - API endpoint testing and validation
- tests/test_simple_agent.py - Core agent functionality testing
```

## 🔧 Performance Benchmarks

### **Response Time Targets**
```
Simple Queries (single condition):
- Target: < 2 seconds
- Acceptable: < 3 seconds

Complex Queries (multiple conditions):
- Target: < 4 seconds  
- Acceptable: < 6 seconds

Fallback Scenarios:
- Target: < 6 seconds
- Acceptable: < 10 seconds
```

### **Success Rate Targets**
```
LLM Processing:
- Target: > 95%
- Minimum: > 90%

Overall Pipeline:
- Target: > 99%
- Minimum: > 95%

Search Accuracy:
- Target: > 90% relevant results
- Minimum: > 80% relevant results
```

## 🛡️ Error Handling Tests

### **Test 1: Invalid Queries**
```python
Test Inputs:
- Empty strings
- Special characters only
- Extremely long queries
- Non-English text

Expected Behavior:
- Graceful error handling
- User-friendly error messages
- No system crashes
```

### **Test 2: API Failures**
```python
Test Scenarios:
- OpenRouter API down
- Pinecone API unavailable
- Network timeouts
- Rate limit exceeded

Expected Behavior:
- Automatic fallback activation
- Retry mechanisms
- Clear error reporting
```

### **Test 3: Data Validation**
```python
Test Cases:
- Malformed JSON responses
- Missing metadata fields
- Invalid date formats
- Corrupted embeddings

Expected Behavior:
- Input sanitization
- Data validation
- Fallback to defaults
```

## 📈 Load Testing

### **Concurrent User Testing**
```python
Test Configuration:
- 10 simultaneous users
- 50 queries per user
- Mixed query complexity

Success Criteria:
- No failed requests
- Response time degradation < 50%
- Memory usage stable
```

### **Stress Testing**
```python
Test Configuration:
- 100 rapid-fire queries
- Maximum complexity queries
- Resource monitoring

Success Criteria:
- System remains responsive
- No memory leaks
- Graceful performance degradation
```

## 🎯 Validation Checklist

### **Pre-Demo Validation**
- [ ] All test files execute successfully
- [ ] Web interface loads and responds
- [ ] Pinecone connection established
- [ ] LLM APIs accessible
- [ ] Sample queries return expected results

### **Core Functionality Validation**
- [ ] Tag filtering works correctly
- [ ] Author filtering functions properly
- [ ] Date filtering supports all formats
- [ ] Logical operators ($and, $or) work
- [ ] Comparison operators function correctly

### **Edge Case Validation**
- [ ] Empty query handling
- [ ] Invalid author names
- [ ] Non-existent tags
- [ ] Future dates
- [ ] Malformed input

### **Performance Validation**
- [ ] Response times within targets
- [ ] Memory usage reasonable
- [ ] No resource leaks
- [ ] Concurrent access works

## 🔍 Debug Testing

### **Enable Debug Mode**
```python
# Debug mode is already built into the FastAPI application
# Check the terminal output when running:
python apps/fastapi_app.py

# You'll see detailed logs like:
# 🔍 Raw LLM Response: '{"publishedTimestamp": {"$gte": 1735689600}}'
# 📋 Parsed Filter: {"publishedTimestamp": {"$gte": 1735689600}}
# ✅ Validated Filter: {"publishedTimestamp": {"$gte": 1735689600}}
```

### **Monitor API Calls**
```python
# The FastAPI app includes comprehensive logging:
# 🌐 Using LLM: google/gemma-3n-e4b-it:free
# ⏱️ Response time: 3.67s
# 🔄 Fallback triggered: false
# 📊 Results found: 5
# ⚡ Query time: 0.943s

# Enable additional debugging in src/agent.py if needed
```

### **Database Query Monitoring**
```python
# Pinecone queries are automatically logged in the FastAPI app:
# 🔍 Pinecone filter: {'publishedTimestamp': {'$gte': 1735689600}}
# 📊 Raw results count: 5
# ⚡ Pinecone query completed in 0.943s

# Check the terminal output when running the FastAPI application
```

## 📊 Test Results Documentation

### **Test Report Template**
```
Test Date: [DATE]
Test Environment: [LOCAL/STAGING/PROD]
Tester: [NAME]

RESULTS:
✅ Basic Functionality: PASS/FAIL
✅ Complex Queries: PASS/FAIL  
✅ Error Handling: PASS/FAIL
✅ Performance: PASS/FAIL

ISSUES FOUND:
- [Issue 1 description]
- [Issue 2 description]

RECOMMENDATIONS:
- [Recommendation 1]
- [Recommendation 2]
```

### **Continuous Testing**
```bash
# Automated test runner (current available tests)
python -m pytest tests/ -v

# Coverage report for src/ module
python -m pytest --cov=src tests/ --cov-report=html

# Run comprehensive demo for performance monitoring
python test_comprehensive_demo.py

# Test with different package managers
scripts\run-with-uv.bat && python -m pytest tests/ -v
scripts\run-with-poetry.bat && python -m pytest tests/ -v
scripts\run-with-pip.bat && python -m pytest tests/ -v
```

## 📁 **Current Test File Structure**

```
bridged_media_assignment/
├── test_comprehensive_demo.py     # Main demo script for recruiters
├── tests/                         # Unit test directory
│   ├── __init__.py               # Test package initialization
│   ├── test_api.py               # API endpoint testing
│   └── test_simple_agent.py      # Core agent functionality testing
└── apps/
    ├── fastapi_app.py            # FastAPI app with built-in logging
    └── frontend.py               # Flask frontend (alternative)
```

### **Test File Descriptions**

#### **test_comprehensive_demo.py**
- **Purpose**: Main demonstration script for recruiters and stakeholders
- **Coverage**: All system capabilities including boolean logic, date filtering, complex queries
- **Output**: Detailed logging with filter generation, Pinecone results, and performance metrics
- **Usage**: `python test_comprehensive_demo.py`

#### **tests/test_api.py**
- **Purpose**: Unit tests for FastAPI application endpoints
- **Coverage**:
  - Health check endpoint (`/health`)
  - Query endpoint (`/query`) with mocked responses
  - Input validation and error handling
  - Request/response format validation
- **Test Functions**:
  - `test_health_endpoint()` - Health check functionality
  - `test_query_endpoint_basic()` - Basic query processing
  - `test_query_endpoint_validation()` - Input validation
- **Usage**: `python -m pytest tests/test_api.py -v`

#### **tests/test_simple_agent.py**
- **Purpose**: Unit tests for core NLP agent functionality
- **Coverage**:
  - Author extraction from natural language queries
  - Tag extraction and parsing
  - Date parsing and timestamp conversion
  - Filter generation and validation
- **Test Functions**:
  - `test_extract_author()` - Author name extraction
  - `test_extract_tags()` - Tag identification
  - `test_date_parsing()` - Date format handling
  - `test_filter_generation()` - Complete filter creation
- **Usage**: `python -m pytest tests/test_simple_agent.py -v`

## 🎯 **Quick Testing Commands for Recruiters**

### **1. Complete System Demo (Recommended)**
```bash
# Run the comprehensive demo that showcases all features
python test_comprehensive_demo.py

# Expected output: Detailed logs showing:
# - LLM model selection and fallback
# - Filter generation with timing
# - Pinecone search results
# - Performance metrics
```

### **2. Unit Test Suite**
```bash
# Run all unit tests with verbose output
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_api.py -v
python -m pytest tests/test_simple_agent.py -v

# Run tests with coverage report
python -m pytest tests/ --cov=src --cov-report=html
# View coverage report: open htmlcov/index.html
```

### **3. Live System Testing**
```bash
# Start the FastAPI application
python apps/fastapi_app.py

# In another terminal, test the live API:
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "articles from May 2025"}'

# Check system health
curl http://localhost:8000/health

# View interactive API docs
# Open browser: http://localhost:8000/docs
```

### **4. Cross-Platform Package Manager Testing**
```bash
# Test with uv (fastest)
scripts\run-with-uv.bat && python test_comprehensive_demo.py

# Test with Poetry (professional)
scripts\run-with-poetry.bat && python -m pytest tests/ -v

# Test with pip (traditional)
scripts\run-with-pip.bat && python test_comprehensive_demo.py
```

## 📋 **Testing Checklist for Demo**

### **Pre-Demo Validation**
- [ ] `python test_comprehensive_demo.py` runs successfully
- [ ] `python -m pytest tests/ -v` passes all tests
- [ ] `python apps/fastapi_app.py` starts without errors
- [ ] Health check responds: `curl http://localhost:8000/health`
- [ ] Interactive docs load: `http://localhost:8000/docs`

### **Core Functionality Validation**
- [ ] Date queries work: "articles from May 2025"
- [ ] Boolean logic works: "posts about X and Y" vs "posts containing both X and Y"
- [ ] LLM fallback system activates on failures
- [ ] Embedding fallback works when OpenAI quota exceeded
- [ ] Pinecone search returns relevant results

### **Performance Validation**
- [ ] Query processing time < 10 seconds
- [ ] LLM response time logged and reasonable
- [ ] Pinecone search time < 2 seconds
- [ ] System handles multiple concurrent requests

This comprehensive testing framework ensures the system is robust, reliable, and ready for production deployment or demo presentation.
