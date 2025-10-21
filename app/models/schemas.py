"""Pydantic schemas for request/response validation"""
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class OutputFormat(str, Enum):
    """Supported output formats"""
    PLAIN_TEXT = "plain_text"
    MARKDOWN = "markdown"
    CSV = "csv"
    XML = "xml"
    JSON = "json"


class PDFQuality(str, Enum):
    """PDF quality assessment"""
    TEXT_BASED = "text_based"
    SCANNED = "scanned"
    MIXED = "mixed"


class ParsedContent(BaseModel):
    """Normalized parsed content structure"""
    title: Optional[str] = Field(None, description="Document title")
    pages: List[Dict[str, Any]] = Field(default_factory=list, description="Page content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    text_content: str = Field("", description="Full text content")
    page_count: int = Field(0, description="Number of pages")


class PDFParseRequest(BaseModel):
    """Request model for PDF parsing"""
    output_format: OutputFormat = Field(
        default=OutputFormat.JSON,
        description="Desired output format"
    )
    force_ocr: bool = Field(
        default=False,
        description="Force OCR even for text-based PDFs"
    )
    include_metadata: bool = Field(
        default=True,
        description="Include document metadata in output"
    )


class PDFParseResponse(BaseModel):
    """Response model for PDF parsing"""
    success: bool = Field(..., description="Whether parsing was successful")
    quality_assessment: PDFQuality = Field(..., description="Assessed PDF quality")
    output_format: OutputFormat = Field(..., description="Format of the output")
    content: str = Field(..., description="Parsed and formatted content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata")
    error: Optional[str] = Field(None, description="Error message if parsing failed")
