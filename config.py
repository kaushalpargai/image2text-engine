import os
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables based on APP_ENV
env = os.getenv("APP_ENV", "local").lower()
if env == "production":
    load_dotenv(".env.production")
else:
    load_dotenv(".env.local")

class Config:
    """Base configuration"""
    APP_NAME = "Image2Text Engine"
    APP_VERSION = "1.0.0"
    
    # Get environment
    ENV = env
    
    # Upload and Results directories
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
    RESULTS_DIR = os.getenv("RESULTS_DIR", "./results")
    
    # OCR Settings
    OCR_TIMEOUT = int(os.getenv("OCR_TIMEOUT", "60"))
    OCR_LANG = "en"
    
    # CORS
    CORS_ENABLED = os.getenv("ENABLE_CORS", "true").lower() == "true"
    CORS_ORIGINS: List[str] = []
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Server
    HOST = os.getenv("IMAGE2TEXT_HOST", "127.0.0.1")
    PORT = int(os.getenv("IMAGE2TEXT_PORT", "8000"))
    DEBUG = False

class LocalConfig(Config):
    """Local development configuration"""
    ENV = "local"
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "*"  # Be permissive locally
    ]
    UPLOAD_DIR = "./uploads"
    RESULTS_DIR = "./results"
    OCR_TIMEOUT = 60

class ProductionConfig(Config):
    """Production configuration"""
    ENV = "production"
    DEBUG = False
    LOG_LEVEL = "INFO"
    CORS_ORIGINS = [
        "https://yourdomain.com",
        "https://api.yourdomain.com",
        "http://email-verification:3000",  # Docker network example
        "http://email-verification:8080",
    ]
    UPLOAD_DIR = "/app/uploads"
    RESULTS_DIR = "/app/results"
    OCR_TIMEOUT = 120

# Select config based on environment
config_map = {
    "local": LocalConfig,
    "production": ProductionConfig,
}

ACTIVE_CONFIG = config_map.get(env, LocalConfig)()

# Ensure directories exist
try:
    os.makedirs(ACTIVE_CONFIG.UPLOAD_DIR, exist_ok=True)
    os.makedirs(ACTIVE_CONFIG.RESULTS_DIR, exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create directories: {e}")
