"""OCR processing module for scanned PDFs"""
import io
from typing import List
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
from app.models.schemas import ParsedContent


class OCRProcessor:
    """Processes scanned PDFs using OCR"""
    
    @staticmethod
    def process(pdf_bytes: bytes) -> ParsedContent:
        """
        Process a scanned PDF using OCR
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            ParsedContent with normalized structure
        """
        # Convert PDF to images
        images = convert_from_bytes(pdf_bytes)
        
        pages_data = []
        full_text = []
        
        for i, image in enumerate(images):
            # Perform OCR on each page
            text = pytesseract.image_to_string(image)
            
            page_data = {
                "page_number": i + 1,
                "text": text,
                "ocr_processed": True,
                "image_size": image.size
            }
            
            pages_data.append(page_data)
            full_text.append(text)
        
        return ParsedContent(
            title=None,  # OCR cannot extract title from scanned documents
            pages=pages_data,
            metadata={"ocr_processed": True, "ocr_engine": "tesseract"},
            text_content="\n\n".join(full_text),
            page_count=len(pages_data)
        )
