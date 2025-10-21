"""Tests for format exporter"""
import pytest
from app.core.format_exporter import FormatExporter
from app.models.schemas import ParsedContent, OutputFormat


@pytest.fixture
def sample_content():
    """Sample parsed content for testing"""
    return ParsedContent(
        title="Test Document",
        pages=[
            {"page_number": 1, "text": "First page content"},
            {"page_number": 2, "text": "Second page content"}
        ],
        metadata={"author": "Test Author", "pages": 2},
        text_content="First page content\n\nSecond page content",
        page_count=2
    )


def test_export_plain_text(sample_content):
    """Test plain text export"""
    exporter = FormatExporter()
    result = exporter.export(sample_content, OutputFormat.PLAIN_TEXT, include_metadata=False)
    assert "First page content" in result
    assert "Second page content" in result


def test_export_markdown(sample_content):
    """Test markdown export"""
    exporter = FormatExporter()
    result = exporter.export(sample_content, OutputFormat.MARKDOWN, include_metadata=True)
    assert "# Test Document" in result
    assert "## Metadata" in result
    assert "### Page 1" in result
    assert "### Page 2" in result


def test_export_csv(sample_content):
    """Test CSV export"""
    exporter = FormatExporter()
    result = exporter.export(sample_content, OutputFormat.CSV, include_metadata=False)
    assert "Page Number,Content" in result
    assert "1," in result
    assert "2," in result


def test_export_xml(sample_content):
    """Test XML export"""
    exporter = FormatExporter()
    result = exporter.export(sample_content, OutputFormat.XML, include_metadata=True)
    assert "<document>" in result
    assert "<title>Test Document</title>" in result
    assert "<metadata>" in result
    assert '<page number="1">' in result


def test_export_json(sample_content):
    """Test JSON export"""
    import json
    exporter = FormatExporter()
    result = exporter.export(sample_content, OutputFormat.JSON, include_metadata=True)
    data = json.loads(result)
    assert data["title"] == "Test Document"
    assert data["page_count"] == 2
    assert "metadata" in data
    assert len(data["pages"]) == 2
