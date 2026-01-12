#!/usr/bin/env python3
"""
Example client to connect to Image2Text Engine from another Docker container
"""
import os
import requests
import json
import time

# Get OCR service URL from environment variable
OCR_SERVICE_URL = os.getenv('OCR_SERVICE_URL', 'http://localhost:8005')

def wait_for_service(max_retries=30, delay=2):
    """Wait for the OCR service to be ready"""
    print(f"Waiting for OCR service at {OCR_SERVICE_URL}...")
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{OCR_SERVICE_URL}/", timeout=5)
            if response.status_code == 200:
                print("✓ OCR service is ready!")
                return True
        except requests.exceptions.RequestException as e:
            print(f"Attempt {i+1}/{max_retries}: Service not ready yet...")
            time.sleep(delay)
    
    print("✗ OCR service failed to start")
    return False

def upload_image(image_path):
    """Upload an image to the OCR service"""
    url = f"{OCR_SERVICE_URL}/upload"
    
    try:
        with open(image_path, 'rb') as f:
            files = {'files': (os.path.basename(image_path), f, 'image/png')}
            response = requests.post(url, files=files)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None

def process_image(file_info):
    """Process uploaded image with OCR"""
    url = f"{OCR_SERVICE_URL}/process"
    
    try:
        response = requests.post(url, json=file_info)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def get_results():
    """Get all OCR results"""
    url = f"{OCR_SERVICE_URL}/results"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting results: {e}")
        return None

def main():
    """Main function demonstrating OCR service integration"""
    print("=" * 60)
    print("Image2Text Engine - Client Example")
    print("=" * 60)
    
    # Wait for service to be ready
    if not wait_for_service():
        return
    
    print("\n" + "=" * 60)
    print("Example 1: Upload and Process Image")
    print("=" * 60)
    
    # Example image path (you would replace this with actual image)
    # For testing in container, you can mount a volume with test images
    test_image = "/app/test_image.png"
    
    if os.path.exists(test_image):
        print(f"\n1. Uploading image: {test_image}")
        upload_result = upload_image(test_image)
        
        if upload_result:
            print(f"✓ Upload successful!")
            print(json.dumps(upload_result, indent=2))
            
            print(f"\n2. Processing image with OCR...")
            process_result = process_image(upload_result)
            
            if process_result:
                print(f"✓ Processing complete!")
                print(json.dumps(process_result, indent=2))
                
                # Extract text from results
                if 'results' in process_result:
                    for result in process_result['results']:
                        print(f"\n--- Extracted Text ---")
                        print(result.get('text', 'No text found'))
                        print(f"Confidence: {result.get('confidence', 0):.2%}")
    else:
        print(f"Test image not found: {test_image}")
        print("To test with an actual image:")
        print("1. Mount a volume with test images")
        print("2. Update the test_image path")
    
    print("\n" + "=" * 60)
    print("Example 2: Get All Results")
    print("=" * 60)
    
    results = get_results()
    if results:
        print(f"✓ Retrieved {len(results.get('results', []))} results")
        print(json.dumps(results, indent=2))
    
    print("\n" + "=" * 60)
    print("Integration Examples Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
