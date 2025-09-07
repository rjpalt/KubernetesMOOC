"""
Basic tests for the authentication sidecar.
These tests focus on the Flask application logic rather than Azure integration.
"""

import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest


# Import the app after mocking Azure dependencies
@patch("app.DefaultAzureCredential")
def test_health_endpoint_with_valid_token(mock_credential):
    """Test health endpoint returns healthy status with valid token"""
    # Mock Azure credential and token response
    mock_token_response = Mock()
    mock_token_response.token = "test-token"
    mock_token_response.expires_on = (datetime.now() + timedelta(hours=1)).timestamp()

    mock_credential.return_value.get_token.return_value = mock_token_response

    # Import app after mocking
    from app import app

    with app.test_client() as client:
        response = client.get("/health")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert data["token_valid"] is True
        assert "expires_at" in data
        assert "timestamp" in data


@patch("app.DefaultAzureCredential")
def test_health_endpoint_with_invalid_token(mock_credential):
    """Test health endpoint returns unhealthy status when token is invalid"""
    # Mock credential failure
    mock_credential.return_value.get_token.side_effect = Exception("Auth failed")

    # This should cause the app to exit, so we need to test differently
    # For now, we'll test the behavior when the app is running but token becomes invalid
    pass  # TODO: Implement test for unhealthy state


@patch("app.DefaultAzureCredential")
@patch("app.requests")
def test_query_proxy_success(mock_requests, mock_credential):
    """Test successful query proxy to Azure"""
    # Mock Azure credential
    mock_token_response = Mock()
    mock_token_response.token = "test-token"
    mock_token_response.expires_on = (datetime.now() + timedelta(hours=1)).timestamp()
    mock_credential.return_value.get_token.return_value = mock_token_response

    # Mock requests response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success", "data": []}
    mock_requests.post.return_value = mock_response

    from app import app

    with app.test_client() as client:
        response = client.post("/api/v1/query", data={"query": "up"})

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"


@patch("app.DefaultAzureCredential")
def test_query_proxy_missing_query(mock_credential):
    """Test query proxy returns error when query parameter is missing"""
    # Mock Azure credential
    mock_token_response = Mock()
    mock_token_response.token = "test-token"
    mock_token_response.expires_on = (datetime.now() + timedelta(hours=1)).timestamp()
    mock_credential.return_value.get_token.return_value = mock_token_response

    from app import app

    with app.test_client() as client:
        response = client.post("/api/v1/query", data={})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Missing query parameter" in data["error"]


if __name__ == "__main__":
    pytest.main([__file__])
