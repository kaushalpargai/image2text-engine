# PaddleOCR Local Web Application

A powerful local web application for extracting text from images using PaddleOCR. Upload thousands of images and receive OCR text displayed side-by-side with each image. 100% local processing with no rate limits!

![PaddleOCR Engine](https://img.shields.io/badge/PaddleOCR-Powered-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![No Rate Limits](https://img.shields.io/badge/Rate%20Limits-None-brightgreen)

## ✨ Features

- 🚀 **Fast OCR Processing** - Powered by PaddleOCR
- 📁 **Batch Upload** - Process multiple images simultaneously
- 💾 **Results Persistence** - All results saved locally in JSON
- 🎨 **Modern UI** - Glassmorphism effects with dark mode
- 📊 **Progress Tracking** - Real-time upload and processing status
- 🔒 **100% Private** - All processing happens on your machine
- ∞ **No Rate Limits** - Process unlimited images
- 📋 **Copy to Clipboard** - Easy text extraction
- 🖼️ **Side-by-Side Display** - Image and text together

## 🛠️ Technology Stack

- **Backend**: FastAPI + PaddleOCR
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Storage**: JSON-based results storage
- **OCR Engine**: PaddleOCR with angle classification

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## 🚀 Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd "c:\Users\kaush\OneDrive\Desktop\PythonPractice\Image2Text Engine"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   This will install:
   - paddlepaddle
   - paddleocr
   - fastapi
   - uvicorn
   - python-multipart
   - pillow

## 🎯 Usage

1. **Start the server**
   ```bash
   uvicorn main:app --reload
   ```

   Or run directly:
   ```bash
   python main.py
   ```

2. **Open your browser**
   Navigate to: `http://127.0.0.1:8000`

3. **Upload images**
   - Click the upload area or drag & drop images
   - Select multiple images (supports all common formats)
   - Click "Upload & Process"

4. **View results**
   - Images and extracted text appear side-by-side
   - Copy text with one click
   - Results are automatically saved

## 📁 Project Structure

```
Image2Text Engine/
├── main.py                 # FastAPI backend server
├── requirements.txt        # Python dependencies
├── static/
│   ├── index.html         # Frontend UI
│   ├── styles.css         # Modern styling
│   └── script.js          # Interactive functionality
├── uploads/               # Uploaded images (auto-created)
├── results/               # OCR results JSON (auto-created)
└── README.md             # This file
```

## 🔧 API Endpoints

### `GET /`
Serves the main web interface

### `POST /upload`
Upload multiple images
- **Body**: multipart/form-data with files
- **Returns**: List of uploaded file information

### `POST /process`
Process uploaded images with OCR
- **Body**: JSON with file information
- **Returns**: OCR results with extracted text

### `GET /results`
Retrieve all processed results
- **Returns**: JSON array of all OCR results

### `DELETE /results`
Clear all saved results
- **Returns**: Confirmation message

## ⚡ Performance Tips

### For Large Volumes (1000+ images)

1. **Enable GPU Acceleration** (if available)
   ```python
   # In main.py, modify OCR initialization:
   ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=True)
   ```

2. **Batch Processing**
   - Upload images in batches of 50-100
   - Monitor system resources

3. **Increase Workers**
   ```bash
   uvicorn main:app --workers 4
   ```

## 🎨 UI Features

- **Glassmorphism Design** - Modern frosted glass effects
- **Dark Mode** - Easy on the eyes
- **Smooth Animations** - Micro-interactions for better UX
- **Responsive Layout** - Works on all screen sizes
- **Progress Indicators** - Real-time feedback
- **Drag & Drop** - Intuitive file upload

## 🔐 Privacy & Security

- ✅ All processing happens locally
- ✅ No data sent to external servers
- ✅ No API keys required
- ✅ No rate limits
- ✅ Full data privacy

## 🚀 Future Enhancements

- [ ] Text highlighting on images
- [ ] Search functionality
- [ ] Export results (CSV, TXT, JSON)
- [ ] Multi-language support
- [ ] PDF support
- [ ] Docker deployment
- [ ] Database integration (SQLite/PostgreSQL)
- [ ] Batch download results

## 🐛 Troubleshooting

### PaddleOCR Installation Issues
If you encounter issues installing PaddleOCR:
```bash
pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple
pip install paddleocr
```

### Port Already in Use
Change the port in `main.py`:
```python
uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)
```

### Memory Issues with Large Batches
- Process fewer images at once
- Close other applications
- Consider enabling GPU acceleration

## 📝 License

This project is open source and available for personal and commercial use.

## 🙏 Acknowledgments

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - OCR engine
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Uvicorn](https://www.uvicorn.org/) - ASGI server

## 📧 Support

For issues or questions, please check the troubleshooting section above.

---

**Made with ❤️ using PaddleOCR and FastAPI**
