# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Pillow
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libtiff-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY templates/ templates/

# Create directories for uploads, outputs, and input
RUN mkdir -p uploads outputs input

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
