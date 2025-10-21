"""API routes for PDF processing"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.models.schemas import PDFParseResponse, OutputFormat, PDFParseRequest
from app.core.pdf_processor import PDFProcessor

router = APIRouter()
pdf_processor = PDFProcessor()


@router.post("/parse", response_model=PDFParseResponse)
async def parse_pdf(
    file: UploadFile = File(..., description="PDF file to parse"),
    output_format: OutputFormat = Form(default=OutputFormat.JSON, description="Output format"),
    force_ocr: bool = Form(default=False, description="Force OCR processing"),
    include_metadata: bool = Form(default=True, description="Include metadata in output")
):
    """
    Parse a PDF file and return content in specified format
    
    - **file**: PDF file to process
    - **output_format**: Desired output format (plain_text, markdown, csv, xml, json)
    - **force_ocr**: Force OCR even for text-based PDFs
    - **include_metadata**: Include document metadata in output
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read PDF file
        pdf_bytes = await file.read()
        
        if len(pdf_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty PDF file")
        
        # Process PDF
        content, quality, metadata = pdf_processor.process(
            pdf_bytes=pdf_bytes,
            output_format=output_format,
            force_ocr=force_ocr,
            include_metadata=include_metadata
        )
        
        return PDFParseResponse(
            success=True,
            quality_assessment=quality,
            output_format=output_format,
            content=content,
            metadata=metadata if include_metadata else None
        )
        
    except Exception as e:
        return PDFParseResponse(
            success=False,
            quality_assessment="text_based",  # Default value for error case
            output_format=output_format,
            content="",
            error=str(e)
        )


@router.post("/export-csv", response_model=PDFParseResponse)
async def export_csv(
    file: UploadFile = File(..., description="PDF file to parse and export as CSV"),
    force_ocr: bool = Form(default=False, description="Force OCR processing"),
    include_metadata: bool = Form(default=True, description="Include metadata in output")
):
    """
    Parse a PDF file and return content as CSV format
    
    - **file**: PDF file to process
    - **force_ocr**: Force OCR even for text-based PDFs
    - **include_metadata**: Include document metadata in output
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read PDF file
        pdf_bytes = await file.read()
        
        if len(pdf_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty PDF file")
        
        # Process PDF
        content, quality, metadata = pdf_processor.process(
            pdf_bytes=pdf_bytes,
            output_format=OutputFormat.CSV,  # Force CSV output
            force_ocr=force_ocr,
            include_metadata=include_metadata
        )
        
        return PDFParseResponse(
            success=True,
            quality_assessment=quality,
            output_format=OutputFormat.CSV,
            content=content,
            metadata=metadata if include_metadata else None
        )
        
    except Exception as e:
        return PDFParseResponse(
            success=False,
            quality_assessment="text_based",  # Default value for error case
            output_format=OutputFormat.CSV,
            content="",
            error=str(e)
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "pdf-parse-transform"}


@router.get("/formats")
async def list_formats():
    """List supported output formats"""
    return {
        "formats": [
            {
                "name": format_type.value,
                "description": f"Export as {format_type.value.replace('_', ' ')}"
            }
            for format_type in OutputFormat
        ]
    }
