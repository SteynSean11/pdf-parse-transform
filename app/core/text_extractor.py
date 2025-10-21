"""Text extraction module for text-based PDFs"""
import io
from typing import Dict, Any, List
import pdfplumber
from app.models.schemas import ParsedContent


class TextExtractor:
    """Extracts text from text-based PDFs"""
    
    @staticmethod
    def extract(pdf_bytes: bytes) -> ParsedContent:
        """
        Extract text from a text-based PDF
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            ParsedContent with normalized structure
        """
        pdf_file = io.BytesIO(pdf_bytes)
        pages_data = []
        full_text = []
        
        with pdfplumber.open(pdf_file) as pdf:
            metadata = pdf.metadata or {}
            
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                
                # Extract tables if any
                tables = page.extract_tables()
                
                page_data = {
                    "page_number": i + 1,
                    "text": text,
                    "has_tables": len(tables) > 0,
                    "table_count": len(tables),
                    "tables": tables if tables else []
                }
                
                pages_data.append(page_data)
                full_text.append(text)
        
        return ParsedContent(
            title=metadata.get("Title") or metadata.get("title"),
            pages=pages_data,
            metadata=dict(metadata),
            text_content="\n\n".join(full_text),
            page_count=len(pages_data)
        )
