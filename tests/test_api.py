"""
Test cases for the FastAPI application endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from apps.fastapi_app import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


def test_query_endpoint_basic():
    """Test the basic query endpoint functionality."""
    # Mock the agent response
    with patch('src.agents.custom_agent.CustomAgent.process_query') as mock_process:
        mock_process.return_value = {
            "filter": {"author": "test"},
            "confidence": 0.9,
            "processing_time": 1.0
        }
        
        response = client.post(
            "/query",
            json={"query": "articles by test author", "agent_type": "custom"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "filter" in data
        assert "confidence" in data


def test_query_endpoint_validation():
    """Test query endpoint input validation."""
    # Test empty query
    response = client.post(
        "/query",
        json={"query": "", "agent_type": "custom"}
    )
    assert response.status_code == 422
    
    # Test invalid agent type
    response = client.post(
        "/query",
        json={"query": "test query", "agent_type": "invalid"}
    )
    assert response.status_code == 422


def test_search_endpoint_basic():
    """Test the basic search endpoint functionality."""
    with patch('src.utils.pinecone_manager.PineconeManager.search') as mock_search:
        mock_search.return_value = {
            "matches": [
                {
                    "id": "test-1",
                    "score": 0.95,
                    "metadata": {"title": "Test Article", "author": "Test Author"}
                }
            ],
            "total_results": 1
        }
        
        response = client.post(
            "/search",
            json={
                "query": "test search",
                "filter": {"author": "Test Author"},
                "top_k": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        assert "total_results" in data


if __name__ == "__main__":
    pytest.main([__file__])
