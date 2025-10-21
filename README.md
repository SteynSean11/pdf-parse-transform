# PDF Parse Transform

A Python FastAPI/FastMCP 2.0 application that intelligently parses PDF documents and transforms them into various formats. The application evaluates PDF quality to determine whether to use direct text extraction or OCR, then normalizes content into a standard structure before exporting to your chosen format.

## Features

- **Smart PDF Processing**: Automatically evaluates PDF quality (text-based, scanned, or mixed) to choose the optimal extraction method
- **Multiple Export Formats**: Support for plain text, markdown, CSV, XML, and JSON
- **OCR Support**: Handles scanned PDFs using Tesseract OCR
- **FastAPI REST API**: Modern, high-performance API with automatic documentation
- **FastMCP 2.0 Integration**: Exposes PDF processing tools via Model Context Protocol
- **Docker Support**: Fully containerized for easy deployment
- **Metadata Preservation**: Extracts and includes document metadata

## Architecture

The application consists of several core components:

- **Quality Evaluator**: Analyzes PDFs to determine processing strategy
- **Text Extractor**: Extracts text from text-based PDFs using pdfplumber
- **OCR Processor**: Processes scanned PDFs using Tesseract OCR and pdf2image
- **Content Normalizer**: Standardizes parsed content structure
- **Format Exporter**: Converts content to requested output format

## Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/SteynSean11/pdf-parse-transform.git
cd pdf-parse-transform
```

2. Build and run with docker-compose:
```bash
docker-compose up -d
```

The FastAPI service will be available at `http://localhost:8000`

### Local Installation

1. Install system dependencies (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run the FastAPI server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Usage

### REST API

#### Parse PDF

**Endpoint**: `POST /api/v1/parse`

**Parameters**:
- `file`: PDF file (multipart/form-data)
- `output_format`: Output format (plain_text, markdown, csv, xml, json) - default: json
- `force_ocr`: Force OCR processing - default: false
- `include_metadata`: Include metadata in output - default: true

**Example using curl**:
```bash
curl -X POST "http://localhost:8000/api/v1/parse" \
  -F "file=@document.pdf" \
  -F "output_format=markdown" \
  -F "include_metadata=true"
```

**Example using Python**:
```python
import requests

with open('document.pdf', 'rb') as f:
    files = {'file': f}
    data = {
        'output_format': 'json',
        'force_ocr': False,
        'include_metadata': True
    }
    response = requests.post('http://localhost:8000/api/v1/parse', files=files, data=data)
    result = response.json()
    print(result['content'])
```

#### List Supported Formats

**Endpoint**: `GET /api/v1/formats`

```bash
curl "http://localhost:8000/api/v1/formats"
```

#### Health Check

**Endpoint**: `GET /api/v1/health`

```bash
curl "http://localhost:8000/api/v1/health"
```

### MCP Tools (Tool Implementations Available)

The application provides MCP-compatible tool implementations that can be used programmatically:

**Available Tools**:
1. **parse_pdf**: Parse a PDF and return content in specified format
2. **list_supported_formats**: Get list of available output formats
3. **evaluate_pdf_quality**: Assess PDF quality without full processing

**Example using the tool implementations**:
```python
import base64
from app.mcp_server import PDFMCPTools

# Initialize tools
tools = PDFMCPTools()

# Encode PDF
with open('document.pdf', 'rb') as f:
    pdf_base64 = base64.b64encode(f.read()).decode()

# Use the parse_pdf tool
result = tools.parse_pdf(
    pdf_base64=pdf_base64,
    output_format='markdown',
    force_ocr=False,
    include_metadata=True
)

print(result['content'])
```

**Note**: The MCP server library (mcp==1.10.0) currently has compatibility issues with Python 3.12. The tool implementations are available and fully functional, but the stdio MCP server is not running. Use the FastAPI REST API for full functionality, or use the `PDFMCPTools` class directly in your Python code.

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Output Formats

### Plain Text
Raw text content extracted from the PDF.

### Markdown
Formatted markdown with headers, metadata section, and page-by-page content.

### CSV
Comma-separated values with page numbers and content.

### XML
Structured XML with document hierarchy, metadata, and page elements.

### JSON
Complete JSON representation including pages, metadata, and full text content.

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Project Structure

```
pdf-parse-transform/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── mcp_server.py        # FastMCP server
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── pdf_processor.py      # Main orchestrator
│   │   ├── quality_evaluator.py  # PDF quality assessment
│   │   ├── text_extractor.py     # Text extraction
│   │   ├── ocr_processor.py      # OCR processing
│   │   ├── content_normalizer.py # Content normalization
│   │   └── format_exporter.py    # Format conversion
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   └── utils/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_models.py
│   └── test_format_exporter.py
├── docker/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Requirements

- Python 3.9+
- Tesseract OCR
- Poppler utilities
- See `requirements.txt` for Python dependencies

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 
