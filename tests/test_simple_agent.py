"""
Test cases for the simple agent functionality.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the root directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from simple_agent import SimpleNLAgent


class TestSimpleNLAgent:
    """Test cases for SimpleNLAgent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = SimpleNLAgent()
    
    def test_extract_author(self):
        """Test author extraction from queries."""
        test_cases = [
            ("articles by John Doe", "John Doe"),
            ("posts from Alice Smith", "Alice Smith"),
            ("content by Dr. Jane Wilson", "Dr. Jane Wilson"),
            ("anything by test author", "test author"),
        ]
        
        for query, expected_author in test_cases:
            result = self.agent.extract_author(query)
            assert result == expected_author, f"Failed for query: {query}"
    
    def test_extract_tags(self):
        """Test tag extraction from queries."""
        test_cases = [
            ("articles about machine learning", ["machine learning"]),
            ("posts tagged with AI and ML", ["AI", "ML"]),
            ("content on vector search", ["vector search"]),
            ("articles about python programming", ["python", "programming"]),
        ]
        
        for query, expected_tags in test_cases:
            result = self.agent.extract_tags(query)
            # Check if all expected tags are found
            for tag in expected_tags:
                assert any(tag.lower() in found_tag.lower() for found_tag in result), \
                    f"Tag '{tag}' not found in result {result} for query: {query}"
    
    def test_extract_date_info(self):
        """Test date extraction from queries."""
        test_cases = [
            ("articles from 2023", {"published_year": {"$eq": 2023}}),
            ("posts from last year", None),  # Relative dates might not be handled
            ("content from June 2023", {"published_year": {"$eq": 2023}, "published_month": {"$eq": 6}}),
        ]
        
        for query, expected_result in test_cases:
            result = self.agent.extract_date_info(query)
            if expected_result is None:
                # For cases where we don't expect a result
                continue
            else:
                assert result is not None, f"Expected date info for query: {query}"
    
    def test_process_query_integration(self):
        """Test the complete query processing pipeline."""
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = {
                "filter": {"author": "John Doe", "tags": {"$in": ["AI"]}},
                "confidence": 0.9
            }
            
            result = self.agent.process_query("articles by John Doe about AI")
            
            assert "filter" in result
            assert "confidence" in result
            assert "processing_time" in result
            assert result["confidence"] >= 0.0
            assert result["confidence"] <= 1.0
    
    def test_build_filter(self):
        """Test filter building functionality."""
        # Test with author only
        filter_result = self.agent.build_filter(
            author="John Doe",
            tags=None,
            date_filter=None
        )
        assert filter_result["author"] == "John Doe"
        
        # Test with tags only
        filter_result = self.agent.build_filter(
            author=None,
            tags=["AI", "ML"],
            date_filter=None
        )
        assert "tags" in filter_result
        assert "$in" in filter_result["tags"]
        
        # Test with date filter
        date_filter = {"published_year": {"$eq": 2023}}
        filter_result = self.agent.build_filter(
            author=None,
            tags=None,
            date_filter=date_filter
        )
        assert "published_year" in filter_result


if __name__ == "__main__":
    pytest.main([__file__])
