"""
Simple Natural Language to Pinecone Query Agent
Exactly as required by the Bridged Media Assignment
Works with REAL Pinecone data - no hardcoded examples
"""

import json
import os
import openai
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleNLAgent:
    """
    Simple agent that converts natural language to Pinecone query filters.
    Uses multiple LLM providers with fallbacks to ensure reliability.
    Works with your real Pinecone data structure.
    """

    def __init__(self):
        """Initialize the agent with multiple LLM clients."""
        # Initialize OpenRouter client
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.openrouter_client = None
        if self.openrouter_api_key:
            self.openrouter_client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_api_key,
            )

        # Initialize OpenAI client as fallback
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_client = None
        if self.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)

        # Reordered models - put working ones first
        self.free_models = [
            "google/gemma-3n-e4b-it:free",           # Works well with JSON
            "qwen/qwen3-8b:free",                    # Good performance
            "mistralai/mistral-small-3.1-24b-instruct:free",  # Reliable
            "sarvamai/sarvam-m:free",                # Backup
            "qwen/qwen3-4b:free",                    # Smaller model
            "deepseek/deepseek-v3-base:free",        # Base model
            "deepseek/deepseek-r1-0528:free"         # R1 model (can be inconsistent)
        ]

        # Fallback to OpenAI if free models fail
        self.openai_model = "gpt-3.5-turbo"
    
    def generate_pinecone_filter(self, natural_language_query: str) -> Dict[str, Any]:
        """
        Convert natural language query to Pinecone filter.

        Args:
            natural_language_query: User's natural language input

        Returns:
            Dictionary containing Pinecone-compatible filter
        """
        try:
            # Create prompt based on real data structure
            prompt = self._create_prompt(natural_language_query)

            # Try free models first, then fallback to OpenAI
            response_text = self._call_llm_with_fallback(prompt)

            if not response_text:
                # If all LLMs fail, use rule-based fallback
                print("⚠️ All LLMs failed, using rule-based extraction")
                return self._rule_based_extraction(natural_language_query)

            # Parse LLM response
            filter_dict = self._parse_response(response_text)

            # Validate and clean the filter
            return self._validate_filter(filter_dict)

        except Exception as e:
            print(f"Error generating filter: {e}")
            # Use rule-based fallback
            return self._rule_based_extraction(natural_language_query)
    
    def _create_prompt(self, query: str) -> str:
        """Create prompt based on REAL Pinecone data structure."""
        return f"""
You are an expert at converting natural language queries into Pinecone database filters.

REAL DATABASE SCHEMA (from actual Pinecone index):
- author: string (e.g., "Jane Doe", "Mary Poppins", "Akainu")
- tags: string containing array format (e.g., "['#RohitSharma', '#DRS', '#RRvsMI']")

DATE FIELD OPTIONS (use timestamp format):
REQUIRED: publishedTimestamp (Unix timestamp number, e.g., 1746141127)
- This is the ONLY date field that works with Pinecone filtering
- Use Unix timestamps (seconds since epoch) for all date comparisons

IMPORTANT: The tags field contains a STRING representation of an array, not an actual array.
For tag searches, you need to search for individual hashtags within the string.

Convert this natural language query into a valid Pinecone filter:
"{query}"

SUPPORTED OPERATORS:
- Equality: $eq (exact match), $ne (not equal)
- Comparison: $gt, $gte, $lt, $lte (for dates/numbers)
- Arrays: $in (any of these values), $nin (none of these values)
- Logic: $and (all conditions), $or (any condition)

CRITICAL BOOLEAN LOGIC RULES:
1. "posts about X and Y" = OR logic (posts related to EITHER X OR Y)
2. "posts containing both X and Y" = AND logic (posts that have BOTH X AND Y)
3. "posts related to X, Y" = OR logic (posts about any of these)
4. "posts with X and also Y" = AND logic (posts that must have both)
5. "posts about X or Y" = OR logic (explicitly stated)

TAG FILTERING RULES:
1. For author: use {{"author": {{"$eq": "Name"}}}} or {{"author": "Name"}}
2. For dates: ALWAYS use publishedTimestamp with Unix timestamps:
   - {{"publishedTimestamp": {{"$gte": 1704067200}}}} for dates >= 2024-01-01
   - {{"publishedTimestamp": {{"$gte": 1735689600, "$lt": 1767225600}}}} for year 2025
   - Convert all dates to Unix timestamps (seconds since epoch)
3. For single tags: use {{"tags": "#HashTag"}}
4. For OR logic (posts about X and Y): use {{"tags": {{"$in": ["#Tag1", "#Tag2"]}}}}
5. For AND logic (posts containing both): use {{"$and": [{{"tags": "#Tag1"}}, {{"tags": "#Tag2"}}]}}
6. Return ONLY valid JSON, no explanations
7. Use current year 2025 for "this year", 2024 for "last year"
8. IMPORTANT: Return ONE single JSON object, not multiple separate objects

REAL EXAMPLES based on actual data:

Query: "articles by Jane Doe"
Filter: {{"author": "Jane Doe"}}

Query: "posts about Rohit Sharma"
Filter: {{"tags": "#RohitSharma"}}

Query: "articles about Shubman Gill"
Filter: {{"tags": "#ShubmanGill"}}

Query: "Mumbai Indians posts"
Filter: {{"tags": "#MumbaiIndians"}}

Query: "IPL 2025 articles"
Filter: {{"tags": "#IPL2025"}}

Query: "articles from May 2025"
Filter: {{"publishedTimestamp": {{"$gte": 1746057600, "$lt": 1748736000}}}}

Query: "posts from June 2025"
Filter: {{"publishedTimestamp": {{"$gte": 1748736000, "$lt": 1751328000}}}}

Query: "articles from 2025"
Filter: {{"publishedTimestamp": {{"$gte": 1735689600, "$lt": 1767225600}}}}

Query: "posts from June 2023"
Filter: {{"publishedTimestamp": {{"$gte": 1685577600, "$lt": 1688169600}}}}

Query: "articles from 2024"
Filter: {{"publishedTimestamp": {{"$gte": 1704067200, "$lt": 1735689600}}}}

Query: "posts from last month"
Filter: {{"publishedTimestamp": {{"$gte": 1748736000, "$lt": 1751328000}}}}

Query: "articles from previous 15 days"
Filter: {{"publishedTimestamp": {{"$gte": 1750636800, "$lt": 1751932800}}}}

Query: "posts about Rohit Sharma and Shubman Gill" (OR logic - posts about either)
Filter: {{"tags": {{"$in": ["#RohitSharma", "#ShubmanGill"]}}}}

Query: "posts containing both Rohit Sharma and Shubman Gill" (AND logic - must have both)
Filter: {{"$and": [{{"tags": "#RohitSharma"}}, {{"tags": "#ShubmanGill"}}]}}

Query: "posts related to Rohit Sharma, Shubman Gill" (OR logic - posts about any)
Filter: {{"tags": {{"$in": ["#RohitSharma", "#ShubmanGill"]}}}}

Query: "posts with Rohit Sharma and also Shubman Gill" (AND logic - must have both)
Filter: {{"$and": [{{"tags": "#RohitSharma"}}, {{"tags": "#ShubmanGill"}}]}}

Query: "IPL articles by Mary Poppins"
Filter: {{"author": "Mary Poppins", "tags": "#IPL2025"}}

Query: "articles about cricket or football" (explicit OR)
Filter: {{"tags": {{"$in": ["#Cricket", "#Football"]}}}}

Query: "posts not by Jane Doe"
Filter: {{"author": {{"$ne": "Jane Doe"}}}}

Query: "articles from 2024 or later" (timestamp)
Filter: {{"publishedTimestamp": {{"$gte": 1704067200}}}}

Query: "posts by Jane Doe about cricket"
Filter: {{"$and": [{{"author": "Jane Doe"}}, {{"tags": "#Cricket"}}]}}

Query: "articles by Alice Zhang from last year about machine learning"
Filter: {{"$and": [{{"author": "Alice Zhang"}}, {{"publishedTimestamp": {{"$gte": 1704067200, "$lt": 1735689600}}}}, {{"tags": "#MachineLearning"}}]}}

BOOLEAN LOGIC DECISION TREE:
1. Look for explicit keywords:
   - "containing both", "with both", "having both", "includes both" → AND logic
   - "about X and Y", "related to X, Y", "posts on X and Y" → OR logic (default)
   - "or", "either" → OR logic (explicit)

2. Context clues:
   - Casual language ("posts about X and Y") → OR logic
   - Specific requirements ("posts containing both X and Y") → AND logic
   - Lists ("posts about X, Y, Z") → OR logic

IMPORTANT TECHNICAL RULES:
- For tag searches, use individual hashtags (like "#RohitSharma") NOT exact string combinations
- Use $in for multiple tag options with OR logic: {{"tags": {{"$in": ["#Tag1", "#Tag2"]}}}}
- Use $and for requiring multiple tags: {{"$and": [{{"tags": "#Tag1"}}, {{"tags": "#Tag2"}}]}}
- Use $or for different field conditions
- Use $and for combining multiple requirements across different fields

DATE HANDLING:
- Always use FULL month/year ranges, not partial ranges
- For "May 2025" use full month: 1746057600 to 1748736000
- For "June 2025" use full month: 1748736000 to 1751328000
- Calculate proper timestamp ranges for all date queries

Now convert: "{query}"

JSON filter:"""
    
    def _call_llm_with_fallback(self, prompt: str) -> Optional[str]:
        """Sequential LLM network - try models one by one in priority order with detailed logging."""
        import time
        print("🔄 Starting sequential LLM network...")
        llm_start_time = time.time()

        # Priority 1: Try OpenRouter free models sequentially
        if self.openrouter_client:
            print(f"🌐 OpenRouter API available - trying {len(self.free_models)} free models")
            for i, model in enumerate(self.free_models, 1):
                model_start = time.time()
                try:
                    print(f"  {i}. Trying {model}...", end=" ")
                    response = self.openrouter_client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=500,
                        temperature=0.1,
                        timeout=10  # Add timeout to fail fast
                    )
                    result = response.choices[0].message.content
                    model_time = time.time() - model_start
                    print(f"✅ SUCCESS ({model_time:.2f}s)")
                    print(f"🎯 Used model: {model}")
                    print(f"📝 Response length: {len(result)} characters")
                    print(f"📄 Response preview: {result[:100]}{'...' if len(result) > 100 else ''}")

                    total_llm_time = time.time() - llm_start_time
                    print(f"⏱️ Total LLM processing time: {total_llm_time:.3f}s")
                    return result
                except Exception as e:
                    model_time = time.time() - model_start
                    error_msg = str(e)[:40] + "..." if len(str(e)) > 40 else str(e)
                    print(f"❌ {error_msg} ({model_time:.2f}s)")
                    # Continue to next model immediately
                    continue

        # Priority 2: Fallback to OpenAI if available
        if self.openai_client:
            try:
                print(f"  Trying OpenAI fallback ({self.openai_model})...", end=" ")
                response = self.openai_client.chat.completions.create(
                    model=self.openai_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.1,
                    timeout=10
                )
                result = response.choices[0].message.content
                print(f"✅ SUCCESS")
                print(f"🎯 Used OpenAI: {self.openai_model}")
                return result
            except Exception as e:
                error_msg = str(e)[:40] + "..." if len(str(e)) > 40 else str(e)
                print(f"❌ {error_msg}")

        print("❌ All LLMs failed - using rule-based fallback")
        return None

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Enhanced JSON parsing to handle different LLM response formats."""
        if not response_text or not response_text.strip():
            return {}

        try:
            # Method 1: Try to extract from code blocks first
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                parsed = json.loads(json_str)
                return self._normalize_filter_format(parsed)

            # Method 2: Find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                parsed = json.loads(json_str)
                return self._normalize_filter_format(parsed)

            # Method 3: Try to find and combine multiple JSON objects
            # Look for all JSON-like objects in the response
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_objects = []

            # Find all potential JSON objects
            for match in re.finditer(r'\{[^}]*\}', response_text):
                json_objects.append(match.group())

            if len(json_objects) >= 2:
                # Try to combine multiple JSON objects into one
                combined_filter = {}
                valid_objects = 0

                for json_obj in json_objects:
                    try:
                        parsed = json.loads(json_obj)
                        if parsed:
                            combined_filter.update(parsed)
                            valid_objects += 1
                    except:
                        continue

                if valid_objects >= 2 and combined_filter:
                    print(f"🔧 Combined {valid_objects} JSON objects into single filter")
                    return self._normalize_filter_format(combined_filter)

            # Method 4: Single JSON object fallback
            for json_obj in json_objects:
                try:
                    parsed = json.loads(json_obj)
                    if parsed:  # If we get a non-empty object
                        return self._normalize_filter_format(parsed)
                except:
                    continue

            return {}

        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing failed: {e}")
            print(f"Response was: {response_text[:100]}...")
            return {}

    def _normalize_filter_format(self, parsed_filter: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize different filter formats from different LLMs."""
        if not parsed_filter:
            return {}

        # Handle cases where LLM returns {"query": "author:Jane Doe"} format
        if "query" in parsed_filter and isinstance(parsed_filter["query"], str):
            query_str = parsed_filter["query"]
            if "author:" in query_str:
                author = query_str.replace("author:", "").strip()
                return {"author": author}

        # Normalize $or to $in for tags (they're functionally equivalent for our use case)
        if "tags" in parsed_filter and isinstance(parsed_filter["tags"], dict):
            if "$or" in parsed_filter["tags"]:
                parsed_filter["tags"]["$in"] = parsed_filter["tags"].pop("$or")

        # Preserve other complex structures
        return parsed_filter

    def _rule_based_extraction(self, query: str) -> Dict[str, Any]:
        """Enhanced rule-based extraction when LLMs fail - works with real data."""
        query_lower = query.lower()
        filter_dict = {}

        # Extract author names (real authors from your data)
        real_authors = ["Jane Doe", "Mary Poppins", "Akainu"]
        for author in real_authors:
            if author.lower() in query_lower:
                filter_dict["author"] = author
                break

        # Extract individual player tags and determine boolean logic
        # Map player names to their hashtag equivalents
        player_tags = []

        # Check for individual players
        if "rohit sharma" in query_lower or "rohit" in query_lower:
            player_tags.append("#RohitSharma")
        if "shubman gill" in query_lower or "shubman" in query_lower:
            player_tags.append("#ShubmanGill")
        if "virat kohli" in query_lower or "virat" in query_lower:
            player_tags.append("#ViratKohli")
        if "shikhar dhawan" in query_lower or "shikhar" in query_lower:
            player_tags.append("#ShikharDhawan")

        # Determine boolean logic based on query phrasing
        if len(player_tags) > 1:
            # Check for AND logic indicators
            and_indicators = [
                "containing both", "with both", "having both", "includes both",
                "posts containing both", "articles containing both",
                "posts with both", "articles with both"
            ]

            use_and_logic = any(indicator in query_lower for indicator in and_indicators)

            if use_and_logic:
                # AND logic: posts must contain ALL these tags
                filter_dict = {"$and": [{"tags": tag} for tag in player_tags]}
            else:
                # OR logic (default): posts about ANY of these players
                filter_dict["tags"] = {"$in": player_tags}
        elif len(player_tags) == 1:
            # Single player - search for articles containing this tag
            filter_dict["tags"] = player_tags[0]
        else:
            # Check for team/topic terms
            if "mumbai indians" in query_lower or "mi" in query_lower:
                filter_dict["tags"] = "#MumbaiIndians"
            elif "rajasthan royals" in query_lower or "rr" in query_lower:
                filter_dict["tags"] = "#RajasthanRoyals"
            elif "gujarat titans" in query_lower or "gt" in query_lower:
                filter_dict["tags"] = "#GujaratTitans"
            elif "ipl 2025" in query_lower or "ipl2025" in query_lower:
                filter_dict["tags"] = "#IPL2025"
            elif "ipl" in query_lower:
                filter_dict["tags"] = "#IPL2025"
            elif "cricket" in query_lower:
                filter_dict["tags"] = "#RohitSharma"  # Default to a cricket-related tag

        # Extract dates
        date_filter = self._extract_date_filter(query)
        if date_filter:
            filter_dict["publishedTimestamp"] = date_filter

        return filter_dict

    def _extract_date_filter(self, query: str) -> Optional[Dict[str, int]]:
        """Extract date filters from query using Unix timestamp format."""
        import datetime
        query_lower = query.lower()
        current_year = 2025  # Current year

        # Handle "last year"
        if "last year" in query_lower:
            # Convert to Unix timestamps
            start_date = datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)
            end_date = datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc)
            return {
                "$gte": int(start_date.timestamp()),
                "$lt": int(end_date.timestamp())
            }

        # Handle "this year" or "2025"
        if "this year" in query_lower or "2025" in query:
            # Convert to Unix timestamps
            start_date = datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc)
            end_date = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
            return {
                "$gte": int(start_date.timestamp()),
                "$lt": int(end_date.timestamp())
            }

        # Handle specific months
        months = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12
        }

        for month_name, month_num in months.items():
            if month_name in query_lower:
                year_match = re.search(r'\b(20\d{2})\b', query)
                year = int(year_match.group(1)) if year_match else current_year

                # Convert to Unix timestamps
                start_date = datetime.datetime(year, month_num, 1, tzinfo=datetime.timezone.utc)
                # Get last day of month
                if month_num == 12:
                    end_date = datetime.datetime(year + 1, 1, 1, tzinfo=datetime.timezone.utc)
                else:
                    end_date = datetime.datetime(year, month_num + 1, 1, tzinfo=datetime.timezone.utc)

                return {
                    "$gte": int(start_date.timestamp()),
                    "$lt": int(end_date.timestamp())
                }

        # Handle relative dates
        if "last month" in query_lower:
            # Calculate last month from current date
            current_date = datetime.datetime(2025, 7, 14, tzinfo=datetime.timezone.utc)  # Current date
            if current_date.month == 1:
                last_month = 12
                last_year = current_date.year - 1
            else:
                last_month = current_date.month - 1
                last_year = current_date.year

            start_date = datetime.datetime(last_year, last_month, 1, tzinfo=datetime.timezone.utc)
            if last_month == 12:
                end_date = datetime.datetime(last_year + 1, 1, 1, tzinfo=datetime.timezone.utc)
            else:
                end_date = datetime.datetime(last_year, last_month + 1, 1, tzinfo=datetime.timezone.utc)

            return {
                "$gte": int(start_date.timestamp()),
                "$lt": int(end_date.timestamp())
            }

        # Handle "previous X days"
        if "previous" in query_lower and "days" in query_lower:
            days_match = re.search(r'previous\s+(\d+)\s+days', query_lower)
            if days_match:
                days = int(days_match.group(1))
                current_date = datetime.datetime(2025, 7, 14, tzinfo=datetime.timezone.utc)
                start_date = current_date - datetime.timedelta(days=days)
                return {
                    "$gte": int(start_date.timestamp()),
                    "$lt": int(current_date.timestamp())
                }

        # Handle "last week"
        if "last week" in query_lower:
            current_date = datetime.datetime(2025, 7, 14, tzinfo=datetime.timezone.utc)
            start_date = current_date - datetime.timedelta(days=7)
            return {
                "$gte": int(start_date.timestamp()),
                "$lt": int(current_date.timestamp())
            }

        return None

    def _validate_filter(self, filter_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the generated filter."""
        if not filter_dict:
            return {}

        # Handle root-level logical operators first
        if "$and" in filter_dict or "$or" in filter_dict:
            # For root-level $and/$or, return as-is after validating structure
            return filter_dict

        # Ensure proper structure for regular filters
        validated = {}

        if "author" in filter_dict:
            author_value = filter_dict["author"]
            if isinstance(author_value, dict):
                # Handle operators like $eq, $ne
                validated["author"] = author_value
            else:
                # Simple string value
                validated["author"] = str(author_value)

        if "tags" in filter_dict:
            tags_value = filter_dict["tags"]
            if isinstance(tags_value, dict):
                # Handle all supported operators: $in, $nin, $or, $and, $eq, $ne
                supported_ops = ["$in", "$nin", "$or", "$and", "$eq", "$ne"]
                if any(op in tags_value for op in supported_ops):
                    validated["tags"] = tags_value
                else:
                    # Unknown dict format, keep as-is
                    validated["tags"] = tags_value
            elif isinstance(tags_value, list):
                validated["tags"] = {"$in": tags_value}
            elif isinstance(tags_value, str):
                # Handle string-based tags (exact match)
                validated["tags"] = tags_value

        # Handle all date field formats
        date_fields = ["publishedDate", "publishedTimestamp", "published_year", "published_month", "published_day"]
        for field in date_fields:
            if field in filter_dict:
                validated[field] = filter_dict[field]

        return validated


# Test function with real queries
def test_agent():
    """Test the agent with real queries."""
    agent = SimpleNLAgent()

    # Test with real data-based queries including boolean logic
    test_queries = [
        "articles by Jane Doe",
        "posts about Rohit Sharma",
        "posts about Rohit Sharma and Shubman Gill",  # Should be OR logic
        "posts containing both Rohit Sharma and Shubman Gill",  # Should be AND logic
        "posts related to Rohit Sharma, Shubman Gill",  # Should be OR logic
        "posts with both Rohit Sharma and Shubman Gill",  # Should be AND logic
        "IPL articles from May 2025",
        "anything by Mary Poppins about cricket",
        "Shubman Gill articles from this year"
    ]

    print("Testing Simple NL Agent with Real Data:")
    print("=" * 60)

    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        filter_result = agent.generate_pinecone_filter(query)
        print("Generated Filter:")
        print(json.dumps(filter_result, indent=2))
        print("-" * 40)


if __name__ == "__main__":
    test_agent()
