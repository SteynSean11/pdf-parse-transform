# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PDF processing and OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Configure Poetry to not create virtual environments
RUN poetry config virtualenvs.create false

# Copy Poetry dependency files
COPY pyproject.toml poetry.lock* ./

# Install Python dependencies using Poetry
RUN poetry install --no-root --no-dev

# Copy validation script and make it executable
COPY validate.sh .
RUN chmod +x validate.sh

# Copy application code
COPY app/ ./app/

# Expose FastAPI port
EXPOSE 8000

# Expose MCP port (if needed)
EXPOSE 8001

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default command (can be overridden in docker-compose)
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
