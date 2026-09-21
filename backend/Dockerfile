FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PyMuPDF and ChromaDB (C++ compiler needed for hnswlib)
RUN apt-get update && apt-get install -y \
    libmupdf-dev \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Copy built frontend static files
COPY static/ ./static/

# Create data directories
RUN mkdir -p /data/uploads /data/chroma_db

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
