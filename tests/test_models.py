"""Tests for data models"""
import pytest
from app.models.schemas import (
    PDFParseRequest,
    PDFParseResponse,
    OutputFormat,
    PDFQuality,
    ParsedContent,
)


def test_output_format_enum():
    """Test OutputFormat enum"""
    assert OutputFormat.PLAIN_TEXT.value == "plain_text"
    assert OutputFormat.MARKDOWN.value == "markdown"
    assert OutputFormat.CSV.value == "csv"
    assert OutputFormat.XML.value == "xml"
    assert OutputFormat.JSON.value == "json"


def test_pdf_quality_enum():
    """Test PDFQuality enum"""
    assert PDFQuality.TEXT_BASED.value == "text_based"
    assert PDFQuality.SCANNED.value == "scanned"
    assert PDFQuality.MIXED.value == "mixed"


def test_parsed_content_model():
    """Test ParsedContent model"""
    content = ParsedContent(
        title="Test Document",
        pages=[{"page_number": 1, "text": "Test content"}],
        metadata={"author": "Test Author"},
        text_content="Test content",
        page_count=1
    )
    assert content.title == "Test Document"
    assert content.page_count == 1
    assert len(content.pages) == 1


def test_pdf_parse_request_model():
    """Test PDFParseRequest model"""
    request = PDFParseRequest(
        output_format=OutputFormat.JSON,
        force_ocr=False,
        include_metadata=True
    )
    assert request.output_format == OutputFormat.JSON
    assert request.force_ocr is False
    assert request.include_metadata is True


def test_pdf_parse_response_model():
    """Test PDFParseResponse model"""
    response = PDFParseResponse(
        success=True,
        quality_assessment=PDFQuality.TEXT_BASED,
        output_format=OutputFormat.JSON,
        content='{"test": "content"}',
        metadata={"pages": 1}
    )
    assert response.success is True
    assert response.quality_assessment == PDFQuality.TEXT_BASED
    assert response.error is None
