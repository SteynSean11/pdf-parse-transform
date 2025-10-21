# Examples

This directory contains example scripts demonstrating how to use the PDF Parse Transform application.

## demo.py

A comprehensive demonstration script that shows:

1. **REST API Usage**
   - Health checks
   - Listing available formats
   - Parsing PDFs to different formats (JSON, Markdown, CSV)

2. **MCP Tool Implementations**
   - Using the PDFMCPTools class directly
   - Evaluating PDF quality
   - Parsing PDFs programmatically

3. **Core Module Usage**
   - Using the PDFProcessor directly
   - Bypassing the API layer for embedded use

### Running the Demo

Make sure the FastAPI server is running:
```bash
cd ..
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Then run the demo in another terminal:
```bash
python examples/demo.py
```

The demo will:
- Create a sample PDF document
- Test all available output formats
- Demonstrate different ways to use the application

## Creating Your Own Examples

You can create additional example scripts using the patterns shown in `demo.py`. The application supports three main integration patterns:

### 1. REST API (Recommended for external applications)
```python
import requests

with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/parse',
        files={'file': f},
        data={'output_format': 'json'}
    )
    result = response.json()
```

### 2. MCP Tools (For programmatic use)
```python
from app.mcp_server import PDFMCPTools
import base64

tools = PDFMCPTools()
with open('document.pdf', 'rb') as f:
    pdf_base64 = base64.b64encode(f.read()).decode()
result = tools.parse_pdf(pdf_base64, output_format='markdown')
```

### 3. Core Modules (For embedded use)
```python
from app.core.pdf_processor import PDFProcessor
from app.models.schemas import OutputFormat

processor = PDFProcessor()
with open('document.pdf', 'rb') as f:
    content, quality, metadata = processor.process(
        pdf_bytes=f.read(),
        output_format=OutputFormat.JSON
    )
```
