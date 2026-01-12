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
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory structure for data (if not mapped via volume, though they should be)
RUN mkdir -p uploads results

# Expose port
EXPOSE 8000

# Set production environment by default
ENV APP_ENV=production

# Run the application
CMD ["python", "main.py"]
