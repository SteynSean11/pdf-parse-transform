"""
Demo script showing various ways to use the PDF Parse Transform application
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import requests
import json

def create_sample_pdf(filename):
    """Create a sample PDF for testing"""
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica", 16)
    
    # Page 1
    c.drawString(100, 750, "Sample Document")
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, "This is a demonstration PDF created for testing.")
    c.drawString(100, 690, "It contains structured content across multiple pages.")
    c.showPage()
    
    # Page 2
    c.setFont("Helvetica", 16)
    c.drawString(100, 750, "Features")
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, "- Automatic quality detection")
    c.drawString(100, 690, "- Multiple export formats")
    c.drawString(100, 660, "- OCR support for scanned documents")
    c.drawString(100, 630, "- Metadata preservation")
    c.showPage()
    
    c.save()
    print(f"Created sample PDF: {filename}")

def demo_api_usage(pdf_file):
    """Demonstrate using the REST API"""
    print("\n" + "="*60)
    print("DEMO: Using the REST API")
    print("="*60)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Test 1: Health check
    print("\n1. Health Check:")
    response = requests.get(f"{base_url}/health")
    print(f"   Status: {response.json()}")
    
    # Test 2: List formats
    print("\n2. List Available Formats:")
    response = requests.get(f"{base_url}/formats")
    formats = response.json()["formats"]
    for fmt in formats:
        print(f"   - {fmt['name']}: {fmt['description']}")
    
    # Test 3: Parse to JSON
    print("\n3. Parse PDF to JSON:")
    with open(pdf_file, 'rb') as f:
        response = requests.post(
            f"{base_url}/parse",
            files={'file': f},
            data={'output_format': 'json', 'include_metadata': True}
        )
    result = response.json()
    print(f"   Success: {result['success']}")
    print(f"   Quality: {result['quality_assessment']}")
    content = json.loads(result['content'])
    print(f"   Pages: {content['page_count']}")
    print(f"   Title: {content.get('title', 'N/A')}")
    
    # Test 4: Parse to Markdown
    print("\n4. Parse PDF to Markdown:")
    with open(pdf_file, 'rb') as f:
        response = requests.post(
            f"{base_url}/parse",
            files={'file': f},
            data={'output_format': 'markdown', 'include_metadata': True}
        )
    result = response.json()
    if result['success']:
        print("   Preview:")
        lines = result['content'].split('\n')[:10]
        for line in lines:
            print(f"   {line}")
        print("   ...")
    
    # Test 5: Parse to CSV
    print("\n5. Parse PDF to CSV:")
    with open(pdf_file, 'rb') as f:
        response = requests.post(
            f"{base_url}/parse",
            files={'file': f},
            data={'output_format': 'csv'}
        )
    result = response.json()
    if result['success']:
        print("   Preview:")
        lines = result['content'].split('\n')[:5]
        for line in lines:
            print(f"   {line}")

def demo_mcp_tools(pdf_file):
    """Demonstrate using MCP tools directly"""
    print("\n" + "="*60)
    print("DEMO: Using MCP Tool Implementations")
    print("="*60)
    
    import base64
    from app.mcp_server import PDFMCPTools
    
    # Initialize tools
    tools = PDFMCPTools()
    
    # Read and encode PDF
    with open(pdf_file, 'rb') as f:
        pdf_base64 = base64.b64encode(f.read()).decode()
    
    # Test 1: List formats
    print("\n1. List Supported Formats:")
    result = tools.list_supported_formats()
    for fmt in result['formats']:
        print(f"   - {fmt['name']}")
    
    # Test 2: Evaluate quality
    print("\n2. Evaluate PDF Quality:")
    result = tools.evaluate_pdf_quality(pdf_base64)
    print(f"   Success: {result['success']}")
    print(f"   Quality: {result['quality']}")
    print(f"   Pages: {result['metadata']['page_count']}")
    
    # Test 3: Parse PDF
    print("\n3. Parse PDF to Plain Text:")
    result = tools.parse_pdf(
        pdf_base64=pdf_base64,
        output_format='plain_text',
        include_metadata=False
    )
    if result['success']:
        print("   Preview:")
        lines = result['content'].split('\n')[:8]
        for line in lines:
            print(f"   {line}")

def demo_programmatic_usage(pdf_file):
    """Demonstrate using the core modules directly"""
    print("\n" + "="*60)
    print("DEMO: Using Core Modules Directly")
    print("="*60)
    
    from app.core.pdf_processor import PDFProcessor
    from app.models.schemas import OutputFormat
    
    # Initialize processor
    processor = PDFProcessor()
    
    # Read PDF
    with open(pdf_file, 'rb') as f:
        pdf_bytes = f.read()
    
    # Process and export to different formats
    formats_to_test = [
        (OutputFormat.PLAIN_TEXT, "Plain Text"),
        (OutputFormat.MARKDOWN, "Markdown"),
        (OutputFormat.JSON, "JSON"),
    ]
    
    for format_enum, format_name in formats_to_test:
        print(f"\n{format_name} Output:")
        content, quality, metadata = processor.process(
            pdf_bytes=pdf_bytes,
            output_format=format_enum,
            include_metadata=False
        )
        print(f"   Quality: {quality.value}")
        print(f"   Content length: {len(content)} characters")
        print(f"   Preview: {content[:100]}...")

def main():
    """Run all demos"""
    # Create sample PDF
    pdf_file = "/tmp/demo_document.pdf"
    create_sample_pdf(pdf_file)
    
    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/api/v1/health", timeout=2)
        if response.status_code == 200:
            # API is running, demo API usage
            demo_api_usage(pdf_file)
        else:
            print("\nNote: API is not running. Start it with:")
            print("  uvicorn app.main:app --host 0.0.0.0 --port 8000")
    except requests.exceptions.RequestException:
        print("\nNote: FastAPI server is not running.")
        print("Start it with: uvicorn app.main:app --host 0.0.0.0 --port 8000")
    
    # Demo MCP tools (work without API)
    demo_mcp_tools(pdf_file)
    
    # Demo programmatic usage (work without API)
    demo_programmatic_usage(pdf_file)
    
    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60)
    print("\nNext steps:")
    print("1. Try the interactive API docs: http://localhost:8000/docs")
    print("2. Use the application with your own PDFs")
    print("3. Integrate the API or tools into your applications")

if __name__ == "__main__":
    main()
