"""Main PDF processing orchestrator"""
from typing import Tuple
from app.models.schemas import PDFQuality, ParsedContent, OutputFormat
from app.core.quality_evaluator import QualityEvaluator
from app.core.text_extractor import TextExtractor
from app.core.ocr_processor import OCRProcessor
from app.core.content_normalizer import ContentNormalizer
from app.core.format_exporter import FormatExporter


class PDFProcessor:
    """Main orchestrator for PDF processing"""
    
    def __init__(self):
        self.quality_evaluator = QualityEvaluator()
        self.text_extractor = TextExtractor()
        self.ocr_processor = OCRProcessor()
        self.content_normalizer = ContentNormalizer()
        self.format_exporter = FormatExporter()
    
    def process(
        self,
        pdf_bytes: bytes,
        output_format: OutputFormat = OutputFormat.JSON,
        force_ocr: bool = False,
        include_metadata: bool = True
    ) -> Tuple[str, PDFQuality, dict]:
        """
        Process PDF and export to specified format
        
        Args:
            pdf_bytes: PDF file content as bytes
            output_format: Desired output format
            force_ocr: Force OCR even for text-based PDFs
            include_metadata: Include metadata in output
            
        Returns:
            Tuple of (formatted_content, quality_assessment, metadata)
        """
        # Evaluate PDF quality
        quality, metadata = self.quality_evaluator.evaluate(pdf_bytes)
        
        # Extract content based on quality and settings
        if force_ocr or quality == PDFQuality.SCANNED:
            parsed_content = self.ocr_processor.process(pdf_bytes)
        elif quality == PDFQuality.MIXED:
            # For mixed PDFs, try text extraction first, fall back to OCR if needed
            try:
                parsed_content = self.text_extractor.extract(pdf_bytes)
                # Check if we got meaningful content
                if len(parsed_content.text_content.strip()) < 100:
                    parsed_content = self.ocr_processor.process(pdf_bytes)
            except Exception:
                parsed_content = self.ocr_processor.process(pdf_bytes)
        else:
            # Text-based PDF
            parsed_content = self.text_extractor.extract(pdf_bytes)
        
        # Normalize content
        normalized_content = self.content_normalizer.normalize(parsed_content)
        
        # Export to requested format
        formatted_output = self.format_exporter.export(
            normalized_content,
            output_format,
            include_metadata
        )
        
        return formatted_output, quality, metadata
