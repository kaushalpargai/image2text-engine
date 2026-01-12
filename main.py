import os
import sys
from pathlib import Path
from datetime import datetime
import shutil
import json
from typing import List
import traceback

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from paddleocr import PaddleOCR

# Import configuration
from config import ACTIVE_CONFIG

app = FastAPI(title=ACTIVE_CONFIG.APP_NAME, version=ACTIVE_CONFIG.APP_VERSION)

# CORS middleware
if ACTIVE_CONFIG.CORS_ENABLED:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ACTIVE_CONFIG.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Initialize PaddleOCR
print(f"Initializing PaddleOCR (lang={ACTIVE_CONFIG.OCR_LANG})...")
# use_angle_cls=True is generally good, but sticking to previous simple init unless needed
# Adding use_gpu=False as a safe default or based on config if we had it, but default is fine.
ocr = PaddleOCR(lang=ACTIVE_CONFIG.OCR_LANG) 
print("PaddleOCR initialized successfully")


# Create necessary directories
UPLOAD_DIR = Path(ACTIVE_CONFIG.UPLOAD_DIR)
RESULTS_DIR = Path(ACTIVE_CONFIG.RESULTS_DIR)
STATIC_DIR = Path("static") # Static assets usually stay with the code

try:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"Error creating directories: {e}")

# Results storage
RESULTS_FILE = RESULTS_DIR / "ocr_results.json"

def load_results():
    """Load existing results from JSON file"""
    if RESULTS_FILE.exists():
        try:
            with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_results(results):
    """Save results to JSON file"""
    try:
        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving results: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    html_file = STATIC_DIR / "index.html"
    if html_file.exists():
        return html_file.read_text(encoding='utf-8')
    return "<h1>PaddleOCR Web App</h1><p>Please create static/index.html</p>"

@app.post("/upload")
async def upload_images(files: List[UploadFile] = File(...)):
    """Upload multiple images"""
    uploaded_files = []
    
    for file in files:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not an image")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        # Sanitize filename just in case
        safe_filename = Path(file.filename).name
        unique_filename = f"{timestamp}_{safe_filename}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append({
                "filename": unique_filename,
                "original_name": file.filename,
                "path": str(file_path)
            })
        except Exception as e:
            print(f"Error saving file {unique_filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    
    return JSONResponse(content={
        "message": f"Successfully uploaded {len(uploaded_files)} files",
        "files": uploaded_files
    })

@app.post("/process")
async def process_images(file_info: dict):
    """Process uploaded images with PaddleOCR"""
    files = file_info.get("files", [])
    results = load_results()
    processed_results = []
    
    for file_data in files:
        filename = file_data.get("filename")
        if not filename:
            continue
            
        file_path = UPLOAD_DIR / filename
        
        if not file_path.exists():
            continue
        
        try:
            # Perform OCR with PaddleOCR
            print(f"Processing file: {file_path}")
            # ocr.ocr returns a list of results
            ocr_result = ocr.ocr(str(file_path))
            print(f"OCR result type: {type(ocr_result)}")
            
            # Extract text from OCR result
            # PaddleOCR can return different formats depending on version
            extracted_text = ""
            confidence = 0
            
            print(f"OCR result structure: {type(ocr_result)}")
            
            # Handle different result formats
            if ocr_result:
                # Format 1: New PaddleX format (dictionary with 'rec_texts' and 'rec_scores')
                if isinstance(ocr_result, list) and len(ocr_result) > 0:
                    first_result = ocr_result[0]
                    
                    if isinstance(first_result, dict):
                        # Dictionary format (newer PaddleX)
                        print("Detected dictionary format (PaddleX)")
                        rec_texts = first_result.get('rec_texts', [])
                        rec_scores = first_result.get('rec_scores', [])
                        
                        if rec_texts:
                            for i, text in enumerate(rec_texts):
                                extracted_text += str(text) + "\n"
                                if i < len(rec_scores):
                                    confidence = max(confidence, rec_scores[i])
                            print(f"Extracted {len(rec_texts)} text items")
                        else:
                            print("No rec_texts found in result")
                    
                    elif isinstance(first_result, list):
                        # List format (older PaddleOCR)
                        print("Detected list format (PaddleOCR)")
                        for line in first_result:
                            try:
                                # line is like [[x,y...], (text, score)]
                                if isinstance(line, (list, tuple)) and len(line) >= 2:
                                    text_info = line[1]
                                    if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                                        text = text_info[0]
                                        score = text_info[1]
                                        
                                        extracted_text += str(text) + "\n"
                                        confidence = max(confidence, score)
                            except (IndexError, TypeError) as e:
                                print(f"Error parsing line: {e}")
                                continue
                
                if extracted_text:
                    print(f"Extracted text length: {len(extracted_text)}")
                else:
                    print("No text detected or empty result")
            else:
                print("OCR result is None or empty")

            # Create result object
            result_obj = {
                "filename": filename,
                "original_name": file_data.get("original_name"),
                "image_url": f"/uploads/{filename}",
                "text": extracted_text.strip() if extracted_text else "No text detected",
                "timestamp": datetime.now().isoformat(),
                "confidence": float(confidence) # Ensure it's JSON serializable
            }
            
            results.append(result_obj)
            processed_results.append(result_obj)

            # Delete the image after successful processing
            try:
                if file_path.exists():
                    file_path.unlink()
                    print(f"Successfully deleted processed file: {filename}")
            except Exception as e:
                print(f"Failed to delete file {filename}: {e}")
            
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            traceback.print_exc()
            processed_results.append({
                "filename": filename,
                "original_name": file_data.get("original_name"),
                "image_url": f"/uploads/{filename}",
                "error": str(e),
                "text": f"Error processing image: {str(e)}"
            })
    
    # Save results
    save_results(results)
    
    return JSONResponse(content={
        "message": f"Processed {len(processed_results)} images",
        "results": processed_results
    })

@app.get("/results")
async def get_results():
    """Get all OCR results"""
    results = load_results()
    return JSONResponse(content={"results": results})

@app.delete("/results")
async def clear_results():
    """Clear all results"""
    save_results([])
    return JSONResponse(content={"message": "Results cleared"})

# Mount static files
# We mount uploads so they can be served. 
# In production, you might serve these via Nginx, but valid for app-serving too.
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

if __name__ == "__main__":
    import uvicorn
    print(f"Starting server on {ACTIVE_CONFIG.HOST}:{ACTIVE_CONFIG.PORT} in {ACTIVE_CONFIG.ENV} mode")
    uvicorn.run(
        "main:app", 
        host=ACTIVE_CONFIG.HOST, 
        port=ACTIVE_CONFIG.PORT, 
        reload=ACTIVE_CONFIG.DEBUG
    )
