"""PDF quality evaluation module"""
import io
from typing import Tuple
from PyPDF2 import PdfReader
from app.models.schemas import PDFQuality


class QualityEvaluator:
    """Evaluates PDF quality to determine processing strategy"""
    
    @staticmethod
    def evaluate(pdf_bytes: bytes) -> Tuple[PDFQuality, dict]:
        """
        Evaluate PDF quality to determine if OCR is needed
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Tuple of (PDFQuality, metadata dict)
        """
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            
            metadata = {
                "page_count": len(reader.pages),
                "encrypted": reader.is_encrypted,
                "metadata": {}
            }
            
            # Extract PDF metadata
            if reader.metadata:
                metadata["metadata"] = {
                    key.replace("/", ""): value
                    for key, value in reader.metadata.items()
                    if value is not None
                }
            
            # Check if PDF has extractable text
            total_chars = 0
            text_pages = 0
            
            for page in reader.pages:
                text = page.extract_text()
                if text and text.strip():
                    total_chars += len(text.strip())
                    text_pages += 1
            
            # Determine quality based on text content
            if total_chars == 0:
                # No text found - likely scanned
                quality = PDFQuality.SCANNED
            elif text_pages == len(reader.pages):
                # All pages have text
                quality = PDFQuality.TEXT_BASED
            else:
                # Some pages have text, some don't
                quality = PDFQuality.MIXED
            
            metadata["text_chars"] = total_chars
            metadata["text_pages"] = text_pages
            metadata["quality"] = quality.value
            
            return quality, metadata
            
        except Exception as e:
            # If we can't read the PDF, assume it needs OCR
            return PDFQuality.SCANNED, {"error": str(e)}
