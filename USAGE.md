# Usage Guide

## Quick Start

### 1. Start the Service

Using Docker:
```bash
docker-compose up -d
```

Or locally:
```bash
chmod +x run.sh
./run.sh
```

### 2. Upload and Parse a PDF

#### Using cURL

```bash
# Parse to JSON (default)
curl -X POST "http://localhost:8000/api/v1/parse" \
  -F "file=@example.pdf"

# Parse to Markdown with metadata
curl -X POST "http://localhost:8000/api/v1/parse" \
  -F "file=@example.pdf" \
  -F "output_format=markdown" \
  -F "include_metadata=true"

# Force OCR processing
curl -X POST "http://localhost:8000/api/v1/parse" \
  -F "file=@scanned.pdf" \
  -F "output_format=plain_text" \
  -F "force_ocr=true"
```

#### Using Python

```python
import requests

# Parse PDF to JSON
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/parse',
        files={'file': f},
        data={
            'output_format': 'json',
            'include_metadata': True
        }
    )
    
result = response.json()
if result['success']:
    print("Quality:", result['quality_assessment'])
    print("Content:", result['content'])
else:
    print("Error:", result['error'])
```

#### Using JavaScript/Node.js

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function parsePDF(filePath, format = 'json') {
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));
    form.append('output_format', format);
    form.append('include_metadata', 'true');
    
    const response = await axios.post(
        'http://localhost:8000/api/v1/parse',
        form,
        { headers: form.getHeaders() }
    );
    
    return response.data;
}

parsePDF('document.pdf', 'markdown')
    .then(result => console.log(result))
    .catch(error => console.error(error));
```

## Output Format Examples

### JSON Output

```json
{
  "success": true,
  "quality_assessment": "text_based",
  "output_format": "json",
  "content": "{\"page_count\": 2, \"title\": \"Sample Document\", ...}",
  "metadata": {
    "page_count": 2,
    "text_pages": 2,
    "quality": "text_based"
  }
}
```

### Markdown Output

```markdown
# Sample Document

## Metadata
- **Author**: John Doe
- **pages**: 2

## Content

### Page 1
This is the content of page 1...

### Page 2
This is the content of page 2...
```

### XML Output

```xml
<?xml version="1.0" ?>
<document>
  <title>Sample Document</title>
  <metadata>
    <item name="Author">John Doe</item>
  </metadata>
  <pages count="2">
    <page number="1">
      <text>Page 1 content...</text>
    </page>
  </pages>
</document>
```

### CSV Output

```csv
Page Number,Content
1,"This is the content of page 1..."
2,"This is the content of page 2..."
```

## Advanced Usage

### Quality Assessment Only

To assess PDF quality without processing:

```python
# Using the MCP tool
import base64

with open('document.pdf', 'rb') as f:
    pdf_base64 = base64.b64encode(f.read()).decode()

result = mcp_client.call_tool('evaluate_pdf_quality', {
    'pdf_base64': pdf_base64
})

print(f"Quality: {result['quality']}")
print(f"Page count: {result['metadata']['page_count']}")
```

### Batch Processing

```python
import os
import requests

def process_directory(directory, output_format='json'):
    results = {}
    
    for filename in os.listdir(directory):
        if filename.lower().endswith('.pdf'):
            filepath = os.path.join(directory, filename)
            
            with open(filepath, 'rb') as f:
                response = requests.post(
                    'http://localhost:8000/api/v1/parse',
                    files={'file': f},
                    data={'output_format': output_format}
                )
                
                results[filename] = response.json()
    
    return results

# Process all PDFs in a directory
results = process_directory('./pdfs', output_format='markdown')
```

### Error Handling

```python
import requests

def safe_parse_pdf(filepath, **kwargs):
    try:
        with open(filepath, 'rb') as f:
            response = requests.post(
                'http://localhost:8000/api/v1/parse',
                files={'file': f},
                data=kwargs,
                timeout=120  # 2 minute timeout
            )
            response.raise_for_status()
            
            result = response.json()
            if not result['success']:
                print(f"Parsing failed: {result.get('error', 'Unknown error')}")
                return None
            
            return result
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

## MCP Integration

**Note**: The MCP server library currently has compatibility issues with Python 3.12. However, the MCP tool implementations are available and can be used programmatically.

### Using MCP Tool Implementations Directly

```python
import base64
from app.mcp_server import PDFMCPTools

# Initialize tools
tools = PDFMCPTools()

# Encode PDF
with open('document.pdf', 'rb') as f:
    pdf_base64 = base64.b64encode(f.read()).decode()

# Parse PDF
result = tools.parse_pdf(
    pdf_base64=pdf_base64,
    output_format='markdown',
    force_ocr=False,
    include_metadata=True
)

# List formats
formats = tools.list_supported_formats()

# Evaluate quality
quality = tools.evaluate_pdf_quality(pdf_base64)
```

### Available MCP Tool Implementations

1. **parse_pdf**
   - Parses PDF and returns content
   - Parameters: pdf_base64, output_format, force_ocr, include_metadata

2. **list_supported_formats**
   - Lists all available output formats
   - No parameters

3. **evaluate_pdf_quality**
   - Assesses PDF quality
   - Parameters: pdf_base64

For full functionality, use the FastAPI REST API at `http://localhost:8000/api/v1/`

## Tips and Best Practices

1. **Choosing Output Format**:
   - Use JSON for programmatic processing
   - Use Markdown for human-readable documents
   - Use CSV for tabular data extraction
   - Use XML for structured data interchange
   - Use plain text for simple content extraction

2. **OCR Performance**:
   - OCR is slower than text extraction
   - The system automatically chooses the best method
   - Use `force_ocr=true` only when necessary
   - For scanned documents, ensure good image quality

3. **Large Files**:
   - Processing time increases with file size
   - Consider splitting very large PDFs
   - Use batch processing for multiple files

4. **Memory Usage**:
   - OCR requires more memory than text extraction
   - Monitor system resources for large files
   - Adjust Docker memory limits if needed

## Troubleshooting

### "Tesseract not found" Error
Install Tesseract OCR:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download installer from https://github.com/UB-Mannheim/tesseract/wiki
```

### "Poppler not found" Error
Install Poppler utilities:
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler

# Windows
# Download from http://blog.alivate.com.au/poppler-windows/
```

### Connection Refused
Ensure the service is running:
```bash
docker-compose ps
# or
curl http://localhost:8000/api/v1/health
```

### Slow Processing
- Check if OCR is being used unnecessarily
- Reduce file size or split large PDFs
- Increase Docker resource limits
- Consider using `force_ocr=false` for text-based PDFs
