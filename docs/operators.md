# Pinecone Filtering Operators Guide

## 📋 Complete Operator Reference

This guide covers all supported Pinecone filtering operators with examples and use cases.

## 🔍 Equality Operators

### **$eq (Exact Match)**
```json
// Basic usage
{"author": {"$eq": "Jane Doe"}}

// Simplified syntax (equivalent)
{"author": "Jane Doe"}
```
**Use Case**: Find exact matches for string or numeric values.

### **$ne (Not Equal)**
```json
{"author": {"$ne": "Jane Doe"}}
```
**Use Case**: Exclude specific values from results.

## 📊 Comparison Operators

### **$gt (Greater Than)**
```json
{"published_year": {"$gt": 2023}}
```

### **$gte (Greater Than or Equal)**
```json
{"publishedTimestamp": {"$gte": 1704067200}}
```

### **$lt (Less Than)**
```json
{"published_month": {"$lt": 6}}
```

### **$lte (Less Than or Equal)**
```json
{"published_day": {"$lte": 15}}
```

**Use Cases**: Date ranges, numeric filtering, temporal queries.

## 📚 Array Operators

### **$in (Any Of These Values)**
```json
// Multiple tag options
{"tags": {"$in": ["#Cricket", "#Football", "#Sports"]}}

// Multiple authors
{"author": {"$in": ["Jane Doe", "John Smith"]}}
```
**Use Case**: OR logic - find documents matching ANY of the specified values.

### **$nin (None Of These Values)**
```json
// Exclude multiple tags
{"tags": {"$nin": ["#Spam", "#Ads", "#Promotional"]}}

// Exclude multiple authors
{"author": {"$nin": ["Banned User", "Deleted Account"]}}
```
**Use Case**: Exclusion logic - filter out unwanted content.

## 🔗 Logical Operators

### **$and (All Conditions Must Match)**
```json
{
  "$and": [
    {"author": "Jane Doe"},
    {"tags": "#Cricket"},
    {"published_year": {"$eq": 2025}}
  ]
}
```
**Use Case**: Combine multiple requirements - ALL must be satisfied.

### **$or (Any Condition Can Match)**
```json
{
  "$or": [
    {"author": "Jane Doe"},
    {"tags": "#VIP"},
    {"published_year": {"$gte": 2025}}
  ]
}
```
**Use Case**: Alternative conditions - ANY can be satisfied.

## 📅 Date Filtering - 3 Format Options

### **Format 1: Unix Timestamp**
```json
// Articles from 2024 onwards
{"publishedTimestamp": {"$gte": 1704067200}}

// Articles from May 2025
{
  "publishedTimestamp": {
    "$gte": 1746057600,
    "$lt": 1748736000
  }
}
```

### **Format 2: ISO Date Strings**
```json
// Articles from 2024 onwards
{"publishedDate": {"$gte": "2024-01-01T00:00:00+00:00"}}

// Articles from May 2025
{
  "publishedDate": {
    "$gte": "2025-05-01T00:00:00+00:00",
    "$lt": "2025-06-01T00:00:00+00:00"
  }
}
```

### **Format 3: Separate Integer Fields**
```json
// Articles from 2024
{"published_year": {"$eq": 2024}}

// Articles from June 2023
{
  "published_year": {"$eq": 2023},
  "published_month": {"$eq": 6}
}

// Articles from specific day
{
  "published_year": {"$eq": 2025},
  "published_month": {"$eq": 5},
  "published_day": {"$eq": 15}
}
```

## 🏷️ Tag Filtering Strategies

### **Single Tag Search**
```json
{"tags": "#RohitSharma"}
```

### **Multiple Tags (OR Logic)**
```json
{"tags": {"$in": ["#Cricket", "#Football", "#Sports"]}}
```

### **Multiple Players (OR Logic)**
```json
{"tags": {"$or": ["#RohitSharma", "#ShubmanGill"]}}
```

### **Tag Exclusion**
```json
{"tags": {"$nin": ["#Spam", "#Ads"]}}
```

## 🎯 Real-World Query Examples

### **1. Complex Author + Date + Tag Query**
```json
{
  "$and": [
    {"author": "Alice Zhang"},
    {"published_year": {"$eq": 2024}},
    {"tags": "#MachineLearning"}
  ]
}
```
**Natural Language**: "articles by Alice Zhang from last year about machine learning"

### **2. Multi-Player Sports Query**
```json
{
  "tags": {"$or": ["#RohitSharma", "#ShubmanGill"]}
}
```
**Natural Language**: "posts about Rohit Sharma and Shubman Gill"

### **3. Date Range with Tag Filter**
```json
{
  "$and": [
    {"publishedTimestamp": {"$gte": 1746057600, "$lt": 1748736000}},
    {"tags": {"$in": ["#IPL2025", "#Cricket"]}}
  ]
}
```
**Natural Language**: "IPL articles from May 2025"

### **4. Author Exclusion Query**
```json
{
  "$and": [
    {"author": {"$ne": "Jane Doe"}},
    {"tags": "#Cricket"}
  ]
}
```
**Natural Language**: "cricket posts not by Jane Doe"

### **5. Multi-Tag OR Query**
```json
{
  "tags": {"$in": ["#Cricket", "#Football", "#Basketball"]}
}
```
**Natural Language**: "articles about cricket or football or basketball"

## ⚡ Performance Tips

### **Efficient Queries**
- Use specific tags rather than broad searches
- Combine filters with $and for precision
- Use timestamp format for date ranges (fastest)

### **Indexing Considerations**
- Separate date fields are most efficient for year/month filtering
- Tag searches work best with individual hashtags
- Author filters are highly optimized

### **Best Practices**
- Use $in for multiple options (better than multiple $or conditions)
- Combine date + tag filters for targeted results
- Use $ne sparingly (can be slower than positive filters)

## 🔧 Operator Priority

1. **Equality operators** ($eq, $ne) - Fastest
2. **Comparison operators** ($gt, $gte, $lt, $lte) - Fast
3. **Array operators** ($in, $nin) - Moderate
4. **Logical operators** ($and, $or) - Depends on sub-conditions

This comprehensive operator support enables precise, flexible querying for any natural language input!
