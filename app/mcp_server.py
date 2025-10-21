"""FastMCP 2.0 server for PDF processing tools"""
import base64
from typing import Optional
from mcp.server.fastmcp import FastMCP
from app.core.pdf_processor import PDFProcessor
from app.models.schemas import OutputFormat

# Initialize MCP server
mcp = FastMCP("pdf-parse-transform")
pdf_processor = PDFProcessor()


@mcp.tool()
def parse_pdf(
    pdf_base64: str,
    output_format: str = "json",
    force_ocr: bool = False,
    include_metadata: bool = True
) -> dict:
    """
    Parse a PDF file and return content in specified format.
    
    Args:
        pdf_base64: Base64-encoded PDF file content
        output_format: Output format (plain_text, markdown, csv, xml, json)
        force_ocr: Force OCR processing even for text-based PDFs
        include_metadata: Include document metadata in output
    
    Returns:
        Dictionary with parsed content and metadata
    """
    try:
        # Decode base64 PDF
        pdf_bytes = base64.b64decode(pdf_base64)
        
        # Validate output format
        try:
            format_enum = OutputFormat(output_format)
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid output format: {output_format}. Valid formats: plain_text, markdown, csv, xml, json"
            }
        
        # Process PDF
        content, quality, metadata = pdf_processor.process(
            pdf_bytes=pdf_bytes,
            output_format=format_enum,
            force_ocr=force_ocr,
            include_metadata=include_metadata
        )
        
        return {
            "success": True,
            "quality_assessment": quality.value,
            "output_format": output_format,
            "content": content,
            "metadata": metadata if include_metadata else None
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def list_supported_formats() -> dict:
    """
    List all supported output formats for PDF parsing.
    
    Returns:
        Dictionary with available formats and their descriptions
    """
    return {
        "formats": [
            {
                "name": format_type.value,
                "description": f"Export as {format_type.value.replace('_', ' ')}"
            }
            for format_type in OutputFormat
        ]
    }


@mcp.tool()
def evaluate_pdf_quality(pdf_base64: str) -> dict:
    """
    Evaluate PDF quality without processing the full content.
    Determines if the PDF is text-based, scanned, or mixed.
    
    Args:
        pdf_base64: Base64-encoded PDF file content
    
    Returns:
        Dictionary with quality assessment and metadata
    """
    try:
        # Decode base64 PDF
        pdf_bytes = base64.b64decode(pdf_base64)
        
        # Evaluate quality
        from app.core.quality_evaluator import QualityEvaluator
        evaluator = QualityEvaluator()
        quality, metadata = evaluator.evaluate(pdf_bytes)
        
        return {
            "success": True,
            "quality": quality.value,
            "metadata": metadata
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # Run MCP server
    mcp.run()
