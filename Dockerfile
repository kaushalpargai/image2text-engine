FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
# libgomp1 is needed for PaddleOCR/PyTorch
# libgl1 and libglib2.0-0 are often needed for opencv-python-headless (used by paddleocr)
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Copy application code
COPY . .

# Set permissions for the app user
# We need to ensure uploads/results exist and are writable
RUN mkdir -p uploads results && \
    chown -R appuser:appuser /app && \
    chmod +x start.sh && \
    sed -i 's/\r$//' start.sh

# Switch to non-root user
USER appuser

# Expose port (Documentation only, actual port set by env)
EXPOSE 8000

# Set production environment by default
ENV APP_ENV=production

# Run the application using the start script
CMD ["./start.sh"]
