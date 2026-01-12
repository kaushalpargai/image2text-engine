# Integration Examples - Image2Text Engine

This document provides practical examples for connecting other services to your Image2Text Engine Docker container.

## Quick Start

### 1. Current Setup (Single Container)
Your container is already running:
```bash
docker ps
# Container: image2text_engine
# Port: 8005:8005
# Access: http://localhost:8005
```

### 2. Connect from Host Machine
Any application on your Windows machine can connect using `http://localhost:8005`

---

## Method 1: Connect from Another Docker Container

### Step 1: Create a Docker Network
```bash
# Create a custom network
docker network create ocr-network

# Connect your existing container to the network
docker network connect ocr-network image2text_engine
```

### Step 2: Run Another Container on the Same Network
```bash
# Example: Run a Python container that can access the OCR service
docker run -it --network ocr-network python:3.9-slim bash

# Inside the container, install requests
pip install requests

# Test connection
python3 -c "import requests; print(requests.get('http://image2text_engine:8005/').status_code)"
```

**Key Point:** Use the container name `image2text_engine` as the hostname when connecting from other containers on the same network.

---

## Method 2: Using Docker Compose (Recommended)

### Step 1: Use the Multi-Service Compose File
```bash
# Stop the current container
docker-compose down

# Start with the multi-service configuration
docker-compose -f docker-compose-multi-service.yml up -d
```

### Step 2: Test the Client Container
```bash
# Install dependencies in the client container
docker exec -it ocr_client pip install -r /app/requirements.txt

# Copy test image to client container
docker cp test_image.png ocr_client:/app/test_image.png

# Run the test client
docker exec -it ocr_client python /app/test_client.py
```

---

## Method 3: API Integration Examples

### Python Example (from Host or Container)
```python
import requests

# From host machine
OCR_URL = "http://localhost:8005"

# From another Docker container on same network
# OCR_URL = "http://image2text_engine:8005"

# Upload and process image
def extract_text(image_path):
    # Upload
    with open(image_path, 'rb') as f:
        files = {'files': f}
        upload_response = requests.post(f"{OCR_URL}/upload", files=files)
    
    # Process
    file_info = upload_response.json()
    process_response = requests.post(f"{OCR_URL}/process", json=file_info)
    
    # Get results
    results = process_response.json()
    return results['results'][0]['text']

# Usage
text = extract_text('invoice.png')
print(text)
```

### cURL Example
```bash
# From host machine
curl -X POST http://localhost:8005/upload \
  -F "files=@test_image.png"

# From another container
curl -X POST http://image2text_engine:8005/upload \
  -F "files=@test_image.png"
```

### Node.js Example
```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

// From host machine
const OCR_URL = 'http://localhost:8005';

// From another Docker container
// const OCR_URL = 'http://image2text_engine:8005';

async function extractText(imagePath) {
  // Upload
  const form = new FormData();
  form.append('files', fs.createReadStream(imagePath));
  
  const uploadResponse = await axios.post(`${OCR_URL}/upload`, form, {
    headers: form.getHeaders()
  });
  
  // Process
  const processResponse = await axios.post(`${OCR_URL}/process`, 
    uploadResponse.data
  );
  
  return processResponse.data.results[0].text;
}

// Usage
extractText('./invoice.png').then(text => console.log(text));
```

---

## Available API Endpoints

### 1. Upload Image
```http
POST /upload
Content-Type: multipart/form-data

Body:
- files: <image file(s)>

Response:
{
  "message": "Successfully uploaded 1 files",
  "files": [
    {
      "filename": "20260110_100000_image.png",
      "original_name": "image.png",
      "path": "/app/uploads/20260110_100000_image.png"
    }
  ]
}
```

### 2. Process Image
```http
POST /process
Content-Type: application/json

Body:
{
  "files": [
    {
      "filename": "20260110_100000_image.png",
      "original_name": "image.png"
    }
  ]
}

Response:
{
  "message": "Processed 1 images",
  "results": [
    {
      "filename": "20260110_100000_image.png",
      "text": "Extracted text here...",
      "confidence": 0.95,
      "timestamp": "2026-01-10T10:00:00"
    }
  ]
}
```

### 3. Get All Results
```http
GET /results

Response:
{
  "results": [...]
}
```

### 4. Clear Results
```http
DELETE /results

Response:
{
  "message": "Results cleared"
}
```

---

## Testing the Integration

### Test 1: From Host Machine
```bash
# Test connection
curl http://localhost:8005/

# Upload and process an image
curl -X POST http://localhost:8005/upload -F "files=@test_image.png"
```

### Test 2: From Another Container
```bash
# Create network and connect containers
docker network create ocr-network
docker network connect ocr-network image2text_engine

# Run test container
docker run -it --network ocr-network --rm python:3.9-slim bash

# Inside the container:
pip install requests
python3 -c "
import requests
response = requests.get('http://image2text_engine:8005/')
print(f'Status: {response.status_code}')
"
```

### Test 3: Using the Client Example
```bash
# Start multi-service setup
docker-compose -f docker-compose-multi-service.yml up -d

# Run the test client
docker exec ocr_client pip install -r /app/requirements.txt
docker cp test_image.png ocr_client:/app/
docker exec ocr_client python /app/test_client.py
```

---

## Common Connection Patterns

### Pattern 1: Microservices Architecture
```
┌─────────────────┐      ┌──────────────────┐
│   Web Frontend  │─────▶│  Backend API     │
│   (Port 3000)   │      │  (Port 8000)     │
└─────────────────┘      └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Image2Text OCR  │
                         │  (Port 8005)     │
                         └──────────────────┘
```

### Pattern 2: Batch Processing
```
┌─────────────────┐      ┌──────────────────┐
│  Batch Processor│─────▶│  Image2Text OCR  │
│  (Cron/Worker)  │      │  (Port 8005)     │
└─────────────────┘      └──────────────────┘
```

### Pattern 3: API Gateway
```
┌─────────────────┐      ┌──────────────────┐
│   API Gateway   │─────▶│  Image2Text OCR  │
│  (Nginx/Kong)   │      │  (Port 8005)     │
└─────────────────┘      └──────────────────┘
```

---

## Troubleshooting

### Issue: Cannot connect from another container
**Solution:**
```bash
# Verify both containers are on the same network
docker network inspect ocr-network

# Ensure the container is running
docker ps | grep image2text_engine
```

### Issue: Connection refused
**Solution:**
```bash
# Check if the service is listening
docker exec image2text_engine netstat -tulpn | grep 8005

# Check logs
docker logs image2text_engine
```

### Issue: DNS resolution fails
**Solution:**
Use the exact container name as defined in docker-compose or when creating the container.

---

## Next Steps

1. **Test the basic connection** using cURL or Python
2. **Integrate into your application** using the API examples
3. **Scale if needed** using Docker Swarm or Kubernetes
4. **Add monitoring** with health checks and logging
5. **Secure the connection** with API keys or OAuth

For more detailed information, see the [Service Integration Guide](./service_integration_guide.md).
