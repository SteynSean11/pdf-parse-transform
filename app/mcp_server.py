"""MCP 2.0 server for PDF processing tools

NOTE: The MCP library (mcp==1.10.0) currently has compatibility issues with Python 3.12.
The server structure is provided for future use when the MCP library is updated.
For now, use the FastAPI REST API which provides full functionality.

The MCP server would expose these tools:
- parse_pdf: Parse a PDF and return content in specified format
- list_supported_formats: List available output formats
- evaluate_pdf_quality: Assess PDF quality without full processing
"""
import base64
import json
from typing import Dict, Any
from app.core.pdf_processor import PDFProcessor
from app.models.schemas import OutputFormat


class PDFMCPTools:
    """MCP tool implementations for PDF processing"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
    
    def parse_pdf(
        self,
        pdf_base64: str,
        output_format: str = "json",
        force_ocr: bool = False,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
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
            content, quality, metadata = self.pdf_processor.process(
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
    
    def list_supported_formats(self) -> Dict[str, Any]:
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
    
    def evaluate_pdf_quality(self, pdf_base64: str) -> Dict[str, Any]:
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


# Tool schema definitions for MCP integration
MCP_TOOLS_SCHEMA = {
    "tools": [
        {
            "name": "parse_pdf",
            "description": "Parse a PDF file and return content in specified format",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pdf_base64": {
                        "type": "string",
                        "description": "Base64-encoded PDF file content"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["plain_text", "markdown", "csv", "xml", "json"],
                        "default": "json",
                        "description": "Output format"
                    },
                    "force_ocr": {
                        "type": "boolean",
                        "default": False,
                        "description": "Force OCR processing"
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include metadata"
                    }
                },
                "required": ["pdf_base64"]
            }
        },
        {
            "name": "list_supported_formats",
            "description": "List all supported output formats for PDF parsing",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "evaluate_pdf_quality",
            "description": "Evaluate PDF quality to determine if it's text-based, scanned, or mixed",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pdf_base64": {
                        "type": "string",
                        "description": "Base64-encoded PDF file content"
                    }
                },
                "required": ["pdf_base64"]
            }
        }
    ]
}


if __name__ == "__main__":
    print("MCP Server for PDF Parse Transform")
    print("=" * 50)
    print("\nNote: MCP library has compatibility issues with Python 3.12")
    print("Use the FastAPI REST API instead: http://localhost:8000/api/v1/")
    print("\nAvailable tools:")
    for tool in MCP_TOOLS_SCHEMA["tools"]:
        print(f"  - {tool['name']}: {tool['description']}")
    print("\nTo test the tool implementations, use the PDFMCPTools class directly.")
    print("\nExample:")
    print("  from app.mcp_server import PDFMCPTools")
    print("  tools = PDFMCPTools()")
    print("  result = tools.list_supported_formats()")
    print("  print(result)")
