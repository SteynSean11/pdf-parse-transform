# Gemini Context: pdf-parse-transform

This document provides context for the `pdf-parse-transform` project, a Python application designed to intelligently parse and transform PDF documents.

## Project Overview

The `pdf-parse-transform` project is a Python-based service that provides a RESTful API for converting PDF files into various structured formats. It automatically determines whether to use direct text extraction or Optical Character Recognition (OCR) based on the quality of the PDF.

The core of the application is built with **FastAPI**, a modern, high-performance Python web framework. It is designed to be run as a containerized service using **Docker**.

### Key Technologies

*   **Backend:** Python 3.9+, FastAPI, Uvicorn
*   **PDF Processing:**
    *   `pdfplumber`: For extracting text from text-based PDFs.
    *   `pytesseract` (Tesseract OCR): For extracting text from scanned or image-based PDFs.
    *   `pdf2image`: For converting PDF pages to images for OCR.
    *   `PyPDF2`: For basic PDF operations.
*   **Data Handling:**
    *   `Pydantic`: For data validation and settings management.
    *   `pandas`: For data manipulation, particularly for CSV export.
    *   `lxml`: For XML export.
*   **API Documentation:** The API is self-documenting via Swagger UI and ReDoc.
*   **Containerization:** Docker, Docker Compose
*   **Testing:** `pytest` is used for unit and integration testing.

### Architecture

The application follows a modular architecture:

*   **`app/main.py`**: The FastAPI application entry point.
*   **`app/api/routes.py`**: Defines the API endpoints for parsing, health checks, and listing formats.
*   **`app/core/pdf_processor.py`**: The main orchestrator that handles the PDF processing workflow.
*   **`app/core/quality_evaluator.py`**: Analyzes the PDF to decide between text extraction and OCR.
*   **`app/core/text_extractor.py`**: Extracts text from text-based PDFs.
*   **`app/core/ocr_processor.py`**: Handles the OCR process for scanned PDFs.
*   **`app/core/content_normalizer.py`**: Standardizes the extracted content.
*   **`app/core/format_exporter.py`**: Converts the normalized content into the desired output format (JSON, CSV, etc.).
*   **`app.models.schemas.py`**: Contains the Pydantic models for API requests and responses.

## Building and Running

### Using Docker (Recommended)

The application is designed to be run with Docker and Docker Compose.

1.  **Build and run the container:**
    ```bash
    docker-compose up -d
    ```

2.  The service will be available at `http://localhost:8000`.

### Local Development

1.  **Install system dependencies:**
    *   Tesseract OCR
    *   Poppler utilities

2.  **Create a virtual environment and install Python dependencies:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Run the development server:**
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    Alternatively, you can use the provided shell script:
    ```bash
    ./run.sh
    ```

## API Usage

*   **Interactive Docs (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Main Parsing Endpoint:** `POST /api/v1/parse`
    *   This endpoint accepts a PDF file and parameters to control the parsing process (`output_format`, `force_ocr`, etc.).

**Example `curl` request:**
```bash
curl -X POST "http://localhost:8000/api/v1/parse" \
  -F "file=@/path/to/your/document.pdf" \
  -F "output_format=json"
```

## Development Conventions

### Testing

*   Tests are located in the `tests/` directory.
*   The project uses `pytest` for testing.
*   Run tests with the following command:
    ```bash
    pytest tests/ -v
    ```

### Code Style

*   The code follows standard Python conventions (PEP 8).
*   Pydantic is used for type hinting and data validation in the API layer.
