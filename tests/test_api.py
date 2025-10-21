"""Tests for API endpoints"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["service"] == "PDF Parse Transform"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_formats():
    """Test list formats endpoint"""
    response = client.get("/api/v1/formats")
    assert response.status_code == 200
    data = response.json()
    assert "formats" in data
    assert len(data["formats"]) == 5  # Should have 5 formats
    
    format_names = [f["name"] for f in data["formats"]]
    assert "plain_text" in format_names
    assert "markdown" in format_names
    assert "csv" in format_names
    assert "xml" in format_names
    assert "json" in format_names


def test_parse_pdf_no_file():
    """Test parse endpoint without file"""
    response = client.post("/api/v1/parse")
    assert response.status_code == 422  # Validation error
