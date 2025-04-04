"""
Unit tests for the Redmine API client
"""

import pytest
from unittest.mock import MagicMock, patch
import json
from app.redmine_api import RedmineAPI

@pytest.fixture
def mock_response():
    """Create a mock response object for testing"""
    mock = MagicMock()
    mock.status_code = 200
    mock.text = json.dumps({"test": "data"})
    mock.json.return_value = {"test": "data"}
    return mock

@pytest.fixture
def redmine_api():
    """Create a RedmineAPI instance for testing"""
    return RedmineAPI("http://localhost:3000", "dummy_api_key")

def test_init():
    """Test RedmineAPI initialization"""
    api = RedmineAPI("http://localhost:3000", "dummy_api_key")
    assert api.base_url == "http://localhost:3000/"
    assert api.api_key == "dummy_api_key"
    assert api.headers["Content-Type"] == "application/json"
    assert api.headers["X-Redmine-API-Key"] == "dummy_api_key"

def test_init_with_env_vars(monkeypatch):
    """Test RedmineAPI initialization with environment variables"""
    monkeypatch.setenv("REDMINE_URL", "http://redmine.example.com")
    monkeypatch.setenv("REDMINE_API_KEY", "env_api_key")
    
    api = RedmineAPI()
    assert api.base_url == "http://redmine.example.com/"
    assert api.api_key == "env_api_key"

@patch("requests.get")
def test_get_issues(mock_get, redmine_api, mock_response):
    """Test get_issues method"""
    mock_response.json.return_value = {"issues": [{"id": 1, "subject": "Test Issue"}]}
    mock_get.return_value = mock_response
    
    issues = redmine_api.get_issues(project_id=1)
    
    assert issues == [{"id": 1, "subject": "Test Issue"}]
    mock_get.assert_called_once()
    assert "projects" in mock_get.call_args[0][0]

@patch("requests.get")
def test_get_issue(mock_get, redmine_api, mock_response):
    """Test get_issue method"""
    mock_response.json.return_value = {"issue": {"id": 1, "subject": "Test Issue"}}
    mock_get.return_value = mock_response
    
    issue = redmine_api.get_issue(1)
    
    assert issue == {"id": 1, "subject": "Test Issue"}
    mock_get.assert_called_once()
    assert "issues/1.json" in mock_get.call_args[0][0]

@patch("requests.post")
def test_create_issue(mock_post, redmine_api, mock_response):
    """Test create_issue method"""
    mock_response.json.return_value = {"issue": {"id": 1, "subject": "New Issue"}}
    mock_post.return_value = mock_response
    
    result = redmine_api.create_issue(
        project_id=1,
        subject="New Issue",
        description="Description",
        tracker_id=2,
        category_id=3
    )
    
    assert result == {"issue": {"id": 1, "subject": "New Issue"}}
    mock_post.assert_called_once()
    assert "issues.json" in mock_post.call_args[0][0]
    assert mock_post.call_args[1]["json"]["issue"]["subject"] == "New Issue"

@patch("requests.put")
def test_update_issue(mock_put, redmine_api, mock_response):
    """Test update_issue method"""
    mock_put.return_value = mock_response
    
    result = redmine_api.update_issue(
        issue_id=1,
        subject="Updated Issue",
        status_id=2
    )
    
    assert result == {"success": True, "message": "Issue #1 updated successfully"}
    mock_put.assert_called_once()
    assert "issues/1.json" in mock_put.call_args[0][0]
    assert mock_put.call_args[1]["json"]["issue"]["subject"] == "Updated Issue"

@patch("requests.put")
def test_create_wiki_page(mock_put, redmine_api, mock_response):
    """Test create_wiki_page method"""
    mock_response.json.return_value = {"wiki_page": {"title": "TestPage", "text": "Content"}}
    mock_put.return_value = mock_response
    
    result = redmine_api.create_wiki_page(
        project_id=1,
        title="TestPage",
        text="Content",
        comments="Created page"
    )
    
    assert result == {"title": "TestPage", "text": "Content"}
    mock_put.assert_called_once()
    assert "projects/1/wiki/TestPage.json" in mock_put.call_args[0][0]
    assert mock_put.call_args[1]["json"]["wiki_page"]["text"] == "Content"
