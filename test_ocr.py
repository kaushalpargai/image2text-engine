from paddleocr import PaddleOCR
from PIL import Image, ImageDraw, ImageFont

# Create a test image with text
img = Image.new('RGB', (300, 100), color='white')
d = ImageDraw.Draw(img)
d.text((10, 30), "Hello OCR Test", fill='black')
img.save('test_image.png')

# Initialize PaddleOCR
print("Initializing PaddleOCR...")
ocr = PaddleOCR(lang='en')

# Test OCR
print("Running OCR on test image...")
result = ocr.ocr('test_image.png')
print(f"OCR Result: {result}")

# Extract text
if result and result[0]:
    for line in result[0]:
        if line and len(line) > 1:
            print(f"Detected text: {line[1][0]}")
else:
    print("No text detected")
