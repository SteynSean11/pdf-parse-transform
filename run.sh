#!/bin/bash
# Start script for PDF Parse Transform services

echo "Starting PDF Parse Transform services..."

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "Running in Docker container"
    exec "$@"
else
    echo "Running locally"
    
    # Check for Python
    if ! command -v python3 &> /dev/null; then
        echo "Python 3 is not installed. Please install Python 3.9 or higher."
        exit 1
    fi
    
    # Check for Tesseract
    if ! command -v tesseract &> /dev/null; then
        echo "Tesseract OCR is not installed. Please install tesseract-ocr."
        exit 1
    fi
    
    # Install dependencies if needed
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    # Start the FastAPI server
    echo "Starting FastAPI server on http://localhost:8000"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi
