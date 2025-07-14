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

### **Basic Functionality Tests**
```bash
# Activate virtual environment
venv\Scripts\activate

# Test core search functionality
python test_improved_search.py

# Test all filtering operators
python test_all_operators.py

# Test date format support
python test_date_formats.py

# Test specific date queries (NEW)
python test_specific_dates.py

# Test date query improvements (NEW)
python test_final_dates.py

# Debug date filtering (NEW)
python debug_full_search.py

# Test complete system
python test_real_system.py
```

### **Frontend Testing**
```bash
# Start web interface
python simple_frontend.py

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

Test Scripts:
- test_specific_dates.py - Comprehensive date query testing
- test_final_dates.py - Validation of improvements
- debug_full_search.py - End-to-end debugging
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
# Add debug prints to simple_agent.py
print(f"🔍 Raw LLM Response: '{response_text}'")
print(f"📋 Parsed Filter: {filter_dict}")
print(f"✅ Validated Filter: {validated}")
```

### **Monitor API Calls**
```python
# Track API usage
print(f"🌐 Using LLM: {model_name}")
print(f"⏱️ Response time: {response_time:.2f}s")
print(f"🔄 Fallback triggered: {fallback_used}")
```

### **Database Query Monitoring**
```python
# Monitor Pinecone queries
print(f"🔍 Pinecone filter: {converted_filter}")
print(f"📊 Results found: {len(matches)}")
print(f"⚡ Query time: {query_time:.3f}s")
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
# Automated test runner
python -m pytest tests/ -v

# Coverage report
python -m pytest --cov=src tests/

# Performance monitoring
python benchmark_tests.py
```

This comprehensive testing framework ensures the system is robust, reliable, and ready for production deployment or demo presentation.
